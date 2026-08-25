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

import json
import re
import sys
import argparse
from datetime import datetime, timezone


QUOTE_PATTERNS = [
    r'^On .{10,} wrote:$',
    r'^-{3,}\s*(Original|Forwarded)\s+(Message|message)\s*-{3,}',
    r'^From:\s+',
    r'^Sent:\s+',
    r'^To:\s+',
    r'^Subject:\s+',
]


def strip_html(html):
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</?(p|div|tr|li|h[1-6])[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', '', html)
    html = (html
            .replace('&nbsp;', ' ')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&amp;', '&')
            .replace('&#39;', "'")
            .replace('&quot;', '"'))
    lines = [l.strip() for l in html.splitlines()]
    lines = [l for l in lines if l]
    return '\n'.join(lines)


def strip_quoted(text):
    lines = text.splitlines()
    output = []
    for line in lines:
        stripped = line.strip()
        if any(re.match(p, stripped) for p in QUOTE_PATTERNS):
            break
        if stripped.startswith('>'):
            continue
        output.append(line)
    return '\n'.join(output).strip()


def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception:
        return None


def format_message(msg):
    sender = msg.get('sender', 'Unknown')
    date = msg.get('date', '')
    subject = msg.get('subject', '')

    body = msg.get('plaintextBody') or msg.get('plaintextbody') or ''
    if not body:
        html = msg.get('htmlBody') or msg.get('htmlbody') or ''
        if html:
            body = strip_html(html)

    body = strip_quoted(body)

    lines = [
        f"FROM:    {sender}",
        f"DATE:    {date}",
    ]
    if subject:
        lines.append(f"SUBJECT: {subject}")
    lines.append('-' * 60)
    lines.append(body or '[no body]')
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
        messages = [m for m in messages if (parse_date(m.get('date', '')) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff]

    if args.latest:
        messages = messages[-args.latest:]

    if not messages:
        print('No messages found matching criteria.')
        return

    print(f'=== {len(messages)} message(s) ===\n')
    for msg in messages:
        print(format_message(msg))
        print()


if __name__ == '__main__':
    main()
