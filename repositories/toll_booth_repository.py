from repositories.json_repository import JSONRepository


class TollBoothRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/toll_booths.json")

    def find_by_booth_id(self, booth_id):

        return self.find_by(
            "booth_id",
            booth_id
        )

    def booth_exists(self, booth_id):

        return (
            self.find_by_booth_id(booth_id)
            is not None
        )

    def get_open_booths(self):

        booths = self.get_all()

        return [
            booth
            for booth in booths
            if booth.get("status") == "OPEN"
        ]