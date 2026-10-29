import csv
import math
from pathlib import Path


DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_bins.csv"
)


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance between two GPS coordinates."""
    earth_radius_km = 6371.0

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * earth_radius_km * math.asin(
        math.sqrt(min(1.0, a))
    )


def load_bins(csv_path=DEFAULT_CSV):
    """Read simulated bin data from CSV."""
    bins = []

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required = {
            "bin_id", "latitude", "longitude", "fill_percent"
        }

        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV is missing required columns.")

        for row in reader:
            fill = float(row["fill_percent"])
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])

            if not 0 <= fill <= 100:
                raise ValueError("Fill percentage must be 0-100.")

            if not -90 <= latitude <= 90:
                raise ValueError("Invalid latitude.")

            if not -180 <= longitude <= 180:
                raise ValueError("Invalid longitude.")

            bins.append({
                "bin_id": row["bin_id"],
                "latitude": latitude,
                "longitude": longitude,
                "fill_percent": fill,
            })

    return bins


def optimize_route(
    bins,
    depot_lat,
    depot_lon,
    threshold=60
):
    """
    Build a greedy collection route.

    Only bins at or above threshold are included.
    At each step, prefer nearby bins while giving fuller bins
    higher priority. This is a heuristic, not a guaranteed
    globally shortest route.
    """
    if not 0 <= threshold <= 100:
        raise ValueError("Threshold must be between 0 and 100.")

    remaining = [
        dict(item) for item in bins
        if item["fill_percent"] >= threshold
    ]

    route = []
    current_lat = depot_lat
    current_lon = depot_lon
    total_distance = 0.0

    while remaining:
        def score(bin_data):
            distance = haversine_km(
                current_lat,
                current_lon,
                bin_data["latitude"],
                bin_data["longitude"],
            )

            # Higher fill gives a stronger priority.
            urgency_factor = 0.5 + (
                bin_data["fill_percent"] / 100.0
            )

            return distance / urgency_factor

        next_bin = min(remaining, key=score)

        leg_distance = haversine_km(
            current_lat,
            current_lon,
            next_bin["latitude"],
            next_bin["longitude"],
        )

        next_bin["distance_from_previous_km"] = round(
            leg_distance, 3
        )

        route.append(next_bin)
        total_distance += leg_distance

        current_lat = next_bin["latitude"]
        current_lon = next_bin["longitude"]
        remaining.remove(next_bin)

    return {
        "route": route,
        "total_distance_km": round(total_distance, 3),
        "bins_to_collect": len(route),
        "threshold_percent": threshold,
    }


def main():
    bins = load_bins()

    # Demo depot location; replace with your actual depot coordinates.
    result = optimize_route(
        bins,
        depot_lat=27.4920,
        depot_lon=77.6730,
        threshold=60,
    )

    print("\nSMART WASTE BIN ROUTE")
    print("-" * 45)

    if not result["route"]:
        print("No bins meet the collection threshold.")
    else:
        for number, bin_data in enumerate(result["route"], start=1):
            print(
                f"{number}. {bin_data['bin_id']} | "
                f"Fill: {bin_data['fill_percent']:.0f}% | "
                f"Leg: {bin_data['distance_from_previous_km']} km"
            )

    print("-" * 45)
    print(f"Bins selected: {result['bins_to_collect']}")
    print(f"Total route distance: {result['total_distance_km']} km")


if __name__ == "__main__":
    main()