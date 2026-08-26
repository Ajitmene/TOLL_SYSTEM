from models.transaction import Transaction
from repositories.transaction_repository import (
    TransactionRepository
)


class TransactionService:

    def __init__(self):

        self.repository = TransactionRepository()

    def create_transaction(
        self,
        transaction_id,
        vehicle_number,
        vehicle_type,
        booth_id,
        operator_id,
        base_toll,
        peak_charge,
        discount,
        payment_method,
        status="SUCCESS"
    ):

        existing = (
            self.repository.find_by_transaction_id(
                transaction_id
            )
        )

        if existing:

            raise ValueError(
                f"Transaction {transaction_id} "
                "already exists."
            )

        transaction = Transaction(
            transaction_id=transaction_id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            booth_id=booth_id,
            operator_id=operator_id,
            base_toll=base_toll,
            peak_charge=peak_charge,
            discount=discount,
            payment_method=payment_method,
            status=status
        )

        self.repository.add(
            transaction.to_dict()
        )

        return transaction

    def get_transaction(self, transaction_id):

        return self.repository.find_by_transaction_id(
            transaction_id
        )

    def get_vehicle_transactions(
        self,
        vehicle_number
    ):

        return self.repository.find_by_vehicle_number(
            vehicle_number
        )

    def get_booth_transactions(self, booth_id):

        return self.repository.get_by_booth(
            booth_id
        )