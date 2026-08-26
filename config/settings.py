PROJECT_NAME = "Smart Toll Booth Collection & Traffic Management System"

CURRENCY = "₹"

DATA_DIR = "data"
LOG_DIR = "logs"


DEFAULT_TOLL_RATES = {
    "Bike": 20,
    "Car": 50,
    "SUV": 80,
    "LCV": 100,
    "Bus": 120,
    "Truck": 150,
    "Multi-Axle": 200
}


PEAK_HOURS = [
    (8, 10),
    (17, 20)
]


PEAK_CHARGES = {
    "Bike": 5,
    "Car": 10,
    "SUV": 15,
    "LCV": 20,
    "Bus": 25,
    "Truck": 30,
    "Multi-Axle": 40
}


FASTAG_DISCOUNT_PERCENTAGE = 10


PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Card",
    "FASTag"
]