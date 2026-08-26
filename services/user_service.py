from models.user import Admin, Manager, TollOperator, User
from repositories.user_repository import UserRepository
from utils.decorators import require_role
from utils.exceptions import (
    DuplicateRecordError,
    RecordNotFoundError,
    ValidationError
)
from utils.id_generator import generate_user_id
from utils.security import hash_password
from utils.validators import validate_non_empty


class UserService:
    """CRUD operations for system users (Admin/Manager/TollOperator).

    Password hashing and the actual login flow live in
    AuthService; this service is about managing accounts once you
    are already authorized to do so.
    """

    ROLE_CLASSES = {
        "Admin": Admin,
        "Manager": Manager,
        "Toll Operator": TollOperator
    }

    def __init__(self):
        self.repository = UserRepository()

    def _build_user(
        self, user_id, username, password, full_name, role, booth_id=None
    ):
        if role == "Toll Operator":
            return TollOperator(
                user_id, username, password, full_name, booth_id
            )

        role_class = self.ROLE_CLASSES.get(role, User)

        if role_class is User:
            return User(user_id, username, password, full_name, role)

        return role_class(user_id, username, password, full_name)

    def register_user(
        self, username, password, full_name, role, booth_id=None
    ):
        validate_non_empty(username, "Username")
        validate_non_empty(password, "Password")
        validate_non_empty(full_name, "Full name")

        if role not in ("Admin", "Manager", "Toll Operator"):
            raise ValidationError(f"Unsupported role: {role}")

        if self.repository.username_exists(username):
            raise DuplicateRecordError(
                f"Username '{username}' is already taken."
            )

        user_id = generate_user_id()
        hashed = hash_password(password)

        user = self._build_user(
            user_id, username, hashed, full_name, role, booth_id
        )

        data = {
            "user_id": user.user_id,
            "username": user.username,
            "password": user.password,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "booth_id": booth_id if role == "Toll Operator" else None
        }

        self.repository.add(data)

        return user

    def get_user_by_username(self, username):
        return self.repository.find_by_username(username)

    def get_all_users(self):
        return self.repository.get_all()

    @require_role("Admin")
    def deactivate_user(self, current_user, username):
        data = self.repository.find_by_username(username)

        if not data:
            raise RecordNotFoundError(f"User '{username}' not found.")

        data["is_active"] = False
        self.repository.update("username", username, data)

    @require_role("Admin")
    def activate_user(self, current_user, username):
        data = self.repository.find_by_username(username)

        if not data:
            raise RecordNotFoundError(f"User '{username}' not found.")

        data["is_active"] = True
        self.repository.update("username", username, data)

    @require_role("Admin")
    def list_users_by_role(self, current_user, role):
        return self.repository.get_by_role(role)
