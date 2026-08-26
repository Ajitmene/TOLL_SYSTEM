from models.violation import Violation
from repositories.violation_repository import ViolationRepository
from utils.exceptions import ValidationError, ViolationNotFoundError
from utils.id_generator import generate_violation_id

# Default fines by violation type. A production system would move
# this into config/settings.py; kept local since it's only used here.
DEFAULT_FINES = {
    "NO_FASTAG": 200,
    "INSUFFICIENT_BALANCE": 150,
    "INVALID_PASS": 150,
    "LANE_VIOLATION": 500,
    "OVERSPEEDING": 1000,
    "OTHER": 100
}


class ViolationService:

    def __init__(self):
        self.repository = ViolationRepository()

    def record_violation(
        self,
        vehicle_number,
        booth_id,
        violation_type,
        description="",
        fine_amount=None
    ):
        if violation_type not in Violation.VALID_TYPES:
            raise ValidationError(
                f"Unsupported violation type: {violation_type}"
            )

        fine = (
            fine_amount
            if fine_amount is not None
            else DEFAULT_FINES.get(violation_type, 100)
        )

        violation = Violation(
            violation_id=generate_violation_id(),
            vehicle_number=vehicle_number,
            booth_id=booth_id,
            violation_type=violation_type,
            fine_amount=fine,
            description=description
        )

        self.repository.add(violation.to_dict())

        return violation

    def get_violation(self, violation_id):
        data = self.repository.find_by_violation_id(violation_id)

        if not data:
            raise ViolationNotFoundError(
                f"Violation {violation_id} not found."
            )

        return self._from_dict(data)

    def get_vehicle_violations(self, vehicle_number):
        return self.repository.find_by_vehicle_number(vehicle_number)

    def get_unpaid_violations(self):
        return self.repository.get_unpaid()

    def pay_fine(self, violation_id):
        violation = self.get_violation(violation_id)
        violation.mark_paid()
        self._save(violation)

        return violation

    def waive_fine(self, violation_id):
        violation = self.get_violation(violation_id)
        violation.waive()
        self._save(violation)

        return violation

    def total_outstanding_fines(self):
        return sum(
            item["fine_amount"] for item in self.get_unpaid_violations()
        )

    def _save(self, violation):
        self.repository.update(
            "violation_id", violation.violation_id, violation.to_dict()
        )

    @staticmethod
    def _from_dict(data):
        violation = Violation(
            violation_id=data["violation_id"],
            vehicle_number=data["vehicle_number"],
            booth_id=data["booth_id"],
            violation_type=data["violation_type"],
            fine_amount=data["fine_amount"],
            description=data.get("description", ""),
            status=data.get("status", "UNPAID")
        )

        return violation
