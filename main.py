"""
Smart Toll Booth Collection & Traffic Management System
---------------------------------------------------------
Command-line entry point. Run with:  python main.py

Wires together every phase of the project: auth/roles, vehicle
management, the toll engine, payments/FASTag, prepaid passes,
violations, multi-booth operations, and reports/analytics.
"""

from config.settings import PAYMENT_METHODS, PROJECT_NAME
from reports.daily_report import generate_daily_report
from reports.report_generator import (
    booth_report,
    export_summary_json,
    export_transactions_csv,
    vehicle_report
)
from services.auth_service import AuthService
from services.booth_service import BoothNetworkService
from services.fastag_service import FASTagService
from services.pass_service import PassService
from services.toll_booth_service import TollBoothService
from services.toll_crossing_service import TollCrossingService
from services.user_service import UserService
from services.vehicle_service import VehicleService
from services.violation_service import ViolationService
from utils.exceptions import TollSystemError
from utils.helpers import (
    format_currency,
    print_divider,
    print_header,
    print_table
)
from utils.logger import get_logger

logger = get_logger("cli")

auth_service = AuthService()
user_service = UserService()
vehicle_service = VehicleService()
booth_service = TollBoothService()
booth_network_service = BoothNetworkService()
fastag_service = FASTagService()
pass_service = PassService()
violation_service = ViolationService()
crossing_service = TollCrossingService()


# ---------------------------------------------------------------
# small input helpers
# ---------------------------------------------------------------

def ask(prompt, default=None):
    value = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return value or default


