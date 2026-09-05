# Presence-Only Completeness Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tools/check_bootstrap_state.py` currently uses `MIN_SECTION_CONTENT_LENGTH = 20` — a character-count proxy for "is this section's content substantive" — as part of a `SessionStart` hook that runs as a plain Python subprocess with no LLM available to it. That threshold is a crude stand-in for a judgment call this hook is structurally incapable of making well. Remove it: the hook becomes a presence-only check (does each required heading exist with *something*, however short, under it — a real, deterministic, non-judgmental fact), and drops missing-section names into its notes so the actual sufficiency judgment ("is this content good enough") is made exactly once, correctly, by the skill that actually reads the file when a user engages with it — which is already how `build-profile`/`define-trajectory`/`offer-negotiator`'s own Session Start checks work.

**Origin:** Direct conversation follow-on, pushing back on a design choice from the earlier `bootstrap-content-validation` plan (already on this branch). Jim's framing: "you're describing tests that are string validation... we have an LLM available to us... can we let it judge if the content is sufficient?" Confirmed direction: the hook cannot call an LLM itself (it's a subprocess with no model access, and doing so would add an API dependency, cost, and latency to every session start, breaking this repo's established stdlib-only convention) — so the fix is to stop asking Python to approximate that judgment at all, and let the already-LLM-judged skill-level checks (built in the `guided-resume-mode` plan) be the sole place sufficiency is ever assessed.

**Architecture:** Two independent surfaces. (1) `tools/check_bootstrap_state.py` — `_section_has_content` becomes a pure presence check (non-empty content under a required heading, no length floor); a new `_missing_sections` function returns which required sections are actually missing/empty, threaded into both notes so they name the gaps instead of just saying "incomplete." (2) The three producing skills' `SKILL.md` files (`build-profile`, `define-trajectory`, `offer-negotiator`) — their own completeness-check instructions already correctly describe LLM-judged sufficiency ("substantive content... not just a placeholder"), but each cites "the same completeness standard `tools/check_bootstrap_state.py` checks" — now misleading, since the hook's standard is deliberately weaker. Reword that cross-reference in all three to accurately describe the relationship: the hook does a cheap presence-only pre-check to decide whether to flag the file at all; the real sufficiency judgment is the skill's own, made when it reads the file for real.

**Tech Stack:** `tools/check_bootstrap_state.py` is Python 3 stdlib only (`json`, `re`, `pathlib`), tested with `unittest`. The `SKILL.md` changes are prose only, not unit-tested, consistent with established convention on this branch.

## Global Constraints

- **The hook makes no sufficiency judgment, ever.** `_section_has_content`'s only question is "is there non-empty content under this heading" — not "is this content good." Whether "TBD" or a three-word answer counts as a real answer is explicitly NOT this hook's job — that's the invoking skill's job, made with real reasoning when it actually reads the file. A test must lock this in: a section with minimal-but-non-empty content (e.g. "TBD", or "Fine.") is treated as present, not flagged.
- **Both notes name the specific missing sections** when the file exists but is incomplete, using the exact required-section-prefix strings already established (`PROFILE_REQUIRED_SECTIONS`, `TRAJECTORY_REQUIRED_SECTIONS`, `COMP_TARGET_REQUIRED_SECTIONS` — unchanged from the prior plan, not touched by this one). When the file doesn't exist at all, the note still says "does not exist" / "doesn't exist yet" (unchanged wording for that case) rather than listing the full required-section list as if they were individually "missing" — that phrasing would read strangely for a file with zero content.
- **`_missing_sections(path, required_sections)` returns the full `required_sections` list unchanged when the file doesn't exist or can't be read** (`OSError`/`UnicodeDecodeError`, preserving the fail-safe-not-fail-open behavior from the prior plan) — every required section is trivially "missing" in that case, even though the notes' wording branches separately on file-exists-or-not for readability.
- **No new required-section lists, no changes to which sections are required for which file** — this plan only changes how "does a required section have content" is judged (presence vs. a length floor) and what the notes say when it's missing. `PROFILE_REQUIRED_SECTIONS`/`TRAJECTORY_REQUIRED_SECTIONS`/`COMP_TARGET_REQUIRED_SECTIONS` and every other file this hook checks are unchanged.
- **The hook's stop-boundary regex logic (prefix-tolerant heading match, `###` sub-heading treated as nested content not a terminator, case-insensitive) is unchanged** — only the length-floor sufficiency check inside it is removed.
- **The three `SKILL.md` files' own sufficiency-judgment instructions ("substantive content... not just a placeholder") do not change in substance** — only the parenthetical describing the hook's role changes, since it now accurately says the hook does presence-only pre-checking, not the same judgment.
- No new Python dependencies; stdlib `re`/`json`/`pathlib` only, matching every other tool on this branch.

