"""
Small formatting / display helpers used by the CLI and reports so
presentation logic doesn't get duplicated across the codebase.
"""

from datetime import datetime

from config.settings import CURRENCY


def format_currency(amount):
    try:
        return f"{CURRENCY}{float(amount):,.2f}"
    except (TypeError, ValueError):
        return f"{CURRENCY}0.00"


def format_datetime(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            return value

    return str(value)


def print_header(title, width=65):
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_divider(width=65):
    print("-" * width)


def print_table(rows, headers):
    """Print a simple left-aligned text table for a list of dict rows."""

    if not rows:
        print("(no records found)")
        return

    widths = [len(h) for h in headers]

    for row in rows:
        for i, header in enumerate(headers):
            widths[i] = max(widths[i], len(str(row.get(header, ""))))

    header_line = "  ".join(
        h.ljust(widths[i]) for i, h in enumerate(headers)
    )

    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        print(
            "  ".join(
                str(row.get(h, "")).ljust(widths[i])
                for i, h in enumerate(headers)
            )
        )
