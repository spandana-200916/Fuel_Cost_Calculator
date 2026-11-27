import json, csv, os, io
from datetime import datetime

TRIPS_FILE = "trips.json"

def initialize_database():
    if not os.path.exists(TRIPS_FILE):
        with open(TRIPS_FILE, "w") as f:
            json.dump([], f)

def _load():
    initialize_database()
    with open(TRIPS_FILE, "r") as f:
        try:
            d = json.load(f)
            return d if isinstance(d, list) else []
        except:
            return []

def _save(trips):
    with open(TRIPS_FILE, "w") as f:
        json.dump(trips, f, indent=2)

# 10 FIELDS - Exactly like your trips.json
def save_trip(username, vehicle, fuel, distance, mileage, fuel_price, fuel_used, total_cost, cost_per_km):
    trips = _load()
    new_id = max([t.get("id", 0) for t in trips], default=0) + 1
    trips.append({
        "id": new_id,
        "username": username,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vehicle": vehicle,
        "fuel": fuel,
        "distance": distance,
        "mileage": mileage,
        "fuel_price": fuel_price,
        "fuel_used": fuel_used,
        "total_cost": total_cost,
        "cost_per_km": cost_per_km
    })
    _save(trips)
    return new_id

def get_user_trips(username):
    return [t for t in _load() if t.get("username") == username]

def search_trips(username, keyword):
    k = keyword.lower()
    return [t for t in get_user_trips(username) if k in str(t.get("vehicle","")).lower() or k in str(t.get("fuel","")).lower() or k in str(t.get("date","")).lower()]

def delete_trip(username, trip_id):
    trips = [t for t in _load() if not (t.get("username")==username and t.get("id")==trip_id)]
    _save(trips)

def export_csv(username):
    trips = get_user_trips(username)
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["id","username","date","vehicle","fuel","distance","mileage","fuel_price","fuel_used","total_cost","cost_per_km"])
    w.writeheader()
    w.writerows(trips)
    return out.getvalue()

def export_json(username):
    return json.dumps(get_user_trips(username), indent=2)