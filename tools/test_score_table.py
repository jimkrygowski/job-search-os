import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import score_table  # noqa: E402

TRAJECTORY = """# Career Trajectory — Test User

**Last reviewed:** 2026-01-01

## What I Love Doing

Building things.

## Must-Haves

- Direct line to the C-level: reports to the CEO, CTO, or CDTO-tier exec —
  title alone isn't the real test.
- Comp floor: $280K base

## Must-Nots

- Bureaucratic or political cultures
- 5-day RTO mandate

## Short-Term Goal (Next Role)

Title: Director+, ideally Head of Engineering or VPE.

**Honest stretch assessment:** This is a lateral move.

## Long-Term Goal (3-5 years)

SVP or CTO.
"""


class ParseCriteriaTest(unittest.TestCase):
    def test_extracts_must_have_bullets_with_ids(self):
        criteria = score_table.parse_criteria(TRAJECTORY)
        must_haves = [c for c in criteria if c["category"] == "Must-Have"]
        self.assertEqual(
            [c["id"] for c in must_haves], ["must-have-1", "must-have-2"]
        )
        self.assertEqual(must_haves[1]["text"], "Comp floor: $280K base")

    def test_joins_wrapped_bullet_continuation_lines(self):
        criteria = score_table.parse_criteria(TRAJECTORY)
        first = next(c for c in criteria if c["id"] == "must-have-1")
        self.assertEqual(
            first["text"],
            "Direct line to the C-level: reports to the CEO, CTO, or "
            "CDTO-tier exec — title alone isn't the real test.",
        )

    def test_extracts_must_not_bullets_with_ids(self):
        criteria = score_table.parse_criteria(TRAJECTORY)
        must_nots = [c for c in criteria if c["category"] == "Must-Not"]
        self.assertEqual(
            [c["text"] for c in must_nots],
            ["Bureaucratic or political cultures", "5-day RTO mandate"],
        )
        self.assertEqual([c["id"] for c in must_nots], ["must-not-1", "must-not-2"])

    def test_extracts_short_term_goal_first_paragraph_only(self):
        criteria = score_table.parse_criteria(TRAJECTORY)
        goal = next(c for c in criteria if c["id"] == "short-term-goal")
        self.assertEqual(goal["category"], "Short-Term Goal")
        self.assertEqual(
            goal["text"], "Title: Director+, ideally Head of Engineering or VPE."
        )

    def test_missing_required_section_raises(self):
        # A section this tool depends on can't silently vanish -- render()'s
        # missing-criteria check only sees the criteria that made it out of
        # parse_criteria(), so a heading it fails to find must be a loud
        # error here, not a quietly shorter criteria list.
        text = TRAJECTORY.replace("## Short-Term Goal (Next Role)", "## Renamed")
        with self.assertRaises(ValueError) as ctx:
            score_table.parse_criteria(text)
        self.assertIn("Short-Term Goal (Next Role)", str(ctx.exception))

    def test_heading_match_is_case_insensitive_and_whitespace_tolerant(self):
        # define-trajectory/SKILL.md documents these section names in a
        # different case ("Must-haves", "Short-term goal (next role)") than
        # the literal headings in a built trajectory.md -- matching must
        # tolerate that instead of silently dropping the section.
        text = TRAJECTORY.replace("## Must-Haves", "##   must-haves")
        criteria = score_table.parse_criteria(text)
        self.assertTrue(any(c["category"] == "Must-Have" for c in criteria))

    def test_bullets_section_with_no_recognized_bullet_markers_raises(self):
        text = TRAJECTORY.replace(
            "- Direct line to the C-level: reports to the CEO, CTO, or CDTO-tier exec —\n"
            "  title alone isn't the real test.\n"
            "- Comp floor: $280K base",
            "Reports to the CEO. Comp floor is $280K base.",
        )
        with self.assertRaises(ValueError) as ctx:
            score_table.parse_criteria(text)
        self.assertIn("Must-Haves", str(ctx.exception))

    def test_recognizes_asterisk_and_plus_bullet_markers(self):
        text = TRAJECTORY.replace(
            "- Direct line to the C-level: reports to the CEO, CTO, or CDTO-tier exec —\n"
            "  title alone isn't the real test.\n"
            "- Comp floor: $280K base",
            "* Reports to the CEO\n+ Comp floor: $280K base",
        )
        criteria = score_table.parse_criteria(text)
        must_haves = [c for c in criteria if c["category"] == "Must-Have"]
        self.assertEqual(
            [c["text"] for c in must_haves], ["Reports to the CEO", "Comp floor: $280K base"]
        )


