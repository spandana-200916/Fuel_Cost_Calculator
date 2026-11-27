
import unittest

from fuel_logic import calculate_fuel


class TestFuelCalculator(unittest.TestCase):

    def test_petrol_calculation(self):
        result = calculate_fuel(
            100, 20, 100, "One Way"
        )

        self.assertEqual(result["fuel_required"], 5)
        self.assertEqual(result["total_cost"], 500)

    def test_round_trip(self):
        result = calculate_fuel(
            100, 20, 100, "Round Trip"
        )

        self.assertEqual(result["distance"], 200)
        self.assertEqual(result["total_cost"], 1000)

    def test_invalid_distance(self):
        with self.assertRaises(ValueError):
            calculate_fuel(
                0, 20, 100, "One Way"
            )

    def test_invalid_mileage(self):
        with self.assertRaises(ValueError):
            calculate_fuel(
                100, 0, 100, "One Way"
            )

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            calculate_fuel(
                100, 20, 0, "One Way"
            )


if __name__ == "__main__":
    unittest.main()
