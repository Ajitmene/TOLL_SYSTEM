import unittest

from tests.base_test import BaseTollTestCase
from services.auth_service import AuthService
from services.user_service import UserService
from utils.exceptions import (
    AccountInactiveError,
    AuthenticationError,
    AuthorizationError,
    DuplicateRecordError
)


class TestAuthAndUserService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.users = UserService()
        self.auth = AuthService()

        self.users.register_user(
            "admin", "admin123", "Site Admin", "Admin"
        )

    def test_login_success(self):
        user = self.auth.login("admin", "admin123")

        self.assertEqual(user["role"], "Admin")
        self.assertNotIn("password", user)

    def test_login_wrong_password_raises(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("admin", "wrongpass")

    def test_login_unknown_user_raises(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("ghost", "whatever")

    def test_duplicate_username_rejected(self):
        with self.assertRaises(DuplicateRecordError):
            self.users.register_user(
                "admin", "somepass", "Another Admin", "Admin"
            )

    def test_deactivated_account_cannot_login(self):
        admin_session = self.auth.login("admin", "admin123")
        self.users.deactivate_user(admin_session, "admin")
        self.auth.logout()

        with self.assertRaises(AccountInactiveError):
            self.auth.login("admin", "admin123")

    def test_require_role_blocks_wrong_role(self):
        self.users.register_user(
            "op1", "pass123", "Operator One", "Toll Operator",
            booth_id="B001"
        )

        operator_session = self.auth.login("op1", "pass123")

        with self.assertRaises(AuthorizationError):
            self.users.deactivate_user(operator_session, "admin")


if __name__ == "__main__":
    unittest.main()
