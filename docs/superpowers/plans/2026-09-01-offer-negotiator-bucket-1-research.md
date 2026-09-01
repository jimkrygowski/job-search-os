# Offer Negotiator — Bucket 1: Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `offer-negotiator/research.md` — an evidence-graded review of salary-negotiation tactics and the equity/comp mechanics `option_value.py` needs — so every later bucket (the tool, the skill's tactical advice) is grounded in cited, dated sources rather than invented facts.

**Architecture:** A single research document, same shape as `career-coach/research.md`: one subsection per topic, each with Source, Evidence quality, Known limitations, and How to use correctly. No code in this bucket.

**Tech Stack:** `WebSearch`/`WebFetch` for research. Markdown output only.

**Spec:** `docs/superpowers/specs/2026-09-01-offer-negotiator-design.md`

## Global Constraints

- No claim goes into `research.md` without a source and, where the source has one, a date (spec §8, Guardrail #2).
- Never invent or paraphrase a claim beyond what its source actually supports (spec §8, Guardrail #1). If a topic has no credible source after a genuine search, say so explicitly in the document rather than omitting the gap silently — future buckets need to know where the evidence is thin.
- No personal tax modeling — the ISO/AMT subsection explains the *mechanism* and *why it's flagged not modeled*, it does not compute anything (spec §2 Non-Goals).
- No claim about a specific company's future prospects — only general base rates/mechanics (spec's whole equity-valuation approach is defaults-by-stage, never company-specific prediction).

## A Note on Task Structure for This Bucket

This bucket is research, not code — there's no test-first cycle. Each task below instead specifies the exact sub-topics to research, the exact search queries to start from, and the exact structural template each subsection must follow (matching `career-coach/research.md`'s existing format). "Done" for a step means the subsection exists with a real source and date, not a placeholder. If a query surfaces no credible source, the step is still done once that gap is written into the document honestly — inventing a citation to fill the template is a spec violation, not a shortcut.

Subsection template (copy for every topic below):

```markdown
### <Topic Name>

**Source:** <author/org, publication, year>

**Evidence quality: <High / Moderate / Low / Anecdotal / Minimal>.** <1-3 sentences on why, citing methodology if known.>

**Known limitations:** <bullets>

**How to use correctly:** <1-3 sentences — how offer-negotiator should apply this>
```

---

### Task 1: Negotiation Tactics Research

**Files:**
- Create: `.claude/skills/offer-negotiator/research.md` (this task writes the file with a header + the "Negotiation Tactics" section only; Task 2 appends to the same file)

**Interfaces:**
- Consumes: nothing (first task in the bucket)
- Produces: `.claude/skills/offer-negotiator/research.md` containing a `## Negotiation Tactics` section with the six subsections below — later buckets (the SKILL.md moments 1 and 3) cite this file's subsection headings directly, so keep the headings exactly as named here.

- [ ] **Step 1: Create the file with header and section scaffold**

```markdown
# Offer Negotiator Skill — Research Basis

This document records the evidence base for every tactic and comp-mechanics
claim the offer-negotiator skill relies on, what was evaluated, and why each
choice was made. It exists so the skill's advice is grounded in evidence,
not accumulated assumption — same purpose as `career-coach/research.md`.

**Research conducted:** <fill in today's actual date when this step runs>
**Scope:** Salary/offer negotiation tactics; equity and comp mechanics for a
U.S. tech job search.

---

## Negotiation Tactics

<!-- subsections added in this task -->
```

- [ ] **Step 2: Research and write "Anchoring & First Offers"**

Search queries to start from: `"anchoring effect" negotiation first offer research`, `Galinsky Mussweiler anchoring negotiation`.

Write a subsection (using the template above) answering: does making the first offer in a negotiation help or hurt the person who makes it, and under what conditions? This directly informs moment #1 (first-contact prep) — whether the user should give a number first or deflect.

- [ ] **Step 3: Research and write "BATNA (Best Alternative to a Negotiated Agreement)"**

