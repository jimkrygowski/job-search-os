# Offer Negotiator — Design

Status: approved by Jim. Bucket 1 (research) complete. Buckets 2-5 not
yet started — see §10 for open items each remaining bucket must resolve.

## 1. Purpose

Make the user a confident, literate negotiator across the full arc of
compensation conversations in a job search — not a single "counter with $X"
calculator. Two goals, in the user's own words:

- **Tactical empowerment** — the right words for the first comp
  conversation, a real plan for a counter-negotiation, the confidence to
  ask the right questions and take the right stance.
- **Package literacy** — understanding what base, variable, and equity
  actually represent, and how to trade between them, since most engineers
  undervalue how little most option grants are really worth and most
  hiring managers are trained to oversell that value.

## 2. Non-Goals

- **Not a single-number calculator.** The skill doesn't try to tell the
  user "the" right counter number — it grounds them in real data and
  tactics so they can reason to one.
- **Not a duplicate of `career-coach`.** The final accept/decline call is
  explicitly `career-coach`'s job (see §6.4) — `offer-negotiator` feeds it
  grounded comp facts, it doesn't re-decide fit.
- **No live market-data scraping.** No dependency on an unofficial
  levels.fyi API or scraper. Comp benchmarks are best-effort, cited,
  dated research — same rigor `company-research` already applies to
  company facts — not a guaranteed live feed.
- **No personal tax modeling in v1.** Equity valuation stays pre-tax, with
  an explicit disclaimer to consult a tax advisor for ISO/AMT exposure.
  Collecting and reasoning about personal income/state tax data is out of
  scope.

## 3. Architecture

