import unittest

from tests.base_test import BaseTollTestCase
from services.violation_service import ViolationService
from utils.exceptions import ValidationError, ViolationNotFoundError


class TestViolationService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = ViolationService()

    def test_record_violation_uses_default_fine(self):
        violation = self.service.record_violation(
            "MH12AB1234", "B001", "NO_FASTAG"
        )

        self.assertEqual(violation.fine_amount, 200)
        self.assertEqual(violation.status, "UNPAID")

    def test_record_violation_invalid_type_raises(self):
        with self.assertRaises(ValidationError):
            self.service.record_violation(
                "MH12AB1234", "B001", "TELEPORTED"
            )

    def test_pay_fine_marks_paid(self):
        violation = self.service.record_violation(
            "MH12AB1234", "B001", "OVERSPEEDING"
        )

        self.service.pay_fine(violation.violation_id)
        refreshed = self.service.get_violation(violation.violation_id)

        self.assertEqual(refreshed.status, "PAID")

    def test_waive_fine(self):
        violation = self.service.record_violation(
            "MH12AB1234", "B001", "LANE_VIOLATION"
        )

        self.service.waive_fine(violation.violation_id)
        refreshed = self.service.get_violation(violation.violation_id)

        self.assertEqual(refreshed.status, "WAIVED")

    def test_unpaid_violations_and_total(self):
        self.service.record_violation("MH12AB1234", "B001", "NO_FASTAG")
        self.service.record_violation(
            "MH14CD5678", "B001", "INSUFFICIENT_BALANCE"
        )

        unpaid = self.service.get_unpaid_violations()
        self.assertEqual(len(unpaid), 2)
        self.assertEqual(self.service.total_outstanding_fines(), 350)

    def test_missing_violation_raises(self):
        with self.assertRaises(ViolationNotFoundError):
            self.service.get_violation("VIO_NOPE")


if __name__ == "__main__":
    unittest.main()
