import unittest

from tests.base_test import BaseTollTestCase
from services.fastag_service import FASTagService
from utils.exceptions import (
    DuplicateRecordError,
    FASTagNotFoundError,
    InsufficientBalanceError
)


class TestFASTagService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = FASTagService()

    def test_create_fastag(self):
        tag = self.service.create_fastag("MH12AB1234", 500)

        self.assertEqual(tag.balance, 500)
        self.assertEqual(tag.status, "ACTIVE")

    def test_duplicate_vehicle_fastag_rejected(self):
        self.service.create_fastag("MH12AB1234", 500)

        with self.assertRaises(DuplicateRecordError):
            self.service.create_fastag("MH12AB1234", 100)

    def test_recharge_increases_balance(self):
        tag = self.service.create_fastag("MH12AB1234", 100)

        new_balance = self.service.recharge(tag.fastag_id, 50)
        self.assertEqual(new_balance, 150)

    def test_deduct_decreases_balance(self):
        tag = self.service.create_fastag("MH12AB1234", 100)

        new_balance = self.service.deduct(tag.fastag_id, 40)
        self.assertEqual(new_balance, 60)

    def test_deduct_insufficient_balance_raises(self):
        tag = self.service.create_fastag("MH12AB1234", 10)

        with self.assertRaises(InsufficientBalanceError):
            self.service.deduct(tag.fastag_id, 100)

    def test_deactivate_and_activate(self):
        tag = self.service.create_fastag("MH12AB1234", 10)

        self.service.deactivate(tag.fastag_id)
        refreshed = self.service.get_fastag(tag.fastag_id)
        self.assertEqual(refreshed.status, "INACTIVE")

        self.service.activate(tag.fastag_id)
        refreshed = self.service.get_fastag(tag.fastag_id)
        self.assertEqual(refreshed.status, "ACTIVE")

    def test_missing_fastag_raises(self):
        with self.assertRaises(FASTagNotFoundError):
            self.service.recharge("FT_NOPE", 10)


if __name__ == "__main__":
    unittest.main()
