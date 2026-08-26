from repositories.json_repository import JSONRepository


class TransactionRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/transactions.json")

    def find_by_transaction_id(self, transaction_id):

        return self.find_by(
            "transaction_id",
            transaction_id
        )

    def find_by_vehicle_number(self, vehicle_number):

        transactions = self.get_all()

        return [
            transaction
            for transaction in transactions
            if transaction.get("vehicle_number")
            == vehicle_number
        ]

    def get_by_booth(self, booth_id):

        transactions = self.get_all()

        return [
            transaction
            for transaction in transactions
            if transaction.get("booth_id")
            == booth_id
        ]