import unittest

from tests.base_test import BaseTollTestCase
from services.pass_service import PassService
from utils.exceptions import PassExpiredError, PassNotFoundError


class TestPassService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = PassService()

    def test_issue_monthly_pass(self):
        toll_pass = self.service.issue_monthly_pass("MH12AB1234", 30)

        self.assertEqual(toll_pass.pass_type, "MONTHLY")
        self.assertTrue(toll_pass.is_usable())

    def test_issue_trip_pass(self):
        toll_pass = self.service.issue_trip_pass("MH12AB1234", 5)

        self.assertEqual(toll_pass.trips_remaining, 5)
        self.assertTrue(toll_pass.is_usable())

    def test_use_trip_pass_decrements_remaining(self):
        toll_pass = self.service.issue_trip_pass("MH12AB1234", 2)

        self.service.use_pass(toll_pass.pass_id, "B001")
        refreshed = self.service.get_pass(toll_pass.pass_id)

        self.assertEqual(refreshed.trips_remaining, 1)

    def test_exhausted_trip_pass_cannot_be_used(self):
        toll_pass = self.service.issue_trip_pass("MH12AB1234", 1)

        self.service.use_pass(toll_pass.pass_id, "B001")

        with self.assertRaises(PassExpiredError):
            self.service.use_pass(toll_pass.pass_id, "B001")

    def test_cancel_pass_makes_it_unusable(self):
        toll_pass = self.service.issue_monthly_pass("MH12AB1234")

        self.service.cancel_pass(toll_pass.pass_id)
        refreshed = self.service.get_pass(toll_pass.pass_id)

        self.assertFalse(refreshed.is_usable())

    def test_get_missing_pass_raises(self):
        with self.assertRaises(PassNotFoundError):
            self.service.get_pass("PASS_NOPE")

    def test_get_usable_pass_for_vehicle(self):
        self.service.issue_monthly_pass("MH12AB1234")

        found = self.service.get_usable_pass_for_vehicle("MH12AB1234")
        self.assertIsNotNone(found)

        none_found = self.service.get_usable_pass_for_vehicle(
            "MH99ZZ0000"
        )
        self.assertIsNone(none_found)


if __name__ == "__main__":
    unittest.main()
