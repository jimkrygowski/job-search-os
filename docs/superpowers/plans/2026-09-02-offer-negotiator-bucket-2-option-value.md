# Offer Negotiator — Bucket 2: `option_value.py` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tools/option_value.py`, a deterministic equity valuation calculator that computes a transparent, staged breakdown (face value → preference-stack-adjusted → exit-probability range → time-value/DLOM range) rather than a single confident number, so `offer-negotiator`'s later buckets can call it instead of freehand-computing real financial math.

**Architecture:** Four pure computation functions, one per adjustment stage, composed by an orchestration function and exposed via a single `compute` CLI subcommand that reads JSON on stdin and prints a JSON breakdown on stdout — same shape as `tools/score_table.py` (stdlib only, argparse, tested with a CLI subprocess test class).

**Tech Stack:** Python 3 stdlib only (`argparse`, `json`, `sys`, `unittest`, `subprocess` in tests). No pip dependencies.

**Spec:** `docs/superpowers/specs/2026-09-01-offer-negotiator-design.md` (§7, as revised for Bucket 2's three confirmed decisions)

## Global Constraints

- Public-company inputs pass through **every** adjustment stage unchanged (no preference-stack, exit-probability, or DLOM adjustment applies — a real market price already exists) (spec §7 steps 2-4, §9).
- The preference-stack adjustment is a **required input with an explicit unconfirmed-placeholder state, never a silently-applied default**: when `preference_stack` or `fully_diluted_shares` is missing, output `"applied": false` plus concrete guidance on what to ask the company for — do not fall back to any generic percentage (spec §7 step 2, revised).
- The exit-probability haircut has **real per-stage tiers**: `public` (no haircut), five specific private-stage tiers (`seed`, `series_a`, `series_b`, `series_c`, `series_d_plus`, each with its own sourced failure-rate range/point from `research.md#exit-rate-base-rates`), and a generic `private` fallback (the old flat aggregate) for when the specific stage isn't known. `series_b` (0.72) and `series_c` (0.82) are each derived from Carta's "Class of 2018" cohort cascade; `series_d_plus` (0.82) is not independently sourced — it holds flat at the `series_c` rate because no transition data exists past that point (spec §7 step 3, revised 2026-09-02).
- Default constants: exit-probability failure rates per stage — seed 0.52–0.69, series_a 0.37–0.85, series_b 0.72 (point), series_c 0.82 (point), series_d_plus 0.82 (point, held flat at series_c — no data past that transition), generic private fallback 0.60–0.75 (all sourced in `research.md#exit-rate-base-rates`; series_b/c/d_plus reflect an explicit 2026-09-02 decision to use more recent, more pessimistic Carta-derived figures over an older, more optimistic Mattermark-derived pattern — see `research.md`'s "Methodology decision" note). DLOM has two modes: a **dynamic mode** interpolating the Longstaff (1995) grid already cited in `research.md#dlom` (20% vol: 1yr=0.17, 2yr=0.25, 5yr=0.41; 30% vol: 1yr=0.26, 2yr=0.39, 5yr=0.66) when time-to-liquidity and volatility are supplied, clamped (never extrapolated) to that cited range; and a **flat 0.20–0.30 fallback band** (source: `research.md#dlom`) when they're not. Every default constant's docstring/comment must cite its `research.md` anchor.
- This tier structure went through four rounds of revision within this plan's own history: (1) originally spec'd as three stage tiers with no real data; (2) collapsed to flat public/private after Bucket 1's research found no supporting source; (3) restored to five real private-stage tiers after the user correctly objected that treating a Series A and a Series D company identically was indefensible, using Mattermark/Rowley's "halving" pattern for series_b/c/d_plus; (4) same day, series_b/c/d_plus revised again after a fourth source (Carta's "Class of 2018" cohort) surfaced real, more pessimistic, more recent per-transition data — the user explicitly directed using the more conservative and more recent figures rather than averaging the two. See `research.md#exit-rate-base-rates` for the full sourcing, the derivation arithmetic, and the specific fabricated/unattributed sources that were checked and rejected along the way.
- No personal tax modeling anywhere in this tool — ISO/AMT is out of scope entirely for `option_value.py`, not even as an optional field (spec §2, §7).
- Every function must accept explicit overrides for its defaults; the tool never asserts a single confident number — the final output is always a range with every stage shown (spec §7).
- Follow `tools/score_table.py`'s conventions exactly: stdlib only, `argparse` subcommand(s), JSON on stdin for input, a `unittest` suite with a separate CLI test class that shells out via `subprocess` (see `tools/test_score_table.py`).

---

### Task 1: Face value

**Files:**
- Create: `tools/option_value.py`
- Create: `tools/test_option_value.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: `compute_face_value(shares: int, strike_price: float, quoted_price: float) -> float` — later tasks call this exact signature.

- [ ] **Step 1: Write the failing tests**

Create `tools/test_option_value.py`:

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import option_value  # noqa: E402


class ComputeFaceValueTest(unittest.TestCase):
    def test_basic_spread(self):
        self.assertEqual(
            option_value.compute_face_value(shares=1000, strike_price=2.00, quoted_price=5.00),
            3000.0,
        )

    def test_underwater_options_floor_at_zero(self):
        self.assertEqual(
            option_value.compute_face_value(shares=1000, strike_price=10.00, quoted_price=5.00),
            0.0,
        )

    def test_zero_shares(self):
        self.assertEqual(
            option_value.compute_face_value(shares=0, strike_price=1.00, quoted_price=5.00),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_option_value.py -v` (or `python3 -m unittest tools.test_option_value -v` if pytest isn't available)
Expected: FAIL with `ModuleNotFoundError: No module named 'option_value'` (the file doesn't exist yet).

- [ ] **Step 3: Write the minimal implementation**

Create `tools/option_value.py`:

```python
#!/usr/bin/env python3
"""Deterministic equity valuation calculator for offer-negotiator.

Computes a transparent, staged valuation of stock options -- face value,
then (where data allows) a preference-stack-adjusted common value, then a
private-company exit-probability range, then a time-value/illiquidity
(DLOM) range -- rather than a single confident number. Mirrors
score_table.py: stdlib only, called by the skill rather than freehand-
computed by the LLM, since this is real financial math.

Default constants below cite their source subsection in
.claude/skills/offer-negotiator/research.md so this tool stays
self-documenting -- see design spec section 7 for how the four stages
compose.
"""


def compute_face_value(shares, strike_price, quoted_price):
    """shares x max(0, quoted_price - strike_price) -- naive face value,
    as a company would present it, before any of the adjustments below."""
    return shares * max(0.0, quoted_price - strike_price)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, 3/3 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py face value calculation"
```

---

### Task 2: Preference-stack adjustment

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: nothing new
- Produces: `compute_preference_adjustment(shares, strike_price, quoted_price, preference_stack=None, fully_diluted_shares=None) -> dict` with keys `applied` (bool), `adjusted_value` (float or None), `common_price` (float or None), `guidance` (str or None) — Task 5's orchestration calls this exact signature and reads these exact keys.

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_option_value.py` (before the `if __name__ == "__main__":` line):

```python
class ComputePreferenceAdjustmentTest(unittest.TestCase):
    def test_missing_preference_stack_returns_unapplied_placeholder(self):
        result = option_value.compute_preference_adjustment(
            shares=1000, strike_price=2.00, quoted_price=5.00,
            preference_stack=None, fully_diluted_shares=1_000_000,
        )
        self.assertFalse(result["applied"])
        self.assertIsNone(result["adjusted_value"])
        self.assertIsNone(result["common_price"])
        self.assertIn("cap table", result["guidance"])

    def test_missing_fully_diluted_shares_returns_unapplied_placeholder(self):
        result = option_value.compute_preference_adjustment(
            shares=1000, strike_price=2.00, quoted_price=5.00,
            preference_stack=2_000_000, fully_diluted_shares=None,
        )
        self.assertFalse(result["applied"])
        self.assertIsNone(result["adjusted_value"])

    def test_guidance_text_names_what_to_ask_for(self):
        result = option_value.compute_preference_adjustment(
            shares=1000, strike_price=2.00, quoted_price=5.00,
        )
        guidance = result["guidance"]
        self.assertIn("preferred capital raised", guidance)
        self.assertIn("preference terms", guidance)
        self.assertIn("fully-diluted shares", guidance)

    def test_computed_residual_claim(self):
        # implied company value = 5.00 * 1,000,000 = $5,000,000
        # residual after $2,000,000 preference stack = $3,000,000
        # common_price = $3,000,000 / 1,000,000 shares = $3.00/share
        # adjusted_value = 1000 * (3.00 - 2.00) = 1000.0
        result = option_value.compute_preference_adjustment(
            shares=1000, strike_price=2.00, quoted_price=5.00,
            preference_stack=2_000_000, fully_diluted_shares=1_000_000,
        )
        self.assertTrue(result["applied"])
        self.assertEqual(result["common_price"], 3.00)
        self.assertEqual(result["adjusted_value"], 1000.0)
        self.assertIsNone(result["guidance"])

    def test_preference_stack_exceeding_company_value_floors_common_at_zero(self):
        # implied company value = 5.00 * 1,000,000 = $5,000,000
        # preference stack of $6,000,000 exceeds it -- common is worthless
        result = option_value.compute_preference_adjustment(
            shares=1000, strike_price=2.00, quoted_price=5.00,
            preference_stack=6_000_000, fully_diluted_shares=1_000_000,
        )
        self.assertTrue(result["applied"])
        self.assertEqual(result["common_price"], 0.0)
        self.assertEqual(result["adjusted_value"], 0.0)

    def test_zero_fully_diluted_shares_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_preference_adjustment(
                shares=1000, strike_price=2.00, quoted_price=5.00,
                preference_stack=2_000_000, fully_diluted_shares=0,
            )

    def test_negative_preference_stack_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_preference_adjustment(
                shares=1000, strike_price=2.00, quoted_price=5.00,
                preference_stack=-1, fully_diluted_shares=1_000_000,
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_option_value.py -v -k ComputePreferenceAdjustmentTest`
Expected: FAIL with `AttributeError: module 'option_value' has no attribute 'compute_preference_adjustment'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `tools/option_value.py`:

```python
# Source: research.md#liquidation-preferences ("How to use correctly") --
# no credible generic "typical stack as % of valuation" figure exists;
# the correct input is the specific company's actual preference stack.
# This is a required input with an explicit unconfirmed-placeholder
# state, never a silently-applied default.
PREFERENCE_STACK_GUIDANCE = (
    "To get a real preference-stack estimate, ask the company (or your "
    "recruiter/hiring manager) for:\n"
    "  - Total preferred capital raised across ALL funding rounds, not "
    "just the most recent round\n"
    "  - Whether preference terms are 1x non-participating (current "
    "market standard) or something more (participating preferred, "
    "above-1x multiples)\n"
    "  - Total fully-diluted shares outstanding, including all option "
    "pools, not just your own grant\n"
    "This is typically available from a cap table summary -- many "
    "companies will share high-level totals even without the full cap "
    "table."
)


def compute_preference_adjustment(shares, strike_price, quoted_price,
                                    preference_stack=None,
                                    fully_diluted_shares=None):
    """Residual-claim common value after the preference stack, per
    research.md#liquidation-preferences: common's per-share value is what
    remains of the implied company value (quoted_price x fully diluted
    shares) after the preference stack is paid, floored at 0.

    Returns a dict with 'applied': False and guidance text when either
    input is missing -- this is a required input with an explicit
    unconfirmed-placeholder state, never a silently-applied default.
    """
    if preference_stack is None or fully_diluted_shares is None:
        return {
            "applied": False,
            "adjusted_value": None,
            "common_price": None,
            "guidance": PREFERENCE_STACK_GUIDANCE,
        }
    if fully_diluted_shares <= 0:
        raise ValueError("fully_diluted_shares must be positive")
    if preference_stack < 0:
        raise ValueError("preference_stack cannot be negative")
    common_price = max(0.0, quoted_price - preference_stack / fully_diluted_shares)
    adjusted_value = shares * max(0.0, common_price - strike_price)
    return {
        "applied": True,
        "adjusted_value": adjusted_value,
        "common_price": common_price,
        "guidance": None,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, all tests (Task 1's 3 + Task 2's 7).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py preference-stack residual-claim adjustment"
```

---

### Task 3: Exit-probability range — real per-stage tiers

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: nothing new
- Produces: `compute_exit_probability_range(value, company_stage, override_low=None, override_high=None) -> dict` with keys `low`, `high`, `failure_rate_low`, `failure_rate_high`. `company_stage` accepts `"public"`, a specific private-stage tier (`"seed"`, `"series_a"`, `"series_b"`, `"series_c"`, `"series_d_plus"`), or `"private"` as a generic fallback for when the specific stage isn't known. Also produces shared helpers `_validate_stage(company_stage)` and `_validate_rate(rate, name)`, both raising `ValueError` — Task 4 reuses these exact helpers rather than redefining them, and Task 4's existing `"private"`-based tests keep working unchanged since `"private"` remains a valid stage string.

**Note on this task's history:** an earlier version of this plan had a flat two-tier (public/private) design, because Bucket 1's original research found no source differentiating private-stage exit rates. Jim correctly pushed back that treating a Series A and a Series D company identically was indefensible, and further research (documented in `research.md#exit-rate-base-rates`) found real, cross-validated per-stage data. This version replaces the flat design.

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_option_value.py`:

```python
class ComputeExitProbabilityRangeTest(unittest.TestCase):
    def test_public_company_passes_through_unchanged(self):
        result = option_value.compute_exit_probability_range(1000.0, "public")
        self.assertEqual(result, {
            "low": 1000.0, "high": 1000.0,
            "failure_rate_low": 0.0, "failure_rate_high": 0.0,
        })

    def test_seed_default_range(self):
        # failure rate range 0.52-0.69 (CB Insights to Mattermark)
        result = option_value.compute_exit_probability_range(1000.0, "seed")
        self.assertEqual(result["low"], 310.0)
        self.assertEqual(result["high"], 480.0)
        self.assertEqual(result["failure_rate_low"], 0.52)
        self.assertEqual(result["failure_rate_high"], 0.69)

    def test_series_a_default_range(self):
        # failure rate range 0.37-0.85 (CB Insights to Carta worst vintage)
        result = option_value.compute_exit_probability_range(1000.0, "series_a")
        self.assertEqual(result["low"], 150.0)
        self.assertEqual(result["high"], 630.0)
        self.assertEqual(result["failure_rate_low"], 0.37)
        self.assertEqual(result["failure_rate_high"], 0.85)

    def test_series_b_default_range(self):
        # failure rate 0.72 (Carta "Class of 2018" cascade, derived), both
        # ends equal -> a point, not a range
        result = option_value.compute_exit_probability_range(1000.0, "series_b")
        self.assertEqual(result["low"], 280.0)
        self.assertEqual(result["high"], 280.0)
        self.assertEqual(result["failure_rate_low"], 0.72)
        self.assertEqual(result["failure_rate_high"], 0.72)

    def test_series_c_default_range(self):
        # failure rate 0.82 (Carta "Class of 2018" cascade, derived)
        result = option_value.compute_exit_probability_range(1000.0, "series_c")
        self.assertEqual(result["low"], 180.0)
        self.assertEqual(result["high"], 180.0)
        self.assertEqual(result["failure_rate_low"], 0.82)
        self.assertEqual(result["failure_rate_high"], 0.82)

    def test_series_d_plus_default_range_holds_flat_at_series_c_rate(self):
        # no transition data exists past Series D+; holds flat at 0.82
        result = option_value.compute_exit_probability_range(1000.0, "series_d_plus")
        self.assertEqual(result["low"], 180.0)
        self.assertEqual(result["high"], 180.0)
        self.assertEqual(result["failure_rate_low"], 0.82)
        self.assertEqual(result["failure_rate_high"], 0.82)

    def test_generic_private_default_range_when_stage_unknown(self):
        # failure rate range 0.60-0.75 -> survival range 0.25-0.40
        result = option_value.compute_exit_probability_range(1000.0, "private")
        self.assertEqual(result["low"], 250.0)
        self.assertEqual(result["high"], 400.0)
        self.assertEqual(result["failure_rate_low"], 0.60)
        self.assertEqual(result["failure_rate_high"], 0.75)

    def test_stage_override(self):
        result = option_value.compute_exit_probability_range(
            1000.0, "series_a", override_low=0.5, override_high=0.5,
        )
        self.assertEqual(result["low"], 500.0)
        self.assertEqual(result["high"], 500.0)
        self.assertEqual(result["failure_rate_low"], 0.5)
        self.assertEqual(result["failure_rate_high"], 0.5)

    def test_invalid_stage_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_exit_probability_range(1000.0, "acquired")
        self.assertIn("acquired", str(ctx.exception))

    def test_invalid_override_rate_above_one_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_exit_probability_range(
                1000.0, "private", override_low=1.5,
            )

    def test_invalid_override_rate_negative_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_exit_probability_range(
                1000.0, "private", override_high=-0.1,
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_option_value.py -v -k ComputeExitProbabilityRangeTest`
Expected: FAIL with `AttributeError: module 'option_value' has no attribute 'compute_exit_probability_range'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `tools/option_value.py`:

```python
VALID_STAGES = ("public", "private", "seed", "series_a", "series_b", "series_c", "series_d_plus")

# Source: research.md#exit-rate-base-rates -- CB Insights, "The Venture
# Capital Funnel" (2018, cohort of 1,119 US tech companies seed-funded
# 2008-2010): 48% graduate Seed->A (52% fail). Mattermark/Rowley (2016,
# independent cohort of 2,011 US software companies seed-funded
# 2009-2012): 31% graduate Seed->A (69% fail). Range reflects both real,
# independent data points.
SEED_FAILURE_RATE_LOW = 0.52
SEED_FAILURE_RATE_HIGH = 0.69

# Source: research.md#exit-rate-base-rates -- CB Insights: 63% graduate
# A->B (37% fail), eventual outcome, 2008-2010 vintage. Carta (Peter
# Walker, 2026, cohort of 10,562 US startups raising Series A 2018-2025):
# graduation swings as low as ~10-12% (2022 vintage, 2-year window) -- a
# shorter observation window than CB Insights', so likely somewhat
# overstates eventual failure; the high end here is conservatively
# rounded down from that raw figure for that reason.
SERIES_A_FAILURE_RATE_LOW = 0.37
SERIES_A_FAILURE_RATE_HIGH = 0.85

# Source: research.md#exit-rate-base-rates -- Carta, "The Startup Class
# of 2018 Where Are They Now" (Peter Walker, Mar 2024, cohort of 3,067 US
# startups incorporated 2018, tracked ~6 years). Derived from the
# published furthest-stage-reached cascade (cumulative reach: Seed 62.9%,
# A 38.9%, B 13.9%, C 3.9%, D+ 0.7%) as B->C conditional failure. Chosen
# over Mattermark/Rowley's older (2009-2012 cohort), more optimistic ~50%
# "halving pattern" estimate for this transition -- an explicit,
# documented choice to prefer the more recent, more pessimistic figure
# (see research.md's "Methodology decision" note), not an averaging of
# the two.
SERIES_B_FAILURE_RATE = 0.72

# Source: research.md#exit-rate-base-rates -- same Carta cohort and
# reasoning as SERIES_B_FAILURE_RATE above, derived as the C->D
# conditional failure rate from the same published cascade.
SERIES_C_FAILURE_RATE = 0.82

# Source: research.md#exit-rate-base-rates -- no transition data exists
# past this cohort's Series D+ bucket (0.7% cumulative reach, no further
# breakdown). Held flat at SERIES_C_FAILURE_RATE as the most recent, most
# pessimistic available anchor, not an independently measured figure for
# this specific transition.
SERIES_D_PLUS_FAILURE_RATE = SERIES_C_FAILURE_RATE

# Source: research.md#exit-rate-base-rates -- Correlation Ventures data
# via Booth (2013)/Levine (2014), cross-referenced against CB Insights'
# aggregate post-mortem tracking: roughly 60-75% of VC-backed positions,
# across all stages combined, return nothing or less than invested
# capital to preferred. This is the fallback for when the specific
# funding stage isn't known -- prefer a specific stage tier when it is.
GENERIC_PRIVATE_FAILURE_RATE_LOW = 0.60
GENERIC_PRIVATE_FAILURE_RATE_HIGH = 0.75

STAGE_DEFAULT_FAILURE_RATES = {
    "seed": (SEED_FAILURE_RATE_LOW, SEED_FAILURE_RATE_HIGH),
    "series_a": (SERIES_A_FAILURE_RATE_LOW, SERIES_A_FAILURE_RATE_HIGH),
    "series_b": (SERIES_B_FAILURE_RATE, SERIES_B_FAILURE_RATE),
    "series_c": (SERIES_C_FAILURE_RATE, SERIES_C_FAILURE_RATE),
    "series_d_plus": (SERIES_D_PLUS_FAILURE_RATE, SERIES_D_PLUS_FAILURE_RATE),
    "private": (GENERIC_PRIVATE_FAILURE_RATE_LOW, GENERIC_PRIVATE_FAILURE_RATE_HIGH),
}


def _validate_stage(company_stage):
    if company_stage not in VALID_STAGES:
        raise ValueError(f"company_stage must be one of {VALID_STAGES}, got {company_stage!r}")


def _validate_rate(rate, name):
    if not 0 <= rate <= 1:
        raise ValueError(f"{name} must be between 0 and 1, got {rate!r}")


def compute_exit_probability_range(value, company_stage,
                                     override_low=None, override_high=None):
    """Applies the exit-probability haircut as a range. 'public' passes
    through unchanged (a real market price already exists). A specific
    private-stage tier (seed/series_a/series_b/series_c/series_d_plus)
    uses that stage's real, sourced failure-rate range from
    research.md#exit-rate-base-rates. 'private' (unspecified stage) uses
    the generic all-stage aggregate as a fallback. Any tier's default can
    be overridden."""
    _validate_stage(company_stage)
    if company_stage == "public":
        return {"low": value, "high": value,
                "failure_rate_low": 0.0, "failure_rate_high": 0.0}
    default_low, default_high = STAGE_DEFAULT_FAILURE_RATES[company_stage]
    failure_rate_low = default_low if override_low is None else override_low
    failure_rate_high = default_high if override_high is None else override_high
    _validate_rate(failure_rate_low, "override_low")
    _validate_rate(failure_rate_high, "override_high")
    return {
        "low": value * (1 - failure_rate_high),
        "high": value * (1 - failure_rate_low),
        "failure_rate_low": failure_rate_low,
        "failure_rate_high": failure_rate_high,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, all tests (10 prior + Task 3's 11 = 21).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py exit-probability range: real per-stage tiers"
```

---

### Task 4: DLOM (time-value/illiquidity) range — dynamic + flat fallback

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: `_validate_stage` and `_validate_rate` from Task 3 (does not redefine them)
- Produces: `compute_dynamic_dlom(time_to_liquidity_years, volatility) -> float` and `compute_dlom_range(value_low, value_high, company_stage, time_to_liquidity_years=None, volatility=None, override_low=None, override_high=None) -> dict` with keys `low`, `high`, `dlom_low`, `dlom_high`, `method` — Task 5's orchestration calls this exact signature. Precedence when multiple inputs are given: stage=public always wins (no discount) → explicit override wins next → dynamic (time+volatility both given) → flat default band fallback.

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_option_value.py`:

```python
class ComputeDynamicDlomTest(unittest.TestCase):
    def test_exact_grid_point_20_percent_vol_2_years(self):
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=2, volatility=0.20),
            0.25,
        )

    def test_exact_grid_point_30_percent_vol_5_years(self):
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=5, volatility=0.30),
            0.66,
        )

    def test_interpolates_between_volatility_curves(self):
        # T=2 exactly on the grid: 20% vol -> 0.25, 30% vol -> 0.39.
        # volatility=0.25 is halfway -> 0.25 + 0.5*(0.39-0.25) = 0.32
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=2, volatility=0.25),
            0.32,
        )

    def test_interpolates_between_time_points(self):
        # volatility=0.20 exactly on the low curve: T=1 -> 0.17, T=2 -> 0.25.
        # T=1.5 is halfway -> 0.17 + 0.5*(0.25-0.17) = 0.21
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=1.5, volatility=0.20),
            0.21,
        )

    def test_time_above_grid_clamps_to_5_years(self):
        # T=10 clamps to T=5; volatility=0.20 exactly on the low curve -> 0.41
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=10, volatility=0.20),
            0.41,
        )

    def test_volatility_below_grid_clamps_to_20_percent(self):
        # volatility=0.05 clamps to 0.20; T=1 exactly on that curve -> 0.17
        self.assertAlmostEqual(
            option_value.compute_dynamic_dlom(time_to_liquidity_years=1, volatility=0.05),
            0.17,
        )


