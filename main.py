import streamlit as st
import matplotlib.pyplot as plt

from auth import register_user, login_user
from fuel_logic import calculate_fuel

from database import (
    initialize_database,
    save_trip,
    get_user_trips,
    search_trips,
    delete_trip,
    export_csv,
    export_json
)

from analytics import (
    calculate_summary,
    fuel_expense_chart,
    vehicle_expense_chart,
    daily_expense_chart
)


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FuelWise - Fuel Calculator",
    page_icon="⛽",
    layout="wide"
)

initialize_database()


# ==========================================
# 2. SESSION MANAGEMENT
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "trip_saved" not in st.session_state:
    st.session_state.trip_saved = False


# ==========================================
# 3. AUTHENTICATION PAGE
# ==========================================

def login_form():

    st.subheader("Welcome Back")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:

        if not username.strip() or not password:
            st.error("Please enter all details.")

        elif login_user(username.strip(), password):
            st.session_state.logged_in = True
            st.session_state.username = username.strip().lower()
            st.rerun()

        else:
            st.error("Invalid username or password.")


def create_account_form():

    st.subheader("Create Your Account")

    st.caption(
        "Username: at least 3 characters (letters, numbers, "
        "underscore). Password: at least 8 characters."
    )

    with st.form("create_account_form", clear_on_submit=False):

        new_username = st.text_input("Choose Username")

        new_password = st.text_input(
            "Choose Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if not submitted:
        return

    username = new_username.strip().lower()

    if not username or not new_password or not confirm_password:
        st.error("Please fill in all the fields.")

    elif len(username) < 3:
        st.error("Username must contain at least 3 characters.")

    elif not username.replace("_", "").isalnum():
        st.error(
            "Username can contain only letters, numbers "
            "and underscore."
        )

    elif len(new_password) < 8:
        st.error("Password must contain at least 8 characters.")

    elif new_password != confirm_password:
        st.error("Passwords do not match.")

    else:
        success, message = register_user(username, new_password)

        if success:
            st.success(
                "Account created successfully! "
                "Please open the Login tab to sign in."
            )
        else:
            st.error(message)


def authentication_page():

    left, center, right = st.columns([1, 1.5, 1])

    with center:

        with st.container(border=True):
            st.title("⛽ FuelWise")
            st.subheader("Smart Fuel Cost Calculator")
            st.caption("Calculate | Track | Save | Travel Smart")

        login_tab, register_tab = st.tabs(
            ["🔐 Login", "📝 Create Account"]
        )

        with login_tab:
            login_form()

        with register_tab:
            create_account_form()


# ==========================================
# 4. DASHBOARD
# ==========================================

def dashboard():

    username = st.session_state.username

    trips = get_user_trips(username)

    summary = calculate_summary(trips)

    st.title("⛽ FuelWise Dashboard")

    st.write(f"Welcome back, {username.title()}!")

    st.info(
        "Monitor your travel distance, fuel usage "
        "and expenses in one place."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Trips", summary["total_trips"])

    c2.metric(
        "Total Distance",
        f'{summary["total_distance"]:,.2f} km'
    )

    c3.metric(
        "Total Expenses",
        f'₹{summary["total_cost"]:,.2f}'
    )

    c4.metric(
        "Fuel Used",
        f'{summary["total_fuel"]:,.2f} L/kg'
    )

    st.subheader("Recent Trip Records")

    if trips:

        for trip in reversed(trips[-5:]):

            st.write(
                f'**{trip["vehicle"]}** | '
                f'{trip["fuel"]} | '
                f'{trip["distance"]} km | '
                f'₹{trip["total_cost"]:.2f}'
            )

    else:

        st.info("No trips saved yet.")


# ==========================================
# 5. FUEL CALCULATOR
# ==========================================

def fuel_calculator():

    st.title("⛽ Fuel Cost Calculator")

    vehicle = st.selectbox(
        "Select Vehicle",
        ["Bike", "Car", "Scooter", "Truck"],
        key="calc_vehicle"
    )

    fuel_type = st.selectbox(
        "Select Fuel Type",
        ["Petrol", "Diesel", "CNG"],
        key="calc_fuel"
    )

    trip_type = st.radio(
        "Trip Type",
        ["One Way", "Round Trip"],
        horizontal=True,
        key="calc_trip_type"
    )

    unit = "kg" if fuel_type == "CNG" else "litre"

    distance = st.number_input(
        "Enter Distance (KM)",
        min_value=1.0,
        value=100.0,
        key="calc_distance"
    )

    mileage = st.number_input(
        f"Enter Mileage (KM per {unit})",
        min_value=1.0,
        value=20.0,
        key="calc_mileage"
    )

    fuel_price = st.number_input(
        f"Fuel Price (₹ per {unit})",
        min_value=1.0,
        value=100.0,
        key="calc_price"
    )

    if st.button(
        "Calculate Fuel Cost",
        key="calculate_button",
        use_container_width=True
    ):

        try:
            data = calculate_fuel(
                distance, mileage, fuel_price, trip_type
            )

            st.session_state.last_result = {
                "vehicle": vehicle,
                "fuel_type": fuel_type,
                "trip_type": trip_type,
                "unit": unit,
                "distance": data["distance"],
                "mileage": mileage,
                "fuel_price": fuel_price,
                "fuel_required": data["fuel_required"],
                "total_cost": data["total_cost"],
                "cost_per_km": data["cost_per_km"]
            }

            st.session_state.trip_saved = False

        except ValueError as error:
            st.error(str(error))

    result = st.session_state.last_result

    if result:

        with st.container(border=True):

            st.subheader("Trip Summary")

            st.write(
                f"**Vehicle:** {result['vehicle']}  |  "
                f"**Fuel:** {result['fuel_type']}  |  "
                f"**Trip:** {result['trip_type']}"
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Distance", f"{result['distance']:.2f} km")

            c2.metric(
                "Fuel Required",
                f"{result['fuel_required']:.2f} {result['unit']}"
            )

            c3.metric("Estimated Cost", f"₹{result['total_cost']:.2f}")

            c4.metric("Cost per KM", f"₹{result['cost_per_km']:.2f}")

        # Save Trip button lives ONLY on the calculator page,
        # and only after a calculation has been made.
        if st.session_state.trip_saved:

            st.success("Trip saved successfully!")

        elif st.button(
            "💾 Save Trip",
            key="save_trip_button",
            use_container_width=True
        ):

            save_trip(
                st.session_state.username,
                result["vehicle"],
                result["fuel_type"],
                result["distance"],
                result["mileage"],
                result["fuel_price"],
                result["fuel_required"],
                result["total_cost"],
                result["cost_per_km"]
            )

            st.session_state.trip_saved = True

            st.rerun()


# ==========================================
# 6. TRIP HISTORY
# ==========================================

def trip_history():

    st.title("📚 Trip History")

    keyword = st.text_input(
        "Search vehicle, fuel type or date",
        key="trip_search"
    )

    if keyword:
        trips = search_trips(st.session_state.username, keyword)
    else:
        trips = get_user_trips(st.session_state.username)

    if not trips:
        st.info("No trip records found.")
        return

    for trip in reversed(trips):

        with st.expander(
            f'#{trip["id"]} - {trip["vehicle"]} - '
            f'₹{trip["total_cost"]:.2f}'
        ):

            st.write("Date:", trip["date"])
            st.write("Fuel:", trip["fuel"])
            st.write("Distance:", trip["distance"], "KM")
            st.write("Mileage:", trip["mileage"])
            st.write("Fuel Price: ₹", trip["fuel_price"])
            st.write("Fuel Used:", trip["fuel_used"])
            st.write("Total Cost: ₹", trip["total_cost"])
            st.write("Cost per KM: ₹", trip["cost_per_km"])

            if st.button(
                "Delete Trip",
                key=f'delete_{trip["id"]}'
            ):

                delete_trip(st.session_state.username, trip["id"])

                st.success("Trip deleted.")

                st.rerun()


# ==========================================
# 7. ANALYTICS
# ==========================================

def analytics_page():

    st.title("📊 Fuel Analytics")

    trips = get_user_trips(st.session_state.username)

    if not trips:
        st.info("Save a trip to view analytics.")
        return

    summary = calculate_summary(trips)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Expenses", f'₹{summary["total_cost"]:,.2f}')

    c2.metric(
        "Average Trip Expense",
        f'₹{summary["average_cost"]:,.2f}'
    )

    c3.metric("Total Fuel Used", f'{summary["total_fuel"]:.2f}')

    st.subheader("Fuel Expense Chart")

    fig = fuel_expense_chart(trips)

    if fig:
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Vehicle Expense Chart")

    fig = vehicle_expense_chart(trips)

    if fig:
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Daily Expense Trend")

    fig = daily_expense_chart(trips)

    if fig:
        st.pyplot(fig)
        plt.close(fig)


# ==========================================
# 8. BUDGET MANAGEMENT
# ==========================================

def budget_page():

    st.title("💰 Fuel Budget Management")

    budget = st.number_input(
        "Enter your fuel budget (₹)",
        min_value=0.0,
        value=5000.0,
        key="fuel_budget"
    )

    trips = get_user_trips(st.session_state.username)

    summary = calculate_summary(trips)

    spent = summary["total_cost"]

    remaining = budget - spent

    c1, c2 = st.columns(2)

    c1.metric("Total Spending", f"₹{spent:,.2f}")

    c2.metric("Remaining Budget", f"₹{remaining:,.2f}")

    if budget > 0:

        st.progress(min(spent / budget, 1.0))

        if spent > budget:
            st.error("Warning! Your fuel budget has been exceeded.")

        elif spent >= budget * 0.8:
            st.warning("You have used 80% of your fuel budget.")

        else:
            st.success("Your fuel spending is within budget.")

    else:

        st.info("Enter a budget greater than 0 to track spending.")


# ==========================================
# 9. REPORT DOWNLOADS
# ==========================================

def reports_page():

    st.title("📄 Fuel Reports")

    trips = get_user_trips(st.session_state.username)

    if not trips:
        st.info("Save a trip to generate reports.")
        return

    st.write(f"Total records available: {len(trips)}")

    st.download_button(
        "Download CSV Report",
        data=export_csv(st.session_state.username),
        file_name="fuel_report.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download JSON Report",
        data=export_json(st.session_state.username),
        file_name="fuel_report.json",
        mime="application/json"
    )


# ==========================================
# 10. MAIN APPLICATION
# ==========================================

if not st.session_state.logged_in:

    authentication_page()

else:

    with st.sidebar:

        st.title("⛽ FuelWise")

        st.write(f"Welcome, {st.session_state.username}")

        st.divider()

        selected_page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Fuel Calculator",
                "Trip History",
                "Analytics",
                "Budget Management",
                "Reports"
            ],
            key="main_navigation"
        )

        st.divider()

        if st.button(
            "Logout",
            key="logout_button",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.last_result = None
            st.session_state.trip_saved = False

            st.rerun()

        st.caption("FuelWise Version 2.0")

    if selected_page == "Dashboard":
        dashboard()

    elif selected_page == "Fuel Calculator":
        fuel_calculator()

    elif selected_page == "Trip History":
        trip_history()

    elif selected_page == "Analytics":
        analytics_page()

    elif selected_page == "Budget Management":
        budget_page()

    elif selected_page == "Reports":
        reports_page()
