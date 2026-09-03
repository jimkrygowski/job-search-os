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

    def test_nan_preference_stack_raises(self):
        # Regression test: NaN < 0 is always False in Python, so the
        # existing negativity check silently let NaN through before this
        # fix -- poisoning the whole downstream computation with NaN.
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_preference_adjustment(
                shares=1000, strike_price=2.00, quoted_price=5.00,
                preference_stack=float("nan"), fully_diluted_shares=1_000_000,
            )
        self.assertIn("preference_stack", str(ctx.exception))

    def test_nan_fully_diluted_shares_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_preference_adjustment(
                shares=1000, strike_price=2.00, quoted_price=5.00,
                preference_stack=2_000_000, fully_diluted_shares=float("nan"),
            )
        self.assertIn("fully_diluted_shares", str(ctx.exception))


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
        self.assertAlmostEqual(result["low"], 310.0)
        self.assertEqual(result["high"], 480.0)
        self.assertEqual(result["failure_rate_low"], 0.52)
        self.assertEqual(result["failure_rate_high"], 0.69)

    def test_series_a_default_range(self):
        # failure rate range 0.37-0.85 (CB Insights to Carta worst vintage)
        result = option_value.compute_exit_probability_range(1000.0, "series_a")
        self.assertAlmostEqual(result["low"], 150.0)
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
        self.assertAlmostEqual(result["low"], 180.0)
        self.assertAlmostEqual(result["high"], 180.0)
        self.assertEqual(result["failure_rate_low"], 0.82)
        self.assertEqual(result["failure_rate_high"], 0.82)

    def test_series_d_plus_default_range_holds_flat_at_series_c_rate(self):
        # no transition data exists past Series D+; holds flat at 0.82
        result = option_value.compute_exit_probability_range(1000.0, "series_d_plus")
        self.assertAlmostEqual(result["low"], 180.0)
        self.assertAlmostEqual(result["high"], 180.0)
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

    def test_inverted_override_rates_raises(self):
        # override_low is meant to be the optimistic (lower) failure rate
        # and override_high the pessimistic (higher) one -- swapping them
        # would silently produce a value range where "low" > "high".
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_exit_probability_range(
                1000.0, "private", override_low=0.9, override_high=0.1,
            )
        self.assertIn("override_low", str(ctx.exception))
        self.assertIn("override_high", str(ctx.exception))

    def test_override_rates_equal_is_allowed(self):
        # a point estimate (low == high) is a legitimate, non-inverted case
        result = option_value.compute_exit_probability_range(
            1000.0, "private", override_low=0.5, override_high=0.5,
        )
        self.assertEqual(result["low"], 500.0)
        self.assertEqual(result["high"], 500.0)


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

    def test_inverted_override_rates_raises(self):
        # dlom_low is meant to be the optimistic (lower) discount and
        # dlom_high the pessimistic (higher) one -- swapping them would
        # silently produce a value range where "low" > "high".
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_dlom_range(
                250.0, 400.0, "private", override_low=0.9, override_high=0.1,
            )
        self.assertIn("override_low", str(ctx.exception))
        self.assertIn("override_high", str(ctx.exception))


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


    def test_public_company_with_preference_stack_still_passes_through_unchanged(self):
        # Regression test: public companies must ignore preference_stack/
        # fully_diluted_shares entirely -- a real market price already
        # exists, so there's no meaningful preference-stack question.
        # face_value = 1000 * (5.00 - 2.00) = 3000.0, unhaircut.
        result = option_value.compute_valuation({
            "shares": 1000,
            "strike_price": 2.00,
            "quoted_price": 5.00,
            "company_stage": "public",
            "preference_stack": 2_000_000,
            "fully_diluted_shares": 1_000_000,
        })
        self.assertEqual(result["final_range"]["low"], 3000.0)
        self.assertEqual(result["final_range"]["high"], 3000.0)
        self.assertFalse(result["preference_adjustment"]["applied"])
        self.assertIsNone(result["preference_adjustment"]["adjusted_value"])
        self.assertIsNone(result["preference_adjustment"]["guidance"])

    def test_negative_shares_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": -1000, "strike_price": 2.00, "quoted_price": 5.00,
                "company_stage": "public",
            })
        self.assertIn("shares", str(ctx.exception))

    def test_negative_strike_price_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": 1000, "strike_price": -2.00, "quoted_price": 5.00,
                "company_stage": "public",
            })
        self.assertIn("strike_price", str(ctx.exception))

    def test_negative_quoted_price_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": 1000, "strike_price": 2.00, "quoted_price": -5.00,
                "company_stage": "public",
            })
        self.assertIn("quoted_price", str(ctx.exception))

    def test_no_caveats_by_default(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
        })
        self.assertEqual(result["caveats"], [])

    def test_generic_private_stage_with_applied_preference_adjustment_adds_caveat(self):
        # Double-counting caveat should fire only for the generic
        # "private" fallback tier combined with an applied preference
        # adjustment -- not for specific stage tiers, and not when the
        # preference adjustment wasn't applied.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "preference_stack": 2_000_000, "fully_diluted_shares": 1_000_000,
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("subordination", result["caveats"][0].lower())

    def test_specific_stage_tier_with_applied_preference_adjustment_has_no_double_counting_caveat(self):
        # series_b is a specific stage tier, not the generic fallback --
        # the double-counting caveat should NOT fire here even though the
        # preference adjustment is applied. It DOES get the single-source
        # caveat (see test_series_b_stage_adds_single_source_caveat) --
        # this test only asserts the double-counting one is absent.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "preference_stack": 2_000_000, "fully_diluted_shares": 1_000_000,
        })
        self.assertFalse(any("subordination" in c.lower() for c in result["caveats"]))

    def test_generic_private_stage_without_preference_adjustment_has_no_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
        })
        self.assertEqual(result["caveats"], [])

    def test_series_b_stage_adds_single_source_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("single source", result["caveats"][0].lower())

    def test_series_c_stage_adds_single_source_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_c",
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("single source", result["caveats"][0].lower())

    def test_series_d_plus_stage_adds_held_flat_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_d_plus",
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("held flat", result["caveats"][0].lower())

    def test_seed_stage_has_no_single_source_caveat(self):
        # seed and series_a are cross-validated against two independent
        # sources -- they should not get the single-source caveat.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "seed",
        })
        self.assertEqual(result["caveats"], [])

    def test_series_a_stage_has_no_single_source_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_a",
        })
        self.assertEqual(result["caveats"], [])

    def test_dynamic_dlom_adds_upper_bound_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "time_to_liquidity_years": 2, "volatility": 0.25,
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("upper bound", result["caveats"][0].lower())

    def test_flat_dlom_fallback_has_no_upper_bound_caveat(self):
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
        })
        self.assertEqual(result["caveats"], [])

    def test_series_b_with_dynamic_dlom_gets_both_caveats(self):
        # Confirms caveats accumulate rather than overwrite -- single-source
        # (from the stage tier) and upper-bound (from dynamic DLOM) are
        # independent conditions that can both apply to the same call.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "time_to_liquidity_years": 2, "volatility": 0.25,
        })
        self.assertEqual(len(result["caveats"]), 2)
        joined = " ".join(result["caveats"]).lower()
        self.assertIn("single source", joined)
        self.assertIn("upper bound", joined)

    def test_partial_exit_probability_override_low_only_still_adds_single_source_caveat(self):
        # Regression test: a caller supplying only override_low used to
        # suppress the single-source caveat entirely, even though the
        # unspecified high side still silently used the tool's own
        # single-source STAGE_DEFAULT_FAILURE_RATES default.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "exit_probability_override": {"low": 0.5},
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("single source", result["caveats"][0].lower())
        self.assertEqual(result["exit_probability_range"]["failure_rate_high"], 0.72)

    def test_partial_exit_probability_override_high_only_still_adds_single_source_caveat(self):
        # override_high must stay >= series_b's flat 0.72 default (which
        # still applies to the un-overridden low side) to avoid an
        # unrelated inverted-range error.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "exit_probability_override": {"high": 0.9},
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("single source", result["caveats"][0].lower())
        self.assertEqual(result["exit_probability_range"]["failure_rate_low"], 0.72)

    def test_full_exit_probability_override_suppresses_single_source_caveat(self):
        # Both sides explicitly supplied -- the tool's own default isn't
        # in use at all, so the caveat about that default correctly
        # doesn't fire.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "series_b",
            "exit_probability_override": {"low": 0.5, "high": 0.5},
        })
        self.assertEqual(result["caveats"], [])

    def test_partial_dlom_override_with_dynamic_inputs_adds_discard_caveat(self):
        # Regression test: a partial dlom_override wins precedence over
        # the dynamic Longstaff calculation entirely for this call, and
        # the missing side silently falls back to the flat default band
        # -- time_to_liquidity_years/volatility are discarded, not
        # blended, with no prior indication of that in the output.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "time_to_liquidity_years": 2, "volatility": 0.25,
            "dlom_override": {"low": 0.05},
        })
        self.assertEqual(len(result["caveats"]), 1)
        self.assertIn("not blended", result["caveats"][0].lower())
        self.assertEqual(result["final_range"]["dlom_high"], option_value.DLOM_HIGH)

    def test_full_dlom_override_with_dynamic_inputs_has_no_discard_caveat(self):
        # Both sides explicitly supplied -- nothing is ambiguously
        # discarded, the caller clearly overrode the whole range on
        # purpose.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "time_to_liquidity_years": 2, "volatility": 0.25,
            "dlom_override": {"low": 0.05, "high": 0.10},
        })
        self.assertEqual(result["caveats"], [])

    def test_partial_dlom_override_without_dynamic_inputs_has_no_discard_caveat(self):
        # No time_to_liquidity_years/volatility supplied at all -- the
        # dynamic path was never in play, so nothing was discarded.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "private",
            "dlom_override": {"low": 0.05},
        })
        self.assertEqual(result["caveats"], [])

    def test_public_stage_with_partial_dlom_override_and_dynamic_inputs_has_no_discard_caveat(self):
        # DLOM doesn't apply to public stock at all -- the caveat about
        # discarding a dynamic calculation would be nonsensical here.
        result = option_value.compute_valuation({
            "shares": 1000, "strike_price": 2.00, "quoted_price": 5.00,
            "company_stage": "public",
            "time_to_liquidity_years": 2, "volatility": 0.25,
            "dlom_override": {"low": 0.05},
        })
        self.assertEqual(result["caveats"], [])

    def test_nan_shares_raises(self):
        # Regression test: NaN comparisons are always False in Python
        # (nan < 0 is False), so the existing negativity check silently
        # let NaN through -- poisoning face_value and every downstream
        # figure with NaN, and producing invalid (non-standard) JSON
        # output via json.dumps.
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": float("nan"), "strike_price": 2.00, "quoted_price": 5.00,
                "company_stage": "public",
            })
        self.assertIn("shares", str(ctx.exception))

    def test_nan_strike_price_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": 1000, "strike_price": float("nan"), "quoted_price": 5.00,
                "company_stage": "public",
            })
        self.assertIn("strike_price", str(ctx.exception))

    def test_nan_quoted_price_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": 1000, "strike_price": 2.00, "quoted_price": float("nan"),
                "company_stage": "public",
            })
        self.assertIn("quoted_price", str(ctx.exception))

    def test_infinite_quoted_price_raises(self):
        with self.assertRaises(ValueError) as ctx:
            option_value.compute_valuation({
                "shares": 1000, "strike_price": 2.00, "quoted_price": float("inf"),
                "company_stage": "public",
            })
        self.assertIn("quoted_price", str(ctx.exception))


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

    def test_compute_command_non_numeric_input_fails_cleanly(self):
        # Regression test: non-numeric JSON values (e.g. shares as a
        # string) used to raise an uncaught TypeError deep in the
        # arithmetic instead of a clean CLI error.
        result = self.run_cli("compute", input_text=(
            '{"shares": "1000", "strike_price": 2.00, "quoted_price": 5.00, '
            '"company_stage": "public"}'
        ))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

    def test_compute_command_nan_input_fails_cleanly(self):
        # Regression test: Python's json module accepts the literal
        # token NaN by default (a non-standard JSON extension), so this
        # sails past json.load and used to poison the whole computation
        # instead of raising a clean, catchable error.
        result = self.run_cli("compute", input_text=(
            '{"shares": NaN, "strike_price": 2.00, "quoted_price": 5.00, '
            '"company_stage": "public"}'
        ))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("shares", result.stderr)


if __name__ == "__main__":
    unittest.main()