class ComputeDlomRangeTest(unittest.TestCase):
    def test_public_company_passes_through_unchanged(self):
        result = option_value.compute_dlom_range(250.0, 400.0, "public")
        self.assertEqual(result["low"], 250.0)
        self.assertEqual(result["high"], 400.0)
        self.assertEqual(result["dlom_low"], 0.0)
        self.assertEqual(result["dlom_high"], 0.0)
        self.assertEqual(result["method"], "public-no-discount")

    def test_private_company_flat_default_band_when_no_dynamic_inputs(self):
        # dlom range 0.20-0.30: low end gets the bigger discount (0.30),
        # high end gets the smaller discount (0.20)
        result = option_value.compute_dlom_range(250.0, 400.0, "private")
        self.assertEqual(result["low"], 175.0)
        self.assertEqual(result["high"], 320.0)
        self.assertEqual(result["dlom_low"], 0.20)
        self.assertEqual(result["dlom_high"], 0.30)
        self.assertEqual(result["method"], "flat-default-band")

    def test_private_company_dynamic_mode_when_time_and_volatility_given(self):
        # dlom = compute_dynamic_dlom(2, 0.25) = 0.32 (verified above)
        # final_low = 250 * (1-0.32) = 170.0; final_high = 400 * (1-0.32) = 272.0
        result = option_value.compute_dlom_range(
            250.0, 400.0, "private",
            time_to_liquidity_years=2, volatility=0.25,
        )
        self.assertAlmostEqual(result["low"], 170.0)
        self.assertAlmostEqual(result["high"], 272.0)
        self.assertAlmostEqual(result["dlom_low"], 0.32)
        self.assertAlmostEqual(result["dlom_high"], 0.32)
        self.assertEqual(result["method"], "dynamic-longstaff-interpolation")

    def test_private_company_override_takes_precedence_over_dynamic(self):
        result = option_value.compute_dlom_range(
            250.0, 400.0, "private",
            time_to_liquidity_years=2, volatility=0.25,
            override_low=0.1, override_high=0.1,
        )
        self.assertEqual(result["low"], 225.0)
        self.assertEqual(result["high"], 360.0)
        self.assertEqual(result["method"], "override")

    def test_invalid_stage_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_dlom_range(250.0, 400.0, "acquired")

    def test_invalid_override_rate_raises(self):
        with self.assertRaises(ValueError):
            option_value.compute_dlom_range(
                250.0, 400.0, "private", override_high=2.0,
            )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_option_value.py -v -k "ComputeDynamicDlomTest or ComputeDlomRangeTest"`
Expected: FAIL with `AttributeError: module 'option_value' has no attribute 'compute_dynamic_dlom'` (and the same for `compute_dlom_range`).

- [ ] **Step 3: Write the minimal implementation**

Append to `tools/option_value.py`:

```python
# Source: research.md#dlom -- Longstaff (1995) option-pricing model,
# cited there at these exact (holding period, volatility) points. These
# are the ONLY points research.md verified; compute_dynamic_dlom()
# linearly interpolates between them -- it does not re-derive Longstaff's
# actual closed-form formula, which this tool does not attempt to
# reimplement -- and clamps inputs outside this grid to the nearest
# cited bound rather than extrapolating beyond verified data.
LONGSTAFF_GRID_YEARS = (1, 2, 5)
LONGSTAFF_GRID_VOL_LOW = 0.20
LONGSTAFF_GRID_VOL_HIGH = 0.30
LONGSTAFF_DLOM_AT_VOL_LOW = (0.17, 0.25, 0.41)   # at 20% vol, by year
LONGSTAFF_DLOM_AT_VOL_HIGH = (0.26, 0.39, 0.66)  # at 30% vol, by year

