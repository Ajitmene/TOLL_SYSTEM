from repositories.json_repository import JSONRepository


class UserRepository(JSONRepository):

    def __init__(self):
        super().__init__("data/users.json")

    def find_by_username(self, username):
        return self.find_by("username", username)

    def find_by_user_id(self, user_id):
        return self.find_by("user_id", user_id)

    def username_exists(self, username):
        return self.find_by_username(username) is not None

    def get_by_role(self, role):
        return self.find_all_by("role", role)
