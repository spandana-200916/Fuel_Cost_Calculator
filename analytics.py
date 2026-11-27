
import matplotlib.pyplot as plt
from collections import defaultdict


def calculate_summary(trips):

    total_trips = len(trips)

    total_distance = sum(
        trip["distance"] for trip in trips
    )

    total_cost = sum(
        trip["total_cost"] for trip in trips
    )

    total_fuel = sum(
        trip["fuel_used"] for trip in trips
    )

    average_cost = (
        total_cost / total_trips
        if total_trips else 0
    )

    return {
        "total_trips": total_trips,
        "total_distance": total_distance,
        "total_cost": total_cost,
        "total_fuel": total_fuel,
        "average_cost": average_cost
    }


def fuel_expense_chart(trips):

    fuel_costs = defaultdict(float)

    for trip in trips:
        fuel_costs[trip["fuel"]] += trip["total_cost"]

    if not fuel_costs:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.bar(
        list(fuel_costs.keys()),
        list(fuel_costs.values())
    )

    ax.set_title("Fuel-wise Expense Analysis")
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Expense (₹)")

    fig.tight_layout()

    return fig


def vehicle_expense_chart(trips):

    vehicle_costs = defaultdict(float)

    for trip in trips:
        vehicle_costs[trip["vehicle"]] += trip["total_cost"]

    if not vehicle_costs:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.pie(
        list(vehicle_costs.values()),
        labels=list(vehicle_costs.keys()),
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Vehicle-wise Expense Distribution")

    fig.tight_layout()

    return fig


def daily_expense_chart(trips):

    daily_costs = defaultdict(float)

    for trip in trips:
        date = trip["date"][:10]
        daily_costs[date] += trip["total_cost"]

    if not daily_costs:
        return None

    dates = sorted(daily_costs.keys())

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        dates,
        [daily_costs[date] for date in dates],
        marker="o"
    )

    ax.set_title("Daily Fuel Expense Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Expense (₹)")

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig
