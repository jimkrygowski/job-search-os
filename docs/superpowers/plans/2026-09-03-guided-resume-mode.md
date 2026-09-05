# Guided Resume Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `build-profile`, `define-trajectory`, and `offer-negotiator`'s Setup Mode each currently have only two session-start branches: file doesn't exist (build from scratch) or file exists (a generic revisit/add-to-it prompt). That second branch doesn't distinguish "genuinely complete, user wants to revise" from "incomplete stub from an interrupted session" — a distinction the bootstrap-content-validation plan just made real and checkable. Add a third branch to all three skills: when a file exists but is incomplete, name the specific gaps and guide the user through finishing only those, rather than a generic prompt or a from-scratch restart. The user is never editing these files directly — they're assisted through completing them, so the agent (not the user) is the one that needs to know exactly what's missing.

**Origin:** Direct follow-on request in conversation (not a PR review comment) after reviewing what `tools/check_bootstrap_state.py`'s new content-completeness check made possible. Confirmed scope: "if the profile is incomplete the flow i'd prefer would be to get the agent running to guide the user through completion of the profile. the user isn't editing it directly — they're being assisted... do it for all 3 skills."

**Architecture:** Three independent full-file replacements, one per skill, each following the identical pattern established in this session's prior bootstrap-content-validation plan: a file counts as "exists" only if every required section (already documented in that skill's own file, from that plan's Task 1) is present with substantive content, not just a heading or a placeholder. Where a skill's session-start check currently branches on raw existence, it now branches three ways: doesn't exist → initial mode (unchanged); exists and complete → revisit mode (unchanged); exists but incomplete → new **Resume Mode**, which names the specific missing/thin sections and works through only those, reusing each skill's existing Initial-Mode per-section guidance rather than duplicating it. No Python code changes — this is entirely skill prose, consistent with the established convention that skill prose isn't unit-tested.

**Tech Stack:** Markdown/prose only. No new dependencies, no test files.

## Global Constraints

- **"Complete" means the same thing here as it does in `tools/check_bootstrap_state.py`**: every required section (per that skill's own already-documented list — `build-profile/SKILL.md`'s `## Output`, `define-trajectory/SKILL.md`'s `## Sections (Mnookin Two-Pager shape)`, `offer-negotiator/SKILL.md`'s `## Setup Mode — Sections`) present as a heading with substantive content underneath, not just the heading itself or a placeholder line. Each skill's new completeness-check instruction explicitly names this as "the same completeness standard `tools/check_bootstrap_state.py` checks" — the standard is conceptually shared even though the hook checks it with a regex and the skill checks it by reading the file directly, since only the skill session has the judgment to tell substantive content from a thin placeholder.
- **Resume Mode never restarts from scratch and never asks a generic "what do you want to add" question when the gap is already known.** It names the specific missing/thin sections and goes straight to finishing them.
- **Resume Mode reuses each skill's existing Initial-Mode per-section guidance for the sections it's completing** — it does not duplicate that guidance in a new form. It only adds the "which sections, and skip the ones already done" framing.
- **Revisit Mode's existing behavior and wording are unchanged** — it only becomes reachable when the file is genuinely complete, which is a routing change (this plan's whole point), not a content change to what Revisit Mode itself says or does.
- **No Python code, no new tests** — this plan touches only `.claude/skills/build-profile/SKILL.md`, `.claude/skills/define-trajectory/SKILL.md`, and `.claude/skills/offer-negotiator/SKILL.md`.
- Follow each file's own established prose conventions exactly (bold mode labels like `**Doesn't exist → initial mode.**`, `### <Heading>` for offer-negotiator's per-moment subsections, etc.) — these are established, working conventions, not something this plan should redesign.

---

### Task 1: `build-profile/SKILL.md` — Resume Mode

**Files:**
- Modify: `.claude/skills/build-profile/SKILL.md` (full-file replacement — see Step 1)

