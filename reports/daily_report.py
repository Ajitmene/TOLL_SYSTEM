from services.report_service import ReportService


def generate_daily_report():

    service = ReportService()

    report = service.summary()

    print("\n")
    print("=" * 65)
    print("          SMART TOLL PLAZA - DAILY REPORT")
    print("=" * 65)

    print(
        f"\nTotal Vehicles     : "
        f"{report['total_vehicles']}"
    )

    print(
        f"Total Collection   : "
        f"₹{report['total_collection']:.2f}"
    )

    print("\nRevenue by Payment Method")
    print("-" * 65)

    for method, amount in (
        report["revenue_by_payment_method"]
        .items()
    ):

        print(
            f"{method:<20}"
            f"₹{amount:>12.2f}"
        )

    print("\nRevenue by Vehicle Type")
    print("-" * 65)

    for vehicle_type, amount in (
        report["revenue_by_vehicle_type"]
        .items()
    ):

        print(
            f"{vehicle_type:<20}"
            f"₹{amount:>12.2f}"
        )

    print("\nVehicle Count by Type")
    print("-" * 65)

    for vehicle_type, count in (
        report["vehicle_count_by_type"]
        .items()
    ):

        print(
            f"{vehicle_type:<20}"
            f"{count:>5}"
        )

    print("\nRevenue by Booth")
    print("-" * 65)

    for booth_id, amount in (
        report["revenue_by_booth"]
        .items()
    ):

        print(
            f"{booth_id:<20}"
            f"₹{amount:>12.2f}"
        )

    print(
        f"\nBest Performing Booth : "
        f"{report['best_performing_booth']}"
    )

    print("=" * 65)