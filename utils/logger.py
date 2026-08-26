"""
Centralized logging configuration for the toll system.

Every module should obtain a logger via `get_logger(__name__)`
instead of using print() for diagnostic/audit output. All logs are
written to logs/system.log (and echoed to the console at WARNING+)
so operational issues are easy to trace after the fact.
"""

import logging
import os

from config.settings import LOG_DIR

_LOG_FILE = os.path.join(LOG_DIR, "system.log")
_configured = False


def _configure_root_logger():
    global _configured

    if _configured:
        return

    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger("toll_system")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

    _configured = True


def get_logger(name="toll_system"):
    """Return a namespaced logger that writes to logs/system.log."""

    _configure_root_logger()

    if name == "toll_system":
        return logging.getLogger("toll_system")

    return logging.getLogger(f"toll_system.{name}")
