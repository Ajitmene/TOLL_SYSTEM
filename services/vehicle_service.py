from models.vehicle import Vehicle
from repositories.vehicle_repository import VehicleRepository
from utils.exceptions import DuplicateRecordError, VehicleNotFoundError
from utils.validators import validate_vehicle_number


class VehicleService:

    def __init__(self):
        self.repository = VehicleRepository()

    def register_vehicle(
        self,
        vehicle_number,
        vehicle_type,
        owner_name,
        owner_phone,
        vehicle_model,
        fuel_type,
        registration_state,
        fastag_id=None
    ):
        vehicle_number = validate_vehicle_number(vehicle_number)

        if self.repository.vehicle_exists(vehicle_number):
            raise DuplicateRecordError(
                f"Vehicle {vehicle_number} already exists."
            )

        vehicle = Vehicle(
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_phone=owner_phone,
            vehicle_model=vehicle_model,
            fuel_type=fuel_type,
            registration_state=registration_state,
            fastag_id=fastag_id
        )

        vehicle_data = {
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type,
            "owner_name": vehicle.owner_name,
            "owner_phone": vehicle.owner_phone,
            "vehicle_model": vehicle.vehicle_model,
            "fuel_type": vehicle.fuel_type,
            "registration_state": vehicle.registration_state,
            "fastag_id": vehicle.fastag_id
        }

        self.repository.add(vehicle_data)

        return vehicle

    def get_vehicle(self, vehicle_number):
        return self.repository.find_by_vehicle_number(vehicle_number)

    def get_all_vehicles(self):
        return self.repository.get_all()

    def get_vehicles_by_type(self, vehicle_type):
        return [
            v for v in self.repository.get_all()
            if v.get("vehicle_type") == vehicle_type
        ]

    def update_vehicle(self, vehicle_number, **fields):
        vehicle = self.repository.find_by_vehicle_number(vehicle_number)

        if not vehicle:
            raise VehicleNotFoundError(
                f"Vehicle {vehicle_number} not found."
            )

        vehicle.update(fields)
        self.repository.update(
            "vehicle_number", vehicle_number, vehicle
        )

        return vehicle

    def assign_fastag(self, vehicle_number, fastag_id):
        return self.update_vehicle(vehicle_number, fastag_id=fastag_id)

    def delete_vehicle(self, vehicle_number):
        if not self.repository.vehicle_exists(vehicle_number):
            raise VehicleNotFoundError(
                f"Vehicle {vehicle_number} not found."
            )

        self.repository.delete("vehicle_number", vehicle_number)
