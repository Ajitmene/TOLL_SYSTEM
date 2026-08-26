from models.toll_pass import TollPass
from repositories.toll_pass_repository import TollPassRepository
from repositories.vehicle_repository import VehicleRepository
from utils.exceptions import PassExpiredError, PassNotFoundError
from utils.id_generator import generate_pass_id

# Simple flat-rate pricing for prepaid passes. In a production
# system these would live in config/settings.py alongside the toll
# rates; kept local here to keep the pricing logic close to the
# feature that uses it.
MONTHLY_PASS_PRICE = 1500
TRIP_PASS_PRICE_PER_TRIP = 45


class PassService:

    def __init__(self):
        self.repository = TollPassRepository()
        self.vehicle_repository = VehicleRepository()

    def issue_monthly_pass(self, vehicle_number, validity_days=30):
        amount_paid = MONTHLY_PASS_PRICE * (validity_days / 30)

        toll_pass = TollPass(
            pass_id=generate_pass_id(),
            vehicle_number=vehicle_number,
            pass_type="MONTHLY",
            validity_days=validity_days,
            trips_remaining=0,
            amount_paid=round(amount_paid, 2)
        )

        self.repository.add(toll_pass.to_dict())

        return toll_pass

    def issue_trip_pass(self, vehicle_number, trip_count, validity_days=90):
        amount_paid = TRIP_PASS_PRICE_PER_TRIP * trip_count

        toll_pass = TollPass(
            pass_id=generate_pass_id(),
            vehicle_number=vehicle_number,
            pass_type="TRIP",
            validity_days=validity_days,
            trips_remaining=trip_count,
            amount_paid=round(amount_paid, 2)
        )

        self.repository.add(toll_pass.to_dict())

        return toll_pass

    def get_pass(self, pass_id):
        data = self.repository.find_by_pass_id(pass_id)

        if not data:
            raise PassNotFoundError(f"Pass {pass_id} not found.")

        return self._from_dict(data)

    def get_passes_for_vehicle(self, vehicle_number):
        return self.repository.find_by_vehicle_number(vehicle_number)

    def get_usable_pass_for_vehicle(self, vehicle_number):
        """Return the first pass for this vehicle that can currently
        be used to cross a booth for free, or None."""

        for data in self.repository.find_by_vehicle_number(
            vehicle_number
        ):
            toll_pass = self._from_dict(data)

            if toll_pass.is_usable():
                return toll_pass

        return None

    def use_pass(self, pass_id, booth_id):
        toll_pass = self.get_pass(pass_id)

        if not toll_pass.is_usable():
            raise PassExpiredError(
                f"Pass {pass_id} is expired, inactive, or exhausted."
            )

        toll_pass.consume_trip(booth_id)
        self._save(toll_pass)

        return toll_pass

    def cancel_pass(self, pass_id):
        toll_pass = self.get_pass(pass_id)
        toll_pass.cancel()
        self._save(toll_pass)

        return toll_pass

    def _save(self, toll_pass):
        self.repository.update(
            "pass_id", toll_pass.pass_id, toll_pass.to_dict()
        )

    @staticmethod
    def _from_dict(data):
        toll_pass = TollPass(
            pass_id=data["pass_id"],
            vehicle_number=data["vehicle_number"],
            pass_type=data["pass_type"],
            issue_date=data["issue_date"],
            validity_days=data["validity_days"],
            trips_remaining=data.get("trips_remaining", 0),
            amount_paid=data.get("amount_paid", 0),
            status=data.get("status", "ACTIVE")
        )

        toll_pass.usage_log = data.get("usage_log", [])

        return toll_pass
