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
