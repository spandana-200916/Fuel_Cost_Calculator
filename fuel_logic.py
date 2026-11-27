
def calculate_fuel(distance, mileage, fuel_price, trip_type):
    # Validate the inputs
    if distance <= 0:
        raise ValueError("Distance must be greater than zero.")

    if mileage <= 0:
        raise ValueError("Mileage must be greater than zero.")

    if fuel_price <= 0:
        raise ValueError("Fuel price must be greater than zero.")

    # Calculate total distance
    total_distance = distance

    if trip_type == "Round Trip":
        total_distance = distance * 2

    # Calculate fuel and expense
    fuel_required = total_distance / mileage
    total_cost = fuel_required * fuel_price
    cost_per_km = total_cost / total_distance

    return {
        "distance": round(total_distance, 2),
        "fuel_required": round(fuel_required, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_km": round(cost_per_km, 2)
    }