# Source: research.md#dlom ("How to use correctly") -- a 20-30% default
# is a defensible judgment call within a literature that spans roughly
# 7% (Bajaj et al.'s controlled estimate) to 40%+ (pre-IPO / option-
# pricing bounds), not a point of convergence. Used as the fallback band
# when time-to-liquidity and volatility aren't supplied for the dynamic
# calculation above. Applies only to private companies; public stock is
# liquid.
DLOM_LOW = 0.20
DLOM_HIGH = 0.30


def _interpolate_1d(x, xs, ys):
    """Linear interpolation of x against sorted xs/ys, clamped at the
    ends rather than extrapolated."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            weight = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + weight * (ys[i + 1] - ys[i])


def compute_dynamic_dlom(time_to_liquidity_years, volatility):
    """DLOM interpolated from the Longstaff (1995) grid cited in
    research.md#dlom. Clamps time and volatility to the cited range
    (1-5 years, 20-30% volatility) rather than extrapolating beyond
    verified data points."""
    dlom_at_vol_low = _interpolate_1d(
        time_to_liquidity_years, LONGSTAFF_GRID_YEARS, LONGSTAFF_DLOM_AT_VOL_LOW)
    dlom_at_vol_high = _interpolate_1d(
        time_to_liquidity_years, LONGSTAFF_GRID_YEARS, LONGSTAFF_DLOM_AT_VOL_HIGH)
    clamped_vol = min(max(volatility, LONGSTAFF_GRID_VOL_LOW), LONGSTAFF_GRID_VOL_HIGH)
    weight = (clamped_vol - LONGSTAFF_GRID_VOL_LOW) / (LONGSTAFF_GRID_VOL_HIGH - LONGSTAFF_GRID_VOL_LOW)
    return dlom_at_vol_low + weight * (dlom_at_vol_high - dlom_at_vol_low)


def compute_dlom_range(value_low, value_high, company_stage,
                         time_to_liquidity_years=None, volatility=None,
                         override_low=None, override_high=None):
    """Applies the time-value/illiquidity (DLOM) discount as a range.
    Precedence: public companies pass through unchanged (liquid) ->
    an explicit override wins next -> a dynamic Longstaff-grid
    interpolation when time_to_liquidity_years and volatility are both
    given -> the flat default band from research.md#dlom otherwise."""
    _validate_stage(company_stage)
    if company_stage == "public":
        return {"low": value_low, "high": value_high,
                "dlom_low": 0.0, "dlom_high": 0.0,
                "method": "public-no-discount"}
    if override_low is not None or override_high is not None:
        dlom_low = DLOM_LOW if override_low is None else override_low
        dlom_high = DLOM_HIGH if override_high is None else override_high
        _validate_rate(dlom_low, "override_low")
        _validate_rate(dlom_high, "override_high")
        return {
            "low": value_low * (1 - dlom_high),
            "high": value_high * (1 - dlom_low),
            "dlom_low": dlom_low,
            "dlom_high": dlom_high,
            "method": "override",
        }
    if time_to_liquidity_years is not None and volatility is not None:
        dlom = compute_dynamic_dlom(time_to_liquidity_years, volatility)
        return {
            "low": value_low * (1 - dlom),
            "high": value_high * (1 - dlom),
            "dlom_low": dlom,
            "dlom_high": dlom,
            "method": "dynamic-longstaff-interpolation",
        }
    return {
        "low": value_low * (1 - DLOM_HIGH),
        "high": value_high * (1 - DLOM_LOW),
        "dlom_low": DLOM_LOW,
        "dlom_high": DLOM_HIGH,
        "method": "flat-default-band",
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, all tests (21 prior + Task 4's 12 = 33).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py DLOM range: dynamic Longstaff-grid interpolation with flat-band fallback"
```

---

### Task 5: Orchestration + CLI

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: `compute_face_value`, `compute_preference_adjustment`, `compute_exit_probability_range`, `compute_dlom_range` from Tasks 1-4 (exact signatures as produced there)
- Produces: `compute_valuation(inputs: dict) -> dict` and a `compute` CLI subcommand — this is the final public interface Bucket 4/5's `SKILL.md` will call.

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_option_value.py` (unit tests for `compute_valuation`, plus the CLI test class):

```python
class ComputeValuationTest(unittest.TestCase):
    def test_full_breakdown_with_preference_stack_and_cash_comparison(self):
        # face_value = 1000 * (5.00 - 2.00) = 3000.0
        # preference: common_price = 5.00 - 2,000,000/1,000,000 = 3.00
        #             adjusted_value = 1000 * (3.00 - 2.00) = 1000.0
        # exit range (private default): low=1000*0.25=250.0, high=1000*0.40=400.0
        # dlom range (private default): low=250*0.70=175.0, high=400*0.80=320.0
        # cash_alternative=1000.0 -> vs_low=1000-175=825.0, vs_high=1000-320=680.0
        result = option_value.compute_valuation({
            "shares": 1000,
            "strike_price": 2.00,
            "quoted_price": 5.00,
            "company_stage": "private",
            "preference_stack": 2_000_000,
            "fully_diluted_shares": 1_000_000,
            "cash_alternative": 1000.0,
        })
        self.assertEqual(result["face_value"], 3000.0)
        self.assertTrue(result["preference_adjustment"]["applied"])
        self.assertEqual(result["preference_adjustment"]["adjusted_value"], 1000.0)
        self.assertEqual(result["exit_probability_range"]["low"], 250.0)
        self.assertEqual(result["exit_probability_range"]["high"], 400.0)
        self.assertEqual(result["final_range"]["low"], 175.0)
        self.assertEqual(result["final_range"]["high"], 320.0)
        self.assertEqual(result["cash_vs_equity_low"], 825.0)
        self.assertEqual(result["cash_vs_equity_high"], 680.0)

    def test_missing_preference_stack_falls_back_to_face_value_for_later_stages(self):
        # preference not applied -> exit/dlom stages use face_value (3000.0)
        # exit range: low=3000*0.25=750.0, high=3000*0.40=1200.0
        # dlom range: low=750*0.70=525.0, high=1200*0.80=960.0
        result = option_value.compute_valuation({
            "shares": 1000,
            "strike_price": 2.00,
            "quoted_price": 5.00,
            "company_stage": "private",
        })
        self.assertFalse(result["preference_adjustment"]["applied"])
        self.assertIsNotNone(result["preference_adjustment"]["guidance"])
        self.assertEqual(result["final_range"]["low"], 525.0)
        self.assertEqual(result["final_range"]["high"], 960.0)

    def test_public_company_passes_through_every_stage(self):
        result = option_value.compute_valuation({
            "shares": 1000,
            "strike_price": 2.00,
            "quoted_price": 5.00,
            "company_stage": "public",
        })
        self.assertEqual(result["face_value"], 3000.0)
        self.assertEqual(result["final_range"]["low"], 3000.0)
        self.assertEqual(result["final_range"]["high"], 3000.0)

    def test_no_cash_alternative_omits_comparison_keys(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "public",
        })
        self.assertNotIn("cash_vs_equity_low", result)
        self.assertNotIn("cash_alternative", result)

    def test_missing_required_key_raises_with_key_name(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "strike_price": 2.00, "quoted_price": 5.00, "company_stage": "public",
            })
        self.assertIn("shares", str(ctx.exception))

    def test_exit_and_dlom_overrides_pass_through(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "exit_probability_override": {"low": 0.5, "high": 0.5},
            "dlom_override": {"low": 0.1, "high": 0.1},
        })
        # face_value=3000.0 -> exit override 0.5/0.5 -> 1500.0/1500.0
        # -> dlom override 0.1/0.1 -> 1350.0/1350.0
        self.assertEqual(result["final_range"]["low"], 1350.0)
        self.assertEqual(result["final_range"]["high"], 1350.0)

    def test_dynamic_dlom_inputs_pass_through_full_breakdown(self):
        # face_value=3000.0; preference applied -> base_for_exit=1000.0
        # exit range (private default): low=250.0, high=400.0
        # dlom dynamic (T=2, vol=0.25) -> 0.32 (verified in Task 4)
        # -> final_low=250*0.68=170.0, final_high=400*0.68=272.0
        # cash_alternative=1000.0 -> vs_low=1000-170=830.0, vs_high=1000-272=728.0
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "preference_stack": 2_000_000, "fully_diluted_shares": 1_000_000,
            "time_to_liquidity_years": 2, "volatility": 0.25,
            "cash_alternative": 1000.0,
        })
        self.assertAlmostEqual(result["final_range"]["low"], 170.0)
        self.assertAlmostEqual(result["final_range"]["high"], 272.0)
        self.assertEqual(result["final_range"]["method"], "dynamic-longstaff-interpolation")
        self.assertAlmostEqual(result["cash_vs_equity_low"], 830.0)
        self.assertAlmostEqual(result["cash_vs_equity_high"], 728.0)

    def test_specific_stage_tier_pass_through_full_breakdown(self):
        # face_value=3000.0; preference applied -> base_for_exit=1000.0
        # exit range (series_b: failure 0.72/0.72) -> low=280.0, high=280.0
        # dlom flat fallback (no time/vol given): low=280*0.70=196.0, high=280*0.80=224.0
        # cash_alternative=1000.0 -> vs_low=1000-196=804.0, vs_high=1000-224=776.0
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "preference_stack": 2_000_000, "fully_diluted_shares": 1_000_000,
            "cash_alternative": 1000.0,
        })
        self.assertEqual(result["exit_probability_range"]["low"], 280.0)
        self.assertEqual(result["exit_probability_range"]["high"], 280.0)
        self.assertEqual(result["final_range"]["low"], 196.0)
        self.assertEqual(result["final_range"]["high"], 224.0)
        self.assertEqual(result["cash_vs_equity_low"], 804.0)
        self.assertEqual(result["cash_vs_equity_high"], 776.0)


class OptionValueCLITest(unittest.TestCase):
    def setUp(self):
        self.script = str(Path(__file__).parent / "option_value.py")

    def run_cli(self, *args, input_text=None):
        import subprocess
        return subprocess.run(
            [sys.executable, self.script, *args],
            input=input_text, capture_output=True, text=True,
        )

    def test_compute_command_reads_stdin_and_prints_json_breakdown(self):
        import json
        inputs = json.dumps({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "public",
        })
        result = self.run_cli("compute", input_text=inputs)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["face_value"], 3000.0)

    def test_compute_command_invalid_json_fails_nonzero(self):
        result = self.run_cli("compute", input_text="not json")
        self.assertNotEqual(result.returncode, 0)

    def test_compute_command_missing_required_key_fails_nonzero(self):
        result = self.run_cli("compute", input_text='{"shares": 1000}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strike_price", result.stderr)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_option_value.py -v -k "ComputeValuationTest or OptionValueCLITest"`
Expected: FAIL — `ComputeValuationTest` fails with `AttributeError: module 'option_value' has no attribute 'compute_valuation'`; `OptionValueCLITest` fails because `option_value.py` isn't runnable as a CLI yet (no `argparse` entry point).

- [ ] **Step 3: Write the minimal implementation**

Append to `tools/option_value.py`:

```python
import argparse
import json
import sys

REQUIRED_KEYS = ("shares", "strike_price", "quoted_price", "company_stage")


def compute_valuation(inputs):
    """Runs all four stages in sequence and returns a full breakdown.

    inputs keys: shares, strike_price, quoted_price, company_stage
    (required); preference_stack, fully_diluted_shares,
    exit_probability_override ({'low', 'high'}), time_to_liquidity_years,
    volatility, dlom_override ({'low', 'high'}), cash_alternative (all
    optional). See compute_dlom_range for how time_to_liquidity_years/
    volatility vs. dlom_override vs. neither are prioritized.
    """
    missing = [k for k in REQUIRED_KEYS if k not in inputs]
    if missing:
        raise ValueError(f"missing required input(s): {missing}")

    shares = inputs["shares"]
    strike_price = inputs["strike_price"]
    quoted_price = inputs["quoted_price"]
    company_stage = inputs["company_stage"]

    face_value = compute_face_value(shares, strike_price, quoted_price)

    preference = compute_preference_adjustment(
        shares, strike_price, quoted_price,
        preference_stack=inputs.get("preference_stack"),
        fully_diluted_shares=inputs.get("fully_diluted_shares"),
    )

    base_for_exit = preference["adjusted_value"] if preference["applied"] else face_value

    exit_override = inputs.get("exit_probability_override") or {}
    exit_range = compute_exit_probability_range(
        base_for_exit, company_stage,
        override_low=exit_override.get("low"),
        override_high=exit_override.get("high"),
    )

    dlom_override = inputs.get("dlom_override") or {}
    final_range = compute_dlom_range(
        exit_range["low"], exit_range["high"], company_stage,
        time_to_liquidity_years=inputs.get("time_to_liquidity_years"),
        volatility=inputs.get("volatility"),
        override_low=dlom_override.get("low"),
        override_high=dlom_override.get("high"),
    )

    result = {
        "face_value": face_value,
        "preference_adjustment": preference,
        "exit_probability_range": exit_range,
        "final_range": final_range,
    }

    cash_alternative = inputs.get("cash_alternative")
    if cash_alternative is not None:
        result["cash_alternative"] = cash_alternative
        result["cash_vs_equity_low"] = cash_alternative - final_range["low"]
        result["cash_vs_equity_high"] = cash_alternative - final_range["high"]

    return result


def cmd_compute(args):
    try:
        inputs = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        result = compute_valuation(inputs)
    except (KeyError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Deterministic equity valuation calculator for offer-negotiator"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_compute = sub.add_parser(
        "compute",
        help="read valuation inputs as JSON on stdin, print a staged breakdown as JSON",
    )
    p_compute.set_defaults(func=cmd_compute)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

Note: this task adds `import argparse`, `import json`, `import sys` at module level — since earlier tasks' code (Tasks 1-4) doesn't use those imports, add them once here at the top of the file alongside the module docstring, not inline.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, all tests (33 prior + Task 5's 11 = 44).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py orchestration and compute CLI subcommand"
```

---

### Task 6: Self-review & finalize

**Files:**
- Modify: `tools/option_value.py` (fixes only, from the review below)

**Interfaces:**
- Consumes: the completed module from Tasks 1-5
- Produces: a finalized `tools/option_value.py` ready for Bucket 4/5's `SKILL.md` to call

- [ ] **Step 1: Docstring citation sweep**

Read through `tools/option_value.py` top to bottom. Confirm every default constant (`SEED_FAILURE_RATE_LOW`/`HIGH`, `SERIES_A_FAILURE_RATE_LOW`/`HIGH`, `SERIES_B_FAILURE_RATE`, `SERIES_C_FAILURE_RATE`, `SERIES_D_PLUS_FAILURE_RATE`, `GENERIC_PRIVATE_FAILURE_RATE_LOW`/`HIGH`, `DLOM_LOW`/`HIGH`, `LONGSTAFF_GRID_YEARS`/`LONGSTAFF_DLOM_AT_VOL_LOW`/`LONGSTAFF_DLOM_AT_VOL_HIGH`, `PREFERENCE_STACK_GUIDANCE`) has a comment citing its specific `research.md` anchor (`#exit-rate-base-rates`, `#dlom`, `#liquidation-preferences`). This is what lets `SKILL.md` (Bucket 4) call this tool without re-reading `research.md`'s prose at runtime — confirm the docstrings alone would let someone understand *why* each default is what it is, without opening `research.md`, including why `SERIES_D_PLUS_FAILURE_RATE` is just an alias for `SERIES_C_FAILURE_RATE` (no transition data exists past that point, not a coincidence) and why the Series B/C/D+ figures are notably higher than Mattermark's older, more optimistic pattern (an explicit, documented choice to prefer more recent and more pessimistic data, not an oversight). Confirm `compute_dynamic_dlom`'s docstring is explicit that it interpolates already-cited data points rather than re-deriving Longstaff's actual closed-form formula — this tool does not implement option-pricing math from scratch.

- [ ] **Step 2: Cross-check against spec §9's explicit test requirements**

Re-read spec §9. Confirm the test suite covers all three explicitly named cases: (a) zero/negative strike spread — `test_underwater_options_floor_at_zero` (Task 1); (b) public-company case with no haircuts applied — `test_public_company_passes_through_every_stage` (Task 5); (c) user-overridden defaults — `test_stage_override` (Task 3) and `test_private_company_override_takes_precedence_over_dynamic` (Task 4) and `test_exit_and_dlom_overrides_pass_through` (Task 5). If any is thin, strengthen it now.

- [ ] **Step 3: Run the full suite once and confirm pristine output**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, 44/44, no warnings.

- [ ] **Step 4: Commit (only if Steps 1-2 produced changes)**

```bash
git add tools/option_value.py
git commit -m "Self-review and finalize option_value.py"
```

If Steps 1-3 found nothing to fix, skip this commit — no empty commits.

---

## Self-Review Notes (plan author)

- **Spec coverage:** All four adjustment stages from spec §7 (as revised) are covered: Task 1 (face value), Task 2 (preference-stack, required-input-with-placeholder per the revision), Task 3 (exit-probability, real per-stage tiers — rewritten 2026-09-02 after the flat two-tier design was correctly rejected; see below), Task 4 (DLOM, dynamic Longstaff-grid interpolation with a flat-band fallback). Task 5 wires them together and adds the cash-alternative comparison spec §7 calls for, plus a new test exercising a specific stage tier end-to-end. The context-efficiency requirement (docstrings cite `research.md`) is built into every task's implementation step, not deferred, and Task 6 verifies it explicitly, now including the new stage-tier constants. No personal tax modeling appears anywhere — ISO/AMT isn't referenced in this tool at all, consistent with spec §2/§7.
- **Design history note:** Task 3 went through two prior versions before this one. Version 1 (spec's original) called for three unsourced stage tiers. Version 2 (Bucket 1's finding) collapsed to flat public/private after finding no supporting source. This version restores real per-stage differentiation after the user correctly objected that flat treatment was indefensible and three further research passes (browser-verified against primary sources — CB Insights, Mattermark, Carta) found real, cross-validated data. `_validate_stage`/`_validate_rate` (Task 3) and Task 4's reuse of them are unaffected by which version of the stage set is active, since Task 4's logic only branches on `== "public"` vs. everything else.
- **Placeholder scan:** No TBD/TODO; every step has real, complete code with computed expected values (hand-verified in step comments, e.g. Task 3's per-tier tests and Task 5's `test_specific_stage_tier_pass_through_full_breakdown`).
- **Type/interface consistency:** Verified `compute_preference_adjustment`'s return dict keys (`applied`, `adjusted_value`, `common_price`, `guidance`) are used identically in Task 5's `compute_valuation`. Verified `compute_exit_probability_range`'s and `compute_dlom_range`'s `low`/`high` keys chain correctly (Task 5 passes `exit_range["low"]`/`["high"]` into `compute_dlom_range`, and now also `time_to_liquidity_years`/`volatility`). Verified Task 4 reuses Task 3's `_validate_stage`/`_validate_rate` rather than redefining them, and that Task 4's existing `"private"`-based tests remain valid unchanged since `"private"` is still in the expanded `VALID_STAGES` tuple. Verified `compute_dlom_range`'s precedence order (public → override → dynamic → flat fallback) is exercised by a distinct test for each branch, including one confirming override beats dynamic when both are supplied. Verified `STAGE_DEFAULT_FAILURE_RATES` dict keys exactly match the non-`"public"` entries in `VALID_STAGES`.
- **Test-count arithmetic re-verified after the Task 3 rewrite:** Task 1 (3) → Task 2 (+7=10) → Task 3 (+11=21) → Task 4 (+12=33) → Task 5 (+11=44). Every task's "Expected: PASS" step states the running total.
