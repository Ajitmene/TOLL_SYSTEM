from services.fastag_service import FASTagService
from services.pass_service import PassService
from services.payment_service import PaymentService
from services.toll_booth_service import TollBoothService
from services.toll_service import TollService
from services.transaction_service import TransactionService
from services.vehicle_service import VehicleService
from services.violation_service import ViolationService
from utils.decorators import log_action
from utils.exceptions import (
    BoothNotFoundError,
    InsufficientBalanceError,
    InvalidPaymentError,
    VehicleNotFoundError
)
from utils.id_generator import generate_transaction_id
from utils.logger import get_logger

logger = get_logger("crossing")


class TollCrossingService:
    """Orchestrates a single vehicle's crossing end-to-end: toll
    calculation, payment (cash/UPI/card/FASTag/prepaid pass),
    transaction logging, booth stats, and violation recording on
    failure. This is the one method main.py calls from the
    "process a crossing" menu option.
    """

    def __init__(self):
        self.vehicle_service = VehicleService()
        self.toll_service = TollService()
        self.payment_service = PaymentService()
        self.fastag_service = FASTagService()
        self.transaction_service = TransactionService()
        self.booth_service = TollBoothService()
        self.pass_service = PassService()
        self.violation_service = ViolationService()

    @log_action("process_vehicle_crossing")
    def process_vehicle_crossing(
        self,
        vehicle_number,
        booth_id,
        operator_id,
        payment_method,
        hour=None,
        **payment_details
    ):
        # ------------------------------------------------
        # 1. Find Vehicle & Booth
        # ------------------------------------------------

        vehicle = self.vehicle_service.get_vehicle(vehicle_number)

        if not vehicle:
            raise VehicleNotFoundError(
                f"Vehicle {vehicle_number} not found."
            )

        booth = self.booth_service.get_booth(booth_id)

        if not booth:
            raise BoothNotFoundError(f"Booth {booth_id} not found.")

        # ------------------------------------------------
        # 2. Free crossing via an active prepaid Pass
        # ------------------------------------------------

        if payment_method == "Pass":
            toll_pass = self.pass_service.get_usable_pass_for_vehicle(
                vehicle_number
            )

            if not toll_pass:
                raise InvalidPaymentError(
                    f"Vehicle {vehicle_number} has no usable toll pass."
                )

            self.pass_service.use_pass(toll_pass.pass_id, booth_id)

            transaction = self.transaction_service.create_transaction(
                transaction_id=generate_transaction_id(),
                vehicle_number=vehicle["vehicle_number"],
                vehicle_type=vehicle["vehicle_type"],
                booth_id=booth_id,
                operator_id=operator_id,
                base_toll=0,
                peak_charge=0,
                discount=0,
                payment_method=f"Pass:{toll_pass.pass_id}",
                status="SUCCESS"
            )

            self.booth_service.record_transaction(
                booth_id, transaction.transaction_id, 0
            )

            return {
                "vehicle": vehicle,
                "toll": {
                    "base_toll": 0, "peak_charge": 0,
                    "discount": 0, "final_amount": 0
                },
                "payment": {
                    "success": True, "method": "Pass",
                    "details": {"pass_id": toll_pass.pass_id}
                },
                "transaction": transaction
            }

        # ------------------------------------------------
        # 3. Calculate Toll
        # ------------------------------------------------

        toll = self.toll_service.calculate_toll(
            vehicle_type=vehicle["vehicle_type"],
            payment_method=payment_method,
            hour=hour
        )

        final_amount = toll["final_amount"]

        # ------------------------------------------------
        # 4. Process Payment
        # ------------------------------------------------

        if payment_method == "FASTag":
            fastag_id = vehicle.get("fastag_id")

            if not fastag_id:
                self.violation_service.record_violation(
                    vehicle_number, booth_id, "NO_FASTAG",
                    "Vehicle attempted FASTag payment with no tag "
                    "linked."
                )

                raise InvalidPaymentError(
                    "Vehicle does not have a FASTag."
                )

            try:
                self.fastag_service.deduct(fastag_id, final_amount)

            except InsufficientBalanceError:
                self.violation_service.record_violation(
                    vehicle_number, booth_id, "INSUFFICIENT_BALANCE",
                    f"FASTag {fastag_id} balance too low for toll of "
                    f"{final_amount}."
                )
                raise

            payment = {
                "success": True,
                "method": "FASTag",
                "details": {
                    "amount": final_amount,
                    "status": "SUCCESS",
                    "transaction_reference": f"FASTAG-{fastag_id}"
                }
            }

        else:
            payment = self.payment_service.process_payment(
                payment_method=payment_method,
                amount=final_amount,
                **payment_details
            )

        if not payment["success"]:
            raise InvalidPaymentError("Payment failed.")

        # ------------------------------------------------
        # 5. Create Transaction & Update Booth Stats
        # ------------------------------------------------

        transaction = self.transaction_service.create_transaction(
            transaction_id=generate_transaction_id(),
            vehicle_number=vehicle["vehicle_number"],
            vehicle_type=vehicle["vehicle_type"],
            booth_id=booth_id,
            operator_id=operator_id,
            base_toll=toll["base_toll"],
            peak_charge=toll["peak_charge"],
            discount=toll["discount"],
            payment_method=payment_method,
            status="SUCCESS"
        )

        self.booth_service.record_transaction(
            booth_id, transaction.transaction_id, final_amount
        )

        logger.info(
            "Crossing processed: vehicle=%s booth=%s amount=%s "
            "method=%s",
            vehicle_number, booth_id, final_amount, payment_method
        )

        return {
            "vehicle": vehicle,
            "toll": toll,
            "payment": payment,
            "transaction": transaction
        }
