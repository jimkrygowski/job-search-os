import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tracker  # noqa: E402


class TrackerLibTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def test_read_table_missing_file_returns_no_rows(self):
        self.assertEqual(tracker.read_table(Path("tracker.md")), [])

    def test_write_then_read_round_trip(self):
        rows = [{
            "Company": "Altana", "Role": "VP Engineering", "Stage": "Screen",
            "Last Activity": "2026-08-19", "Next Action": "Follow up",
            "Next Action Date": "2026-08-26",
        }]
        tracker.write_table(Path("tracker.md"), rows, tracker.ACTIVE_TITLE)
        self.assertEqual(tracker.read_table(Path("tracker.md")), rows)

    def test_round_trip_survives_pipe_and_comma_in_cell(self):
        rows = [{
            "Company": "Bed | Bath & Beyond, Inc.", "Role": "CTO",
            "Stage": "Identified", "Last Activity": "2026-08-20",
            "Next Action": "", "Next Action Date": "",
        }]
        tracker.write_table(Path("tracker.md"), rows, tracker.ACTIVE_TITLE)
        self.assertEqual(tracker.read_table(Path("tracker.md")), rows)

    def test_no_column_alignment_padding(self):
        rows = [
            {"Company": "A", "Role": "Short", "Stage": "S",
             "Last Activity": "2026-01-01", "Next Action": "",
             "Next Action Date": ""},
            {"Company": "A Very Long Company Name Inc",
             "Role": "Longer Role Title", "Stage": "S",
             "Last Activity": "2026-01-01", "Next Action": "",
             "Next Action Date": ""},
        ]
        text = tracker.serialize_table(rows, tracker.ACTIVE_TITLE)
        short_row_line = [l for l in text.splitlines() if l.startswith("| A |")]
        self.assertEqual(short_row_line, ["| A | Short | S | 2026-01-01 |  |  |"])


class TrackerCLITest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)
        self.tracker_py = str(Path(self._cwd) / "tools" / "tracker.py")

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, self.tracker_py, *args],
            capture_output=True, text=True,
        )

    def test_add_then_list_shows_new_row(self):
        result = self.run_cli(
            "add", "Altana", "VP Engineering",
            "--stage", "Identified", "--next-action-date", "2026-08-26",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("list")
        self.assertIn("Altana", result.stdout)
        self.assertIn("VP Engineering", result.stdout)

    def test_add_duplicate_fails(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        result = self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)

    def test_update_status_on_missing_row_fails(self):
        result = self.run_cli("update-status", "Nope", "Nowhere", "--stage", "X")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)

    def test_update_status_changes_stage_and_next_action(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Identified")
        self.run_cli(
            "update-status", "Altana", "VP Engineering",
            "--stage", "Screen", "--next-action", "Call",
            "--next-action-date", "2026-09-01",
        )
        result = self.run_cli("list")
        self.assertIn("Screen", result.stdout)
        self.assertIn("Call", result.stdout)

    def test_record_event_updates_next_action_without_changing_stage(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Screen")
        self.run_cli(
            "record-event", "Altana", "VP Engineering",
            "--event", "Onsite interview", "--date", "2026-09-05",
        )
        result = self.run_cli("list")
        self.assertIn("Screen", result.stdout)
        self.assertIn("Onsite interview", result.stdout)

    def test_close_moves_row_to_closed_and_writes_notes(self):
        self.run_cli("add", "Altana", "VP Engineering", "--stage", "Screen")
        result = self.run_cli(
            "close", "Altana", "VP Engineering",
            "--reason", "Role was put on hold",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        active = self.run_cli("list")
        self.assertNotIn("Altana", active.stdout)

        closed = self.run_cli("list", "--closed")
        self.assertIn("Altana", closed.stdout)

        notes = Path("opportunity/Altana/VP Engineering/notes.md").read_text()
        self.assertIn("Role was put on hold", notes)

    def test_close_missing_row_fails(self):
        result = self.run_cli("close", "Nope", "Nowhere", "--reason", "n/a")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