One new skill, one new tool, one new standing state artifact — consistent
with the existing engine/data split (`CLAUDE.md`, README "Built like
software, not a prompt"):

- `.claude/skills/offer-negotiator/SKILL.md` — single, mode-aware skill
  (same pattern as `score-opportunity`), covering all four negotiation
  moments (§6). Rejected splitting into one skill per moment (fragments
  state — moment #2's equity breakdown feeds moment #3's counter
  strategy directly) and rejected a separate "comp philosophy setup"
  skill (unlike `build-profile`/`define-trajectory`, comp-philosophy
  setup is small and only ever feeds this one skill).
- `.claude/skills/offer-negotiator/research.md` — evidence-graded review
  of salary-negotiation tactics and equity/comp mechanics, same pattern
  as `career-coach/research.md`.
- `tools/option_value.py` + `tools/test_option_value.py` — deterministic
  equity valuation calculator, same shape as `tools/score_table.py`
  (stdlib only, argparse subcommands, tested). See §7.
- `state/career/comp_target.md` — new standing artifact: walk-away
  minimums, cash/equity/benefits priority, equity risk tolerance,
  deal-breakers. Analogous to `trajectory.md`. Exact fields are decided
  when that bucket is built, not in this doc.

## 4. Bootstrap Integration

`comp_target.md` setup becomes an explicit step in `bootstrap`, not a lazy
first-use prompt:

- `bootstrap/SKILL.md` gets a new step 5 (after `define-trajectory`,
  before wrap-up): invoke `offer-negotiator` in its setup mode to build
  `comp_target.md`.
- `bootstrap`'s "check existing state" step gains a third condition:
  profile + trajectory exist but `comp_target.md` doesn't → go straight
  to the setup-mode call instead of restarting the full flow.

## 5. Retroactive Upgrade Path (existing installs)

This repo is public; users who already ran `bootstrap` before this
feature existed have `profile.md`/`trajectory.md` but no `comp_target.md`.
They need a way to discover the new capability without a hard gate:

- `tools/check_bootstrap_state.py` gains a second condition alongside the
  existing new-user check: if `profile.md` and `trajectory.md` both exist
  but `comp_target.md` doesn't, inject a **soft, non-blocking** note —
  distinct in urgency from the new-user hard gate. Wording conveys "you're
  missing a capability," not "you must comply": e.g. *"comp_target.md
  doesn't exist yet — offer-negotiator (comp coaching/benchmarking) won't
  be able to ground its advice in your actual walk-away numbers until
  it's set up. Mention this and offer to set it up, but address whatever
  the user asked first."*
- No new "already told them" state needed — the note stops firing
  naturally once `comp_target.md` exists, same mechanism as the existing
  new-user check.
- `CLAUDE.md` gets a short paragraph documenting this behavior, parallel
  to the existing paragraph documenting the new-user hook.

## 6. The Four Moments

All four live in one `SKILL.md`, dispatched by context (what the user
says, or an explicit ask if ambiguous). Every market-data claim carries a
source and date — applying `CLAUDE.md` guardrail #2, not a new guardrail.

### 6.1 First-contact prep

No market data required beyond what's knowable from the JD/conversation
(role, level, geo). Output is tactical: how to answer "what are your comp
expectations" without anchoring low, deflection language, when to give a
range vs. decline to answer. Grounded in `research.md` tactics.

### 6.2 Offer breakdown

Offer numbers (base/bonus/equity/benefits) come from the user (pasted
offer letter or verbal recap), saved to that opportunity's `notes.md`.
Market context comes from best-effort cited research (`WebSearch`/
`WebFetch`) — every benchmark sourced and dated, none asserted without a
source. Equity is run through `option_value.py` (§7) rather than valued
at face value.

### 6.3 Counter-negotiation planning

Synthesizes §6.2's breakdown, `comp_target.md`'s walk-away numbers, and
`research.md` tactics into a specific talking-points script for that
opportunity, written to its `notes.md`.

### 6.4 Final accept/decline — hands off to `career-coach`

`career-coach` already scores "Compensation & upside" as one of five
dimensions in its Evaluation Template (`career-coach/SKILL.md`) alongside
role scope, growth trajectory, cultural fit, and problem fit — it's not
comp-only, and it already reads `notes.md` per its existing Session Start
Protocol. So `offer-negotiator` does **not** run its own decision session
at this moment. Instead it:

1. Ensures the opportunity's `notes.md` has a clear, sourced comp summary
   (offer breakdown + `option_value.py` output + fit against
   `comp_target.md`) — already produced by §6.2/§6.3, not new work.
2. Explicitly invokes `career-coach` for that opportunity's full decision
   session — same in-session hand-off pattern `bootstrap` uses for
   `build-profile`/`define-trajectory`.

Zero changes required to `career-coach.md` itself — the integration point
(the "Compensation & upside" row) already exists.

## 7. `option_value.py` — Equity Valuation

Real problem: private-company equity has no market price. A model that
outputs one confident dollar figure is false precision. The tool computes
a **transparent range with separately labeled adjustments**, not a single
blended discount — each one visible and overridable so the tool teaches,
not just outputs a number:

1. **Face value** — shares × (quoted price − strike), as naively presented
   by the company.
2. **Preference-stack / common-vs-preferred haircut** — the quoted "last
   round" price is what *preferred* investors paid; common stock (what
   options convert to) sits behind the liquidation preference stack and
   is worth less, sometimes zero in a modest exit. **Revised per
   `research.md`'s finding (no credible generic "% of valuation" figure
   exists): this is a required input with an explicit unconfirmed-
   placeholder state, not a silently-applied default.** The tool computes
   a real residual-claim value when the user supplies the company's total
   preference stack and fully-diluted share count; when either is
   missing, it outputs an explicit "UNCONFIRMED — placeholder, not a real
   estimate" state rather than a quiet default number, plus concrete
   guidance on what to ask the company for (total preferred capital
   raised across all rounds, preference terms, fully-diluted share count)
   so the user can go get the real figure.
3. **Exit-probability haircut** — most venture-backed companies never
   return value to common stockholders. **Revised to two tiers, not
   three:** public companies get no exit-probability haircut (a real
   market price exists, the question is moot); private companies get one
   flat, disclosed default rate (cited in `research.md`), user-overridable
   per call. `research.md` found no source that credibly differentiates
   early-stage from late-stage private — inventing that split would
   assert a number no source supports, so it's collapsed to public vs.
   private rather than the three-way stage split originally proposed
   here.
4. **Time-value discount** — illiquid startup equity warrants a higher
   discount rate than public-market investments, given undiversifiable,
   concentrated risk and multi-year uncertain time-to-liquidity. Public
   companies get no discount (liquid). **For private companies, two
   modes:** when the user supplies a time-to-liquidity estimate and a
   volatility assumption, the discount is computed dynamically by
   interpolating the Longstaff (1995) option-pricing grid `research.md`
   already cites (concrete points at 1/2/5-year holding periods and
   20%/30% volatility) — clamped to that cited range, never extrapolated
   beyond it. When those inputs aren't supplied, it falls back to the
   flat default range cited in `research.md`. Either way, user-overridable.
   This dynamic mode was added 2026-09-02 after independently
   re-verifying (fresh research, prompted by two external AI chats
   proposing unsourced stage-differentiated tables) that no credible
   source supports stage-tiered exit-probability or DLOM constants — but
   that the already-cited Longstaff grid supported a real, grounded
   dynamic calculation the original flat-band design was leaving on the
   table.

