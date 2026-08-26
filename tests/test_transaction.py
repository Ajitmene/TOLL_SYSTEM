import unittest

from tests.base_test import BaseTollTestCase
from services.transaction_service import TransactionService


class TestTransactionService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = TransactionService()

    def _create_sample(self, transaction_id="TXN001"):
        return self.service.create_transaction(
            transaction_id=transaction_id,
            vehicle_number="MH12AB1234",
            vehicle_type="Car",
            booth_id="B001",
            operator_id="OP001",
            base_toll=50,
            peak_charge=10,
            discount=6,
            payment_method="FASTag"
        )

    def test_create_transaction_success(self):
        transaction = self._create_sample()

        self.assertEqual(transaction.final_amount, 54)
        self.assertEqual(self.service.repository.count(), 1)

    def test_create_duplicate_transaction_raises(self):
        self._create_sample()

        with self.assertRaises(ValueError):
            self._create_sample()

    def test_get_transaction(self):
        self._create_sample()

        found = self.service.get_transaction("TXN001")
        self.assertIsNotNone(found)
        self.assertEqual(found["vehicle_number"], "MH12AB1234")

    def test_get_vehicle_transactions(self):
        self._create_sample("TXN001")
        self._create_sample("TXN002")

        results = self.service.get_vehicle_transactions("MH12AB1234")
        self.assertEqual(len(results), 2)

    def test_get_booth_transactions(self):
        self._create_sample("TXN001")

        results = self.service.get_booth_transactions("B001")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
