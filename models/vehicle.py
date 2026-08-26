class Vehicle:

    def __init__(
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
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.owner_name = owner_name
        self.owner_phone = owner_phone
        self.vehicle_model = vehicle_model
        self.fuel_type = fuel_type
        self.registration_state = registration_state
        self.fastag_id = fastag_id

    def __str__(self):
        return (
            f"Vehicle Number : {self.vehicle_number}\n"
            f"Vehicle Type   : {self.vehicle_type}\n"
            f"Owner Name     : {self.owner_name}\n"
            f"Vehicle Model  : {self.vehicle_model}\n"
            f"Fuel Type      : {self.fuel_type}\n"
            f"State          : {self.registration_state}\n"
            f"FASTag ID      : {self.fastag_id}"
        )