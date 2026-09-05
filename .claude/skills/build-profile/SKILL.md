---
name: build-profile
description: Use when a user needs to create or update their career profile — either as part of first-time bootstrap or any time their background needs re-capturing. Guides a conversation about career history, best/worst jobs and bosses, and produces state/career/profile.md.
---

# Build Profile

## Purpose

Produce `state/career/profile.md` — the source of truth for who this person is
professionally. Read by every other skill in this system (`career-coach`,
`tailor-resume`, `score-opportunity`, `define-trajectory`, etc.), so it
must be concrete, not vague.

## Session Start

1. Check whether `state/career/profile.md` already exists, and if so,
   whether it's complete — every section in `## Output` below present as
   a `##` heading with real, substantive content underneath, not just
   the heading itself or a placeholder like "TBD."
   `tools/check_bootstrap_state.py`'s SessionStart hook only checks that
   each heading exists with *something* under it (a cheap presence
   check, no judgment call) to decide whether to flag this file at all
   — the actual judgment of whether the content is good enough is yours
   to make here, reading the real file.
   - **Doesn't exist → initial mode.**
   - **Exists and complete → revisit mode.** Tell the user what's
     already captured and ask whether they want to add to it, correct
     something, or redo a section — don't silently overwrite.
   - **Exists but incomplete → resume mode.** A previous session likely
     got interrupted. Tell the user plainly what's already captured and
     which sections are still missing or thin, then go straight to
     finishing those — don't restart from scratch, and don't ask a
     generic "what do you want to add" question when the gap is already
     clear.
2. (Initial mode and resume mode) Ask whether they have an existing
   resume to seed from (`state/career/resume/master_resume.md`, or a
   resume they can paste/upload) — skip this if they already answered
   in a prior session. If yes, read it and draft an initial pass at the
   relevant sections for them to correct rather than starting from a
   blank page (in resume mode, only the sections still missing or thin).
   If no, build those sections from conversation alone.
   - If the user provides an existing resume (pasted, uploaded, or
     otherwise supplied) and `state/career/resume/master_resume.md` doesn't
     already exist, write it there as-is (creating the `state/career/resume/`
     directory if needed) so it becomes the source-of-truth resume other
     skills (`tailor-resume`) depend on.

## What to Capture

Work through these one at a time — don't dump all the questions at once:

1. **Career history** — company by company: what they did, what changed,
   why they moved on.
2. **Best job, and why.** What specifically made it the best — the work,
   the people, the autonomy, the growth, the outcome?
3. **Worst job, and why.** Same level of specificity.
4. **Best boss, and why.** What did that person actually do that made
   them good to work for?
5. **Worst boss, and why.**
6. **Patterns.** After all five, name back to the user what you're
   noticing — a real pattern across their answers, not a generic
   observation. This feeds `define-trajectory` directly.

## Resume Mode — Conversation Guide

Name which of the six sections in `## Output` are missing or thin, then
work through only those — in the order listed in `## What to Capture` —
one at a time, the same way `## What to Capture` describes. Skip
sections that are already there with real content; don't re-ask
questions the user already answered in a prior session.

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

## Guardrails

- Never invent career history the user didn't state. If a resume you're
  seeding from has a gap or unclear detail, ask rather than assume.
- One question at a time — follow up on interesting answers before
  moving to the next section.