**Interfaces:**
- Consumes: nothing from other tasks (fully independent — a different file than Tasks 2-3 touch).
- Produces: nothing consumed elsewhere in this plan.

**Verify (no automated test — prose file, consistent with established convention):** after writing, confirm: (a) `## Session Start` step 1 has three branches (doesn't exist / exists+complete / exists+incomplete), each correctly labeled; (b) a new `## Resume Mode — Conversation Guide` section exists between `## What to Capture` and `## Output`, and explicitly points back to `## Output`'s six sections and `## What to Capture`'s ordering rather than re-describing them; (c) `## Output`'s six load-bearing headings and everything below them are otherwise unchanged from the current file; (d) `## Guardrails` is otherwise unchanged.

- [ ] **Step 1: Replace `.claude/skills/build-profile/SKILL.md` in full**

```markdown
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
   a `##` heading with substantive content underneath, not just the
   heading itself or a placeholder line (the same completeness standard
   `tools/check_bootstrap_state.py` checks).
   - **Doesn't exist → first-time build.**
   - **Exists and complete → revisit mode.** Tell the user what's
     already captured and ask whether they want to add to it, correct
     something, or redo a section — don't silently overwrite.
   - **Exists but incomplete → resume mode.** A previous session likely
     got interrupted. Tell the user plainly what's already captured and
     which sections are still missing or thin, then go straight to
     finishing those — don't restart from scratch, and don't ask a
     generic "what do you want to add" question when the gap is already
     clear.
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
```

- [ ] **Step 2: Verify against the checklist above**

Read the file back and confirm the four points in this task's Verify section.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/build-profile/SKILL.md
git commit -m "Add build-profile Resume Mode for incomplete profile.md"
```

---

### Task 2: `define-trajectory/SKILL.md` — Resume Mode

**Files:**
- Modify: `.claude/skills/define-trajectory/SKILL.md` (full-file replacement — see Step 1)

**Interfaces:**
- Consumes: nothing from other tasks (fully independent — a different file than Tasks 1/3 touch).
- Produces: nothing consumed elsewhere in this plan.

**Verify (no automated test — prose file, consistent with established convention):** after writing, confirm: (a) `## Session Start` step 1 has three branches (doesn't exist / exists+complete / exists+incomplete); (b) a new `## Resume Mode — Conversation Guide` section exists between `## Initial Mode — Conversation Guide` and `## Revisit Mode — Conversation Guide`, and points back to `## Sections (Mnookin Two-Pager shape)` and reuses Initial Mode's guidance rather than duplicating it; (c) `## Sections (Mnookin Two-Pager shape)`'s eight load-bearing headings and its `score_table.py`/`check_bootstrap_state.py` note are otherwise unchanged; (d) `## Initial Mode`, `## Revisit Mode`, and `## Guardrails` content is otherwise unchanged from the current file.

- [ ] **Step 1: Replace `.claude/skills/define-trajectory/SKILL.md` in full**

```markdown
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
   it's complete — every section in `## Sections (Mnookin Two-Pager
   shape)` below present as a `##` heading with substantive content
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
```

- [ ] **Step 2: Verify against the checklist above**

Read the file back and confirm the four points in this task's Verify section.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/define-trajectory/SKILL.md
git commit -m "Add define-trajectory Resume Mode for incomplete trajectory.md"
```

---

### Task 3: `offer-negotiator/SKILL.md` — Setup Mode Resume

**Files:**
- Modify: `.claude/skills/offer-negotiator/SKILL.md` (full-file replacement — see Step 1)

**Interfaces:**
- Consumes: nothing from Tasks 1-2 (fully independent — a different file).
- Produces: nothing consumed elsewhere in this plan.

**Verify (no automated test — prose file, consistent with established convention):** after writing, confirm: (a) `## Session Start` step 1's dispatch fallback condition and step 2 (Setup Mode's own exists-check) both use the completeness standard, not raw existence; (b) a new `## Setup Mode — Resume Conversation Guide` section exists between `## Setup Mode — Initial Conversation Guide` and `## Setup Mode — Revisit Conversation Guide`, and points back to `## Setup Mode — Sections` and reuses the Initial Conversation Guide's guidance rather than duplicating it; (c) every other moment (`## First-Contact Prep`, `## Offer Breakdown`, `## Counter-Negotiation Planning`, `## Final Accept/Decline`) and `## Guardrails` are completely unchanged from the current file — this task touches only the dispatch condition, step 2, and the new Resume section.