Also flagged, not modeled: exercise cost and tax timing (ISO/AMT exposure
can trigger real cash tax liability on paper gains before any liquidity
event) — surfaced as a disclaimer, not computed, per §2.

Output shows every stage of the adjustment and why, then compares the
risk-adjusted range against the cash-now alternative — cash is certain,
liquid, and immediately realized; equity is a subordinated, time-delayed,
probability-weighted claim contingent on vesting, an exit occurring, and
that exit clearing the preference stack with room left for common.

Mirrors `score_table.py`: stdlib only, argparse subcommands, called by the
skill rather than freehand-computed by the LLM — this is real financial
math, not something that should be non-deterministic session to session.

Per §10's context-efficiency item: every default constant's docstring
cites the specific `research.md` subsection it comes from, so the tool is
self-documenting and `SKILL.md` (Bucket 4) can call it and relay its
output without re-reading `research.md`'s Equity & Comp Mechanics prose
at runtime.

## 8. Guardrails

No new guardrails. Existing `CLAUDE.md` guardrails apply directly:

- #1 (never invent experience) → never invent comp facts; offer numbers
  come only from what the user provides.
- #2 (never assert unsupported opinion) → every market benchmark and
  equity-valuation default carries a source/rationale and, where
  applicable, a date.

## 9. Testing & Validation

- `option_value.py` gets a stdlib `unittest` suite
  (`test_option_value.py`) covering the adjustment math and edge cases:
  zero/negative strike spread (underwater options), public-company case
  (no preference-stack or exit-probability haircut applies), and
  user-overridden defaults.
- The skill itself (prose/conversation across the four moments) is not
  unit-tested, consistent with `interview-prep`/`company-research` today.

## 10. Open Items for Implementation Buckets

Deliberately left for the bucket that builds them, not resolved here:

- Exact field list and conversation shape for `comp_target.md` setup
  (Bucket 3).
- ~~Specific cited exit-probability and preference-stack default
  figures~~ — done in Bucket 1: `research.md` now has the sourced
  figures and flags an explicit, unresolved conflict between the
  evidence and this spec's §7 steps 2/3 (see `research.md`'s
  "Conflict with the design spec" notes under Exit-Rate Base Rates and
  Liquidation Preferences). **Bucket 2 must resolve that conflict**
  before finalizing `option_value.py`'s defaults — either find/accept a
  stage-differentiated source, or revise §7 to a flat/placeholder
  default as `research.md` recommends.
- ~~`research.md`'s full evidence review of negotiation tactics~~ — done
  in Bucket 1 (`.claude/skills/offer-negotiator/research.md` +
  `research-source.md` for full citations).
- **Context-efficiency: build-time vs. runtime content (Bucket 2).**
  `research.md`'s Equity & Comp Mechanics half (~458 lines) exists
  mainly to inform `option_value.py`'s hardcoded defaults, not to be
  re-read by the live skill every session. When designing Bucket 2,
  decide explicitly whether that reasoning gets baked into the tool
  (e.g. as docstrings/comments citing back to `research.md`) so
  `SKILL.md` can call the tool and relay its output without re-reading
  the full DLOM/exit-rate/preference-stack prose at runtime. Don't
  leave this implicit — it's the single biggest lever on how much of
  `research.md` the live agent's context carries per session.
- **Selective per-moment loading + a moment index (Bucket 4).**
  `SKILL.md` (moments 1 & 2, and by extension moment 3 in Bucket 5)
  must not read all of `research.md` for every moment — e.g. moment 1
  (first-contact prep) only needs Anchoring/BATNA/Deflecting, not
  Gender-Framing or any Equity & Comp Mechanics content. Add a short
  index/table near the top of `research.md` mapping each of the four
  moments to the specific subsections it needs, and write `SKILL.md` to
  load only those subsections per moment rather than the whole file.
