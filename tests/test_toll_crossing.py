import unittest

from tests.base_test import BaseTollTestCase
from services.fastag_service import FASTagService
from services.pass_service import PassService
from services.toll_booth_service import TollBoothService
from services.toll_crossing_service import TollCrossingService
from services.vehicle_service import VehicleService
from services.violation_service import ViolationService
from utils.exceptions import InsufficientBalanceError, InvalidPaymentError


class TestTollCrossingService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.vehicles = VehicleService()
        self.booths = TollBoothService()
        self.fastags = FASTagService()
        self.passes = PassService()
        self.violations = ViolationService()
        self.crossing = TollCrossingService()

        self.vehicles.register_vehicle(
            "MH12AB1234", "Car", "Ajit", "9876543210", "Swift",
            "Petrol", "Maharashtra"
        )
        self.booths.create_booth(
            "Main Booth", "NH48", 1, operator_id="OP001",
            booth_id="B001"
        )

    def test_cash_crossing_updates_booth_stats(self):
        result = self.crossing.process_vehicle_crossing(
            "MH12AB1234", "B001", "OP001", "Cash", hour=12
        )

        self.assertEqual(result["toll"]["final_amount"], 50)

        booth = self.booths.get_booth("B001")
        self.assertEqual(booth.vehicle_count, 1)
        self.assertEqual(booth.total_collection, 50)

    def test_fastag_crossing_deducts_balance(self):
        tag = self.fastags.create_fastag("MH12AB1234", 500)
        self.vehicles.assign_fastag("MH12AB1234", tag.fastag_id)

        result = self.crossing.process_vehicle_crossing(
            "MH12AB1234", "B001", "OP001", "FASTag", hour=9
        )

        refreshed = self.fastags.get_fastag(tag.fastag_id)
        self.assertEqual(refreshed.balance, 500 - result["toll"]["final_amount"])

    def test_fastag_crossing_without_tag_records_violation(self):
        with self.assertRaises(InvalidPaymentError):
            self.crossing.process_vehicle_crossing(
                "MH12AB1234", "B001", "OP001", "FASTag"
            )

        violations = self.violations.get_unpaid_violations()
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["violation_type"], "NO_FASTAG")

    def test_fastag_crossing_insufficient_balance_records_violation(self):
        tag = self.fastags.create_fastag("MH12AB1234", 1)
        self.vehicles.assign_fastag("MH12AB1234", tag.fastag_id)

        with self.assertRaises(InsufficientBalanceError):
            self.crossing.process_vehicle_crossing(
                "MH12AB1234", "B001", "OP001", "FASTag", hour=9
            )

        violations = self.violations.get_unpaid_violations()
        self.assertEqual(len(violations), 1)
        self.assertEqual(
            violations[0]["violation_type"], "INSUFFICIENT_BALANCE"
        )

    def test_pass_crossing_is_free_and_consumes_trip(self):
        toll_pass = self.passes.issue_trip_pass("MH12AB1234", 2)

        result = self.crossing.process_vehicle_crossing(
            "MH12AB1234", "B001", "OP001", "Pass"
        )

        self.assertEqual(result["toll"]["final_amount"], 0)

        refreshed = self.passes.get_pass(toll_pass.pass_id)
        self.assertEqual(refreshed.trips_remaining, 1)

    def test_unknown_vehicle_raises(self):
        with self.assertRaises(Exception):
            self.crossing.process_vehicle_crossing(
                "GJ01ZZ9999", "B001", "OP001", "Cash"
            )


if __name__ == "__main__":
    unittest.main()
