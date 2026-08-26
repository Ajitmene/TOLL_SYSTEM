import unittest

from tests.base_test import BaseTollTestCase
from services.payment_service import PaymentService


class TestPaymentService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = PaymentService()

    def test_cash_payment_always_succeeds(self):
        result = self.service.process_payment("Cash", 100)

        self.assertTrue(result["success"])
        self.assertEqual(result["details"]["transaction_reference"], "CASH")

    def test_upi_payment_success(self):
        result = self.service.process_payment(
            "UPI", 100, upi_id="ajit@upi"
        )

        self.assertTrue(result["success"])
        self.assertIn("ajit@upi", result["details"]["transaction_reference"])

    def test_upi_payment_missing_id_fails(self):
        result = self.service.process_payment("UPI", 100, upi_id=None)
        self.assertFalse(result["success"])

    def test_card_payment_success(self):
        result = self.service.process_payment(
            "Card", 100, card_last_four="1234"
        )
        self.assertTrue(result["success"])

    def test_card_payment_invalid_digits_fails(self):
        result = self.service.process_payment(
            "Card", 100, card_last_four="12"
        )
        self.assertFalse(result["success"])

    def test_fastag_payment_sufficient_balance(self):
        result = self.service.process_payment(
            "FASTag", 50, fastag_id="FT001", balance=200
        )
        self.assertTrue(result["success"])

    def test_fastag_payment_insufficient_balance(self):
        result = self.service.process_payment(
            "FASTag", 500, fastag_id="FT001", balance=10
        )
        self.assertFalse(result["success"])

    def test_unsupported_payment_method_raises(self):
        with self.assertRaises(ValueError):
            self.service.process_payment("Bitcoin", 100)


if __name__ == "__main__":
    unittest.main()
