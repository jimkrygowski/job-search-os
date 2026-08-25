---
name: tailor-resume
description: Use when a user wants a resume and/or cover letter tailored to a specific opportunity already in the pipeline. Reads state/career/resume/master_resume.md and the opportunity's jd.md, writes resume.md and cover_letter.md into that opportunity's folder.
---

# Tailor Resume

## Purpose

Produce `resume.md` and `cover_letter.md` in the target opportunity's
resolved folder (see Session Start) from the master resume and the
specific JD — without inventing anything not in the master resume or
`state/career/profile.md`.

## Session Start

Resolve the opportunity folder via
`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` — never
construct the path yourself from the typed Company/Role, so you land in
the exact folder `score-opportunity` already created. Read
`state/career/resume/master_resume.md`, `state/career/profile.md`, and
the resolved folder's `jd.md`. If any of these don't exist, tell the user
what's missing rather than improvising around the gap (a missing `jd.md`
means `score-opportunity` hasn't been run yet; no master resume means the
user hasn't provided one yet via `build-profile`, or needs to add
`state/career/resume/master_resume.md` directly).

## Resume

1. Identify the JD's key requirements and keywords.
2. Select and reorder relevant experience from the master resume — do not
   add experience, skills, or accomplishments that aren't in the master
   resume or something the user states directly in this conversation.
3. Where the JD wants something the master resume doesn't clearly show,
   say so to the user rather than papering over it — ask if there's
   relevant experience missing from the master resume, or flag it as a
   real gap.
4. Write `resume.md` inside the resolved opportunity folder. ATS-friendly:
   no tables, no columns, no graphics.
5. Include a brief keyword-gap note at the end of your chat response (not
   the file) — what the JD asks for that the tailored resume doesn't
   fully cover.

## Cover Letter

Write `cover_letter.md` inside the same resolved opportunity folder,
connecting specific experience from the master resume to the company's
stated needs in the JD. Ask the user if there's a specific angle they
want emphasized before drafting.

## Guardrails

- Never invent experience, metrics, or accomplishments. Every claim must
  trace to `state/career/resume/master_resume.md`, `state/career/profile.md`, or something the user
  says directly.
- This skill never sends anything — it only writes files.
