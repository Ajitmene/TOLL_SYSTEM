from datetime import datetime


class Transaction:

    def __init__(
        self,
        transaction_id,
        vehicle_number,
        vehicle_type,
        booth_id,
        operator_id,
        base_toll,
        peak_charge=0,
        discount=0,
        payment_method="Cash",
        status="SUCCESS"
    ):
        self.transaction_id = transaction_id
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.booth_id = booth_id
        self.operator_id = operator_id

        self.base_toll = base_toll
        self.peak_charge = peak_charge
        self.discount = discount

        self.payment_method = payment_method
        self.status = status

        self.transaction_datetime = datetime.now()

    @property
    def final_amount(self):
        return self.base_toll + self.peak_charge - self.discount

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type,
            "booth_id": self.booth_id,
            "operator_id": self.operator_id,
            "base_toll": self.base_toll,
            "peak_charge": self.peak_charge,
            "discount": self.discount,
            "final_amount": self.final_amount,
            "payment_method": self.payment_method,
            "status": self.status,
            "transaction_datetime":
                self.transaction_datetime.isoformat()
        }

    def __str__(self):
        return (
            f"Transaction ID : {self.transaction_id}\n"
            f"Vehicle Number  : {self.vehicle_number}\n"
            f"Vehicle Type    : {self.vehicle_type}\n"
            f"Booth ID        : {self.booth_id}\n"
            f"Operator ID     : {self.operator_id}\n"
            f"Base Toll       : ₹{self.base_toll}\n"
            f"Peak Charge     : ₹{self.peak_charge}\n"
            f"Discount        : ₹{self.discount}\n"
            f"Final Amount    : ₹{self.final_amount}\n"
            f"Payment Method  : {self.payment_method}\n"
            f"Status          : {self.status}\n"
            f"Date & Time     : {self.transaction_datetime}"
        )