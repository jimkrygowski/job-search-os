---
name: interview-prep
description: Use when a user has an upcoming interview or call and wants a prep briefing. Reads the opportunity's jd.md, notes.md, contacts.md, and state/career/trajectory.md to produce likely questions and talking points.
---

# Interview Prep

## Purpose

Produce a prep briefing ahead of a specific call or interview.

## Session Start

Identify which opportunity and which stage of interview this is for, and
resolve its folder via
`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` — never
construct the path yourself from the typed Company/Role. Read `jd.md`,
`notes.md`, and `contacts.md` from that folder, plus
`state/career/trajectory.md`.

## Briefing Contents

1. **Who they're likely talking to** — from `contacts.md`, plus what's
   known about that person's role and priorities from `notes.md`.
2. **Likely questions** — grounded in the JD and this stage of the
   process (a recruiter screen asks different things than a CEO round).
3. **Suggested talking points** — drawn from `state/career/profile.md` and
   `state/career/resume/master_resume.md`, matched to what this specific interviewer likely
   cares about. Don't invent accomplishments to fit — if there's a gap
   between what they'll probably ask and what the user has to offer, name
   it and help them think through how to answer honestly.
4. **Questions the user should ask** — grounded in `state/career/trajectory.md`
   must-haves/must-nots that this stage of the process can actually
   surface information about (e.g. reporting line, team structure).

## Output

Write the briefing into the chat response. If the user wants it saved,
append it to the resolved opportunity folder's `notes.md` under an
`## Interview Prep (<date>)` heading.
