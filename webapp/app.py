"""
Smart Toll Plaza — web console
-------------------------------
A Flask front end over the existing services/ layer. No business
logic lives here: every route is a thin adapter that collects form
input, calls the same service classes the CLI (main.py) uses, and
renders the result. Run with:

    python webapp/app.py

then open http://127.0.0.1:5000
"""

import os
import sys
from datetime import datetime
from functools import wraps

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for
)

# Make the project root importable regardless of the working
# directory this script is launched from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from services.auth_service import AuthService                 # noqa: E402
from services.booth_service import BoothNetworkService         # noqa: E402
from services.fastag_service import FASTagService              # noqa: E402
from services.pass_service import PassService                  # noqa: E402
from services.report_service import ReportService               # noqa: E402
from services.toll_booth_service import TollBoothService       # noqa: E402
from services.toll_crossing_service import TollCrossingService  # noqa: E402
from services.user_service import UserService                  # noqa: E402
from services.vehicle_service import VehicleService             # noqa: E402
from services.violation_service import ViolationService         # noqa: E402
from reports.report_generator import (                          # noqa: E402
    export_summary_json, export_transactions_csv
)
from config.settings import PAYMENT_METHODS, PROJECT_NAME       # noqa: E402
from utils.exceptions import TollSystemError                    # noqa: E402

app = Flask(__name__)
app.secret_key = os.environ.get("TOLL_SECRET_KEY", "dev-secret-change-me")

auth_service = AuthService()
user_service = UserService()
vehicle_service = VehicleService()
booth_service = TollBoothService()
booth_network_service = BoothNetworkService()
fastag_service = FASTagService()
pass_service = PassService()
violation_service = ViolationService()
report_service = ReportService()
crossing_service = TollCrossingService()


def seed_admin_if_needed():
    if not user_service.get_all_users():
        user_service.register_user(
            username="admin",
            password="admin123",
            full_name="System Administrator",
            role="Admin"
        )


# ---------------------------------------------------------------
# auth helpers
# ---------------------------------------------------------------

def current_user():
    return session.get("user")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if user["role"] not in roles:
                flash(
                    f"Your role ({user['role']}) doesn't have access "
                    "to that page.", "error"
                )
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.context_processor
def inject_globals():
    return {
        "current_user": current_user(),
        "project_name": PROJECT_NAME,
        "now": datetime.now()
    }


