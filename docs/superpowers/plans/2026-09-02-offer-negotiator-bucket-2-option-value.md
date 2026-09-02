# Offer Negotiator — Bucket 2: `option_value.py` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tools/option_value.py`, a deterministic equity valuation calculator that computes a transparent, staged breakdown (face value → preference-stack-adjusted → exit-probability range → time-value/DLOM range) rather than a single confident number, so `offer-negotiator`'s later buckets can call it instead of freehand-computing real financial math.

**Architecture:** Four pure computation functions, one per adjustment stage, composed by an orchestration function and exposed via a single `compute` CLI subcommand that reads JSON on stdin and prints a JSON breakdown on stdout — same shape as `tools/score_table.py` (stdlib only, argparse, tested with a CLI subprocess test class).

**Tech Stack:** Python 3 stdlib only (`argparse`, `json`, `sys`, `unittest`, `subprocess` in tests). No pip dependencies.

**Spec:** `docs/superpowers/specs/2026-09-01-offer-negotiator-design.md` (§7, as revised for Bucket 2's three confirmed decisions)

## Global Constraints

- Public-company inputs pass through **every** adjustment stage unchanged (no preference-stack, exit-probability, or DLOM adjustment applies — a real market price already exists) (spec §7 steps 2-4, §9).
- The preference-stack adjustment is a **required input with an explicit unconfirmed-placeholder state, never a silently-applied default**: when `preference_stack` or `fully_diluted_shares` is missing, output `"applied": false` plus concrete guidance on what to ask the company for — do not fall back to any generic percentage (spec §7 step 2, revised).
- The exit-probability haircut has **exactly two tiers — public and private** — never differentiate early-stage from late-stage private; `research.md` found no source that credibly supports that split (spec §7 step 3, revised).
- Default constants: exit-probability failure rate **0.60–0.75** (source: `research.md#exit-rate-base-rates`), DLOM discount **0.20–0.30** (source: `research.md#dlom`). Every default constant's docstring/comment must cite its `research.md` anchor.
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

### Task 3: Exit-probability range

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: nothing new
- Produces: `compute_exit_probability_range(value, company_stage, override_low=None, override_high=None) -> dict` with keys `low`, `high`, `failure_rate_low`, `failure_rate_high`. Also produces shared helpers `_validate_stage(company_stage)` and `_validate_rate(rate, name)`, both raising `ValueError` — Task 4 reuses these exact helpers rather than redefining them.

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

    def test_private_company_default_range(self):
        # failure rate range 0.60-0.75 -> survival range 0.25-0.40
        result = option_value.compute_exit_probability_range(1000.0, "private")
        self.assertEqual(result["low"], 250.0)
        self.assertEqual(result["high"], 400.0)
        self.assertEqual(result["failure_rate_low"], 0.60)
        self.assertEqual(result["failure_rate_high"], 0.75)

    def test_private_company_override(self):
        result = option_value.compute_exit_probability_range(
            1000.0, "private", override_low=0.5, override_high=0.5,
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
VALID_STAGES = ("public", "private")

# Source: research.md#exit-rate-base-rates ("How to use correctly") --
# roughly 60-75% of VC-backed positions return nothing or less than
# invested capital to preferred. Applies only to private companies;
# public companies have a real market price and no exit-probability
# haircut applies. research.md explicitly found no source that credibly
# differentiates early-stage from late-stage private -- do not add a
# third tier without a real source.
EXIT_FAILURE_RATE_LOW = 0.60
EXIT_FAILURE_RATE_HIGH = 0.75


def _validate_stage(company_stage):
    if company_stage not in VALID_STAGES:
        raise ValueError(f"company_stage must be one of {VALID_STAGES}, got {company_stage!r}")


def _validate_rate(rate, name):
    if not 0 <= rate <= 1:
        raise ValueError(f"{name} must be between 0 and 1, got {rate!r}")


def compute_exit_probability_range(value, company_stage,
                                     override_low=None, override_high=None):
    """Applies the exit-probability haircut as a range: public companies
    pass through unchanged (a real market price already exists); private
    companies apply the default failure-rate range from
    research.md#exit-rate-base-rates (or an override), returning a
    (low, high) value range plus the failure rates used."""
    _validate_stage(company_stage)
    if company_stage == "public":
        return {"low": value, "high": value,
                "failure_rate_low": 0.0, "failure_rate_high": 0.0}
    failure_rate_low = EXIT_FAILURE_RATE_LOW if override_low is None else override_low
    failure_rate_high = EXIT_FAILURE_RATE_HIGH if override_high is None else override_high
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
Expected: PASS, all tests (10 prior + Task 3's 6 = 16).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py exit-probability range adjustment"
```

---

### Task 4: DLOM (time-value/illiquidity) range

**Files:**
- Modify: `tools/option_value.py`
- Modify: `tools/test_option_value.py`

**Interfaces:**
- Consumes: `_validate_stage` and `_validate_rate` from Task 3 (does not redefine them)
- Produces: `compute_dlom_range(value_low, value_high, company_stage, override_low=None, override_high=None) -> dict` with keys `low`, `high`, `dlom_low`, `dlom_high` — Task 5's orchestration calls this exact signature.

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_option_value.py`:

```python
class ComputeDlomRangeTest(unittest.TestCase):
    def test_public_company_passes_through_unchanged(self):
        result = option_value.compute_dlom_range(250.0, 400.0, "public")
        self.assertEqual(result, {
            "low": 250.0, "high": 400.0,
            "dlom_low": 0.0, "dlom_high": 0.0,
        })

    def test_private_company_default_range(self):
        # dlom range 0.20-0.30: low end gets the bigger discount (0.30),
        # high end gets the smaller discount (0.20)
        result = option_value.compute_dlom_range(250.0, 400.0, "private")
        self.assertEqual(result["low"], 175.0)
        self.assertEqual(result["high"], 320.0)
        self.assertEqual(result["dlom_low"], 0.20)
        self.assertEqual(result["dlom_high"], 0.30)

    def test_private_company_override(self):
        result = option_value.compute_dlom_range(
            250.0, 400.0, "private", override_low=0.1, override_high=0.1,
        )
        self.assertEqual(result["low"], 225.0)
        self.assertEqual(result["high"], 360.0)

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

Run: `python3 -m pytest tools/test_option_value.py -v -k ComputeDlomRangeTest`
Expected: FAIL with `AttributeError: module 'option_value' has no attribute 'compute_dlom_range'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `tools/option_value.py`:

```python
# Source: research.md#dlom ("How to use correctly") -- a 20-30% default
# is a defensible judgment call within a literature that spans roughly
# 7% (Bajaj et al.'s controlled estimate) to 40%+ (pre-IPO / option-
# pricing bounds), not a point of convergence. Applies only to private
# companies; public stock is liquid.
DLOM_LOW = 0.20
DLOM_HIGH = 0.30


def compute_dlom_range(value_low, value_high, company_stage,
                         override_low=None, override_high=None):
    """Applies the time-value/illiquidity (DLOM) discount as a range:
    public companies pass through unchanged (liquid); private companies
    apply the default discount range from research.md#dlom (or an
    override) to each end of the incoming range."""
    _validate_stage(company_stage)
    if company_stage == "public":
        return {"low": value_low, "high": value_high,
                "dlom_low": 0.0, "dlom_high": 0.0}
    dlom_low = DLOM_LOW if override_low is None else override_low
    dlom_high = DLOM_HIGH if override_high is None else override_high
    _validate_rate(dlom_low, "override_low")
    _validate_rate(dlom_high, "override_high")
    return {
        "low": value_low * (1 - dlom_high),
        "high": value_high * (1 - dlom_low),
        "dlom_low": dlom_low,
        "dlom_high": dlom_high,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, all tests (16 prior + Task 4's 5 = 21).

- [ ] **Step 5: Commit**

```bash
git add tools/option_value.py tools/test_option_value.py
git commit -m "Add option_value.py DLOM (time-value/illiquidity) range adjustment"
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
    exit_probability_override ({'low', 'high'}), dlom_override
    ({'low', 'high'}), cash_alternative (all optional).
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
Expected: PASS, all tests (21 prior + Task 5's 9 = 30).

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

Read through `tools/option_value.py` top to bottom. Confirm every default constant (`EXIT_FAILURE_RATE_LOW`/`HIGH`, `DLOM_LOW`/`HIGH`, `PREFERENCE_STACK_GUIDANCE`) has a comment citing its specific `research.md` anchor (`#exit-rate-base-rates`, `#dlom`, `#liquidation-preferences`). This is what lets `SKILL.md` (Bucket 4) call this tool without re-reading `research.md`'s prose at runtime — confirm the docstrings alone would let someone understand *why* each default is what it is, without opening `research.md`.

- [ ] **Step 2: Cross-check against spec §9's explicit test requirements**

Re-read spec §9. Confirm the test suite covers all three explicitly named cases: (a) zero/negative strike spread — `test_underwater_options_floor_at_zero` (Task 1); (b) public-company case with no haircuts applied — `test_public_company_passes_through_every_stage` (Task 5); (c) user-overridden defaults — `test_private_company_override` (Tasks 3 and 4) and `test_exit_and_dlom_overrides_pass_through` (Task 5). If any is thin, strengthen it now.

- [ ] **Step 3: Run the full suite once and confirm pristine output**

Run: `python3 -m pytest tools/test_option_value.py -v`
Expected: PASS, 30/30, no warnings.

- [ ] **Step 4: Commit (only if Steps 1-2 produced changes)**

```bash
git add tools/option_value.py
git commit -m "Self-review and finalize option_value.py"
```

If Steps 1-3 found nothing to fix, skip this commit — no empty commits.

---

## Self-Review Notes (plan author)

- **Spec coverage:** All four adjustment stages from spec §7 (as revised) are covered: Task 1 (face value), Task 2 (preference-stack, required-input-with-placeholder per the revision), Task 3 (exit-probability, two-tier per the revision), Task 4 (DLOM). Task 5 wires them together and adds the cash-alternative comparison spec §7 calls for. The context-efficiency requirement (docstrings cite `research.md`) is built into every task's implementation step, not deferred, and Task 6 verifies it explicitly. No personal tax modeling appears anywhere — ISO/AMT isn't referenced in this tool at all, consistent with spec §2/§7.
- **Placeholder scan:** No TBD/TODO; every step has real, complete code with computed expected values (hand-verified in step comments, e.g. Task 5's `test_full_breakdown_with_preference_stack_and_cash_comparison`).
- **Type/interface consistency:** Verified `compute_preference_adjustment`'s return dict keys (`applied`, `adjusted_value`, `common_price`, `guidance`) are used identically in Task 5's `compute_valuation`. Verified `compute_exit_probability_range`'s and `compute_dlom_range`'s `low`/`high` keys chain correctly (Task 5 passes `exit_range["low"]`/`["high"]` into `compute_dlom_range`). Verified Task 4 reuses Task 3's `_validate_stage`/`_validate_rate` rather than redefining them (stated explicitly in Task 4's Interfaces block).
