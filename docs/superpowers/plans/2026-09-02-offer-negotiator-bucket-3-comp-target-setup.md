# Offer Negotiator — Bucket 3: `comp_target.md` Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the setup-mode session that produces `state/career/comp_target.md` — the standing record of walk-away numbers, comp-component priorities, and deal-breakers — and wire it into `bootstrap` (new-user path) and `check_bootstrap_state.py` (retroactive-upgrade path for existing installs), per spec §3-§5.

**Architecture:** Three independent surfaces, no shared code between them: (1) a new `.claude/skills/offer-negotiator/SKILL.md` in setup-mode-only form (mirrors `define-trajectory/SKILL.md`'s Session Start / Sections / Initial-mode / Revisit-mode shape); (2) `bootstrap/SKILL.md` gains a step invoking that setup mode plus an updated existing-state check; (3) `tools/check_bootstrap_state.py` gains a second, non-blocking condition for users who already bootstrapped before this feature existed, documented in `CLAUDE.md` alongside the existing new-user paragraph. Buckets 4-5 will later extend `offer-negotiator/SKILL.md` with the four negotiation moments and broaden its frontmatter description — this bucket only builds and wires the setup mode.

**Tech Stack:** `check_bootstrap_state.py` is Python 3 stdlib only (`json`, `pathlib`), tested with `unittest` via `subprocess`, mirroring `tools/test_score_table.py`'s `ScoreTableCLITest` pattern. `SKILL.md` files are prose, not unit-tested, consistent with `interview-prep`/`company-research`/`define-trajectory` today (spec §9).

**Spec:** `docs/superpowers/specs/2026-09-01-offer-negotiator-design.md` (§3 architecture, §4 bootstrap integration, §5 retroactive upgrade path, §10 open item "Exact field list and conversation shape for `comp_target.md` setup (Bucket 3)")

## Global Constraints

- `comp_target.md`'s walk-away numbers must be built around a real BATNA (a competing offer, a current-job timeline, or an honest search-runway estimate) — per `research.md`'s explicit direction: "This is the concept `comp_target.md` (Bucket 3) should be built around... The skill should push the user to articulate their actual BATNA, not an aspirational one." Never invent one the user hasn't stated (CLAUDE.md guardrail #1).
- The soft retroactive-upgrade note's wording follows the spec's suggested text closely (§5): conveys "you're missing a capability," not "you must comply," and — unlike the new-user hard gate — does **not** block or reorder the assistant's first reply; it only asks that the note be mentioned and setup offered before addressing whatever the user asked.
- `bootstrap`'s "check existing state" step must require **all three** of `profile.md`, `trajectory.md`, and `comp_target.md` to treat setup as already complete (spec §4) — two-of-three is no longer sufficient to skip straight to "already done."
- No new guardrails: everything here falls under existing CLAUDE.md guardrails #1 (never invent experience/facts) and #2 (never assert unsupported opinion) — see spec §8.
- Follow `tools/test_score_table.py`'s `ScoreTableCLITest` conventions for the new hook test: `tempfile.TemporaryDirectory()` + `os.chdir` + `subprocess.run([sys.executable, script], ...)`, not direct function import, since the hook's real contract is "what does it print to stdout when run as a script."

---

### Task 1: `check_bootstrap_state.py` — retroactive-upgrade note + `CLAUDE.md` docs

**Files:**
- Modify: `tools/check_bootstrap_state.py`
- Create: `tools/test_check_bootstrap_state.py`
- Modify: `CLAUDE.md:10-16` (insert a new paragraph immediately after)

**Interfaces:**
- Consumes: nothing (no dependency on Tasks 2/3 — the note's text is self-contained and doesn't require `offer-negotiator/SKILL.md` to exist to be correct).
- Produces: nothing consumed by later tasks in this plan.

- [ ] **Step 1: Write the failing tests**

Create `tools/test_check_bootstrap_state.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify the new-behavior cases fail**

Run: `python3 -m pytest tools/test_check_bootstrap_state.py -v` (or `python3 -m unittest tools.test_check_bootstrap_state -v`)

Expected: `test_no_state_at_all_emits_new_user_note`, `test_trajectory_without_profile_still_emits_new_user_note`, `test_profile_only_emits_nothing`, and `test_all_three_present_emits_nothing` PASS against the current script (its existing behavior already covers these). `test_profile_and_trajectory_without_comp_target_emits_soft_note` FAILS — the current script prints nothing once `profile.md` exists, so `json.loads(result.stdout)` raises `json.decoder.JSONDecodeError` on the empty string.

- [ ] **Step 3: Write the implementation**

Replace `tools/check_bootstrap_state.py` in full:

```python
#!/usr/bin/env python3
"""SessionStart hook: flags missing setup before Claude's first reply.

Checks state/career/profile.md, trajectory.md, and comp_target.md and
injects at most one note:
- profile.md missing: hard-gate new-user note (must lead the first reply).
- profile.md and trajectory.md exist but comp_target.md doesn't: soft,
  non-blocking note that offer-negotiator setup hasn't been run.
- All three exist: no note.
"""
import json
from pathlib import Path


def _emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))


