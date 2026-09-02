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


if __name__ == "__main__":
    unittest.main()
