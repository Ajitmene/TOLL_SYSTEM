from repositories.user_repository import UserRepository
from utils.exceptions import AccountInactiveError, AuthenticationError
from utils.logger import get_logger
from utils.security import verify_password

logger = get_logger("auth")


class AuthService:
    """Handles login/logout and holds the currently authenticated
    user for the running CLI session.

    `login()` returns a plain dict (not a model instance) because
    that's the shape every service's `@require_role` decorator
    expects as the `current_user` argument -- it can be handed
    straight through to any role-protected method.
    """

    def __init__(self):
        self.repository = UserRepository()
        self.current_user = None

    def login(self, username, password):
        data = self.repository.find_by_username(username)

        if not data or not verify_password(password, data["password"]):
            logger.warning("Failed login attempt for '%s'", username)
            raise AuthenticationError("Invalid username or password.")

        if not data.get("is_active", True):
            raise AccountInactiveError(
                f"Account '{username}' has been deactivated."
            )

        # Never keep the password hash around in memory longer than
        # necessary once identity is confirmed.
        session_user = {
            k: v for k, v in data.items() if k != "password"
        }

        self.current_user = session_user

        logger.info(
            "User '%s' (role=%s) logged in.",
            username, data.get("role")
        )

        return session_user

    def logout(self):
        if self.current_user:
            logger.info(
                "User '%s' logged out.", self.current_user["username"]
            )

        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def has_role(self, *roles):
        return bool(self.current_user) and (
            self.current_user.get("role") in roles
        )

    def require_login(self):
        if not self.is_authenticated():
            raise AuthenticationError("You must log in first.")

        return self.current_user
