---
name: bootstrap
description: Use when a new user is setting up this system for the first time, or when state/career/profile.md, state/career/trajectory.md, or state/career/comp_target.md don't exist yet. Runs a Python preflight check, then build-profile, then define-trajectory, then offer-negotiator's setup mode, in sequence.
---

# Bootstrap

## Purpose

First-time setup orchestrator. Gets a new user from a fresh `git clone`
to a working `state/career/profile.md`, `state/career/trajectory.md`, and
`state/career/comp_target.md`.

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

2. **Check existing state.** "Exists" below means exists AND has all of
   its required sections filled in with real content (see
   `build-profile`, `define-trajectory`, and `offer-negotiator`'s own
   `SKILL.md` for each file's required headings) — not just present on
   disk. A file with the right headings but empty or stub content under
   them doesn't count; treat it the same as if the file didn't exist,
   and re-run the skill that produces it rather than skipping past it.
   - If `state/career/profile.md`, `state/career/trajectory.md`, and
     `state/career/comp_target.md` all exist by that standard, tell the
     user setup already looks complete and ask if they want to revisit
     any of them (hand off to `build-profile`, `define-trajectory`, or
     `offer-negotiator` directly) rather than re-running bootstrap.
   - If `state/career/profile.md` doesn't exist (by that standard),
     continue to step 3 — if the file is present but incomplete, mention
     that a previous session may have been interrupted before finishing
     it.
   - If `state/career/profile.md` exists but `state/career/trajectory.md`
     doesn't, skip to step 4.
   - If `state/career/profile.md` and `state/career/trajectory.md` both
     exist but `state/career/comp_target.md` doesn't, skip to step 5.

3. **Run `build-profile`.** Don't proceed to step 4 until
   `state/career/profile.md` is complete (see step 2's definition).

4. **Run `define-trajectory`** — it will detect from the file itself
   whether that's initial mode (missing) or resume mode (incomplete).

5. **Run `offer-negotiator`** — it will detect from the file itself
   whether that's initial mode (missing) or resume mode (incomplete).

6. **Wrap up.** Tell the user what was created and point them at
   `score-opportunity` as the natural next step — pasting in a JD to
   evaluate.
