from models.fastag import FASTag
from repositories.fastag_repository import FASTagRepository
from utils.exceptions import (
    DuplicateRecordError,
    FASTagNotFoundError,
    InsufficientBalanceError
)
from utils.id_generator import generate_fastag_id


class FASTagService:

    def __init__(self):
        self.repository = FASTagRepository()

    def create_fastag(
        self,
        vehicle_number,
        initial_balance=0,
        fastag_id=None
    ):
        fastag_id = fastag_id or generate_fastag_id()

        if self.repository.fastag_exists(fastag_id):
            raise DuplicateRecordError(
                f"FASTag {fastag_id} already exists."
            )

        existing_vehicle = self.repository.find_by_vehicle_number(
            vehicle_number
        )

        if existing_vehicle:
            raise DuplicateRecordError(
                "This vehicle already has a FASTag."
            )

        fastag = FASTag(
            fastag_id=fastag_id,
            vehicle_number=vehicle_number,
            balance=initial_balance
        )

        self._save_fastag(fastag)

        return fastag

    def recharge(self, fastag_id, amount):
        fastag = self._require_fastag(fastag_id)

        new_balance = fastag.recharge(amount)

        self._save_fastag(fastag, update=True)

        return new_balance

    def deduct(self, fastag_id, amount):
        fastag = self._require_fastag(fastag_id)

        if fastag.balance < amount:
            raise InsufficientBalanceError(
                f"FASTag {fastag_id} has insufficient balance "
                f"({fastag.balance:.2f}) for a toll of {amount:.2f}."
            )

        new_balance = fastag.deduct(amount)

        self._save_fastag(fastag, update=True)

        return new_balance

    def deactivate(self, fastag_id):
        fastag = self._require_fastag(fastag_id)
        fastag.deactivate()
        self._save_fastag(fastag, update=True)

        return fastag

    def activate(self, fastag_id):
        fastag = self._require_fastag(fastag_id)
        fastag.activate()
        self._save_fastag(fastag, update=True)

        return fastag

    def get_fastag(self, fastag_id):
        data = self.repository.find_by_fastag_id(fastag_id)

        if not data:
            return None

        return self._from_dict(data)

    def get_all_fastags(self):
        return self.repository.get_all()

    def _require_fastag(self, fastag_id):
        data = self.repository.find_by_fastag_id(fastag_id)

        if not data:
            raise FASTagNotFoundError(f"FASTag {fastag_id} not found.")

        return self._from_dict(data)

    def _save_fastag(self, fastag, update=False):
        data = {
            "fastag_id": fastag.fastag_id,
            "vehicle_number": fastag.vehicle_number,
            "balance": fastag.balance,
            "status": fastag.status,
            "transaction_history": fastag.transaction_history
        }

        if update:
            self.repository.update(
                "fastag_id", fastag.fastag_id, data
            )
        else:
            self.repository.add(data)

    @staticmethod
    def _from_dict(data):
        fastag = FASTag(
            fastag_id=data["fastag_id"],
            vehicle_number=data["vehicle_number"],
            balance=data["balance"],
            status=data["status"]
        )

        fastag.transaction_history = data.get(
            "transaction_history", []
        )

        return fastag
