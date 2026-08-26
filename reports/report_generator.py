"""
Exports the current system summary (see ReportService.summary) to
disk as JSON or CSV, and can build ad-hoc reports scoped to a single
vehicle or booth. Used by the CLI "Reports & Analytics" menu.
"""

import csv
import json
import os
from datetime import datetime

from services.report_service import ReportService

DEFAULT_EXPORT_DIR = "reports/exports"


def _ensure_export_dir():
    os.makedirs(DEFAULT_EXPORT_DIR, exist_ok=True)


def export_summary_json(file_path=None):
    service = ReportService()
    summary = service.summary()

    _ensure_export_dir()

    if not file_path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            DEFAULT_EXPORT_DIR, f"summary_{stamp}.json"
        )

    with open(file_path, "w") as f:
        json.dump(summary, f, indent=4)

    return file_path


def export_transactions_csv(file_path=None):
    service = ReportService()
    transactions = service.get_all_transactions()

    _ensure_export_dir()

    if not file_path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            DEFAULT_EXPORT_DIR, f"transactions_{stamp}.csv"
        )

    if not transactions:
        with open(file_path, "w") as f:
            f.write("")
        return file_path

    fieldnames = list(transactions[0].keys())

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

    return file_path


def vehicle_report(vehicle_number):
    service = ReportService()

    transactions = [
        t for t in service.get_all_transactions()
        if t.get("vehicle_number") == vehicle_number
    ]

    total_spent = sum(
        t.get("final_amount", 0)
        for t in transactions
        if t.get("status") == "SUCCESS"
    )

    return {
        "vehicle_number": vehicle_number,
        "total_crossings": len(transactions),
        "total_spent": total_spent,
        "transactions": transactions
    }


def booth_report(booth_id):
    service = ReportService()

    transactions = [
        t for t in service.get_all_transactions()
        if t.get("booth_id") == booth_id
    ]

    total_collected = sum(
        t.get("final_amount", 0)
        for t in transactions
        if t.get("status") == "SUCCESS"
    )

    return {
        "booth_id": booth_id,
        "total_crossings": len(transactions),
        "total_collected": total_collected,
        "transactions": transactions
    }