def ask_float(prompt, default=None):
    raw = ask(prompt, default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        print("Please enter a valid number.")
        return ask_float(prompt, default)


def ask_menu(title, options):
    """options: list of (key, label). Returns the chosen key."""

    print_header(title)

    for key, label in options:
        print(f"  {key}. {label}")

    print_divider()

    return ask("Choose an option")


def pause():
    input("\nPress Enter to continue...")


# ---------------------------------------------------------------
# auth
# ---------------------------------------------------------------

def login_screen():
    print_header(PROJECT_NAME)

    while True:
        username = ask("Username")
        password = ask("Password")

        try:
            user = auth_service.login(username, password)
            print(f"\nWelcome, {user['full_name']} ({user['role']})!")
            return user

        except TollSystemError as exc:
            print(f"\nLogin failed: {exc}\n")

            if ask("Try again? (y/n)", "y").lower() != "y":
                return None


def seed_admin_if_needed():
    if not user_service.get_all_users():
        user_service.register_user(
            username="admin",
            password="admin123",
            full_name="System Administrator",
            role="Admin"
        )

        logger.info("Bootstrapped default admin/admin123 account.")


# ---------------------------------------------------------------
# vehicle management (phase 5)
# ---------------------------------------------------------------

def menu_register_vehicle():
    print_header("Register Vehicle")

    try:
        vehicle = vehicle_service.register_vehicle(
            vehicle_number=ask("Vehicle Number (e.g. MH12AB1234)"),
            vehicle_type=ask(
                "Vehicle Type (Bike/Car/SUV/LCV/Bus/Truck/Multi-Axle)"
            ),
            owner_name=ask("Owner Name"),
            owner_phone=ask("Owner Phone"),
            vehicle_model=ask("Vehicle Model"),
            fuel_type=ask("Fuel Type"),
            registration_state=ask("Registration State")
        )

        print("\nVehicle registered successfully!\n")
        print(vehicle)

    except TollSystemError as exc:
        print(f"\nError: {exc}")


def menu_view_vehicles():
    print_header("All Registered Vehicles")

    rows = vehicle_service.get_all_vehicles()

    print_table(
        rows,
        ["vehicle_number", "vehicle_type", "owner_name", "fastag_id"]
    )


def menu_vehicle_lookup():
    vehicle_number = ask("Enter vehicle number")
    vehicle = vehicle_service.get_vehicle(vehicle_number)

    if not vehicle:
        print("Vehicle not found.")
        return

    print_header(f"Vehicle: {vehicle_number}")

    for key, value in vehicle.items():
        print(f"{key:<20}: {value}")


# ---------------------------------------------------------------
# FASTag (phase 7)
# ---------------------------------------------------------------

def menu_create_fastag():
    print_header("Issue FASTag")

    try:
        vehicle_number = ask("Vehicle Number")
        initial_balance = ask_float("Initial recharge amount", "0")

        fastag = fastag_service.create_fastag(
            vehicle_number, initial_balance
        )

        vehicle_service.assign_fastag(vehicle_number, fastag.fastag_id)

        print(f"\nFASTag issued: {fastag.fastag_id}\n")
        print(fastag)

    except TollSystemError as exc:
        print(f"\nError: {exc}")


def menu_recharge_fastag():
    try:
        fastag_id = ask("FASTag ID")
        amount = ask_float("Recharge amount")

        new_balance = fastag_service.recharge(fastag_id, amount)

        print(f"\nRecharge successful. New balance: "
              f"{format_currency(new_balance)}")

    except TollSystemError as exc:
        print(f"\nError: {exc}")


# ---------------------------------------------------------------
# passes (phase 8)
# ---------------------------------------------------------------

def menu_issue_pass():
    print_header("Issue Toll Pass")

    pass_type = ask("Pass type (MONTHLY/TRIP)", "MONTHLY").upper()
    vehicle_number = ask("Vehicle Number")

    try:
        if pass_type == "MONTHLY":
            days = int(ask_float("Validity (days)", "30"))
            toll_pass = pass_service.issue_monthly_pass(
                vehicle_number, days
            )
        else:
            trips = int(ask_float("Number of trips", "10"))
            toll_pass = pass_service.issue_trip_pass(
                vehicle_number, trips
            )

        print(f"\nPass issued: {toll_pass.pass_id}\n")
        print(toll_pass)

    except TollSystemError as exc:
        print(f"\nError: {exc}")


# ---------------------------------------------------------------
# crossings (phase 6/7/8 combined)
# ---------------------------------------------------------------

def menu_process_crossing(current_user):
    print_header("Process Vehicle Crossing")

    vehicle_number = ask("Vehicle Number")
    booth_id = ask("Booth ID")

    print(f"Payment methods: {', '.join(PAYMENT_METHODS + ['Pass'])}")
    payment_method = ask("Payment Method", "Cash")

    extra = {}

    if payment_method == "UPI":
        extra["upi_id"] = ask("UPI ID")
    elif payment_method == "Card":
        extra["card_last_four"] = ask("Card last 4 digits")

    try:
        result = crossing_service.process_vehicle_crossing(
            vehicle_number=vehicle_number,
            booth_id=booth_id,
            operator_id=current_user.get(
                "booth_id", current_user["user_id"]
            ),
            payment_method=payment_method,
            **extra
        )

        print("\nCrossing processed successfully!")
        print(f"Transaction ID : {result['transaction'].transaction_id}")
        print(
            f"Amount Charged : "
            f"{format_currency(result['toll']['final_amount'])}"
        )

    except TollSystemError as exc:
        print(f"\nCrossing failed: {exc}")


# ---------------------------------------------------------------
# booths (phase 10)
# ---------------------------------------------------------------

def menu_create_booth():
    print_header("Create Toll Booth")

    try:
        booth = booth_service.create_booth(
            booth_name=ask("Booth Name"),
            location=ask("Location"),
            lane_number=ask("Lane Number"),
            operator_id=ask("Operator ID (optional)", "")
        )

        print(f"\nBooth created: {booth.booth_id}\n")
        print(booth)

    except TollSystemError as exc:
        print(f"\nError: {exc}")


def menu_booth_status():
    print_header("Booth Network Status")

    status = booth_network_service.get_network_status()

    for key, value in status.items():
        print(f"{key:<20}: {value}")

    print("\nAll Booths")
    print_table(
        booth_service.get_all_booths(),
        ["booth_id", "booth_name", "location", "status",
         "vehicle_count", "total_collection"]
    )


# ---------------------------------------------------------------
# violations (phase 9)
# ---------------------------------------------------------------

def menu_view_violations():
    print_header("Unpaid Violations")

    rows = violation_service.get_unpaid_violations()

    print_table(
        rows,
        ["violation_id", "vehicle_number", "booth_id",
         "violation_type", "fine_amount"]
    )

    print(
        f"\nTotal outstanding fines: "
        f"{format_currency(violation_service.total_outstanding_fines())}"
    )


def menu_pay_violation():
    violation_id = ask("Violation ID")

    try:
        violation_service.pay_fine(violation_id)
        print("\nFine paid successfully.")

    except TollSystemError as exc:
        print(f"\nError: {exc}")


# ---------------------------------------------------------------
# reports (phase 11)
# ---------------------------------------------------------------

def menu_reports():
    while True:
        choice = ask_menu("Reports & Analytics", [
            ("1", "Daily summary report (console)"),
            ("2", "Export summary as JSON"),
            ("3", "Export all transactions as CSV"),
            ("4", "Vehicle history report"),
            ("5", "Booth report"),
            ("0", "Back")
        ])

        if choice == "1":
            generate_daily_report()
        elif choice == "2":
            path = export_summary_json()
            print(f"\nExported to {path}")
        elif choice == "3":
            path = export_transactions_csv()
            print(f"\nExported to {path}")
        elif choice == "4":
            report = vehicle_report(ask("Vehicle Number"))
            print(f"\nCrossings: {report['total_crossings']}")
            print(f"Total Spent: {format_currency(report['total_spent'])}")
        elif choice == "5":
            report = booth_report(ask("Booth ID"))
            print(f"\nCrossings: {report['total_crossings']}")
            print(
                f"Total Collected: "
                f"{format_currency(report['total_collected'])}"
            )
        elif choice == "0":
            return
        else:
            print("Invalid option.")

        pause()


# ---------------------------------------------------------------
# role-based menus
# ---------------------------------------------------------------

def admin_menu(current_user):
    while True:
        choice = ask_menu(f"Admin Menu - {current_user['full_name']}", [
            ("1", "Register vehicle"),
            ("2", "View all vehicles"),
            ("3", "Vehicle lookup"),
            ("4", "Issue FASTag"),
            ("5", "Recharge FASTag"),
            ("6", "Issue toll pass"),
            ("7", "Create toll booth"),
            ("8", "Booth network status"),
            ("9", "Process a vehicle crossing"),
            ("10", "View unpaid violations"),
            ("11", "Pay a violation fine"),
            ("12", "Reports & analytics"),
            ("13", "Register new system user"),
            ("0", "Logout")
        ])

        actions = {
            "1": menu_register_vehicle,
            "2": menu_view_vehicles,
            "3": menu_vehicle_lookup,
            "4": menu_create_fastag,
            "5": menu_recharge_fastag,
            "6": menu_issue_pass,
            "7": menu_create_booth,
            "8": menu_booth_status,
            "10": menu_view_violations,
            "11": menu_pay_violation,
        }

        if choice in actions:
            actions[choice]()
            pause()
        elif choice == "9":
            menu_process_crossing(current_user)
            pause()
        elif choice == "12":
            menu_reports()
        elif choice == "13":
            menu_register_user()
            pause()
        elif choice == "0":
            return
        else:
            print("Invalid option.")
            pause()


def menu_register_user():
    print_header("Register System User")

    try:
        role = ask("Role (Admin/Manager/Toll Operator)", "Toll Operator")
        booth_id = ask("Booth ID (Toll Operator only)", "") or None

        user_service.register_user(
            username=ask("Username"),
            password=ask("Password"),
            full_name=ask("Full Name"),
            role=role,
            booth_id=booth_id
        )

        print("\nUser registered successfully.")

    except TollSystemError as exc:
        print(f"\nError: {exc}")


def manager_menu(current_user):
    while True:
        choice = ask_menu(f"Manager Menu - {current_user['full_name']}", [
            ("1", "View all vehicles"),
            ("2", "Booth network status"),
            ("3", "View unpaid violations"),
            ("4", "Reports & analytics"),
            ("0", "Logout")
        ])

        if choice == "1":
            menu_view_vehicles()
            pause()
        elif choice == "2":
            menu_booth_status()
            pause()
        elif choice == "3":
            menu_view_violations()
            pause()
        elif choice == "4":
            menu_reports()
        elif choice == "0":
            return
        else:
            print("Invalid option.")
            pause()


def operator_menu(current_user):
    while True:
        choice = ask_menu(
            f"Toll Operator Menu - {current_user['full_name']}", [
                ("1", "Register vehicle"),
                ("2", "Process a vehicle crossing"),
                ("3", "Vehicle lookup"),
                ("0", "Logout")
            ]
        )

        if choice == "1":
            menu_register_vehicle()
            pause()
        elif choice == "2":
            menu_process_crossing(current_user)
            pause()
        elif choice == "3":
            menu_vehicle_lookup()
            pause()
        elif choice == "0":
            return
        else:
            print("Invalid option.")
            pause()


ROLE_MENUS = {
    "Admin": admin_menu,
    "Manager": manager_menu,
    "Toll Operator": operator_menu
}


# ---------------------------------------------------------------
# entry point
# ---------------------------------------------------------------

def main():
    seed_admin_if_needed()

    while True:
        current_user = login_screen()

        if current_user is None:
            print("\nGoodbye!")
            break

        menu = ROLE_MENUS.get(current_user["role"])

        if menu:
            menu(current_user)
        else:
            print("No menu configured for this role.")

        auth_service.logout()

        if ask("\nLog in as another user? (y/n)", "n").lower() != "y":
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
