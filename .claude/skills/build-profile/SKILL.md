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

1. Check whether `state/career/profile.md` already exists.
   - If it exists, tell the user what's already captured and ask whether
     they want to add to it, correct something, or redo a section — don't
     silently overwrite.
   - If it doesn't exist, this is a first-time build.
2. Ask whether they have an existing resume to seed from
   (`state/career/resume/master_resume.md`, or a resume they can paste/upload).
   If yes, read it and draft an initial pass at the sections below for
   them to correct rather than starting from a blank page. If no, build
   the sections from conversation alone.
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

## Output

Write `state/career/profile.md` with clear headers matching the sections above.
Use the user's own words and specifics where possible — this file is
read by skills that draft resumes and cover letters, and vague profile
content produces vague drafts.

## Guardrails

- Never invent career history the user didn't state. If a resume you're
  seeding from has a gap or unclear detail, ask rather than assume.
- One question at a time — follow up on interesting answers before
  moving to the next section.
