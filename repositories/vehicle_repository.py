from repositories.json_repository import JSONRepository


class VehicleRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/vehicles.json")

    def find_by_vehicle_number(self, vehicle_number):
        return self.find_by(
            "vehicle_number",
            vehicle_number
        )

    def vehicle_exists(self, vehicle_number):
        return (
            self.find_by_vehicle_number(vehicle_number)
            is not None
        )