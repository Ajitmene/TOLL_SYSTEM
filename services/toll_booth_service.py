from models.toll_booth import TollBooth
from repositories.toll_booth_repository import TollBoothRepository
from utils.exceptions import BoothNotFoundError, DuplicateRecordError
from utils.id_generator import generate_booth_id


class TollBoothService:

    def __init__(self):
        self.repository = TollBoothRepository()

    def create_booth(
        self,
        booth_name,
        location,
        lane_number,
        operator_id=None,
        booth_id=None
    ):
        booth_id = booth_id or generate_booth_id()

        if self.repository.booth_exists(booth_id):
            raise DuplicateRecordError(
                f"Booth {booth_id} already exists."
            )

        booth = TollBooth(
            booth_id=booth_id,
            booth_name=booth_name,
            location=location,
            lane_number=lane_number,
            operator_id=operator_id
        )

        self.repository.add(booth.to_dict())

        return booth

    def get_booth(self, booth_id):
        data = self.repository.find_by_booth_id(booth_id)

        if not data:
            return None

        return self._from_dict(data)

    def get_all_booths(self):
        return self.repository.get_all()

    def get_open_booths(self):
        return self.repository.get_open_booths()

    def record_transaction(self, booth_id, transaction_id, amount):
        booth = self._require_booth(booth_id)

        booth.record_transaction(transaction_id, amount)

        self._update_booth(booth)

        return booth

    def close_booth(self, booth_id):
        booth = self._require_booth(booth_id)
        booth.close_booth()
        self._update_booth(booth)

        return booth

    def open_booth(self, booth_id):
        booth = self._require_booth(booth_id)
        booth.open_booth()
        self._update_booth(booth)

        return booth

    def mark_maintenance(self, booth_id):
        booth = self._require_booth(booth_id)
        booth.mark_maintenance()
        self._update_booth(booth)

        return booth

    def _require_booth(self, booth_id):
        booth = self.get_booth(booth_id)

        if not booth:
            raise BoothNotFoundError(f"Booth {booth_id} not found.")

        return booth

    def _update_booth(self, booth):
        self.repository.update(
            "booth_id", booth.booth_id, booth.to_dict()
        )

    @staticmethod
    def _from_dict(data):
        booth = TollBooth(
            booth_id=data["booth_id"],
            booth_name=data["booth_name"],
            location=data["location"],
            lane_number=data["lane_number"],
            operator_id=data.get("operator_id"),
            status=data.get("status", "OPEN")
        )

        booth.vehicle_count = data.get("vehicle_count", 0)
        booth.total_collection = data.get("total_collection", 0)
        booth.last_transaction_id = data.get("last_transaction_id")

        return booth
