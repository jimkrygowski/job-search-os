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