---

### Task 1: `tools/check_bootstrap_state.py` — presence-only check + missing-section diagnostics

**Files:**
- Modify: `tools/check_bootstrap_state.py`
- Modify: `tools/test_check_bootstrap_state.py`

**Interfaces:**
- Consumes: nothing from Task 2 (fully independent — different files, and Task 2 doesn't reference any new Python symbol this task introduces by name, only by description).
- Produces: nothing consumed elsewhere in this plan. (Task 2's prose edits describe the hook's new behavior in general terms, not by calling out specific function names.)

**Verify:** automated — full `unittest` suite.

- [ ] **Step 1: Write the failing tests**

Replace `tools/test_check_bootstrap_state.py` in full:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tools.test_check_bootstrap_state -v`

Expected: most tests FAIL — `_missing_sections` doesn't exist yet (`AttributeError`), and `_section_has_content` still has the length-floor behavior so `test_short_or_placeholder_content_now_passes` fails against the current implementation. Some hook-level tests may coincidentally pass or fail for the wrong reason against the old code (e.g. `test_no_state_at_all_emits_new_user_note_with_does_not_exist` — the old note text also contains "does not exist" as part of "does not exist or is incomplete," so that specific assertion might pass by coincidence pre-implementation; the `MissingSectionsTest` class and `test_short_or_placeholder_content_now_passes` are the ones that must genuinely fail).

- [ ] **Step 3: Write the implementation**

Replace `tools/check_bootstrap_state.py` in full:

```python
#!/usr/bin/env python3
"""SessionStart hook: flags missing or incomplete setup before Claude's
first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note, naming which required sections are missing or
empty. This is a presence check, not a sufficiency judgment: it only
asks whether each required section has *something* written under its
heading, not whether that content is actually good. This hook runs as a
plain subprocess before Claude's turn starts -- it has no LLM available
to judge whether content is substantive, so it doesn't try. That
judgment belongs entirely to the skill that actually reads the file when
a user engages with it (build-profile/define-trajectory/offer-
negotiator's own Session Start checks), which is where it happens
correctly.

- profile.md missing or has empty/missing required sections: hard-gate
  new-user note (must lead the first reply), naming which sections.
- profile.md complete (by presence), trajectory.md complete,
  comp_target.md missing or has empty/missing required sections: soft,
  non-blocking note, naming which sections.
- All three complete: no note.
"""
import json
import re
from pathlib import Path

PROFILE_PATH = Path("state/career/profile.md")
TRAJECTORY_PATH = Path("state/career/trajectory.md")
COMP_TARGET_PATH = Path("state/career/comp_target.md")

# build-profile/SKILL.md's ## Output section mandates these six headings
# (by prefix -- real headers append a descriptive suffix, e.g.
# "## Best Job: Some Company").
PROFILE_REQUIRED_SECTIONS = [
    "Career History", "Best Job", "Worst Job", "Best Boss", "Worst Boss", "Patterns",
]

# define-trajectory/SKILL.md's Mnookin Two-Pager sections, matched by
# short stable prefix so a parenthetical detail changing (e.g.
# "Long-Term Goal (3-5 years)") doesn't break this check.
TRAJECTORY_REQUIRED_SECTIONS = [
    "What I Love Doing", "What I Hate Doing", "Must-Haves", "Must-Nots",
    "Short-Term Goal", "Long-Term Goal", "Strengths", "Weaknesses",
]

# offer-negotiator/SKILL.md's ## Setup Mode -- Sections headings.
# "Last reviewed" is a one-line field, not a section with body content,
# so it's excluded here (same as trajectory.md above).
COMP_TARGET_REQUIRED_SECTIONS = [
    "BATNA", "Target / Ask Range", "Walk-Away Minimums",
    "Cash / Equity / Benefits Priority", "Equity Risk Tolerance", "Deal-Breakers",
]


def _section_has_content(text, heading_prefix):
    """True if `text` has a "##"-level heading starting with
    heading_prefix (case-insensitive), followed by non-empty content
    before the next "##"-or-higher heading or end of string.

    This is a presence check, not a sufficiency judgment -- "is there
    anything here at all," not "is this good enough." Whether present
    content is actually substantive is a real judgment call, and this
    hook has no LLM available to make it (it runs as a plain subprocess
    before Claude's turn starts). That judgment happens exactly once,
    correctly, in the skill that actually reads the file -- not
    approximated here with a character-count threshold.

    Mirrors score_table.py's _section_body regex approach (same stop-
    boundary: the next "##" heading or EOF, so a "###" sub-heading is
    correctly treated as nested content, not a terminator) but matches
    the heading by prefix rather than requiring an exact line, since
    build-profile's real headers append a descriptive suffix.
    """
    pattern = re.compile(
        rf"^##[ \t]+{re.escape(heading_prefix)}[^\n]*$(.*?)(?=^##[ \t]|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(text)
    if m is None:
        return False
    return len(m.group(1).strip()) > 0


def _missing_sections(path, required_sections):
    """Returns the subset of required_sections that are missing or
    empty. A missing or unreadable file trivially returns the full
    list -- every required section is "missing" in that case."""
    if not path.exists():
        return list(required_sections)
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return list(required_sections)
    return [s for s in required_sections if not _section_has_content(text, s)]


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    profile_missing = _missing_sections(PROFILE_PATH, PROFILE_REQUIRED_SECTIONS)
    if profile_missing:
        if not PROFILE_PATH.exists():
            detail = "does not exist"
        else:
            detail = "is missing: " + ", ".join(profile_missing)
        _emit(
            f"state/career/profile.md {detail}. This is a new user who "
            "has not run bootstrap yet (or started it and didn't "
            "finish). Your very first reply this session, before "
            "addressing anything else the user asked, must say so "
            "plainly and offer to run the `bootstrap` skill now."
        )
        return

    trajectory_missing = _missing_sections(TRAJECTORY_PATH, TRAJECTORY_REQUIRED_SECTIONS)
    comp_target_missing = _missing_sections(COMP_TARGET_PATH, COMP_TARGET_REQUIRED_SECTIONS)
    if not trajectory_missing and comp_target_missing:
        if not COMP_TARGET_PATH.exists():
            detail = "doesn't exist yet"
        else:
            detail = "is missing: " + ", ".join(comp_target_missing)
        _emit(
            f"state/career/comp_target.md {detail} — offer-negotiator "
            "(comp coaching/benchmarking) won't be able to ground its "
            "advice in your actual walk-away numbers until it's set up. "
            "Mention this and offer to set it up, but address whatever "
            "the user asked first."
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tools.test_check_bootstrap_state -v`
Expected: all tests PASS.

- [ ] **Step 5: Run the full project test suite**

Run: `python3 -m unittest discover -s tools`
Expected: all tests PASS (no regressions in `test_score_table.py`, `test_option_value.py`, `test_tracker.py`, `test_gmail_extract.py`).

- [ ] **Step 6: Commit**

```bash
git add tools/check_bootstrap_state.py tools/test_check_bootstrap_state.py
git commit -m "Make bootstrap hook a presence-only check, not a sufficiency judgment"
```

---

### Task 2: Three `SKILL.md` files — accurate hook/skill relationship wording

**Files:**
- Modify: `.claude/skills/build-profile/SKILL.md`
- Modify: `.claude/skills/define-trajectory/SKILL.md`
- Modify: `.claude/skills/offer-negotiator/SKILL.md`

**Interfaces:**
- Consumes: nothing from Task 1 (this task describes the hook's new behavior in prose; it doesn't call any Python symbol by name).
- Produces: nothing consumed elsewhere in this plan.

**Verify (no automated test — prose files, consistent with established convention):** after writing, confirm all three files' completeness-check sentences: (a) still correctly instruct the skill itself to judge "real, substantive content... not a placeholder" (unchanged in substance); (b) no longer claim the hook applies "the same completeness standard" — instead accurately describe the hook as presence-only and the skill as where sufficiency judgment actually happens; (c) nothing else in any of the three files changed.

- [ ] **Step 1: Edit `.claude/skills/build-profile/SKILL.md`**

Find (in `## Session Start`, step 1):
```
1. Check whether `state/career/profile.md` already exists, and if so,
   whether it's complete — every section in `## Output` below present as
   a `##` heading with substantive content underneath, not just the
   heading itself or a placeholder line (the same completeness standard
   `tools/check_bootstrap_state.py` checks).
```
Replace with:
```
1. Check whether `state/career/profile.md` already exists, and if so,
   whether it's complete — every section in `## Output` below present as
   a `##` heading with real, substantive content underneath, not just
   the heading itself or a placeholder like "TBD."
   `tools/check_bootstrap_state.py`'s SessionStart hook only checks that
   each heading exists with *something* under it (a cheap presence
   check, no judgment call) to decide whether to flag this file at all
   — the actual judgment of whether the content is good enough is yours
   to make here, reading the real file.
```

- [ ] **Step 2: Edit `.claude/skills/define-trajectory/SKILL.md`**

Find (in `## Session Start`, step 1):
```
1. Check whether `state/career/trajectory.md` exists, and if so, whether
   it's complete — every `##` section listed in `## Sections (Mnookin
   Two-Pager shape)` below present as a `##` heading with substantive content
   underneath, not just the heading itself or a placeholder line (the
   same completeness standard `tools/check_bootstrap_state.py` checks).
```
Replace with:
```
1. Check whether `state/career/trajectory.md` exists, and if so, whether
   it's complete — every `##` section listed in `## Sections (Mnookin
   Two-Pager shape)` below present as a `##` heading with real,
   substantive content underneath, not just the heading itself or a
   placeholder like "TBD." `tools/check_bootstrap_state.py`'s
   SessionStart hook only checks that each heading exists with
   *something* under it (a cheap presence check, no judgment call) to
   decide whether to flag this file at all — the actual judgment of
   whether the content is good enough is yours to make here, reading
   the real file.
```

- [ ] **Step 3: Edit `.claude/skills/offer-negotiator/SKILL.md`**

Find (in `## Session Start`, step 2):
```
2. (Setup Mode only) Check whether `state/career/comp_target.md` exists,
   and if so, whether it's complete — every `##` section listed in
   `## Setup Mode — Sections` below present as a `##` heading with substantive content
   underneath, not just the heading itself or a placeholder line (the
   same completeness standard `tools/check_bootstrap_state.py` checks).
```
Replace with:
```
2. (Setup Mode only) Check whether `state/career/comp_target.md` exists,
   and if so, whether it's complete — every `##` section listed in
   `## Setup Mode — Sections` below present as a `##` heading with real,
   substantive content underneath, not just the heading itself or a
   placeholder like "TBD." `tools/check_bootstrap_state.py`'s
   SessionStart hook only checks that each heading exists with
   *something* under it (a cheap presence check, no judgment call) to
   decide whether to flag this file at all — the actual judgment of
   whether the content is good enough is yours to make here, reading
   the real file.
```

(Verify the exact current wording of each block against the live files before applying — this task's brief will carry the precise current text.)

- [ ] **Step 4: Verify against the checklist above**

Read all three files back and confirm the three points in this task's Verify section.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/build-profile/SKILL.md .claude/skills/define-trajectory/SKILL.md .claude/skills/offer-negotiator/SKILL.md
git commit -m "Clarify hook does presence-only checks, skills judge sufficiency"
```
