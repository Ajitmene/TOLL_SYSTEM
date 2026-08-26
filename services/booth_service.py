from repositories.toll_booth_repository import TollBoothRepository
from utils.exceptions import BoothNotFoundError, ValidationError


class BoothNetworkService:
    """Network-level operations across multiple toll booths/lanes.

    TollBoothService (services/toll_booth_service.py) owns CRUD and
    lifecycle for a single booth. This service sits one layer above
    it and answers questions that only make sense across the whole
    plaza network -- which lane a car should be routed to, how load
    is distributed, and reassigning operators between booths.
    """

    def __init__(self):
        self.repository = TollBoothRepository()

    def get_network_status(self):
        booths = self.repository.get_all()

        return {
            "total_booths": len(booths),
            "open_booths": len(
                [b for b in booths if b.get("status") == "OPEN"]
            ),
            "closed_booths": len(
                [b for b in booths if b.get("status") == "CLOSED"]
            ),
            "maintenance_booths": len(
                [b for b in booths if b.get("status") == "MAINTENANCE"]
            ),
        }

    def get_least_busy_open_booth(self):
        """Suggest the open booth with the fewest vehicles served so
        far -- a simple load-balancing recommendation for routing
        incoming traffic to the shortest lane."""

        open_booths = self.repository.get_open_booths()

        if not open_booths:
            raise BoothNotFoundError("No open booths available.")

        return min(open_booths, key=lambda b: b.get("vehicle_count", 0))

    def get_booths_by_location(self, location):
        return [
            booth for booth in self.repository.get_all()
            if location.lower() in booth.get("location", "").lower()
        ]

    def reassign_operator(self, booth_id, new_operator_id):
        booth = self.repository.find_by_booth_id(booth_id)

        if not booth:
            raise BoothNotFoundError(f"Booth {booth_id} not found.")

        if not new_operator_id:
            raise ValidationError("New operator id is required.")

        booth["operator_id"] = new_operator_id
        self.repository.update("booth_id", booth_id, booth)

        return booth

    def network_collection_total(self):
        return sum(
            booth.get("total_collection", 0)
            for booth in self.repository.get_all()
        )

    def rank_booths_by_collection(self):
        booths = self.repository.get_all()

        return sorted(
            booths,
            key=lambda b: b.get("total_collection", 0),
            reverse=True
        )
