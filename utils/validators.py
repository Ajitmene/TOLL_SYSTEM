"""
Reusable input validation helpers shared across services and the
CLI layer. Each validator raises utils.exceptions.ValidationError
with a human readable message on failure, or returns True.
"""

import re

from utils.exceptions import ValidationError

VEHICLE_NUMBER_PATTERN = re.compile(
    r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$"
)

PHONE_PATTERN = re.compile(r"^[6-9][0-9]{9}$")


def validate_vehicle_number(vehicle_number):
    if not vehicle_number:
        raise ValidationError("Vehicle number is required.")

    normalized = vehicle_number.strip().upper().replace(" ", "")

    if not VEHICLE_NUMBER_PATTERN.match(normalized):
        raise ValidationError(
            f"'{vehicle_number}' is not a valid vehicle "
            "registration number (expected e.g. MH12AB1234)."
        )

    return normalized


def validate_phone_number(phone):
    if not phone:
        raise ValidationError("Phone number is required.")

    normalized = str(phone).strip()

    if not PHONE_PATTERN.match(normalized):
        raise ValidationError(
            f"'{phone}' is not a valid 10-digit Indian phone number."
        )

    return normalized


def validate_positive_amount(amount, field_name="Amount"):
    try:
        value = float(amount)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number.")

    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")

    return value


def validate_non_empty(value, field_name="Field"):
    if value is None or str(value).strip() == "":
        raise ValidationError(f"{field_name} cannot be empty.")

    return str(value).strip()


def validate_choice(value, choices, field_name="Field"):
    if value not in choices:
        raise ValidationError(
            f"{field_name} must be one of {choices}, got '{value}'."
        )

    return value
