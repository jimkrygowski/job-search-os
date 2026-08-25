#!/usr/bin/env python3
"""
Extract new messages from a saved Gmail thread JSON file.
Strips HTML, quoted history, and boilerplate — returns only readable new content.

Usage:
    python3 gmail_extract.py <thread_json_file> [--after YYYY-MM-DD] [--latest N]

Examples:
    # Show all messages newer than June 15
    python3 gmail_extract.py thread.json --after 2026-06-15

    # Show only the 2 most recent messages
    python3 gmail_extract.py thread.json --latest 2

    # Show everything (all messages, cleaned)
    python3 gmail_extract.py thread.json
"""

import email.utils
import html
import json
import re
import sys
import argparse
from datetime import datetime, timezone


# Patterns that unambiguously mark the start of quoted history on their own.
UNAMBIGUOUS_QUOTE_PATTERNS = [
    r'^On .{10,} wrote:$',
    r'^-{3,}\s*(Original|Forwarded)\s+(Message|message)\s*-{3,}',
]

# Header-field lines (Outlook-style quoted blocks). A single line starting
# with one of these is not enough on its own — a genuine message body can
# start a line with "From: my perspective..." — so these only count as a
# quote boundary when another header field follows within a couple of
# lines, matching the shape of a real quoted-header block.
HEADER_FIELD_PATTERNS = [
    r'^From:\s+',
    r'^Sent:\s+',
    r'^To:\s+',
    r'^Subject:\s+',
]

BODY_FIELD_CANDIDATES = ['plaintextBody', 'plaintextbody', 'plainTextBody', 'textBody', 'text']
HTML_FIELD_CANDIDATES = ['htmlBody', 'htmlbody', 'html']


def strip_html(raw_html):
    raw_html = re.sub(r'<style[^>]*>.*?</style>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    raw_html = re.sub(r'<script[^>]*>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    raw_html = re.sub(r'<br\s*/?>', '\n', raw_html, flags=re.IGNORECASE)
    raw_html = re.sub(r'</?(p|div|tr|li|h[1-6])[^>]*>', '\n', raw_html, flags=re.IGNORECASE)
    raw_html = re.sub(r'<[^>]+>', '', raw_html)
    raw_html = html.unescape(raw_html)
    lines = [l.strip() for l in raw_html.splitlines()]
    lines = [l for l in lines if l]
    return '\n'.join(lines)


def strip_quoted(text):
    lines = text.splitlines()
    output = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if any(re.match(p, stripped) for p in UNAMBIGUOUS_QUOTE_PATTERNS):
            break
        if any(re.match(p, stripped) for p in HEADER_FIELD_PATTERNS):
            window = [l.strip() for l in lines[i + 1:i + 3]]
            if any(re.match(p, w) for w in window for p in HEADER_FIELD_PATTERNS):
                break
        if stripped.startswith('>'):
            i += 1
            continue
        output.append(lines[i])
        i += 1
    return '\n'.join(output).strip()


def parse_date(date_str):
    """Parse a message date that may be ISO 8601 or RFC 2822 (the standard
    email Date header format). Returns None only if neither format parses —
    callers must not treat that as "very old", since silently excluding an
    unparseable-but-recent message is the exact bug this tool exists to
    prevent."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        pass
    try:
        return email.utils.parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        return None


def extract_body(msg):
    """Returns (body_text, field_was_found). field_was_found lets callers
    distinguish "we recognized a body field and it was empty" (genuinely
    empty message) from "we didn't recognize any body field name" (likely
    schema mismatch / extraction failure) — the two silently looked
    identical before this fix."""
    for key in BODY_FIELD_CANDIDATES:
        if key in msg:
            return msg[key] or '', True
    for key in HTML_FIELD_CANDIDATES:
        if key in msg:
            return strip_html(msg[key] or ''), True
    return '', False


def format_message(msg):
    sender = msg.get('sender', 'Unknown')
    date = msg.get('date', '')
    subject = msg.get('subject', '')

    body, field_found = extract_body(msg)
    body = strip_quoted(body)

    lines = [
        f"FROM:    {sender}",
        f"DATE:    {date}",
    ]
    if subject:
        lines.append(f"SUBJECT: {subject}")
    lines.append('-' * 60)
    if body:
        lines.append(body)
    elif field_found:
        lines.append('[no body]')
    else:
        lines.append('[no body — no recognized body field in source JSON; '
                      'expected one of plaintextBody/htmlBody]')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Extract messages from Gmail thread JSON')
    parser.add_argument('file', help='Path to thread JSON file')
    parser.add_argument('--after', help='Only show messages after this date (YYYY-MM-DD)')
    parser.add_argument('--latest', type=int, help='Only show the N most recent messages')
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

    messages = data.get('messages', [])

    if args.after:
        cutoff = datetime.fromisoformat(args.after).replace(tzinfo=timezone.utc)

        def after_cutoff(msg):
            parsed = parse_date(msg.get('date', ''))
            if parsed is None:
                # Unparseable date: fail open. Silently excluding a message
                # we couldn't date is exactly the bug this tool exists to
                # prevent — better to show an extra message than drop one.
                return True
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed > cutoff

        messages = [m for m in messages if after_cutoff(m)]

    if args.latest is not None:
        messages = messages[-args.latest:] if args.latest > 0 else []

    if not messages:
        print('No messages found matching criteria.')
        return

    print(f'=== {len(messages)} message(s) ===\n')
    for msg in messages:
        print(format_message(msg))
        print()


if __name__ == '__main__':
    main()