Search queries: `Fisher Ury Getting to Yes BATNA`, `Harvard Negotiation Project BATNA salary negotiation`.

Write the subsection. This is the foundational "know your walk-away power" concept that ties directly to `comp_target.md` (Bucket 3) — note that connection explicitly in the "How to use correctly" field.

- [ ] **Step 4: Research and write "Deflecting Salary History / Expectation Questions"**

Search queries: `salary history ban states list`, `salary expectation question negotiation response research`.

Write the subsection. Note: many U.S. states/cities have banned employers from asking salary *history* (this is legislative fact, cite the actual law/tracker, dated) — distinguish this from salary *expectation* questions, which remain legal almost everywhere and need a tactical (not legal) answer.

- [ ] **Step 5: Research and write "Integrative (Multi-Issue) Negotiation"**

Search queries: `integrative negotiation multi-issue log-rolling research`, `Malhotra Bazerman Negotiation Genius package negotiation`.

Write the subsection. This underpins the "package literacy — trading between dimensions" goal from the spec's Purpose section — connect explicitly.

- [ ] **Step 6: Research and write "Gender and Framing Effects in Salary Negotiation"**

Search queries: `Babcock Laschever Women Don't Ask negotiation research`, `gender salary negotiation backlash research`.

Write the subsection with real care on evidence caveats — this is a contested area of research (some findings on negotiation "backlash" have had replication issues). Follow `career-coach/research.md`'s honest-about-weak-evidence pattern rather than overclaiming.

- [ ] **Step 7: Research and write "Deadline and Pressure Tactics"**

Search queries: `exploding offer negotiation tactic research`, `time pressure concession negotiation research`.

Write the subsection covering how to recognize and respond to "this offer expires in 24 hours"-style pressure — directly feeds moment #3 (counter-negotiation planning).

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/offer-negotiator/research.md
git commit -m "Add negotiation tactics research to offer-negotiator research.md"
```

---

### Task 2: Equity & Comp Mechanics Research

**Files:**
- Modify: `.claude/skills/offer-negotiator/research.md` (append `## Equity & Comp Mechanics` section)

