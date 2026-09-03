---
name: define-trajectory
description: Use when a user needs to define or revisit their target role and career direction — as part of first-time bootstrap, or any time real feedback (an interview outcome, a networking conversation, a "golden question" conversation) suggests their must-haves have changed. Builds or updates state/career/trajectory.md in the Mnookin Two-Pager format.
---

# Define Trajectory

## Purpose

Produce or update `state/career/trajectory.md` — the target-role definition
used by `score-opportunity`, `career-coach`, and `interview-prep`. Shaped
as a "Mnookin Two-Pager" (from *Never Search Alone*, Phyl Terry): a
concise, honest pitch document, not an internal wishlist. It should be
something the user could actually hand to a recruiter or a contact.

## Session Start

1. Check whether `state/career/trajectory.md` exists, and if so, whether
   it's complete — every `##` section listed in `## Sections (Mnookin
   Two-Pager shape)` below present as a `##` heading with substantive content
   underneath, not just the heading itself or a placeholder line (the
   same completeness standard `tools/check_bootstrap_state.py` checks).
   - **Doesn't exist → initial mode.** Build it from scratch.
   - **Exists and complete → revisit mode.** Summarize it back to the
     user, ask what's changed. Update in place — don't rebuild from
     scratch. Update the `Last reviewed:` field when done, regardless of
     how much changed.
   - **Exists but incomplete → resume mode.** A previous session likely
     got interrupted. Tell the user plainly which sections are already
     captured and which are still missing or thin, then go straight to
     finishing those.
2. Read `state/career/profile.md` first if it exists — trajectory should build
   on the patterns identified there, not ignore them.

## Sections (Mnookin Two-Pager shape)

- **Last reviewed:** `<date>`
- **What I love doing** — the work itself, specifically.
- **What I hate doing** — equally specific.
- **Must-haves** — non-negotiable for the next role.
- **Must-nots** — dealbreakers.
- **Short-term goal (next role)** — what the next role needs to be.
- **Long-term goal (3-5 years)** — where this is heading.
- **Strengths** — grounded in `state/career/profile.md`, not generic.
- **Weaknesses / stretch areas** — honest, not softened.

Write `**Last reviewed:** <date>` as a one-line field near the top (not
its own section), then a `##` heading for each of the other eight items
above, using this exact wording as the start of the heading: `## What I
Love Doing`, `## What I Hate Doing`, `## Must-Haves`, `## Must-Nots`,
`## Short-Term Goal (Next Role)`, `## Long-Term Goal (3-5 years)`,
`## Strengths`, `## Weaknesses / Stretch Areas`. These headings are
load-bearing in two places: `tools/score_table.py` requires the
Must-Haves/Must-Nots/Short-Term-Goal headings verbatim to parse scoring
criteria, and `tools/check_bootstrap_state.py` checks all eight (by
prefix) to confirm this file represents finished work, not an
interrupted session.

## Initial Mode — Conversation Guide

Ask one at a time, in the order above. For must-haves/must-nots, push for
specificity — "good culture" is not a must-have, "reports to the CEO or
founder, not another engineering exec" is.

For the short-term goal, do an honest stretch assessment: given
`state/career/profile.md`, is the target role a lateral move, a stretch, or a
reach? Say so directly. If it's a stretch or reach, talk through how to
position existing experience or what gap needs filling before or during
the search.

## Resume Mode — Conversation Guide

Name which sections from `## Sections (Mnookin Two-Pager shape)` are
missing or thin, then work through only those, one at a time, using the
same guidance as Initial Mode above for each. Skip sections that are
already there with real content — don't re-ask what the user already
answered in a prior session. Update `Last reviewed:` when done, same as
Revisit Mode.

## Revisit Mode — Conversation Guide

Ask what prompted the revisit (or say what you noticed, if you're the one
triggering it — a `career-coach` staleness flag, or feedback from a
recent interview/conversation). Go section by section only where
something might have changed — don't re-litigate settled sections.
Explicitly ask the Never Search Alone "golden question" if the user has
had any recent networking or informational conversations: *"Based on
what [contact] told you, would you approach this search any differently
now?"*

## Guardrails

- Stay honest, not aspirational — the stretch/gap assessment only works
  if it isn't softened for comfort.
- Don't silently overwrite in revisit mode — confirm changes before
  writing.
