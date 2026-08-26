"""
Custom exception hierarchy for the Smart Toll Booth Collection
& Traffic Management System.

Using a dedicated hierarchy (instead of bare ValueError/Exception)
lets services raise precise, catchable errors and lets main.py /
tests distinguish between failure types cleanly.

All exceptions inherit from ValueError as well, so any existing
code that catches ValueError continues to work unchanged.
"""


class TollSystemError(ValueError):
    """Base class for all application-specific errors."""


# ---------------------------------------------------------------
# Generic / validation
# ---------------------------------------------------------------

class ValidationError(TollSystemError):
    """Raised when input data fails validation rules."""


class DuplicateRecordError(TollSystemError):
    """Raised when attempting to create a record that already exists."""


class RecordNotFoundError(TollSystemError):
    """Raised when a requested record cannot be found."""


# ---------------------------------------------------------------
# Authentication & authorization
# ---------------------------------------------------------------

class AuthenticationError(TollSystemError):
    """Raised when login credentials are invalid."""


class AuthorizationError(TollSystemError):
    """Raised when a user lacks permission for an action."""


class AccountInactiveError(TollSystemError):
    """Raised when a user account has been deactivated."""


# ---------------------------------------------------------------
# Domain specific
# ---------------------------------------------------------------

class VehicleNotFoundError(RecordNotFoundError):
    """Raised when a vehicle cannot be located."""


class BoothNotFoundError(RecordNotFoundError):
    """Raised when a toll booth cannot be located."""


class BoothClosedError(TollSystemError):
    """Raised when a transaction is attempted at a closed booth."""


class FASTagNotFoundError(RecordNotFoundError):
    """Raised when a FASTag account cannot be located."""


class InsufficientBalanceError(TollSystemError):
    """Raised when a FASTag does not have enough balance."""


class InvalidPaymentError(TollSystemError):
    """Raised when a payment cannot be processed."""


class PassNotFoundError(RecordNotFoundError):
    """Raised when a toll pass cannot be located."""


class PassExpiredError(TollSystemError):
    """Raised when a toll pass has expired or is exhausted."""


class ViolationNotFoundError(RecordNotFoundError):
    """Raised when a violation record cannot be located."""
