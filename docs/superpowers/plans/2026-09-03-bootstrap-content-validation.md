# Bootstrap Hook Content Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tools/check_bootstrap_state.py` currently treats `Path(...).exists()` as proof a file represents finished work. It doesn't — a session interrupted mid-workflow can leave a stub file that exists but is empty or missing whole sections, and the hook would silently treat that as "done." Replace existence checks with content checks: each required file must exist AND have every one of its known sections present with non-trivial content. Also formalize `profile.md`'s section schema, which — unlike `trajectory.md` and `comp_target.md` — was never pinned down to exact headers anywhere in the codebase.

**Origin:** Raised in PR #8 review (github.com/jimkrygowski/job-search-os/pull/8, review comment on `tools/check_bootstrap_state.py`). Scope confirmed directly: "I would want a check that is deeper than 'required headers exist'. I'd want a check for content. so yes build something. Also profile.md should get a more formalized schema and a check to go with it."

**Architecture:** Two independent surfaces. (1) `build-profile/SKILL.md` and `offer-negotiator/SKILL.md` get explicit, exact required-header guidance for the files they produce — `build-profile`'s is a codification of what it already, in practice, produces (verified against a real, complete `profile.md` already on disk — see Global Constraints), not a new invented format; `offer-negotiator`'s Setup Mode has never actually generated a real `comp_target.md`, so this is the first time its output headers are pinned down at all. (2) `tools/check_bootstrap_state.py` gets a section-content parser (mirroring `tools/score_table.py`'s existing `_section_body` regex approach, extended to prefix-match a heading rather than requiring an exact line, since `build-profile`'s real headers append a descriptive suffix like "Best Job: Linkable Networks") and a completeness check per file, replacing the three plain `.exists()` calls. The hook's existing two-branch structure (hard-gate new-user note / soft comp_target.md note) is unchanged — only what "the file is there" means gets stricter.

**Tech Stack:** Python 3 stdlib only (`re`, `pathlib`), tested with `unittest`. No new dependencies.

## Global Constraints

