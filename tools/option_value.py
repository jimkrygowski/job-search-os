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
