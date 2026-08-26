import unittest

from tests.base_test import BaseTollTestCase
from services.toll_service import TollService


class TestTollService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = TollService()

    def test_get_base_toll_known_type(self):
        self.assertEqual(self.service.get_base_toll("Car"), 50)

    def test_get_base_toll_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_base_toll("Spaceship")

    def test_is_peak_hour(self):
        self.assertTrue(self.service.is_peak_hour(9))
        self.assertTrue(self.service.is_peak_hour(18))
        self.assertFalse(self.service.is_peak_hour(12))

    def test_peak_charge_applied_only_in_peak_hours(self):
        self.assertEqual(self.service.get_peak_charge("Car", 9), 10)
        self.assertEqual(self.service.get_peak_charge("Car", 12), 0)

    def test_fastag_discount_calculation(self):
        discount = self.service.calculate_fastag_discount(100)
        self.assertEqual(discount, 10)

    def test_calculate_toll_cash_off_peak(self):
        result = self.service.calculate_toll("Car", "Cash", hour=12)

        self.assertEqual(result["base_toll"], 50)
        self.assertEqual(result["peak_charge"], 0)
        self.assertEqual(result["discount"], 0)
        self.assertEqual(result["final_amount"], 50)

    def test_calculate_toll_fastag_peak(self):
        result = self.service.calculate_toll("Car", "FASTag", hour=9)

        # base(50) + peak(10) = 60, 10% discount = 6
        self.assertEqual(result["base_toll"], 50)
        self.assertEqual(result["peak_charge"], 10)
        self.assertEqual(result["discount"], 6.0)
        self.assertEqual(result["final_amount"], 54.0)


if __name__ == "__main__":
    unittest.main()
