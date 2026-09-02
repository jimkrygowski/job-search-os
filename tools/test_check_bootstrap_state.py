import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CheckBootstrapStateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)
        self.script = str(Path(self._cwd) / "tools" / "check_bootstrap_state.py")

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def run_hook(self):
        return subprocess.run(
            [sys.executable, self.script],
            capture_output=True, text=True,
        )

    def test_no_state_at_all_emits_new_user_note(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("bootstrap", context)
        self.assertIn("new user", context)

    def test_trajectory_without_profile_still_emits_new_user_note(self):
        career_dir = Path("state/career")
        career_dir.mkdir(parents=True)
        (career_dir / "trajectory.md").write_text("x")
        result = self.run_hook()
        payload = json.loads(result.stdout)
        self.assertIn("new user", payload["hookSpecificOutput"]["additionalContext"])

    def test_profile_only_emits_nothing(self):
        career_dir = Path("state/career")
        career_dir.mkdir(parents=True)
        (career_dir / "profile.md").write_text("x")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_profile_and_trajectory_without_comp_target_emits_soft_note(self):
        career_dir = Path("state/career")
        career_dir.mkdir(parents=True)
        (career_dir / "profile.md").write_text("x")
        (career_dir / "trajectory.md").write_text("x")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("comp_target.md", context)
        self.assertIn("offer-negotiator", context)
        self.assertNotIn("new user", context)

    def test_all_three_present_emits_nothing(self):
        career_dir = Path("state/career")
        career_dir.mkdir(parents=True)
        (career_dir / "profile.md").write_text("x")
        (career_dir / "trajectory.md").write_text("x")
        (career_dir / "comp_target.md").write_text("x")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
