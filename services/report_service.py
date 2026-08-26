from repositories.transaction_repository import TransactionRepository
from repositories.violation_repository import ViolationRepository


class ReportService:
    """Aggregates raw transaction (and violation) records into the
    summary numbers used by reports/daily_report.py and
    reports/report_generator.py.
    """

    def __init__(self):
        self.transaction_repository = TransactionRepository()
        self.violation_repository = ViolationRepository()

    def get_all_transactions(self):
        return self.transaction_repository.get_all()

    def successful_transactions(self):
        return [
            transaction
            for transaction in self.get_all_transactions()
            if transaction.get("status") == "SUCCESS"
        ]

    def total_collection(self):
        return sum(
            transaction.get("final_amount", 0)
            for transaction in self.successful_transactions()
        )

    def total_vehicles(self):
        return len(self.successful_transactions())

    def revenue_by_payment_method(self):
        report = {}

        for transaction in self.successful_transactions():
            method = transaction.get("payment_method")
            amount = transaction.get("final_amount", 0)
            report[method] = report.get(method, 0) + amount

        return report

    def revenue_by_vehicle_type(self):
        report = {}

        for transaction in self.successful_transactions():
            vehicle_type = transaction.get("vehicle_type")
            amount = transaction.get("final_amount", 0)
            report[vehicle_type] = report.get(vehicle_type, 0) + amount

        return report

    def vehicle_count_by_type(self):
        report = {}

        for transaction in self.successful_transactions():
            vehicle_type = transaction.get("vehicle_type")
            report[vehicle_type] = report.get(vehicle_type, 0) + 1

        return report

    def revenue_by_booth(self):
        report = {}

        for transaction in self.successful_transactions():
            booth_id = transaction.get("booth_id")
            amount = transaction.get("final_amount", 0)
            report[booth_id] = report.get(booth_id, 0) + amount

        return report

    def best_performing_booth(self):
        revenue = self.revenue_by_booth()

        if not revenue:
            return None

        return max(revenue, key=revenue.get)

    def outstanding_fines_total(self):
        return sum(
            item.get("fine_amount", 0)
            for item in self.violation_repository.get_unpaid()
        )

    def summary(self):
        return {
            "total_vehicles": self.total_vehicles(),
            "total_collection": self.total_collection(),
            "revenue_by_payment_method": self.revenue_by_payment_method(),
            "revenue_by_vehicle_type": self.revenue_by_vehicle_type(),
            "vehicle_count_by_type": self.vehicle_count_by_type(),
            "revenue_by_booth": self.revenue_by_booth(),
            "best_performing_booth": self.best_performing_booth(),
            "outstanding_fines_total": self.outstanding_fines_total()
        }
