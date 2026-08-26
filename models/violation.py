from datetime import datetime


class Violation:
    """A recorded toll-rule violation, e.g. a vehicle that crossed
    without sufficient FASTag balance, without a valid tag/pass, or
    was flagged for a lane/speed infraction by an operator.
    """

    VALID_TYPES = (
        "NO_FASTAG",
        "INSUFFICIENT_BALANCE",
        "INVALID_PASS",
        "LANE_VIOLATION",
        "OVERSPEEDING",
        "OTHER"
    )

    def __init__(
        self,
        violation_id,
        vehicle_number,
        booth_id,
        violation_type,
        fine_amount,
        description="",
        status="UNPAID"
    ):
        if violation_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unsupported violation type: {violation_type}. "
                f"Expected one of {self.VALID_TYPES}."
            )

        self.violation_id = violation_id
        self.vehicle_number = vehicle_number
        self.booth_id = booth_id
        self.violation_type = violation_type
        self.fine_amount = float(fine_amount)
        self.description = description
        self.status = status
        self.recorded_at = datetime.now()
        self.paid_at = None

    def mark_paid(self):
        if self.status == "PAID":
            raise ValueError(
                f"Violation {self.violation_id} is already paid."
            )

        self.status = "PAID"
        self.paid_at = datetime.now()

    def waive(self):
        self.status = "WAIVED"

    def to_dict(self):
        return {
            "violation_id": self.violation_id,
            "vehicle_number": self.vehicle_number,
            "booth_id": self.booth_id,
            "violation_type": self.violation_type,
            "fine_amount": self.fine_amount,
            "description": self.description,
            "status": self.status,
            "recorded_at": self.recorded_at.isoformat(),
            "paid_at": (
                self.paid_at.isoformat() if self.paid_at else None
            )
        }

    def __str__(self):
        return (
            f"Violation ID   : {self.violation_id}\n"
            f"Vehicle Number : {self.vehicle_number}\n"
            f"Booth ID       : {self.booth_id}\n"
            f"Type           : {self.violation_type}\n"
            f"Fine Amount    : \u20b9{self.fine_amount:.2f}\n"
            f"Status         : {self.status}\n"
            f"Recorded At    : {self.recorded_at}"
        )
