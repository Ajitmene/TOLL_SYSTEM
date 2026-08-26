from datetime import datetime


class FASTag:

    def __init__(
        self,
        fastag_id,
        vehicle_number,
        balance=0,
        status="ACTIVE"
    ):
        self.fastag_id = fastag_id
        self.vehicle_number = vehicle_number
        self.balance = float(balance)
        self.status = status
        self.transaction_history = []

    def recharge(self, amount):

        if amount <= 0:
            raise ValueError(
                "Recharge amount must be greater than zero."
            )

        if self.status != "ACTIVE":
            raise ValueError(
                "FASTag account is not active."
            )

        self.balance += amount

        self.transaction_history.append({
            "type": "RECHARGE",
            "amount": amount,
            "balance_after": self.balance,
            "datetime": datetime.now().isoformat()
        })

        return self.balance

    def deduct(self, amount):

        if amount <= 0:
            raise ValueError(
                "Deduction amount must be greater than zero."
            )

        if self.status != "ACTIVE":
            raise ValueError(
                "FASTag account is not active."
            )

        if self.balance < amount:
            raise ValueError(
                "Insufficient FASTag balance."
            )

        self.balance -= amount

        self.transaction_history.append({
            "type": "TOLL_DEDUCTION",
            "amount": amount,
            "balance_after": self.balance,
            "datetime": datetime.now().isoformat()
        })

        return self.balance

    def deactivate(self):
        self.status = "INACTIVE"

    def activate(self):
        self.status = "ACTIVE"

    def __str__(self):

        return (
            f"FASTag ID       : {self.fastag_id}\n"
            f"Vehicle Number  : {self.vehicle_number}\n"
            f"Balance         : ₹{self.balance:.2f}\n"
            f"Status          : {self.status}\n"
            f"Transactions    : "
            f"{len(self.transaction_history)}"
        )