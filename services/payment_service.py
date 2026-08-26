from models.payment import (
    CashPayment,
    UPIPayment,
    CardPayment,
    FASTagPayment
)


class PaymentService:

    def process_payment(
        self,
        payment_method,
        amount,
        **kwargs
    ):

        payment = self._create_payment_method(
            payment_method,
            amount,
            **kwargs
        )

        success = payment.process_payment()

        return {
            "success": success,
            "method": payment_method,
            "details": payment.get_payment_details()
        }

    def _create_payment_method(
        self,
        payment_method,
        amount,
        **kwargs
    ):

        if payment_method == "Cash":

            return CashPayment(amount)

        elif payment_method == "UPI":

            return UPIPayment(
                amount,
                kwargs.get("upi_id")
            )

        elif payment_method == "Card":

            return CardPayment(
                amount,
                kwargs.get("card_last_four")
            )

        elif payment_method == "FASTag":

            return FASTagPayment(
                amount,
                kwargs.get("fastag_id"),
                kwargs.get("balance", 0)
            )

        else:

            raise ValueError(
                f"Unsupported payment method: "
                f"{payment_method}"
            )