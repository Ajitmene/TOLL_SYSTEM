from datetime import datetime, timedelta


class TollPass:
    """A prepaid toll pass: either a fixed-duration MONTHLY pass
    (unlimited crossings within the validity window) or a TRIP pass
    (a fixed number of prepaid crossings, consumed one at a time).
    """

    VALID_TYPES = ("MONTHLY", "TRIP")

    def __init__(
        self,
        pass_id,
        vehicle_number,
        pass_type,
        issue_date=None,
        validity_days=30,
        trips_remaining=0,
        amount_paid=0.0,
        status="ACTIVE"
    ):
        if pass_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unsupported pass type: {pass_type}. "
                f"Expected one of {self.VALID_TYPES}."
            )

        self.pass_id = pass_id
        self.vehicle_number = vehicle_number
        self.pass_type = pass_type

        self.issue_date = (
            datetime.fromisoformat(issue_date)
            if isinstance(issue_date, str)
            else (issue_date or datetime.now())
        )

        self.validity_days = validity_days
        self.expiry_date = self.issue_date + timedelta(
            days=validity_days
        )

        self.trips_remaining = trips_remaining
        self.amount_paid = float(amount_paid)
        self.status = status
        self.usage_log = []

    def is_expired(self, as_of=None):
        as_of = as_of or datetime.now()
        return as_of > self.expiry_date

    def is_usable(self):
        if self.status != "ACTIVE":
            return False

        if self.is_expired():
            return False

        if self.pass_type == "TRIP" and self.trips_remaining <= 0:
            return False

        return True

    def consume_trip(self, booth_id):
        if not self.is_usable():
            raise ValueError(
                f"Pass {self.pass_id} cannot be used "
                "(expired, inactive, or exhausted)."
            )

        if self.pass_type == "TRIP":
            self.trips_remaining -= 1

        self.usage_log.append({
            "booth_id": booth_id,
            "datetime": datetime.now().isoformat()
        })

    def cancel(self):
        self.status = "CANCELLED"

    def to_dict(self):
        return {
            "pass_id": self.pass_id,
            "vehicle_number": self.vehicle_number,
            "pass_type": self.pass_type,
            "issue_date": self.issue_date.isoformat(),
            "validity_days": self.validity_days,
            "expiry_date": self.expiry_date.isoformat(),
            "trips_remaining": self.trips_remaining,
            "amount_paid": self.amount_paid,
            "status": self.status,
            "usage_log": self.usage_log
        }

    def __str__(self):
        return (
            f"Pass ID          : {self.pass_id}\n"
            f"Vehicle Number   : {self.vehicle_number}\n"
            f"Pass Type        : {self.pass_type}\n"
            f"Issue Date       : {self.issue_date}\n"
            f"Expiry Date      : {self.expiry_date}\n"
            f"Trips Remaining  : {self.trips_remaining}\n"
            f"Amount Paid      : \u20b9{self.amount_paid:.2f}\n"
            f"Status           : {self.status}"
        )