# ---------------------------------------------------------------
# auth routes
# ---------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = auth_service.login(username, password)
            session["user"] = user
            flash(f"Welcome back, {user['full_name']}.", "success")
            return redirect(url_for("dashboard"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    auth_service.logout()
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# dashboard
# ---------------------------------------------------------------

@app.route("/")
@login_required
def dashboard():
    summary = report_service.summary()
    network = booth_network_service.get_network_status()
    recent_transactions = list(
        reversed(report_service.get_all_transactions())
    )[:8]
    open_violations = violation_service.get_unpaid_violations()[:6]

    return render_template(
        "dashboard.html",
        summary=summary,
        network=network,
        recent_transactions=recent_transactions,
        open_violations=open_violations
    )


# ---------------------------------------------------------------
# vehicles
# ---------------------------------------------------------------

@app.route("/vehicles")
@login_required
def vehicles():
    q = request.args.get("q", "").strip().upper()
    all_vehicles = vehicle_service.get_all_vehicles()

    if q:
        all_vehicles = [
            v for v in all_vehicles
            if q in v.get("vehicle_number", "").upper()
            or q in v.get("owner_name", "").upper()
        ]

    return render_template("vehicles.html", vehicles=all_vehicles, q=q)


@app.route("/vehicles/register", methods=["GET", "POST"])
@login_required
def vehicle_register():
    if request.method == "POST":
        try:
            vehicle = vehicle_service.register_vehicle(
                vehicle_number=request.form.get("vehicle_number", ""),
                vehicle_type=request.form.get("vehicle_type"),
                owner_name=request.form.get("owner_name", ""),
                owner_phone=request.form.get("owner_phone", ""),
                vehicle_model=request.form.get("vehicle_model", ""),
                fuel_type=request.form.get("fuel_type"),
                registration_state=request.form.get(
                    "registration_state", ""
                )
            )
            flash(
                f"Vehicle {vehicle.vehicle_number} registered "
                "successfully.", "success"
            )
            return redirect(url_for("vehicles"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    return render_template("vehicle_form.html")


@app.route("/vehicles/<vehicle_number>")
@login_required
def vehicle_detail(vehicle_number):
    vehicle = vehicle_service.get_vehicle(vehicle_number)

    if not vehicle:
        flash(f"Vehicle {vehicle_number} not found.", "error")
        return redirect(url_for("vehicles"))

    transactions = report_service.transaction_repository.\
        find_by_vehicle_number(vehicle_number)
    passes = pass_service.get_passes_for_vehicle(vehicle_number)
    vehicle_violations = violation_service.get_vehicle_violations(
        vehicle_number
    )
    fastag = None
    if vehicle.get("fastag_id"):
        fastag = fastag_service.get_fastag(vehicle["fastag_id"])

    total_spent = sum(
        t.get("final_amount", 0) for t in transactions
        if t.get("status") == "SUCCESS"
    )

    return render_template(
        "vehicle_detail.html",
        vehicle=vehicle,
        transactions=list(reversed(transactions)),
        passes=passes,
        violations=vehicle_violations,
        fastag=fastag,
        total_spent=total_spent
    )


# ---------------------------------------------------------------
# booths
# ---------------------------------------------------------------

@app.route("/booths")
@login_required
def booths():
    all_booths = booth_service.get_all_booths()
    network = booth_network_service.get_network_status()
    return render_template("booths.html", booths=all_booths, network=network)


@app.route("/booths/create", methods=["GET", "POST"])
@roles_required("Admin")
def booth_create():
    if request.method == "POST":
        try:
            booth = booth_service.create_booth(
                booth_name=request.form.get("booth_name", ""),
                location=request.form.get("location", ""),
                lane_number=request.form.get("lane_number", ""),
                operator_id=request.form.get("operator_id") or None
            )
            flash(f"Booth {booth.booth_id} created.", "success")
            return redirect(url_for("booths"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    return render_template("booth_form.html")


@app.route("/booths/<booth_id>/status/<action>", methods=["POST"])
@roles_required("Admin", "Manager")
def booth_status_change(booth_id, action):
    try:
        if action == "open":
            booth_service.open_booth(booth_id)
        elif action == "close":
            booth_service.close_booth(booth_id)
        elif action == "maintenance":
            booth_service.mark_maintenance(booth_id)
        flash(f"Booth {booth_id} updated to {action.upper()}.", "success")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("booths"))


# ---------------------------------------------------------------
# crossing (the core operational screen)
# ---------------------------------------------------------------

@app.route("/crossing", methods=["GET", "POST"])
@login_required
def crossing():
    result = None
    user = current_user()

    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number", "")
        booth_id = request.form.get("booth_id", "")
        payment_method = request.form.get("payment_method", "Cash")

        extra = {}
        if payment_method == "UPI":
            extra["upi_id"] = request.form.get("upi_id", "")
        elif payment_method == "Card":
            extra["card_last_four"] = request.form.get(
                "card_last_four", ""
            )

        try:
            result = crossing_service.process_vehicle_crossing(
                vehicle_number=vehicle_number,
                booth_id=booth_id,
                operator_id=user.get("booth_id") or user["user_id"],
                payment_method=payment_method,
                **extra
            )
            flash(
                f"Crossing processed — "
                f"₹{result['toll']['final_amount']:.2f} charged via "
                f"{payment_method}.", "success"
            )
        except TollSystemError as exc:
            flash(str(exc), "error")

    all_booths = booth_service.get_open_booths()

    return render_template(
        "crossing.html",
        result=result,
        booths=all_booths,
        payment_methods=PAYMENT_METHODS + ["Pass"]
    )


# ---------------------------------------------------------------
# fastags
# ---------------------------------------------------------------

@app.route("/fastags")
@login_required
def fastags():
    all_tags = fastag_service.get_all_fastags()
    return render_template("fastags.html", fastags=all_tags)


@app.route("/fastags/create", methods=["GET", "POST"])
@login_required
def fastag_create():
    if request.method == "POST":
        try:
            vehicle_number = request.form.get("vehicle_number", "")
            initial_balance = float(
                request.form.get("initial_balance", 0) or 0
            )

            tag = fastag_service.create_fastag(
                vehicle_number, initial_balance
            )
            vehicle_service.assign_fastag(vehicle_number, tag.fastag_id)

            flash(f"FASTag {tag.fastag_id} issued.", "success")
            return redirect(url_for("fastags"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    return render_template("fastag_form.html")


@app.route("/fastags/<fastag_id>/recharge", methods=["POST"])
@login_required
def fastag_recharge(fastag_id):
    try:
        amount = float(request.form.get("amount", 0) or 0)
        new_balance = fastag_service.recharge(fastag_id, amount)
        flash(
            f"FASTag {fastag_id} recharged. New balance: "
            f"₹{new_balance:.2f}", "success"
        )
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("fastags"))


@app.route("/fastags/<fastag_id>/toggle", methods=["POST"])
@roles_required("Admin")
def fastag_toggle(fastag_id):
    try:
        tag = fastag_service.get_fastag(fastag_id)
        if tag.status == "ACTIVE":
            fastag_service.deactivate(fastag_id)
            flash(f"FASTag {fastag_id} deactivated.", "info")
        else:
            fastag_service.activate(fastag_id)
            flash(f"FASTag {fastag_id} reactivated.", "success")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("fastags"))


# ---------------------------------------------------------------
# toll passes
# ---------------------------------------------------------------

@app.route("/passes")
@login_required
def passes():
    from repositories.toll_pass_repository import TollPassRepository
    all_passes = TollPassRepository().get_all()
    return render_template("passes.html", passes=all_passes)


@app.route("/passes/issue", methods=["GET", "POST"])
@login_required
def pass_issue():
    if request.method == "POST":
        pass_type = request.form.get("pass_type", "MONTHLY")
        vehicle_number = request.form.get("vehicle_number", "")

        try:
            if pass_type == "MONTHLY":
                days = int(request.form.get("validity_days", 30) or 30)
                toll_pass = pass_service.issue_monthly_pass(
                    vehicle_number, days
                )
            else:
                trips = int(request.form.get("trip_count", 10) or 10)
                toll_pass = pass_service.issue_trip_pass(
                    vehicle_number, trips
                )

            flash(f"Pass {toll_pass.pass_id} issued.", "success")
            return redirect(url_for("passes"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    return render_template("pass_form.html")


@app.route("/passes/<pass_id>/cancel", methods=["POST"])
@roles_required("Admin")
def pass_cancel(pass_id):
    try:
        pass_service.cancel_pass(pass_id)
        flash(f"Pass {pass_id} cancelled.", "info")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("passes"))


# ---------------------------------------------------------------
# violations
# ---------------------------------------------------------------

@app.route("/violations")
@login_required
def violations():
    from repositories.violation_repository import ViolationRepository
    all_violations = list(reversed(ViolationRepository().get_all()))
    return render_template("violations.html", violations=all_violations)


@app.route("/violations/<violation_id>/pay", methods=["POST"])
@login_required
def violation_pay(violation_id):
    try:
        violation_service.pay_fine(violation_id)
        flash(f"Fine for {violation_id} marked as paid.", "success")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("violations"))


@app.route("/violations/<violation_id>/waive", methods=["POST"])
@roles_required("Admin")
def violation_waive(violation_id):
    try:
        violation_service.waive_fine(violation_id)
        flash(f"Fine for {violation_id} waived.", "info")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("violations"))


# ---------------------------------------------------------------
# reports
# ---------------------------------------------------------------

@app.route("/reports")
@login_required
def reports():
    summary = report_service.summary()
    return render_template("reports.html", summary=summary)


@app.route("/reports/export/<fmt>")
@login_required
def reports_export(fmt):
    try:
        if fmt == "json":
            path = export_summary_json()
        elif fmt == "csv":
            path = export_transactions_csv()
        else:
            flash("Unknown export format.", "error")
            return redirect(url_for("reports"))

        flash(f"Exported to {path}", "success")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("reports"))


# ---------------------------------------------------------------
# users (Admin only)
# ---------------------------------------------------------------

@app.route("/users")
@roles_required("Admin")
def users():
    all_users = user_service.get_all_users()
    return render_template("users.html", users=all_users)


@app.route("/users/register", methods=["GET", "POST"])
@roles_required("Admin")
def user_register():
    if request.method == "POST":
        try:
            role = request.form.get("role", "Toll Operator")
            booth_id = request.form.get("booth_id") or None

            user_service.register_user(
                username=request.form.get("username", ""),
                password=request.form.get("password", ""),
                full_name=request.form.get("full_name", ""),
                role=role,
                booth_id=booth_id
            )
            flash("User registered successfully.", "success")
            return redirect(url_for("users"))
        except TollSystemError as exc:
            flash(str(exc), "error")

    all_booths = booth_service.get_all_booths()
    return render_template("user_form.html", booths=all_booths)


@app.route("/users/<username>/toggle", methods=["POST"])
@roles_required("Admin")
def user_toggle(username):
    try:
        data = user_service.get_user_by_username(username)
        acting_user = current_user()

        if data.get("is_active", True):
            user_service.deactivate_user(acting_user, username)
            flash(f"User '{username}' deactivated.", "info")
        else:
            user_service.activate_user(acting_user, username)
            flash(f"User '{username}' activated.", "success")
    except TollSystemError as exc:
        flash(str(exc), "error")

    return redirect(url_for("users"))


# ---------------------------------------------------------------
# entry point
# ---------------------------------------------------------------

if __name__ == "__main__":
    seed_admin_if_needed()
    app.run(debug=True, host="127.0.0.1", port=5000)