- [ ] **Step 1: Replace `.claude/skills/offer-negotiator/SKILL.md` in full**

```markdown
---
name: offer-negotiator
description: Use when a user needs help with compensation — defining or revisiting their target (walk-away numbers, BATNA, target/ask range, comp priorities) as part of first-time bootstrap, prepping talking points for an early comp conversation before any offer exists, breaking down an actual offer's numbers against market data and option_value.py, planning a specific counter-negotiation script once an offer is broken down, or handing an opportunity's final accept/decline decision off to career-coach with the comp facts it needs. Builds or updates state/career/comp_target.md, and writes sourced offer breakdowns and counter-negotiation plans to that opportunity's notes.md.
---

# Offer Negotiator

## Purpose

Helps a user navigate compensation across the full arc of a job search:
building and revisiting their standing compensation target (Setup Mode),
prepping talking points for an early comp conversation before any offer
exists (First-Contact Prep), breaking down an actual offer's numbers
against sourced market data and a real equity valuation (Offer
Breakdown), turning that breakdown into a specific counter-negotiation
script (Counter-Negotiation Planning), and — once negotiation is done —
handing the actual accept/decline call to `career-coach` with real comp
facts already in `notes.md` (Final Accept/Decline). Grounded throughout
in a real BATNA, `research.md`'s evidence-graded negotiation tactics, and
`option_value.py`'s deterministic equity math — never in invented numbers
or generic scripts.

## Disclaimer

This skill is AI assistance, not a financial advisor, a lawyer, or a
CPA. Like any AI system, it can make mistakes — miscount a number, cite
a stale market figure, or reason imperfectly about a specific offer's
terms. Everything it produces (target ranges, offer breakdowns, counter
scripts) is meant to sharpen the user's own thinking and give them
language to work with, not a decision made on their behalf. The user is
solely responsible for verifying the numbers and reasoning here, and for
the negotiation and accept/decline decisions they ultimately make.

Equity valuation specifically carries real tax consequences this skill
does not model (design spec §2, §7): exercising ISOs can trigger real
cash Alternative Minimum Tax liability on a paper gain — before any
liquidity event, and even if the company's value later falls — while
NSOs create ordinary income tax at exercise regardless of option type
(`research.md`'s ISO vs. NSO Tax Treatment and AMT section). Flag this
risk whenever exercise timing comes up in Offer Breakdown or
Counter-Negotiation Planning, and tell the user to model their specific
numbers with a qualified tax advisor or CPA before exercising anything
— never estimate or recommend a specific tax outcome.

## Session Start

1. Determine which moment this session is:
   - If the user has an actual offer in hand, determine what they want to
     do with it:
     - Break its numbers down (base/bonus/equity/benefits) against
       market data → **Offer Breakdown**. Skip the rest of this section
       and go straight to that section below.
     - Plan how to counter or negotiate it → **Counter-Negotiation
       Planning**. Skip the rest of this section and go straight to that
       section below.
     - Decide whether to accept or decline it → **Final Accept/Decline**.
       Skip the rest of this section and go straight to that section
       below.
   - If the user has an upcoming conversation where they expect to be
     asked about comp expectations and doesn't have an offer in hand yet
     (a recruiter screen, an early call) → **First-Contact Prep**. Skip
     the rest of this section and go straight to that section below.
   - If the user explicitly wants to define/revisit their walk-away
     numbers, target range, comp priorities, or deal-breakers, or if none
     of the above apply and `state/career/comp_target.md` doesn't exist
     or is incomplete → **Setup Mode**. Continue with step 2 below.
   - If it's ambiguous which the user wants, ask directly rather than
     guessing.
2. (Setup Mode only) Check whether `state/career/comp_target.md` exists,
   and if so, whether it's complete — every section in `## Setup Mode —
   Sections` below present as a `##` heading with substantive content
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
3. (Setup Mode only) Read `state/career/trajectory.md` if it exists — its
   "Comp floor" must-have, if one is stated there, is a starting anchor
   for the more granular numbers this file captures, not a substitute for
   them.