**Interfaces:**
- Consumes: the file created in Task 1 (appends to it, doesn't recreate it)
- Produces: a `## Equity & Comp Mechanics` section with five subsections whose headings later feed `option_value.py`'s default constants (Bucket 2) and the "flagged, not modeled" tax disclaimer text (spec §7) — keep headings exactly as named here so Bucket 2 can cite them.

- [ ] **Step 1: Add section heading**

Append to `research.md`:

```markdown
---

## Equity & Comp Mechanics

<!-- subsections added in this task -->
```

- [ ] **Step 2: Research and write "Startup Exit-Rate Base Rates by Stage"**

Search queries: `Correlation Ventures venture capital returns study`, `CB Insights startup failure rate statistics`, `Carta state of private markets exit data`, `NVCA venture outcomes data`.

Write the subsection with actual cited figures (or ranges) for how often venture-backed companies at different stages (early-stage private, late-stage private, public) produce any payout to common stockholders. This is the direct source for `option_value.py`'s exit-probability-haircut defaults (spec §7, step 3) — be explicit in "How to use correctly" that these become that tool's default constants, and be explicit about how stale-dated or thin the data is if that's the case, per the Global Constraint above.

- [ ] **Step 3: Research and write "Liquidation Preferences & the Preference Stack"**

Search queries: `liquidation preference explained venture capital`, `Holloway Guide to Equity Compensation liquidation preference`, `NVCA model term sheet liquidation preference`.

Write the subsection explaining how preferred stock's liquidation preference subordinates common stock in an exit, and what typical preference terms (1x non-participating vs. participating, stacking across rounds) look like. This is the direct source for `option_value.py`'s preference-stack haircut default (spec §7, step 2).

- [ ] **Step 4: Research and write "409A Valuation vs. Preferred Price Gap"**

Search queries: `409A valuation common stock vs preferred price gap`, `why is 409A valuation lower than preferred price`.

Write the subsection explaining why the IRS-required 409A valuation (used to set strike price) is deliberately lower than what preferred investors pay, and by roughly how much in practice if any source quantifies it. This grounds the "notional value is measured against the wrong price" explanation from the design conversation (spec §7 step 1/2).

- [ ] **Step 5: Research and write "Discount for Lack of Marketability (DLOM)"**

Search queries: `discount for lack of marketability DLOM startup equity`, `Damodaran illiquidity discount private company valuation`.

Write the subsection on the standard finance/valuation concept for discounting illiquid equity, and typical cited ranges. This grounds `option_value.py`'s time-value/illiquidity discount default (spec §7, step 4).

- [ ] **Step 6: Research and write "ISO vs. NSO Tax Treatment and AMT (flagged, not modeled)"**

Search queries: `ISO vs NSO tax treatment difference`, `AMT incentive stock options exercise risk`.

Write the subsection explaining the mechanism (why exercising ISOs can trigger AMT liability on paper gains before any liquidity event, and how NSOs differ) clearly enough that the skill can explain it accurately to a user — but explicitly note in "How to use correctly" that this is explanatory only; per spec §2/§7, `option_value.py` does not compute personal tax exposure.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/offer-negotiator/research.md
git commit -m "Add equity and comp mechanics research to offer-negotiator research.md"
```

---

### Task 3: Self-Review & Finalize

**Files:**
- Modify: `.claude/skills/offer-negotiator/research.md` (fixes only, from the review below)

**Interfaces:**
- Consumes: the completed file from Tasks 1-2
- Produces: a finalized `research.md` that Buckets 2, 4, and 5 can cite without further changes

- [ ] **Step 1: Citation completeness pass**

Read through every subsection. For each one, confirm it has a non-empty **Source**, an **Evidence quality** rating, and that any factual claim in the prose (not just the Source line) traces back to that source or is explicitly labeled as this document's own inference. Fix any subsection that fails this check — either strengthen the citation or rewrite the claim as a labeled inference.

- [ ] **Step 2: Cross-check against the spec's open items**

Re-read spec §10 ("Open Items for Implementation Buckets"). Confirm `research.md` now contains: (a) the full evidence review of negotiation tactics, and (b) cited figures (or an honest "no good data exists" statement) for exit-probability and preference-stack defaults. If either is thin, note it plainly in the document rather than silently shipping a gap — Bucket 2 needs to know if it's building on a weak citation.

- [ ] **Step 3: Verify headings match what later buckets expect**

Confirm the document has exactly these top-level subsection headings under `## Negotiation Tactics`: Anchoring & First Offers, BATNA (Best Alternative to a Negotiated Agreement), Deflecting Salary History / Expectation Questions, Integrative (Multi-Issue) Negotiation, Gender and Framing Effects in Salary Negotiation, Deadline and Pressure Tactics. And under `## Equity & Comp Mechanics`: Startup Exit-Rate Base Rates by Stage, Liquidation Preferences & the Preference Stack, 409A Valuation vs. Preferred Price Gap, Discount for Lack of Marketability (DLOM), ISO vs. NSO Tax Treatment and AMT (flagged, not modeled). Fix any heading drift now — Bucket 2 will cite these by name.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/offer-negotiator/research.md
git commit -m "Self-review and finalize offer-negotiator research.md"
```

---

## Self-Review Notes (plan author)

- **Spec coverage:** §10's two research open items (negotiation tactics review, cited equity-valuation defaults) are both covered — Task 1 and Task 2 respectively. §8 guardrails are enforced via the Global Constraints and the per-step sourcing requirement. `research.md`'s existence itself satisfies spec §3's file-structure line for this file.
- **Placeholder scan:** No TBD/fill-in-later left in the actual template content — the template fields (Source, Evidence quality, etc.) are structural, not placeholders, and every step names the specific queries and specific claim to research, matching this bucket's adapted "no placeholders" bar (see note above the tasks).
- **Type/heading consistency:** Task 3 Step 3 explicitly locks the heading list so Buckets 2/4/5 have a stable citation target.
