---
name: company-research
description: Use when a user wants research on a target company — for a new opportunity or ahead of an interview. Writes cited findings into that opportunity's notes.md.
---

# Company Research

## Purpose

Research a company relevant to a specific opportunity and record findings
in `state/opportunity/<Company>/<Role>/notes.md` with sources attached.

## Session Start

Confirm which opportunity this research is for, then resolve its folder
via `python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` —
never construct the path yourself from the typed Company/Role. If that
folder doesn't exist yet, ask whether to run `score-opportunity` first —
but proceed anyway if the user wants to look before pasting the JD.

## What to Research

- Recent news, funding, leadership changes
- Product/market position and how the role's function fits into it
- Anything relevant to the specific role — team size, reporting line,
  recent org changes
- Anything relevant to the person's must-haves/must-nots from
  `state/career/trajectory.md` (e.g. if remote-vs-hybrid is a must-have, look
  for signal on that specifically)

## Output

Append to `notes.md` in the resolved opportunity folder under a
`## Company Research (<date>)` heading. Every finding gets a source (URL,
or "user's own knowledge" if it came from the conversation, or "my
inference" if you're inferring rather than citing something concrete —
label it explicitly, don't blend it in as fact).
