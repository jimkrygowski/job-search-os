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


if __name__ == "__main__":
    unittest.main()
