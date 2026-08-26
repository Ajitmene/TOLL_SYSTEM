import random
from datetime import datetime


def generate_transaction_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"TXN{timestamp}"


def generate_user_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"USR{timestamp}"


def generate_pass_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"PASS{timestamp}"


def generate_violation_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"VIO{timestamp}"


def generate_fastag_id():
    suffix = random.randint(10000, 99999)
    return f"FT{suffix}"


def generate_booth_id():
    suffix = random.randint(100, 999)
    return f"B{suffix}"
