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
