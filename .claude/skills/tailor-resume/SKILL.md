---
name: tailor-resume
description: Use when a user wants a resume and/or cover letter tailored to a specific opportunity already in the pipeline. Reads career/resume/master_resume.md and the opportunity's jd.md, writes resume.md and cover_letter.md into that opportunity's folder.
---

# Tailor Resume

## Purpose

Produce `opportunity/<Company>/<Role>/resume.md` and
`opportunity/<Company>/<Role>/cover_letter.md` from the master resume and
the specific JD — without inventing anything not in the master resume or
`career/profile.md`.

## Session Start

Read `career/resume/master_resume.md`, `career/profile.md`, and the
target opportunity's `jd.md`. If any of these don't exist, tell the user
what's missing rather than improvising around the gap (a missing `jd.md`
means `score-opportunity` hasn't been run yet; no master resume means
`build-profile` hasn't produced one).

## Resume

1. Identify the JD's key requirements and keywords.
2. Select and reorder relevant experience from the master resume — do not
   add experience, skills, or accomplishments that aren't in the master
   resume or something the user states directly in this conversation.
3. Where the JD wants something the master resume doesn't clearly show,
   say so to the user rather than papering over it — ask if there's
   relevant experience missing from the master resume, or flag it as a
   real gap.
4. Write `opportunity/<Company>/<Role>/resume.md`. ATS-friendly: no
   tables, no columns, no graphics.
5. Include a brief keyword-gap note at the end of your chat response (not
   the file) — what the JD asks for that the tailored resume doesn't
   fully cover.

## Cover Letter

Write `opportunity/<Company>/<Role>/cover_letter.md`, connecting specific
experience from the master resume to the company's stated needs in the
JD. Ask the user if there's a specific angle they want emphasized before
drafting.

## Guardrails

- Never invent experience, metrics, or accomplishments. Every claim must
  trace to `master_resume.md`, `career/profile.md`, or something the user
  says directly.
- This skill never sends anything — it only writes files.