## Setup Mode — Sections

Read only `research.md`'s "Anchoring & First Offers" and "BATNA (Best Alternative to a Negotiated Agreement)" subsections (see the moment index near the top of that file) — skip the rest.

Write `state/career/comp_target.md` with `**Last reviewed:** <date>` as
a one-line field near the top (not its own section), then a `##`
heading for each of the other six items below, using this exact wording
as the start of the heading: `## BATNA`, `## Target / Ask Range`,
`## Walk-Away Minimums`, `## Cash / Equity / Benefits Priority`,
`## Equity Risk Tolerance`, `## Deal-Breakers`. These headings are
load-bearing: `tools/check_bootstrap_state.py` checks for them (by
prefix) to confirm this file represents finished setup, not an
interrupted session.

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

## Setup Mode — Resume Conversation Guide

Name which sections from `## Setup Mode — Sections` are missing or thin,
then work through only those, one at a time, using the same guidance as
the Initial Conversation Guide above for each. Skip sections that are
already there with real content. Update `Last reviewed:` when done, same
as the Revisit Conversation Guide.

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

Read only `research.md`'s "Anchoring & First Offers", "BATNA (Best
Alternative to a Negotiated Agreement)", and "Deflecting Salary History /
Expectation Questions" subsections (see the moment index near the top of
that file) — skip the rest.

### Session Start

1. Identify the role/level/geo context — from the JD if one's been
   scored (`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"`
   to resolve the folder and read `jd.md`), or from what the user
   describes in conversation if no opportunity has been created yet.
2. Read `state/career/comp_target.md` if it exists, for the target/ask
   range and walk-away minimums — this moment should ground any number it
   suggests in that file, not invent one.

If `state/career/comp_target.md` doesn't exist yet, mention that running Setup Mode first would ground this session's numbers better — but do the First-Contact Prep the user asked for first, don't block on it.

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

## Offer Breakdown

Breaks down an actual offer's numbers — base, bonus, equity, benefits —
against market context, and runs any equity grant through
`option_value.py` (below) rather than accepting the company's face-value
pitch.

