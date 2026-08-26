class User:

    def __init__(
        self,
        user_id,
        username,
        password,
        full_name,
        role
    ):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"

        return (
            f"User ID     : {self.user_id}\n"
            f"Username    : {self.username}\n"
            f"Full Name   : {self.full_name}\n"
            f"Role        : {self.role}\n"
            f"Status      : {status}"
        )


class Admin(User):

    def __init__(
        self,
        user_id,
        username,
        password,
        full_name
    ):
        super().__init__(
            user_id,
            username,
            password,
            full_name,
            "Admin"
        )

    def get_permissions(self):
        return [
            "MANAGE_USERS",
            "MANAGE_BOOTHS",
            "MANAGE_TOLL_RATES",
            "VIEW_REPORTS",
            "VIEW_TRANSACTIONS",
            "MANAGE_SYSTEM"
        ]

class Manager(User):

    def __init__(
        self,
        user_id,
        username,
        password,
        full_name
    ):
        super().__init__(
            user_id,
            username,
            password,
            full_name,
            "Manager"
        )

    def get_permissions(self):
        return [
            "VIEW_REPORTS",
            "VIEW_TRANSACTIONS",
            "VIEW_BOOTH_STATUS",
            "VIEW_ANALYTICS"
        ]

class TollOperator(User):

    def __init__(
        self,
        user_id,
        username,
        password,
        full_name,
        booth_id
    ):
        super().__init__(
            user_id,
            username,
            password,
            full_name,
            "Toll Operator"
        )

        self.booth_id = booth_id

    def get_permissions(self):
        return [
            "REGISTER_VEHICLE",
            "PROCESS_PAYMENT",
            "CREATE_TRANSACTION",
            "VIEW_TRANSACTIONS"
        ]