from repositories.json_repository import JSONRepository


class ViolationRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/violations.json")

    def find_by_violation_id(self, violation_id):
        return self.find_by("violation_id", violation_id)

    def find_by_vehicle_number(self, vehicle_number):
        return self.find_all_by("vehicle_number", vehicle_number)

    def get_unpaid(self):
        return [
            item for item in self.get_all()
            if item.get("status") == "UNPAID"
        ]
