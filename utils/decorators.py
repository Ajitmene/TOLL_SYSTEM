"""
Function decorators used throughout the services layer:

- `require_role`   : enforce role-based access control
- `log_action`      : audit-log every call (and failure) to logs/system.log
- `handle_exceptions`: convert unexpected errors into TollSystemError
                       so the CLI layer only ever has to catch one type

Convention: any service method that needs authorization takes the
acting user as its first positional argument (after `self`) as a
dict with at least a "role" key -- this is what UserService /
AuthService hand back after a successful login.
"""

import functools

from utils.exceptions import AuthorizationError, TollSystemError
from utils.logger import get_logger

logger = get_logger("audit")


def require_role(*allowed_roles):
    """Restrict a method to users whose 'role' is in allowed_roles."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, current_user, *args, **kwargs):

            role = None

            if isinstance(current_user, dict):
                role = current_user.get("role")
            else:
                role = getattr(current_user, "role", None)

            if role not in allowed_roles:
                logger.warning(
                    "Permission denied for role=%s on %s "
                    "(requires one of %s)",
                    role, func.__name__, allowed_roles
                )

                raise AuthorizationError(
                    f"Role '{role}' is not permitted to perform "
                    f"'{func.__name__}'. Requires one of: "
                    f"{', '.join(allowed_roles)}."
                )

            return func(self, current_user, *args, **kwargs)

        return wrapper

    return decorator


def log_action(action_name=None):
    """Log every invocation of the wrapped function, plus failures."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            name = action_name or func.__name__

            logger.info("ACTION START: %s", name)

            try:
                result = func(*args, **kwargs)

                logger.info("ACTION SUCCESS: %s", name)

                return result

            except Exception as exc:
                logger.error(
                    "ACTION FAILED: %s | %s: %s",
                    name, type(exc).__name__, exc
                )
                raise

        return wrapper

    return decorator


def handle_exceptions(func):
    """Wrap unexpected exceptions into a TollSystemError.

    Exceptions that are already part of our TollSystemError
    hierarchy are re-raised untouched so callers can still branch
    on the specific type.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except TollSystemError:
            raise

        except Exception as exc:
            logger.exception("Unexpected error in %s", func.__name__)

            raise TollSystemError(
                f"Unexpected error in {func.__name__}: {exc}"
            ) from exc

    return wrapper
