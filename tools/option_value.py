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
        "low": round(value * (1 - failure_rate_high), 1),
        "high": round(value * (1 - failure_rate_low), 1),
        "failure_rate_low": failure_rate_low,
        "failure_rate_high": failure_rate_high,
    }