- **Section-content matching must be prefix-tolerant, not exact-line, unlike `score_table.py`'s existing regex.** Verified directly against the real `profile.md` already on disk (`state/career/profile.md`) that `build-profile` produces headers like `## Best Job: Linkable Networks` and `## Worst Boss: Eli Daniel (Jellyfish, first head of engineering)` — a required-section check for "Best Job" or "Worst Boss" must match a heading that *starts with* that label, not one that equals it exactly, or this feature would break on the very file it's meant to validate.
- **A section counts as having content only if there is non-trivial text between its heading and the next `##`-or-higher heading (or EOF).** Mirror `score_table.py:28-38`'s `_section_body` stop-boundary logic (`(?=^##[ \t]|\Z)`, `re.MULTILINE | re.DOTALL | re.IGNORECASE`) so that a required `##` section's `###` sub-headings (e.g. `profile.md`'s per-job entries under `## Career History`) are correctly treated as nested content, not section terminators.
- **"Non-trivial" is a length floor, not semantic judgment.** This is a fast, deterministic `SessionStart` hook — it cannot make an LLM call to judge content quality. `MIN_SECTION_CONTENT_LENGTH = 20` (characters, after `.strip()`) is the threshold: long enough to reject an empty or single-word placeholder section, short enough not to reject a genuinely terse real answer. Document this reasoning at the constant's definition, the same way `option_value.py`'s constants document their sourcing.
- **The hook's existing two-branch structure and note wording do not change** — only the definition of "does this file represent finished work" does. `state/career/profile.md`/`trajectory.md`/`comp_target.md` become "exists AND has all required sections with content" everywhere the hook currently checks `.exists()`.
- **`profile.md`'s formalized headers must match what `build-profile` already produces in real use**, not invent a new format: `Career History`, `Best Job`, `Worst Job`, `Best Boss`, `Worst Boss`, `Patterns` (verified against `state/career/profile.md`'s real headings, which also include extra sections beyond these six — the check requires these six to be present with content, and does not reject extra sections).
- **`comp_target.md`'s headers are being formalized for the first time** — no real generated file exists yet to check against (verified: `state/career/comp_target.md` does not exist on this machine). Base them directly on `offer-negotiator/SKILL.md`'s existing `## Setup Mode — Sections` bold labels: `BATNA`, `Target / Ask Range`, `Walk-Away Minimums`, `Cash / Equity / Benefits Priority`, `Equity Risk Tolerance`, `Deal-Breakers`. `Last reviewed` is a one-line metadata field (`**Last reviewed:** <date>`, matching how `trajectory.md` already writes it), not its own section with body content — excluded from the required-sections-with-content list for both `comp_target.md` and `trajectory.md`.
- **`trajectory.md`'s required sections use short, stable prefixes**, not full literal headings, so the check doesn't break if a parenthetical detail changes: `What I Love Doing`, `What I Hate Doing`, `Must-Haves`, `Must-Nots`, `Short-Term Goal`, `Long-Term Goal`, `Strengths`, `Weaknesses` (matching `state/career/trajectory.md`'s real headings — `Short-Term Goal (Next Role)`, `Long-Term Goal (3-5 years)`, `Weaknesses / Stretch Areas` — via prefix, not exact match).
- No new Python dependencies; stdlib `re` only, matching `score_table.py`'s convention.

---

### Task 1: Formalize `profile.md` and `comp_target.md` header conventions

**Files:**
- Modify: `.claude/skills/build-profile/SKILL.md`
- Modify: `.claude/skills/offer-negotiator/SKILL.md`

**Interfaces:**
- Consumes: nothing (independent of Task 2).
- Produces: the exact required-section-prefix strings Task 2's validator checks for. Task 2 must use these exact strings, not invent its own.

**Verify (no automated test — prose file, consistent with spec §9's precedent for skill files):** after writing, confirm: (a) `build-profile/SKILL.md`'s new header guidance matches `state/career/profile.md`'s six real section headings by prefix (Career History, Best Job, Worst Job, Best Boss, Worst Boss, Patterns); (b) `offer-negotiator/SKILL.md`'s new header guidance gives `## `-level headers for all six `Setup Mode — Sections` bold labels except `Last reviewed`, which stays a one-line field.

- [ ] **Step 1: Add explicit header guidance to `build-profile/SKILL.md`**

Find the `## Output` section, which currently reads:

```markdown
## Output

Write `state/career/profile.md` with clear headers matching the sections above.
Use the user's own words and specifics where possible — this file is
read by skills that draft resumes and cover letters, and vague profile
content produces vague drafts.
```

Replace it with:

```markdown
## Output

Write `state/career/profile.md` with a `##` heading for each section
above, using this exact wording as the start of the heading (a
descriptive suffix after it is fine and encouraged — e.g. `## Best Job:
Linkable Networks` rather than a bare `## Best Job`):

- `## Career History`
- `## Best Job` (append `: <company/role>` or similar)
- `## Worst Job` (same)
- `## Best Boss` (same)
- `## Worst Boss` (same)
- `## Patterns`

These six headings are load-bearing: `tools/check_bootstrap_state.py`
checks for them (by prefix) to confirm this file represents finished
work, not an interrupted session. Additional `##` sections beyond these
six (e.g. a callout the user's story clearly needs) are fine to add.

Use the user's own words and specifics where possible — this file is
read by skills that draft resumes and cover letters, and vague profile
content produces vague drafts.
```

- [ ] **Step 2: Add explicit header guidance to `offer-negotiator/SKILL.md`**

Find the `## Setup Mode — Sections` section (which currently starts with the read-scope line and then lists six bold-labeled bullets: Last reviewed, BATNA, Target / ask range, Walk-away minimums, Cash / equity / benefits priority, Equity risk tolerance, Deal-breakers). Immediately after the read-scope line (`Read only \`research.md\`'s...`) and before the first bullet (`- **Last reviewed:**`), insert:

```markdown

Write `state/career/comp_target.md` with `**Last reviewed:** <date>` as
a one-line field near the top (not its own section), then a `##`
heading for each of the other six items below, using this exact wording
as the start of the heading: `## BATNA`, `## Target / Ask Range`,
`## Walk-Away Minimums`, `## Cash / Equity / Benefits Priority`,
`## Equity Risk Tolerance`, `## Deal-Breakers`. These headings are
load-bearing: `tools/check_bootstrap_state.py` checks for them (by
prefix) to confirm this file represents finished setup, not an
interrupted session.
```

(Verify the exact current wording of the read-scope line and first bullet against the live file before inserting — this task's brief will carry the precise current text.)

- [ ] **Step 3: Verify against the checklist above**

Read both files back. Confirm the six `build-profile` prefixes match `state/career/profile.md`'s real headings, and the six `offer-negotiator` headers are all present as `##`-level guidance distinct from the `Last reviewed` field.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/build-profile/SKILL.md .claude/skills/offer-negotiator/SKILL.md
git commit -m "Formalize profile.md and comp_target.md section headers"
```

---

### Task 2: Content-validation logic in `check_bootstrap_state.py`

**Files:**
- Modify: `tools/check_bootstrap_state.py`
- Modify: `tools/test_check_bootstrap_state.py`

**Interfaces:**
- Consumes: Task 1's exact required-header strings (by name, not by reading Task 1's file content — this task hardcodes the same six-item lists Task 1 established, since they're now the contract both files share).
- Produces: nothing consumed elsewhere.

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tools.test_check_bootstrap_state -v` (or `python3 -m pytest tools/test_check_bootstrap_state.py -v` if pytest is available)

Expected: `ModuleNotFoundError`/`AttributeError`-style failures — `_section_has_content`, `_file_is_complete`, `PROFILE_REQUIRED_SECTIONS`, `TRAJECTORY_REQUIRED_SECTIONS`, `COMP_TARGET_REQUIRED_SECTIONS` don't exist yet in `check_bootstrap_state.py`. The old three tests this file used to have (new-user note, profile-only, soft note) are superseded by this rewrite's equivalents (`test_no_state_at_all_emits_new_user_note`, `test_complete_profile_only_emits_nothing`, `test_complete_profile_and_trajectory_without_comp_target_emits_soft_note`) — expected FAIL for a different reason (the hook still uses `.exists()`, which would actually make the "complete" fixtures pass by accident today, so don't be surprised if a couple of the hook-level tests pass even before the rewrite — the *content-level* tests (`SectionHasContentTest`, `FileIsCompleteTest`, the two stub-file hook tests) are the ones that must fail pre-implementation.

- [ ] **Step 3: Write the implementation**

Replace `tools/check_bootstrap_state.py` in full:

```python
#!/usr/bin/env python3
"""SessionStart hook: flags missing or incomplete setup before Claude's
first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note. A file only counts as done if it exists AND
has every one of its required sections present with real content --
existence alone doesn't prove a workflow ran to completion (a session
that gets interrupted mid-build-profile can leave a stub file that
exists but is empty or missing whole sections).

- profile.md missing or incomplete: hard-gate new-user note (must lead
  the first reply).
- profile.md complete, trajectory.md complete, comp_target.md missing
  or incomplete: soft, non-blocking note that offer-negotiator setup
  hasn't been run.
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

# Length floor (characters, after .strip()) for a section's body text to
# count as real content rather than an empty/placeholder stub. Long
# enough to reject "TBD" or nothing at all; short enough not to reject a
# genuinely terse real answer. A judgment call, not a measured constant
# -- this is a fast, deterministic hook, not an LLM call, so it can't
# make a quality judgment, only a presence-and-length one.
MIN_SECTION_CONTENT_LENGTH = 20


def _section_has_content(text, heading_prefix):
    """True if `text` has a "##"-level heading starting with
    heading_prefix (case-insensitive), followed by at least
    MIN_SECTION_CONTENT_LENGTH characters of stripped content before the
    next "##"-or-higher heading or end of string.

    Mirrors score_table.py's _section_body regex approach (same stop-
    boundary: the next "##" heading or EOF, so a "###" sub-heading is
    correctly treated as nested content, not a terminator) but matches
    the heading by prefix rather than requiring an exact line, since
    build-profile's real headers append a descriptive suffix.
    """
    pattern = re.compile(
        rf"^##[ \t]+{re.escape(heading_prefix)}.*$(.*?)(?=^##[ \t]|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(text)
    if m is None:
        return False
    return len(m.group(1).strip()) >= MIN_SECTION_CONTENT_LENGTH


def _file_is_complete(path, required_sections):
    if not path.exists():
        return False
    text = path.read_text()
    return all(_section_has_content(text, s) for s in required_sections)


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    if not _file_is_complete(PROFILE_PATH, PROFILE_REQUIRED_SECTIONS):
        _emit(
            "state/career/profile.md does not exist or is incomplete. "
            "This is a new user who has not run bootstrap yet (or "
            "started it and didn't finish). Your very first reply this "
            "session, before addressing anything else the user asked, "
            "must say so plainly and offer to run the `bootstrap` skill "
            "now."
        )
        return

    if (
        _file_is_complete(TRAJECTORY_PATH, TRAJECTORY_REQUIRED_SECTIONS)
        and not _file_is_complete(COMP_TARGET_PATH, COMP_TARGET_REQUIRED_SECTIONS)
    ):
        _emit(
            "state/career/comp_target.md doesn't exist yet or is "
            "incomplete — offer-negotiator (comp coaching/benchmarking) "
            "won't be able to ground its advice in your actual "
            "walk-away numbers until it's set up. Mention this and "
            "offer to set it up, but address whatever the user asked "
            "first."
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
git commit -m "Validate section content, not just file existence, in bootstrap hook"
```
