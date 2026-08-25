import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gmail_extract  # noqa: E402


class ParseDateTest(unittest.TestCase):
    def test_parses_iso8601(self):
        parsed = gmail_extract.parse_date("2026-08-25T14:30:00Z")
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 8)
        self.assertEqual(parsed.day, 25)

    def test_parses_rfc2822_email_header_format(self):
        # This is the standard format of a real email Date: header — the
        # exact case the original implementation silently failed on.
        parsed = gmail_extract.parse_date("Mon, 25 Aug 2026 14:30:00 -0400")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 8)
        self.assertEqual(parsed.day, 25)

    def test_truly_unparseable_date_returns_none(self):
        self.assertIsNone(gmail_extract.parse_date("not a date at all"))

    def test_empty_date_returns_none(self):
        self.assertIsNone(gmail_extract.parse_date(""))


class AfterCutoffFailOpenTest(unittest.TestCase):
    """Exercises main()'s --after filtering end-to-end via the CLI, since
    the fail-open behavior lives in main(), not in parse_date() itself."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.script = str(Path(__file__).parent / "gmail_extract.py")

    def tearDown(self):
        self._tmpdir.cleanup()

    def write_thread(self, messages):
        path = Path(self._tmpdir.name) / "thread.json"
        path.write_text(json.dumps({"messages": messages}))
        return path

    def run_cli(self, thread_path, *args):
        return subprocess.run(
            [sys.executable, self.script, str(thread_path), *args],
            capture_output=True, text=True,
        )

    def test_rfc2822_date_after_cutoff_is_included(self):
        thread = self.write_thread([
            {"sender": "a@example.com", "date": "Mon, 25 Aug 2026 14:30:00 -0400",
             "plaintextBody": "hello"},
        ])
        result = self.run_cli(thread, "--after", "2026-08-20")
        self.assertIn("hello", result.stdout)
        self.assertIn("1 message(s)", result.stdout)

    def test_unparseable_date_is_included_not_silently_dropped(self):
        thread = self.write_thread([
            {"sender": "a@example.com", "date": "garbled-not-a-real-date",
             "plaintextBody": "important new message"},
        ])
        result = self.run_cli(thread, "--after", "2026-08-20")
        self.assertIn("important new message", result.stdout)
        self.assertIn("1 message(s)", result.stdout)

    def test_iso_date_before_cutoff_is_excluded(self):
        thread = self.write_thread([
            {"sender": "a@example.com", "date": "2026-01-01T00:00:00Z",
             "plaintextBody": "old message"},
        ])
        result = self.run_cli(thread, "--after", "2026-08-20")
        self.assertIn("No messages found", result.stdout)


class LatestFlagTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.script = str(Path(__file__).parent / "gmail_extract.py")

    def tearDown(self):
        self._tmpdir.cleanup()

    def write_thread(self, n):
        messages = [
            {"sender": "a@example.com", "date": "2026-08-25T00:00:00Z",
             "plaintextBody": f"message {i}"}
            for i in range(n)
        ]
        path = Path(self._tmpdir.name) / "thread.json"
        path.write_text(json.dumps({"messages": messages}))
        return path

    def run_cli(self, thread_path, *args):
        return subprocess.run(
            [sys.executable, self.script, str(thread_path), *args],
            capture_output=True, text=True,
        )

    def test_latest_zero_shows_no_messages(self):
        thread = self.write_thread(3)
        result = self.run_cli(thread, "--latest", "0")
        self.assertIn("No messages found", result.stdout)

    def test_latest_two_shows_two_most_recent(self):
        thread = self.write_thread(3)
        result = self.run_cli(thread, "--latest", "2")
        self.assertNotIn("message 0", result.stdout)
        self.assertIn("message 1", result.stdout)
        self.assertIn("message 2", result.stdout)


class StripQuotedTest(unittest.TestCase):
    def test_removes_on_wrote_quote_block(self):
        text = "New content here.\nOn Mon, Aug 25, 2026 at 2:00 PM Jane wrote:\n> old stuff"
        self.assertEqual(gmail_extract.strip_quoted(text), "New content here.")

    def test_removes_real_outlook_style_quoted_header_block(self):
        text = (
            "My reply text.\n"
            "From: Someone\n"
            "Sent: Monday, August 25, 2026\n"
            "To: Me\n"
            "Subject: Re: thing\n"
            "quoted original content"
        )
        self.assertEqual(gmail_extract.strip_quoted(text), "My reply text.")

    def test_body_line_starting_with_from_colon_is_not_treated_as_quote_boundary(self):
        # Real message content that happens to start a line with "From:"
        # but isn't followed by another header field — not a quoted block.
        text = "From: my perspective, this role looks like a great fit."
        self.assertEqual(
            gmail_extract.strip_quoted(text),
            "From: my perspective, this role looks like a great fit.",
        )


class ExtractBodyTest(unittest.TestCase):
    def test_recognized_field_with_content(self):
        body, found = gmail_extract.extract_body({"plaintextBody": "hello"})
        self.assertEqual(body, "hello")
        self.assertTrue(found)

    def test_recognized_field_but_empty_is_distinguishable_from_missing(self):
        body, found = gmail_extract.extract_body({"plaintextBody": ""})
        self.assertEqual(body, "")
        self.assertTrue(found)  # field existed, message is genuinely empty

    def test_unrecognized_schema_reports_field_not_found(self):
        body, found = gmail_extract.extract_body({"textBody": "hello"})
        # "textBody" isn't in the exact original two-casing guess, but it
        # is a real candidate schema name — confirm it's still recognized.
        self.assertEqual(body, "hello")
        self.assertTrue(found)

    def test_truly_unknown_schema_is_not_silently_treated_as_empty_message(self):
        body, found = gmail_extract.extract_body({"someOtherField": "hello"})
        self.assertEqual(body, "")
        self.assertFalse(found)

    def test_format_message_distinguishes_empty_from_unrecognized_schema(self):
        empty_msg = gmail_extract.format_message({"plaintextBody": ""})
        self.assertIn("[no body]", empty_msg)
        self.assertNotIn("no recognized body field", empty_msg)

        unrecognized_msg = gmail_extract.format_message({"someOtherField": "x"})
        self.assertIn("no recognized body field", unrecognized_msg)


class StripHtmlTest(unittest.TestCase):
    def test_decodes_common_named_entities_beyond_the_original_hardcoded_six(self):
        html_input = "<p>It&rsquo;s here &mdash; don&#8217;t miss it&hellip;</p>"
        result = gmail_extract.strip_html(html_input)
        self.assertIn("It’s here", result)
        self.assertIn("—", result)  # mdash
        self.assertIn("…", result)  # hellip
        self.assertNotIn("&rsquo;", result)
        self.assertNotIn("&mdash;", result)
        self.assertNotIn("&#8217;", result)
        self.assertNotIn("&hellip;", result)


if __name__ == "__main__":
    unittest.main()
