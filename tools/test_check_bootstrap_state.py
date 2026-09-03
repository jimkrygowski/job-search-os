import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_bootstrap_state  # noqa: E402


PROFILE_COMPLETE = """# Profile

## Career History

### Director, Engineering | Some Co | 2020-2026

Did real work here, led a team, shipped things, none of that is a
placeholder -- this line is long enough to pass the content-length floor.

## Best Job: Some Co

It was the best because of specific, concrete reasons that take up more
than twenty characters of real prose.

## Worst Job: Another Co

It was the worst for equally specific, concrete, non-placeholder reasons.

## Best Boss: Jane Doe

Specific concrete reasons this boss was good, not just a name.

## Worst Boss: John Roe

Specific concrete reasons this boss was bad, not just a name.

## Patterns

A real synthesized pattern across the above, not a placeholder line.
"""

TRAJECTORY_COMPLETE = """# Trajectory

**Last reviewed:** 2026-09-03

## What I Love Doing

Real, specific prose describing what this person loves doing at work.

## What I Hate Doing

Real, specific prose describing what this person hates doing at work.

## Must-Haves

- A real must-have with enough specific detail to not be a placeholder

## Must-Nots

- A real must-not with enough specific detail to not be a placeholder

## Short-Term Goal (Next Role)

Real, specific prose describing the short-term goal in enough detail.

## Long-Term Goal (3-5 years)

Real, specific prose describing the long-term goal in enough detail.

## Strengths

- A real strength with enough specific detail to not be a placeholder

## Weaknesses / Stretch Areas

- A real weakness with enough specific detail to not be a placeholder
"""

COMP_TARGET_COMPLETE = """# Comp Target

**Last reviewed:** 2026-09-03

## BATNA

A real, specific BATNA description with enough detail to not be a stub.

## Target / Ask Range

A real, specific target range description with enough detail to matter.

## Walk-Away Minimums

A real, specific walk-away floor description with enough detail here.

## Cash / Equity / Benefits Priority

A real, specific priority ranking description with enough detail here.

## Equity Risk Tolerance

A real, specific risk-tolerance description with enough detail here.

## Deal-Breakers

A real, specific deal-breakers description with enough detail here.
"""


class SectionHasContentTest(unittest.TestCase):
    def test_exact_heading_with_content_passes(self):
        text = "## Foo\n\nReal content here, well over the length floor.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_prefix_heading_with_suffix_and_content_passes(self):
        # Regression case: build-profile's real headers append a
        # descriptive suffix, e.g. "## Best Job: Some Company".
        text = "## Best Job: Some Company\n\nReal content here, over the length floor.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Best Job"))

    def test_missing_heading_fails(self):
        text = "## Something Else\n\nReal content here, over the length floor.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_heading_present_but_empty_body_fails(self):
        text = "## Foo\n\n## Bar\n\nReal content under Bar, over the length floor.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_heading_present_with_thin_placeholder_content_fails(self):
        text = "## Foo\n\nTBD\n\n## Bar\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_sub_heading_is_treated_as_nested_content_not_a_terminator(self):
        # A "##" section's own "###" sub-headings (e.g. profile.md's
        # per-job entries under "## Career History") must count as
        # content, not end the section early.
        text = (
            "## Career History\n\n"
            "### Some Job | Some Co | 2020-2026\n\n"
            "Real content about this job, over the length floor easily.\n\n"
            "## Best Job: Some Co\n\nReal content here.\n"
        )
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Career History"))

    def test_sub_heading_level_does_not_satisfy_required_heading(self):
        # Complementary case to the nested-content test above: a "###"
        # heading must NOT itself count as satisfying a required "##"
        # section, even if its text matches the required prefix.
        text = "### Best Job: Some Co\n\nReal content here, over the length floor.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Best Job"))

    def test_matching_is_case_insensitive(self):
        text = "## foo\n\nReal content here, well over the length floor.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_last_section_in_file_reads_to_eof(self):
        text = "## Foo\n\nReal content here, well over the length floor.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))


class FileIsCompleteTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def test_missing_file_is_incomplete(self):
        self.assertFalse(check_bootstrap_state._file_is_complete(
            Path("nope.md"), ["Foo"]
        ))

    def test_complete_profile_passes(self):
        Path("profile.md").write_text(PROFILE_COMPLETE)
        self.assertTrue(check_bootstrap_state._file_is_complete(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        ))

    def test_profile_missing_one_section_fails(self):
        text = PROFILE_COMPLETE.replace("## Patterns", "## Something Else")
        Path("profile.md").write_text(text)
        self.assertFalse(check_bootstrap_state._file_is_complete(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        ))

    def test_complete_trajectory_passes(self):
        Path("trajectory.md").write_text(TRAJECTORY_COMPLETE)
        self.assertTrue(check_bootstrap_state._file_is_complete(
            Path("trajectory.md"), check_bootstrap_state.TRAJECTORY_REQUIRED_SECTIONS
        ))

    def test_complete_comp_target_passes(self):
        Path("comp_target.md").write_text(COMP_TARGET_COMPLETE)
        self.assertTrue(check_bootstrap_state._file_is_complete(
            Path("comp_target.md"), check_bootstrap_state.COMP_TARGET_REQUIRED_SECTIONS
        ))

    def test_stub_file_with_headers_but_no_content_fails(self):
        stub = "\n\n".join(f"## {s}" for s in check_bootstrap_state.PROFILE_REQUIRED_SECTIONS)
        Path("profile.md").write_text(stub)
        self.assertFalse(check_bootstrap_state._file_is_complete(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        ))


class CheckBootstrapStateHookTest(unittest.TestCase):
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

    def _write(self, relpath, text):
        path = Path(relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_no_state_at_all_emits_new_user_note(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("bootstrap", context)
        self.assertIn("new user", context)

    def test_stub_profile_emits_new_user_note_same_as_missing(self):
        # Regression test for the PR #8 review finding: existence alone
        # used to satisfy this check. A profile.md that exists but is an
        # empty/stub file must be treated the same as a missing one.
        self._write("state/career/profile.md", "## Career History\n")
        result = self.run_hook()
        payload = json.loads(result.stdout)
        self.assertIn("new user", payload["hookSpecificOutput"]["additionalContext"])

    def test_complete_profile_only_emits_nothing(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_complete_profile_and_trajectory_without_comp_target_emits_soft_note(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", TRAJECTORY_COMPLETE)
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("comp_target.md", context)
        self.assertIn("offer-negotiator", context)
        self.assertNotIn("new user", context)

    def test_stub_trajectory_does_not_trigger_soft_note(self):
        # A stub trajectory.md (exists, incomplete) must not count as
        # "trajectory exists" for the soft-note condition, same as a
        # missing trajectory.md today.
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", "## What I Love Doing\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_stub_comp_target_still_triggers_soft_note(self):
        # A stub comp_target.md (exists, incomplete) must be treated the
        # same as a missing one for the soft-note condition.
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", TRAJECTORY_COMPLETE)
        self._write("state/career/comp_target.md", "## BATNA\n")
        result = self.run_hook()
        payload = json.loads(result.stdout)
        self.assertIn("comp_target.md", payload["hookSpecificOutput"]["additionalContext"])

    def test_all_three_complete_emits_nothing(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", TRAJECTORY_COMPLETE)
        self._write("state/career/comp_target.md", COMP_TARGET_COMPLETE)
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