This moment needs no `research.md` content directly — the Equity & Comp
Mechanics reasoning is already baked into `option_value.py`'s docstrings
(per `research.md`'s moment index); market-benchmark sourcing follows
CLAUDE.md guardrail #2 (every claim needs a source and a date), not this
file.

### Session Start

Confirm which opportunity this offer is for, then resolve its folder via
`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` — never
construct the path yourself. If that folder doesn't exist yet, run
`score-opportunity` first, or ask whether to.

If `state/career/comp_target.md` doesn't exist yet, mention that Setup Mode would give this breakdown a walk-away number to compare against — but do the Offer Breakdown the user asked for first, don't block on it.

### Gathering the Offer

Get the offer numbers from the user — a pasted offer letter, or a verbal
recap of what was said on a call. Never invent or assume a number that
wasn't given. Capture, at minimum:
- Base salary
- Bonus (target %, and whether it's guaranteed in year one)
- Equity grant: share count (or %), strike price (for options), and the
  company's stated/quoted share price (last-round preferred price, 409A,
  or public price — note which)
- The company's funding stage (`public`, or `seed`/`series_a`/
  `series_b`/`series_c`/`series_d_plus`/generic `private` if the specific
  stage isn't known) — needed for `option_value.py`'s `company_stage`
  input
- Benefits: health/dental/vision, retirement match, PTO policy, any
  other named perks

### Market Context

Research comparable comp for this role/level/geo using `WebSearch`/
`WebFetch`. Every benchmark gets a source and a date — CLAUDE.md
guardrail #2 applies directly; never assert a market figure without one.
If no credible source is found, say so rather than guessing a number.

### Valuing the Equity

Never value equity at face value (shares × spread) alone — run it through
`option_value.py`:

```
python3 tools/option_value.py compute
```

reading a JSON object on stdin with these keys (required: `shares`,
`strike_price`, `quoted_price`, `company_stage`; optional:
`preference_stack`, `fully_diluted_shares`, `exit_probability_override`
(`{"low", "high"}`), `time_to_liquidity_years`, `volatility`,
`dlom_override` (`{"low", "high"}`), `cash_alternative`) — see
`tools/option_value.py`'s own docstrings for exactly what each optional
key does and its sourcing. The tool prints a JSON breakdown (face value,
preference-stack adjustment, exit-probability range, final risk-adjusted
range, and any caveats) — relay this breakdown, including every caveat it
returns, rather than collapsing it into a single number. For a
private-stage grant, if `preference_stack`/`fully_diluted_shares` weren't
supplied, the tool's `preference_adjustment.applied` will be `false` with
guidance on what to ask the company for — pass that guidance back to the
user rather than silently treating the equity as fully at face value.

For an RSU grant (no strike price), pass `strike_price: 0` — the tool's face-value math (`shares * max(0, quoted_price - strike_price)`) handles this correctly. If a required input (share count, quoted price, or company stage) genuinely isn't known, ask the user for it rather than guessing — the tool will reject a missing required key outright, and a guessed number is worse than an honest "we don't have this yet."

### Output

Write the breakdown to the resolved opportunity's `notes.md` under a
`## Offer Breakdown (<date>)` heading: the raw offer numbers as given,
the sourced market context, and `option_value.py`'s full output
(including its caveats) for the equity component.

## Counter-Negotiation Planning

Synthesizes an offer's breakdown, `state/career/comp_target.md`'s
walk-away numbers and priorities, and `research.md`'s negotiation
tactics into a specific talking-points script for countering a real
offer — not a generic "always counter 10-15%" template.

Read only `research.md`'s "Integrative (Multi-Issue) Negotiation",
"Gender and Framing Effects in Salary Negotiation", and "Deadline and
Pressure Tactics" subsections (see the moment index near the top of that
file) — skip the rest.

### Session Start

1. Confirm which opportunity this is for, then resolve its folder via
   `python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` —
   never construct the path yourself.
2. Read that folder's `notes.md`, specifically its most recent
   `## Offer Breakdown (<date>)` section. If none exists, offer to run
   Offer Breakdown first, or ask the user for the offer numbers directly
   — never fabricate numbers to skip this step.
3. Read `state/career/comp_target.md` if it exists, for the target/ask
   range, walk-away minimums, and cash/equity/benefits priority.

If `state/career/comp_target.md` doesn't exist yet, mention that Setup Mode would ground this plan in real numbers rather than whatever the user states in the moment — but proceed with what the user gives directly in conversation, don't block on it.

### What to Produce

1. **Package framing across dimensions** — per `research.md`'s
   Integrative (Multi-Issue) Negotiation findings: don't negotiate base
   salary in isolation. Use `comp_target.md`'s cash/equity/benefits
   priority (or ask for one directly if it's missing) to identify which
   dimensions the user actually weights higher, and build trade language
   from that (e.g. "flexible on start date for a larger signing bonus")
   rather than sequential single-issue haggling.
2. **The specific counter number**, grounded in `comp_target.md`'s
   target/ask range and the Offer Breakdown's numbers (including
   `option_value.py`'s equity valuation, not the company's face-value
   figure) — never invent a number the user hasn't grounded in one of
   those two sources or their own stated conversation.