def main():
    if not Path("state/career/profile.md").exists():
        _emit(
            "state/career/profile.md does not exist. This is a new "
            "user who has not run bootstrap yet. Your very first "
            "reply this session, before addressing anything else the "
            "user asked, must say so plainly and offer to run the "
            "`bootstrap` skill now."
        )
        return

    if (
        Path("state/career/trajectory.md").exists()
        and not Path("state/career/comp_target.md").exists()
    ):
        _emit(
            "state/career/comp_target.md doesn't exist yet — "
            "offer-negotiator (comp coaching/benchmarking) won't be able "
            "to ground its advice in your actual walk-away numbers until "
            "it's set up. Mention this and offer to set it up, but "
            "address whatever the user asked first."
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_check_bootstrap_state.py -v`
Expected: all 5 tests PASS.

- [ ] **Step 5: Document the new condition in `CLAUDE.md`**

In `CLAUDE.md`, immediately after the existing paragraph that ends `...Don't wait to be asked, and don't improvise your own setup flow.` (currently lines 10-16), insert a new paragraph:

```markdown

The same hook also checks a second, softer condition: if
`state/career/profile.md` and `state/career/trajectory.md` both exist but
`state/career/comp_target.md` doesn't, it injects a non-blocking note that
`offer-negotiator` setup hasn't been run. Unlike the new-user note, this
one doesn't gate your first reply — mention it and offer to set it up,
but address whatever the user asked first.
```

- [ ] **Step 6: Commit**

```bash
git add tools/check_bootstrap_state.py tools/test_check_bootstrap_state.py CLAUDE.md
git commit -m "Add retroactive comp_target.md upgrade note to bootstrap hook"
```

---

### Task 2: `.claude/skills/offer-negotiator/SKILL.md` — setup mode

**Files:**
- Create: `.claude/skills/offer-negotiator/SKILL.md`

**Interfaces:**
- Consumes: nothing (no dependency on Task 1; Task 3 depends on this file existing so it can be referenced by name from `bootstrap/SKILL.md`).
- Produces: the `offer-negotiator` skill name/frontmatter that Task 3 references, and the "Setup Mode" entry point that step 5 of `bootstrap/SKILL.md` (Task 3) invokes.

**Verify (no automated test — prose skill file, consistent with spec §9):** after writing, read the file back and confirm: (a) frontmatter `name:` is exactly `offer-negotiator` and matches the directory name; (b) every field listed in the spec's four setup-mode categories — walk-away minimums, cash/equity/benefits priority, equity risk tolerance, deal-breakers (spec §3) — appears under `## Sections`, plus the BATNA section research.md directs this file to be built around; (c) the file never asserts a BATNA, number, or timeline on the user's behalf — only describes how to elicit one.

- [ ] **Step 1: Write `.claude/skills/offer-negotiator/SKILL.md`**

```markdown
---
name: offer-negotiator
description: Use when a user needs to define or revisit their compensation target — walk-away numbers grounded in a real BATNA, cash/equity/benefits priorities, equity risk tolerance, and deal-breakers — as part of first-time bootstrap or any time their situation changes (a competing offer, a job-search runway change, negotiation feedback). Builds or updates state/career/comp_target.md.
---

# Offer Negotiator

## Purpose

Produce or update `state/career/comp_target.md` — the standing record of
this person's walk-away numbers, compensation-component priorities, and
deal-breakers. Grounded in a real BATNA (Best Alternative to a Negotiated
Agreement) rather than an aspirational figure, so later negotiation
sessions and `career-coach`'s final accept/decline call have something
concrete to reason against, not just a wish.

## Session Start

1. Check whether `state/career/comp_target.md` exists.
   - **Doesn't exist → initial mode.** Build it from scratch.
   - **Exists → revisit mode.** Summarize it back to the user, ask what's
     changed. Update in place — don't rebuild from scratch. Update the
     `Last reviewed:` field when done, regardless of how much changed.
2. Read `state/career/trajectory.md` if it exists — its "Comp floor"
   must-have, if one is stated there, is a starting anchor for the more
   granular numbers this file captures, not a substitute for them.

## Sections

- **Last reviewed:** `<date>`
- **BATNA (walk-away alternative)** — the real, concrete alternative that
  gives the numbers below their teeth: a competing offer (with real
  numbers, if any), a firm timeline on a current job, or an honest
  estimate of how long they can search without an offer. Not an
  aspirational number. See `research.md`.
- **Walk-away minimums** — base-salary floor and total-comp floor, below
  which the user declines regardless of how the rest of the package looks.
- **Cash / equity / benefits priority** — how they'd trade between the
  three if a company offered to shift the mix (e.g. more equity for less
  cash, or vice versa), ranked, with the reasoning.
- **Equity risk tolerance** — how much illiquid, probability-weighted
  upside they're willing to hold in place of certain cash, given their own
  risk appetite and financial runway.
- **Deal-breakers** — specific comp-structure terms that end the
  discussion outright (e.g. no severance, no acceleration on change of
  control, an equity-only offer), independent of the headline number.

## Initial Mode — Conversation Guide

Ask one at a time, in the order above.

For BATNA, push for something concrete and real, not aspirational. An
un-communicated or fictional BATNA does nothing for leverage in an actual
negotiation, but the user's own clarity about their real alternative still
shapes what their walk-away number should honestly be. If they have no
current offer and no real timeline pressure, say so plainly rather than
inventing one — "I need a job in 3 months" only counts as BATNA if it's
true.

For walk-away minimums, check consistency against
`state/career/trajectory.md`'s comp floor if one exists. Note explicitly
if this session's numbers refine or diverge from that must-have, but
don't silently overwrite `trajectory.md` — that file belongs to
`define-trajectory`.

For equity risk tolerance, ask plainly: startup equity is often worth
substantially less than the headline valuation implies once illiquidity
and exit probability are priced in — how much of an offer is the user
comfortable having riding on that uncertain outcome versus locked in as
cash?

## Revisit Mode — Conversation Guide

Ask what prompted the revisit — a new offer in hand, a changed financial
situation, feedback from a negotiation that didn't land — or say what you
noticed, if you're the one triggering it. Go section by section only
where something might have changed — don't re-litigate settled sections.
BATNA is the section most likely to be stale — always confirm it's still
accurate before relying on it later in the same session.

## Guardrails

- Never invent a BATNA, a competing offer, or a timeline the user hasn't
  stated. An invented alternative is worse than none — acting on false
  leverage can blow up a real negotiation.
- Don't silently overwrite in revisit mode — confirm changes before
  writing.
```

- [ ] **Step 2: Verify against the checklist above**

Read the file back. Confirm the frontmatter `name`, the five `## Sections` entries (BATNA, walk-away minimums, cash/equity/benefits priority, equity risk tolerance, deal-breakers), and that no guardrail is violated.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/offer-negotiator/SKILL.md
git commit -m "Add offer-negotiator SKILL.md setup mode for comp_target.md"
```

---

### Task 3: Wire `offer-negotiator` setup mode into `bootstrap`

**Files:**
- Modify: `.claude/skills/bootstrap/SKILL.md`

**Interfaces:**
- Consumes: the `offer-negotiator` skill name from Task 2 (referenced by name only — this task doesn't read Task 2's file contents, just invokes the skill the way step 3/4 already invoke `build-profile`/`define-trajectory`).
- Produces: nothing consumed elsewhere in this plan.

**Verify (no automated test — prose skill file, consistent with spec §9):** after editing, read the file back and confirm: (a) the "already complete" branch of step 2 now names all three files; (b) a new branch of step 2 routes straight to the new step when only `comp_target.md` is missing; (c) the new step numbering is internally consistent (no gap, no duplicate step number, wrap-up is the last step).

- [ ] **Step 1: Edit `.claude/skills/bootstrap/SKILL.md`**

Replace the entire `## Steps` section with:

```markdown
## Steps

1. **Preflight check.** Run:
   ```
   python3 --version
   ```
   If this fails (command not found) or reports a version below 3.9, stop
   and tell the user Python 3 is required, with install instructions:
   - macOS: `brew install python3` (or the installer at python.org)
   - Linux: use your distribution's package manager (e.g.
     `apt install python3` on Debian/Ubuntu)
   - Windows: install from python.org, checking "Add to PATH"

   Don't attempt to install Python automatically — this is a machine-wide
   change outside this repo, and the user should control it. Once they
   confirm Python is available, re-run the check before continuing.

2. **Check existing state.**
   - If `state/career/profile.md`, `state/career/trajectory.md`, and
     `state/career/comp_target.md` all already exist, tell the user setup
     already looks complete and ask if they want to revisit any of them
     (hand off to `build-profile`, `define-trajectory`, or
     `offer-negotiator` directly) rather than re-running bootstrap.
   - If `state/career/profile.md` doesn't exist, continue to step 3.
   - If `state/career/profile.md` exists but `state/career/trajectory.md`
     doesn't, skip to step 4.
   - If `state/career/profile.md` and `state/career/trajectory.md` both
     exist but `state/career/comp_target.md` doesn't, skip to step 5.

3. **Run `build-profile`.** Don't proceed to step 4 until
   `state/career/profile.md` is written.

4. **Run `define-trajectory`** (initial mode, since
   `state/career/trajectory.md` doesn't exist yet).

5. **Run `offer-negotiator`** (initial mode, since
   `state/career/comp_target.md` doesn't exist yet).

6. **Wrap up.** Tell the user what was created and point them at
   `score-opportunity` as the natural next step — pasting in a JD to
   evaluate.
```

- [ ] **Step 2: Verify against the checklist above**

Read the file back. Confirm step 2's three routing conditions plus the "all complete" branch, and that steps are numbered 1-6 with no gaps.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/bootstrap/SKILL.md
git commit -m "Route bootstrap step 5 to offer-negotiator setup mode"
```
