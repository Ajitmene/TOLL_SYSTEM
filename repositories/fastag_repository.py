from repositories.json_repository import JSONRepository


class FASTagRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/fastags.json")

    def find_by_fastag_id(self, fastag_id):

        return self.find_by(
            "fastag_id",
            fastag_id
        )

    def find_by_vehicle_number(self, vehicle_number):

        return self.find_by(
            "vehicle_number",
            vehicle_number
        )

    def fastag_exists(self, fastag_id):

        return (
            self.find_by_fastag_id(fastag_id)
            is not None
        )