3. **Deadline/pressure handling**, if the offer carries a short fuse —
   per `research.md`'s Deadline and Pressure Tactics findings: name an
   artificially short deadline as a pressure tactic, and coach a firm,
   calm response (asking for a brief, specific extension and stating
   why) rather than rushing a concession. Where relevant, it's fair to
   note that exploding offers carry a documented downside for the
   employer too (a reciprocation effect after acceptance) — but never
   cite a specific turnover-rate or retention statistic for exploding
   offers, since `research.md` found no rigorously sourced field figure
   for that claim.
4. **If the user raises a concern about being judged for negotiating
   assertively** — per `research.md`'s Gender and Framing Effects
   findings: take the concern seriously, it has real experimental
   grounding. Framing the ask with a stated, market-data-backed rationale
   is consistent with what that research suggests reduces backlash risk
   — but never assert that gender predicts how someone should negotiate
   as a general rule.
5. **Where the floor is** — state the walk-away minimum from
   `comp_target.md` explicitly in the plan, and what the user does if
   the company's best-and-final lands under it. If no walk-away number
   exists (e.g. `comp_target.md` doesn't exist yet), say so rather than
   implying one.

### Output

Write the counter-negotiation script to the resolved opportunity's
`notes.md` under a `## Counter-Negotiation Plan (<date>)` heading: the
specific ask, the package trade-offs, and how to handle any pressure
tactics present in the offer.

## Final Accept/Decline

Hands this opportunity's actual accept/decline decision off to
`career-coach` rather than running its own decision session —
`career-coach`'s Evaluation Template already scores "Compensation &
upside" as one of its Opportunity Fit dimensions, and its Session Start
Protocol already reads this opportunity's `notes.md`. This moment's only job is to
make sure that file has real comp facts for `career-coach` to read.

This moment needs no `research.md` content — per design spec §6.4, it is
a hand-off, not its own research session.

### Session Start

Confirm which opportunity this is for, then resolve its folder via
`python3 tools/tracker.py opportunity-path "<Company>" "<Role>"` — never
construct the path yourself.

### What to Do

1. Check the resolved opportunity's `notes.md` for a clear, sourced comp
   summary — an `## Offer Breakdown (<date>)` section and, ideally, a
   `## Counter-Negotiation Plan (<date>)` section. If either is missing,
   say so plainly and offer to run it first — but don't block if the user
   wants to proceed with what's already there.
2. Explicitly invoke `career-coach` for this opportunity's full decision
   session — same in-session hand-off pattern `bootstrap` uses for
   `build-profile`/`define-trajectory`.

### Output

None directly from this moment — the hand-off to `career-coach` produces
the actual decision-session output, using the comp summary this moment
confirmed is in `notes.md`.

## Guardrails

- Never invent a BATNA, a competing offer, or a timeline the user hasn't
  stated. An invented alternative is worse than none — acting on false
  leverage can blow up a real negotiation.
- Don't silently overwrite in revisit mode — confirm changes before
  writing.
- Never assert a target/ask number in First-Contact Prep that isn't
  grounded in `comp_target.md` or the user's own conversation — this
  moment coaches how to use a number, it doesn't invent one.
- Never invent offer numbers, market benchmarks, or valuation figures in
  Offer Breakdown that the user, a cited source, or `option_value.py`
  itself didn't produce.
- Never invent a counter number or trade-off in Counter-Negotiation
  Planning that the user hasn't grounded in `comp_target.md`, the Offer
  Breakdown, or their own stated conversation.
- Never assert that gender predicts how someone should negotiate, and
  never cite an unsourced statistic (e.g. a specific turnover rate) for
  exploding-offer consequences — per `research.md`'s explicit cautions on
  both.
- Never render an accept/decline recommendation directly in Final
  Accept/Decline — that's `career-coach`'s job. This moment only confirms
  the comp facts it needs are in `notes.md` and hands off.
```

- [ ] **Step 2: Verify against the checklist above**

Read the file back and confirm the three points in this task's Verify section.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/offer-negotiator/SKILL.md
git commit -m "Add offer-negotiator Setup Mode Resume for incomplete comp_target.md"
```
