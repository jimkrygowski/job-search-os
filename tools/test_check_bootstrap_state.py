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

Did real work here, led a team, shipped things.

## Best Job: Some Co

It was the best because of specific, concrete reasons.

## Worst Job: Another Co

It was the worst for equally specific, concrete reasons.

## Best Boss: Jane Doe

Specific concrete reasons this boss was good.

## Worst Boss: John Roe

Specific concrete reasons this boss was bad.

## Patterns

A real synthesized pattern across the above.
"""

TRAJECTORY_COMPLETE = """# Trajectory

**Last reviewed:** 2026-09-03

## What I Love Doing

Real prose describing what this person loves doing at work.

## What I Hate Doing

Real prose describing what this person hates doing at work.

## Must-Haves

- A real must-have

## Must-Nots

- A real must-not

## Short-Term Goal (Next Role)

Real prose describing the short-term goal.

## Long-Term Goal (3-5 years)

Real prose describing the long-term goal.

## Strengths

- A real strength

## Weaknesses / Stretch Areas

- A real weakness
"""

COMP_TARGET_COMPLETE = """# Comp Target

**Last reviewed:** 2026-09-03

## BATNA

A real BATNA description.

## Target / Ask Range

A real target range description.

## Walk-Away Minimums

A real walk-away floor description.

## Cash / Equity / Benefits Priority

A real priority ranking description.

## Equity Risk Tolerance

A real risk-tolerance description.

## Deal-Breakers

A real deal-breakers description.
"""


class SectionHasContentTest(unittest.TestCase):
    def test_exact_heading_with_content_passes(self):
        text = "## Foo\n\nReal content here.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_prefix_heading_with_suffix_and_content_passes(self):
        # Regression case: build-profile's real headers append a
        # descriptive suffix, e.g. "## Best Job: Some Company".
        text = "## Best Job: Some Company\n\nReal content here.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Best Job"))

    def test_missing_heading_fails(self):
        text = "## Something Else\n\nReal content here.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_heading_present_but_empty_body_fails(self):
        text = "## Foo\n\n## Bar\n\nReal content under Bar.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_short_or_placeholder_content_now_passes(self):
        # Deliberate behavior change from the prior length-floor design:
        # this hook does presence-only checking, not sufficiency
        # judgment -- it has no LLM available to tell a real terse
        # answer from a placeholder. Any non-empty content passes;
        # judging whether "TBD" is a real answer is the invoking skill's
        # job, made when it actually reads the file.
        text = "## Foo\n\nTBD\n\n## Bar\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_sub_heading_is_treated_as_nested_content_not_a_terminator(self):
        # A "##" section's own "###" sub-headings (e.g. profile.md's
        # per-job entries under "## Career History") must count as
        # content, not end the section early.
        text = (
            "## Career History\n\n"
            "### Some Job | Some Co | 2020-2026\n\n"
            "Real content about this job.\n\n"
            "## Best Job: Some Co\n\nReal content here.\n"
        )
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Career History"))

    def test_sub_heading_level_does_not_satisfy_required_heading(self):
        # Complementary case: a "###" heading must NOT itself count as
        # satisfying a required "##" section, even if its text matches
        # the required prefix.
        text = "### Best Job: Some Co\n\nReal content here.\n"
        self.assertFalse(check_bootstrap_state._section_has_content(text, "Best Job"))

    def test_matching_is_case_insensitive(self):
        text = "## foo\n\nReal content here.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Foo"))

    def test_last_section_in_file_reads_to_eof(self):
        text = "## Foo\n\nSome earlier content.\n\n## Bar\n\nReal content, last section.\n"
        self.assertTrue(check_bootstrap_state._section_has_content(text, "Bar"))


class MissingSectionsTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def test_missing_file_returns_full_required_list(self):
        result = check_bootstrap_state._missing_sections(
            Path("nope.md"), ["Foo", "Bar"]
        )
        self.assertEqual(result, ["Foo", "Bar"])

    def test_complete_profile_returns_empty_list(self):
        Path("profile.md").write_text(PROFILE_COMPLETE)
        result = check_bootstrap_state._missing_sections(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        )
        self.assertEqual(result, [])

    def test_partial_profile_returns_exactly_the_missing_sections(self):
        text = """## Career History

Real career history content.

## Best Job: Some Co

Real content.

## Worst Job: Another Co

Real content.

## Best Boss: Jane Doe

Real content.

## Patterns
"""
        Path("profile.md").write_text(text)
        result = check_bootstrap_state._missing_sections(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        )
        self.assertEqual(sorted(result), sorted(["Worst Boss", "Patterns"]))

    def test_stub_headers_with_no_content_returns_all(self):
        stub = "\n\n".join(f"## {s}" for s in check_bootstrap_state.PROFILE_REQUIRED_SECTIONS)
        Path("profile.md").write_text(stub)
        result = check_bootstrap_state._missing_sections(
            Path("profile.md"), check_bootstrap_state.PROFILE_REQUIRED_SECTIONS
        )
        self.assertEqual(result, check_bootstrap_state.PROFILE_REQUIRED_SECTIONS)


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

    def test_no_state_at_all_emits_new_user_note_with_does_not_exist(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("does not exist", context)
        self.assertIn("bootstrap", context)
        self.assertIn("new user", context)

    def test_partial_profile_emits_new_user_note_naming_missing_sections(self):
        self._write("state/career/profile.md", "## Career History\n\nReal content.\n")
        result = self.run_hook()
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("is missing:", context)
        self.assertIn("Best Job", context)
        self.assertIn("Patterns", context)
        self.assertIn("new user", context)

    def test_profile_with_thin_but_present_content_counts_as_complete(self):
        # Locks in the deliberate presence-only behavior: this hook no
        # longer judges sufficiency, so a section with minimal but
        # non-empty content is treated the same as a fully fleshed-out
        # one -- that judgment belongs to the invoking skill.
        text = """## Career History

Fine.

## Best Job: Some Co

Fine.

## Worst Job: Another Co

Fine.

## Best Boss: Jane Doe

Fine.

## Worst Boss: John Roe

Fine.

## Patterns

Fine.
"""
        self._write("state/career/profile.md", text)
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

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
        self.assertIn("doesn't exist yet", context)
        self.assertIn("comp_target.md", context)
        self.assertIn("offer-negotiator", context)
        self.assertNotIn("new user", context)

    def test_partial_comp_target_emits_soft_note_naming_missing_sections(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", TRAJECTORY_COMPLETE)
        self._write("state/career/comp_target.md", "## BATNA\n\nReal content.\n")
        result = self.run_hook()
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("is missing:", context)
        self.assertIn("Target / Ask Range", context)
        self.assertIn("comp_target.md", context)

    def test_stub_trajectory_does_not_trigger_soft_note(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", "## What I Love Doing\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_all_three_complete_emits_nothing(self):
        self._write("state/career/profile.md", PROFILE_COMPLETE)
        self._write("state/career/trajectory.md", TRAJECTORY_COMPLETE)
        self._write("state/career/comp_target.md", COMP_TARGET_COMPLETE)
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
