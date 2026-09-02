---
name: offer-negotiator
description: Use when a user needs help with compensation — defining or revisiting their target (walk-away numbers, BATNA, target/ask range, comp priorities) as part of first-time bootstrap, or prepping talking points for an early comp conversation before any offer exists. Builds or updates state/career/comp_target.md, or produces first-contact negotiation talking points.
---

# Offer Negotiator

## Purpose

Helps a user navigate compensation across their job search: building and
revisiting their standing compensation target (Setup Mode), and prepping
talking points for an early comp conversation before any offer exists
(First-Contact Prep). Grounded throughout in a real BATNA and
`research.md`'s evidence-graded negotiation tactics, never in invented
numbers or generic scripts.

## Session Start

1. Determine which moment this session is:
   - If `state/career/comp_target.md` doesn't exist, or the user
     explicitly wants to define/revisit their walk-away numbers, target
     range, comp priorities, or deal-breakers → **Setup Mode**. Continue
     with step 2 below.
   - If the user has an upcoming conversation where they expect to be
     asked about comp expectations and doesn't have an offer in hand yet
     (a recruiter screen, an early call) → **First-Contact Prep**. Skip
     the rest of this section and go straight to that section below.
   - If it's ambiguous which the user wants, ask directly rather than
     guessing.
2. (Setup Mode only) Check whether `state/career/comp_target.md` exists.
   - **Doesn't exist → initial mode.** Build it from scratch.
   - **Exists → revisit mode.** Summarize it back to the user, ask what's
     changed. Update in place — don't rebuild from scratch. Update the
     `Last reviewed:` field when done, regardless of how much changed.
3. (Setup Mode only) Read `state/career/trajectory.md` if it exists — its
   "Comp floor" must-have, if one is stated there, is a starting anchor
   for the more granular numbers this file captures, not a substitute for
   them.

## Setup Mode — Sections

- **Last reviewed:** `<date>`
- **BATNA (walk-away alternative)** — the real, concrete alternative that
  gives the numbers below their teeth: a competing offer (with real
  numbers, if any), a firm timeline on a current job, or an honest
  estimate of how long they can search without an offer. Not an
  aspirational number. See `research.md`.
- **Target / ask range** — the specific number or range to actually lead
  with in a first-contact or counter conversation, distinct from the
  walk-away floor below. Per `research.md`'s Anchoring & First Offers
  research, a specific, well-justified number anchors more strongly than
  a round one or waiting to be anchored first — this is what later
  negotiation-moment sessions pull from when giving a number. See
  `research.md`.
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

## Setup Mode — Initial Conversation Guide

Ask one at a time, in the order above.

For BATNA, push for something concrete and real, not aspirational. An
un-communicated or fictional BATNA does nothing for leverage in an actual
negotiation, but the user's own clarity about their real alternative still
shapes what their walk-away number should honestly be. If they have no
current offer and no real timeline pressure, say so plainly rather than
inventing one — "I need a job in 3 months" only counts as BATNA if it's
true.

For the target/ask range, keep it clearly distinct from the walk-away
minimum below — the target is the ambitious, well-justified number to
lead with, not the number they'd merely accept. Per `research.md`, a
specific figure lands harder than a round one, so push for precision
over a vague band.

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

## Setup Mode — Revisit Conversation Guide

Ask what prompted the revisit — a new offer in hand, a changed financial
situation, feedback from a negotiation that didn't land — or say what you
noticed, if you're the one triggering it. Go section by section only
where something might have changed — don't re-litigate settled sections.
BATNA is the section most likely to be stale — always confirm it's still
accurate before relying on it later in the same session.

## First-Contact Prep

Tactical prep for an early comp conversation — a recruiter screen or
first call — before any offer exists. No market-data research needed:
this moment works entirely from the JD/conversation (role, level, geo)
and, if it exists, `state/career/comp_target.md`.

Read only `research.md`'s "Anchoring & First Offers", "BATNA", and
"Deflecting Salary History / Expectation Questions" subsections (see the
moment index near the top of that file) — skip the rest.

### Session Start

1. Identify the role/level/geo context — from the JD if one's been
   scored (`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"`
   to resolve the folder and read `jd.md`), or from what the user
   describes in conversation if no opportunity has been created yet.
2. Read `state/career/comp_target.md` if it exists, for the target/ask
   range and walk-away minimums — this moment should ground any number it
   suggests in that file, not invent one.

### What to Produce

1. **How to answer "what are your comp expectations."** Per
   `research.md`'s Anchoring & First Offers findings: if the user has a
   real target range (from `comp_target.md` or credible public comp
   data) and the counterpart likely doesn't have better information than
   they do, coach them to give a specific, well-justified number first —
   not a round one, and not silence. If they don't yet know the role's
   real band, or the counterpart clearly has better market visibility
   (e.g. an in-house recruiter), coach deflection instead.
2. **Deflection language**, when deflection is the right play — per
   `research.md`'s Deflecting Salary History / Expectation Questions
   findings: redirect to role fit and the employer's budgeted range
   before naming a number, without being evasive to the point of
   damaging rapport.
3. **When to give a range vs. decline to answer** — tie this explicitly
   back to whether the user has real market information (from
   `comp_target.md`) and how much leverage they'd give up by naming a
   number too early, per the BATNA and Anchoring findings above.

### Output

Deliver the talking points directly in the chat response. If there's a
resolved opportunity folder for this conversation and the user wants it
saved, append it to that opportunity's `notes.md` under a
`## First-Contact Prep (<date>)` heading.

## Guardrails

- Never invent a BATNA, a competing offer, or a timeline the user hasn't
  stated. An invented alternative is worse than none — acting on false
  leverage can blow up a real negotiation.
- Don't silently overwrite in revisit mode — confirm changes before
  writing.
- Never assert a target/ask number in First-Contact Prep that isn't
  grounded in `comp_target.md` or the user's own conversation — this
  moment coaches how to use a number, it doesn't invent one.
