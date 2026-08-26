import unittest

from tests.base_test import BaseTollTestCase
from services.booth_service import BoothNetworkService
from services.toll_booth_service import TollBoothService
from utils.exceptions import BoothNotFoundError, DuplicateRecordError


class TestBoothServices(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.booths = TollBoothService()
        self.network = BoothNetworkService()

    def test_create_booth(self):
        booth = self.booths.create_booth(
            "Main Booth", "NH48", 1, operator_id="OP001",
            booth_id="B001"
        )

        self.assertEqual(booth.status, "OPEN")

    def test_duplicate_booth_id_rejected(self):
        self.booths.create_booth(
            "Main Booth", "NH48", 1, booth_id="B001"
        )

        with self.assertRaises(DuplicateRecordError):
            self.booths.create_booth(
                "Another Booth", "NH48", 2, booth_id="B001"
            )

    def test_record_transaction_updates_stats(self):
        self.booths.create_booth("Main Booth", "NH48", 1, booth_id="B001")

        self.booths.record_transaction("B001", "TXN001", 50)
        booth = self.booths.get_booth("B001")

        self.assertEqual(booth.vehicle_count, 1)
        self.assertEqual(booth.total_collection, 50)

    def test_closed_booth_rejects_transactions(self):
        self.booths.create_booth("Main Booth", "NH48", 1, booth_id="B001")
        self.booths.close_booth("B001")

        with self.assertRaises(ValueError):
            self.booths.record_transaction("B001", "TXN001", 50)

    def test_missing_booth_raises(self):
        with self.assertRaises(BoothNotFoundError):
            self.booths.close_booth("B_GHOST")

    def test_network_status_counts(self):
        self.booths.create_booth("Booth A", "NH48", 1, booth_id="B001")
        self.booths.create_booth("Booth B", "NH48", 2, booth_id="B002")
        self.booths.close_booth("B002")

        status = self.network.get_network_status()

        self.assertEqual(status["total_booths"], 2)
        self.assertEqual(status["open_booths"], 1)
        self.assertEqual(status["closed_booths"], 1)

    def test_least_busy_open_booth(self):
        self.booths.create_booth("Booth A", "NH48", 1, booth_id="B001")
        self.booths.create_booth("Booth B", "NH48", 2, booth_id="B002")

        self.booths.record_transaction("B001", "TXN001", 50)

        busiest_free = self.network.get_least_busy_open_booth()
        self.assertEqual(busiest_free["booth_id"], "B002")


if __name__ == "__main__":
    unittest.main()