class RenderTableTest(unittest.TestCase):
    def setUp(self):
        self.criteria = [
            {"id": "must-have-1", "category": "Must-Have", "text": "Reports to CEO"},
            {"id": "must-not-1", "category": "Must-Not", "text": "5-day RTO"},
        ]

    def test_renders_fixed_header_and_one_row_per_criterion(self):
        scores = [
            {"id": "must-have-1", "score": "Meets", "rationale": "JD says so"},
            {"id": "must-not-1", "score": "Fails", "rationale": "Office mandatory"},
        ]
        table = score_table.render_table(self.criteria, scores)
        lines = table.splitlines()
        self.assertEqual(lines[0], "| Criterion | Score | Rationale |")
        self.assertEqual(lines[1], "| --- | --- | --- |")
        self.assertEqual(
            lines[2],
            "| **Must-Have:** Reports to CEO | ✅ Meets | JD says so |",
        )
        self.assertEqual(
            lines[3],
            "| **Must-Not:** 5-day RTO | ❌ Fails | Office mandatory |",
        )

    def test_score_value_is_case_insensitive(self):
        scores = [
            {"id": "must-have-1", "score": "meets", "rationale": ""},
            {"id": "must-not-1", "score": "FAILS", "rationale": ""},
        ]
        table = score_table.render_table(self.criteria, scores)
        self.assertIn("✅ Meets", table)
        self.assertIn("❌ Fails", table)

    def test_missing_score_for_a_criterion_raises(self):
        scores = [{"id": "must-have-1", "score": "Meets", "rationale": ""}]
        with self.assertRaises(ValueError) as ctx:
            score_table.render_table(self.criteria, scores)
        self.assertIn("must-not-1", str(ctx.exception))

    def test_unknown_criterion_id_raises(self):
        scores = [
            {"id": "must-have-1", "score": "Meets", "rationale": ""},
            {"id": "must-not-1", "score": "Fails", "rationale": ""},
            {"id": "nonexistent", "score": "Meets", "rationale": ""},
        ]
        with self.assertRaises(ValueError) as ctx:
            score_table.render_table(self.criteria, scores)
        self.assertIn("nonexistent", str(ctx.exception))

    def test_invalid_score_value_raises(self):
        scores = [
            {"id": "must-have-1", "score": "Sort of", "rationale": ""},
            {"id": "must-not-1", "score": "Fails", "rationale": ""},
        ]
        with self.assertRaises(ValueError) as ctx:
            score_table.render_table(self.criteria, scores)
        self.assertIn("Sort of", str(ctx.exception))

    def test_escapes_pipe_characters_in_cell_text(self):
        criteria = [{"id": "x", "category": "Must-Have", "text": "Reports to CEO | CTO"}]
        scores = [{"id": "x", "score": "Meets", "rationale": "Fits A | B"}]
        table = score_table.render_table(criteria, scores)
        self.assertIn("Reports to CEO \\| CTO", table)
        self.assertIn("Fits A \\| B", table)

    def test_non_dict_score_entry_raises_value_error_not_attribute_error(self):
        scores = ["must-have-1", {"id": "must-not-1", "score": "Fails", "rationale": ""}]
        with self.assertRaises(ValueError):
            score_table.render_table(self.criteria, scores)

    def test_non_string_rationale_raises_value_error_not_attribute_error(self):
        scores = [
            {"id": "must-have-1", "score": "Meets", "rationale": 5},
            {"id": "must-not-1", "score": "Fails", "rationale": ""},
        ]
        with self.assertRaises(ValueError):
            score_table.render_table(self.criteria, scores)


class ScoreTableCLITest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)
        self.script = str(Path(self._cwd) / "tools" / "score_table.py")
        traj_dir = Path("state/career")
        traj_dir.mkdir(parents=True)
        (traj_dir / "trajectory.md").write_text(TRAJECTORY)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmpdir.cleanup()

    def run_cli(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, self.script, *args],
            input=input_text, capture_output=True, text=True,
        )

    def test_criteria_command_prints_json_covering_every_bullet(self):
        result = self.run_cli("criteria")
        self.assertEqual(result.returncode, 0, result.stderr)
        criteria = json.loads(result.stdout)
        self.assertEqual(len(criteria), 5)
        self.assertIn("must-have-1", [c["id"] for c in criteria])

    def test_criteria_command_missing_trajectory_file_fails(self):
        os.remove("state/career/trajectory.md")
        result = self.run_cli("criteria")
        self.assertNotEqual(result.returncode, 0)

    def test_render_command_reads_stdin_and_prints_table(self):
        criteria = json.loads(self.run_cli("criteria").stdout)
        scores = [
            {"id": c["id"], "score": "Unknown", "rationale": ""} for c in criteria
        ]
        result = self.run_cli("render", input_text=json.dumps(scores))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| Criterion | Score | Rationale |", result.stdout)
        self.assertIn("❓ Unknown", result.stdout)

    def test_render_command_missing_criterion_fails_nonzero(self):
        result = self.run_cli("render", input_text="[]")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must-have-1", result.stderr)


if __name__ == "__main__":
    unittest.main()
