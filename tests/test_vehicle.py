import unittest

from tests.base_test import BaseTollTestCase
from services.vehicle_service import VehicleService
from utils.exceptions import (
    DuplicateRecordError,
    ValidationError,
    VehicleNotFoundError
)


class TestVehicleService(BaseTollTestCase):

    def setUp(self):
        super().setUp()
        self.service = VehicleService()

    def _register_sample(self, number="MH12AB1234"):
        return self.service.register_vehicle(
            vehicle_number=number,
            vehicle_type="Car",
            owner_name="Ajit",
            owner_phone="9876543210",
            vehicle_model="Swift",
            fuel_type="Petrol",
            registration_state="Maharashtra"
        )

    def test_register_vehicle_success(self):
        vehicle = self._register_sample()
        self.assertEqual(vehicle.vehicle_number, "MH12AB1234")
        self.assertEqual(self.service.repository.count(), 1)

    def test_register_normalizes_vehicle_number(self):
        vehicle = self._register_sample("mh 12 ab 1234")
        self.assertEqual(vehicle.vehicle_number, "MH12AB1234")

    def test_register_duplicate_vehicle_raises(self):
        self._register_sample()

        with self.assertRaises(DuplicateRecordError):
            self._register_sample()

    def test_register_invalid_vehicle_number_raises(self):
        with self.assertRaises(ValidationError):
            self._register_sample("NOT-A-PLATE")

    def test_get_vehicle_found_and_not_found(self):
        self._register_sample()

        self.assertIsNotNone(self.service.get_vehicle("MH12AB1234"))
        self.assertIsNone(self.service.get_vehicle("MH99ZZ0000"))

    def test_assign_fastag(self):
        self._register_sample()

        updated = self.service.assign_fastag("MH12AB1234", "FT12345")
        self.assertEqual(updated["fastag_id"], "FT12345")

    def test_update_missing_vehicle_raises(self):
        with self.assertRaises(VehicleNotFoundError):
            self.service.update_vehicle("MH00XX0000", owner_name="Bob")

    def test_delete_vehicle(self):
        self._register_sample()

        self.service.delete_vehicle("MH12AB1234")
        self.assertIsNone(self.service.get_vehicle("MH12AB1234"))

    def test_get_vehicles_by_type(self):
        self._register_sample("MH12AB1234")
        self.service.register_vehicle(
            vehicle_number="MH14CD5678",
            vehicle_type="SUV",
            owner_name="Bob",
            owner_phone="9123456780",
            vehicle_model="Creta",
            fuel_type="Diesel",
            registration_state="Maharashtra"
        )

        cars = self.service.get_vehicles_by_type("Car")
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0]["vehicle_number"], "MH12AB1234")


if __name__ == "__main__":
    unittest.main()
