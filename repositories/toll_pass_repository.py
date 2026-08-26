from repositories.json_repository import JSONRepository


class TollPassRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/passes.json")

    def find_by_pass_id(self, pass_id):
        return self.find_by("pass_id", pass_id)

    def find_by_vehicle_number(self, vehicle_number):
        return self.find_all_by("vehicle_number", vehicle_number)

    def pass_exists(self, pass_id):
        return self.find_by_pass_id(pass_id) is not None

    def get_active_passes(self):
        return [
            item for item in self.get_all()
            if item.get("status") == "ACTIVE"
        ]
