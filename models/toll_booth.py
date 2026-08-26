from datetime import datetime


class TollBooth:

    def __init__(
        self,
        booth_id,
        booth_name,
        location,
        lane_number,
        operator_id=None,
        status="OPEN"
    ):
        self.booth_id = booth_id
        self.booth_name = booth_name
        self.location = location
        self.lane_number = lane_number
        self.operator_id = operator_id
        self.status = status

        self.vehicle_count = 0
        self.total_collection = 0.0
        self.last_transaction_id = None
        self.last_transaction_time = None

    def open_booth(self):
        self.status = "OPEN"

    def close_booth(self):
        self.status = "CLOSED"

    def mark_maintenance(self):
        self.status = "MAINTENANCE"

    def record_transaction(
        self,
        transaction_id,
        amount
    ):
        if self.status != "OPEN":
            raise ValueError(
                f"Booth {self.booth_id} is not open."
            )

        self.vehicle_count += 1
        self.total_collection += amount

        self.last_transaction_id = transaction_id
        self.last_transaction_time = datetime.now()

    def to_dict(self):

        return {
            "booth_id": self.booth_id,
            "booth_name": self.booth_name,
            "location": self.location,
            "lane_number": self.lane_number,
            "operator_id": self.operator_id,
            "status": self.status,
            "vehicle_count": self.vehicle_count,
            "total_collection": self.total_collection,
            "last_transaction_id":
                self.last_transaction_id,
            "last_transaction_time":
                (
                    self.last_transaction_time.isoformat()
                    if self.last_transaction_time
                    else None
                )
        }

    def __str__(self):

        return (
            f"Booth ID          : {self.booth_id}\n"
            f"Booth Name        : {self.booth_name}\n"
            f"Location          : {self.location}\n"
            f"Lane Number       : {self.lane_number}\n"
            f"Operator ID       : {self.operator_id}\n"
            f"Status            : {self.status}\n"
            f"Vehicle Count     : {self.vehicle_count}\n"
            f"Total Collection  : "
            f"₹{self.total_collection:.2f}\n"
            f"Last Transaction  : "
            f"{self.last_transaction_id}"
        )