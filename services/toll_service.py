from datetime import datetime

from config.settings import (
    DEFAULT_TOLL_RATES,
    PEAK_HOURS,
    PEAK_CHARGES,
    FASTAG_DISCOUNT_PERCENTAGE
)


class TollService:

    def get_base_toll(self, vehicle_type):

        if vehicle_type not in DEFAULT_TOLL_RATES:
            raise ValueError(
                f"Unsupported vehicle type: {vehicle_type}"
            )

        return DEFAULT_TOLL_RATES[vehicle_type]

    def is_peak_hour(self, hour=None):

        if hour is None:
            hour = datetime.now().hour

        for start_hour, end_hour in PEAK_HOURS:

            if start_hour <= hour < end_hour:
                return True

        return False

    def get_peak_charge(self, vehicle_type, hour=None):

        if not self.is_peak_hour(hour):
            return 0

        return PEAK_CHARGES.get(vehicle_type, 0)

    def calculate_fastag_discount(self, amount):

        return amount * FASTAG_DISCOUNT_PERCENTAGE / 100

    def calculate_toll(
        self,
        vehicle_type,
        payment_method="Cash",
        hour=None
    ):

        base_toll = self.get_base_toll(vehicle_type)

        peak_charge = self.get_peak_charge(
            vehicle_type,
            hour
        )

        subtotal = base_toll + peak_charge

        discount = 0

        if payment_method == "FASTag":
            discount = self.calculate_fastag_discount(
                subtotal
            )

        final_amount = subtotal - discount

        return {
            "base_toll": base_toll,
            "peak_charge": peak_charge,
            "discount": round(discount, 2),
            "final_amount": round(final_amount, 2)
        }