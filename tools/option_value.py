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

import argparse
import json
import sys


def compute_face_value(shares, strike_price, quoted_price):
    """shares x max(0, quoted_price - strike_price) -- naive face value,
    as a company would present it, before any of the adjustments below."""
    return shares * max(0.0, quoted_price - strike_price)


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
#
# Caution -- double-counting risk (research.md#exit-rate-base-rates):
# this generic tier's underlying data reflects return-to-preferred
# outcomes, the same subordination effect compute_preference_adjustment
# already models above. Applying both to the same valuation risks
# discounting that effect twice. Per research.md, this caution applies
# regardless of which tier is used, but it carries this risk most
# directly for this generic fallback tier; the seed/series_a/series_b/
# series_c/series_d_plus tiers above are sourced from next-round-
# graduation data instead -- a different mechanism, though not one
# research.md declares entirely free of the same risk.
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


def _validate_range_order(low, high, low_name, high_name):
    """Guards against an inverted low/high pair -- e.g. a caller passing
    override_low=0.9, override_high=0.1 by mistake. low/high here name
    the *rate* pair (optimistic vs. pessimistic), not the output value
    range they produce, which is why this check can't just compare the
    already-computed output dict's "low"/"high" keys after the fact."""
    if low > high:
        raise ValueError(
            f"{low_name} ({low!r}) cannot exceed {high_name} ({high!r})"
        )


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
    _validate_range_order(failure_rate_low, failure_rate_high, "override_low", "override_high")
    return {
        "low": value * (1 - failure_rate_high),
        "high": value * (1 - failure_rate_low),
        "failure_rate_low": failure_rate_low,
        "failure_rate_high": failure_rate_high,
    }


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
    # Defense-in-depth: unreachable with the current fixed 3-point,
    # sorted Longstaff grid (the clamps above and the loop's bracket
    # search together cover the full [xs[0], xs[-1]] range), but a
    # future change to the grid (e.g. unsorted or empty xs) should fail
    # loud-ish rather than silently returning None.
    return ys[-1]


def compute_dynamic_dlom(time_to_liquidity_years, volatility):
    """DLOM interpolated from the Longstaff (1995) grid cited in
    research.md#dlom. This function linearly interpolates between those
    already-cited data points -- it does not re-derive Longstaff's
    actual closed-form option-pricing formula, which this tool does not
    attempt to reimplement. Clamps time and volatility to the cited
    range (1-5 years, 20-30% volatility) rather than extrapolating
    beyond verified data points.

    Per research.md#dlom, the Longstaff grid values are explicit upper
    bounds under an unrealistic perfect-timing assumption, not central
    estimates -- actual discounts should be lower. Treat this function's
    result as potentially conservative (i.e., possibly higher than a
    more realistic discount would be), not a best-guess point estimate.
    """
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
    given -> the flat default band from research.md#dlom otherwise.

    A *partial* override (only override_low or only override_high
    supplied) still wins this precedence entirely for this call: the
    missing side falls back to the flat default (DLOM_LOW/DLOM_HIGH),
    and time_to_liquidity_years/volatility are silently ignored even if
    also supplied -- they are never blended with a partial override."""
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
        _validate_range_order(dlom_low, dlom_high, "override_low", "override_high")
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


REQUIRED_KEYS = ("shares", "strike_price", "quoted_price", "company_stage")


def compute_valuation(inputs):
    """Runs all four stages in sequence and returns a full breakdown.

    inputs keys: shares, strike_price, quoted_price, company_stage
    (required); preference_stack, fully_diluted_shares,
    exit_probability_override ({'low', 'high'}), time_to_liquidity_years,
    volatility, dlom_override ({'low', 'high'}), cash_alternative (all
    optional). See compute_dlom_range for how time_to_liquidity_years/
    volatility vs. dlom_override vs. neither are prioritized.

    The returned dict always includes a 'caveats' key (a list of plain-
    language warning strings, empty by default) so callers reading only
    this JSON -- not this module's source comments -- still see any
    known risk in how the figures combine. Currently the only condition
    that populates it is the generic 'private' stage combined with an
    applied preference-stack adjustment (see the double-counting caution
    above GENERIC_PRIVATE_FAILURE_RATE_LOW/HIGH).

    'public' company_stage passes face_value through unchanged at every
    stage -- including skipping the preference-stack computation
    entirely -- since a real market price already exists and there's no
    meaningful preference-stack question for freely-traded common stock.
    """
    missing = [k for k in REQUIRED_KEYS if k not in inputs]
    if missing:
        raise ValueError(f"missing required input(s): {missing}")

    shares = inputs["shares"]
    strike_price = inputs["strike_price"]
    quoted_price = inputs["quoted_price"]
    company_stage = inputs["company_stage"]

    if shares < 0:
        raise ValueError(f"shares cannot be negative, got {shares!r}")
    if strike_price < 0:
        raise ValueError(f"strike_price cannot be negative, got {strike_price!r}")
    if quoted_price < 0:
        raise ValueError(f"quoted_price cannot be negative, got {quoted_price!r}")

    face_value = compute_face_value(shares, strike_price, quoted_price)

    if company_stage == "public":
        # A real market price already exists -- there's no meaningful
        # preference-stack question for common stock that trades freely.
        # Skip the real computation entirely rather than letting a
        # supplied preference_stack/fully_diluted_shares silently apply
        # a nonsensical haircut to a public company.
        preference = {
            "applied": False,
            "adjusted_value": None,
            "common_price": None,
            "guidance": None,
        }
    else:
        preference = compute_preference_adjustment(
            shares, strike_price, quoted_price,
            preference_stack=inputs.get("preference_stack"),
            fully_diluted_shares=inputs.get("fully_diluted_shares"),
        )

    base_for_exit = face_value if company_stage == "public" else (
        preference["adjusted_value"] if preference["applied"] else face_value
    )

    caveats = []
    if company_stage == "private" and preference["applied"]:
        caveats.append(
            "The generic 'private' exit-probability rate is sourced from "
            "return-to-preferred data, which may already partially "
            "reflect the same subordination effect the preference-stack "
            "adjustment above has applied -- treat the combination as a "
            "rough, potentially conservative-biased estimate, not a "
            "precise figure."
        )

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
        "caveats": caveats,
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
    except (KeyError, ValueError, TypeError) as e:
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
