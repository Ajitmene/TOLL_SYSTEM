from abc import ABC, abstractmethod


class PaymentMethod(ABC):

    def __init__(self, amount):
        self.amount = amount
        self.status = "PENDING"
        self.transaction_reference = None

    @abstractmethod
    def process_payment(self):
        pass

    def get_payment_details(self):
        return {
            "amount": self.amount,
            "status": self.status,
            "transaction_reference": self.transaction_reference
        }


class CashPayment(PaymentMethod):

    def process_payment(self):
        self.status = "SUCCESS"
        self.transaction_reference = "CASH"

        return True


class UPIPayment(PaymentMethod):

    def __init__(self, amount, upi_id):
        super().__init__(amount)
        self.upi_id = upi_id

    def process_payment(self):

        if not self.upi_id:
            self.status = "FAILED"
            return False

        self.status = "SUCCESS"
        self.transaction_reference = (
            f"UPI-{self.upi_id}"
        )

        return True


class CardPayment(PaymentMethod):

    def __init__(self, amount, card_last_four):
        super().__init__(amount)
        self.card_last_four = card_last_four

    def process_payment(self):

        if len(str(self.card_last_four)) != 4:
            self.status = "FAILED"
            return False

        self.status = "SUCCESS"

        self.transaction_reference = (
            f"CARD-XXXX{self.card_last_four}"
        )

        return True


class FASTagPayment(PaymentMethod):

    def __init__(self, amount, fastag_id, balance):
        super().__init__(amount)

        self.fastag_id = fastag_id
        self.balance = balance

    def process_payment(self):

        if self.balance < self.amount:
            self.status = "FAILED"

            return False

        self.balance -= self.amount

        self.status = "SUCCESS"

        self.transaction_reference = (
            f"FASTAG-{self.fastag_id}"
        )

        return True