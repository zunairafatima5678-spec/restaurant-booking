import datetime as dt
import requests
import streamlit as st

st.title("Pakistan Restaurant Booking Portal")
base_url = st.text_input("Backend URL", "http://127.0.0.1:8000").rstrip("/")

# --- Schedule Booking ---
customer_name = st.text_input("Customer name")
special_request = st.text_input("Special Request")
start_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))
start_time = st.time_input("Time", value=dt.time(9, 0))

if st.button("Schedule"):
    start_dt = dt.datetime.combine(start_date, start_time)
    payload = {
        "customer_name": customer_name.strip(),
        "special_request": special_request.strip() or "",
        "start_time": start_dt.isoformat(),
    }
    try:
        resp = requests.post(
            f"{base_url}/schedule_booking/", json=payload, timeout=10
        )
        resp.raise_for_status()
        st.success("Scheduled Successfully! 🎉")
    except requests.RequestException as exc:
        st.error(f"Schedule failed: {exc}")

st.divider()

# --- Cancel Booking ---
st.subheader("Cancel")
cancel_name = st.text_input("Customer name to cancel", key="cancel_name")
cancel_date = st.date_input("Date to cancel", key="cancel_date", value=dt.date.today())

if st.button("Cancel booking"):
    payload = {"customer_name": cancel_name.strip(), "date": cancel_date.isoformat()}
    try:
        resp = requests.post(f"{base_url}/cancel_booking/", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json() if resp.content else {}
        st.success(f"Canceled: {data.get('canceled_count', 0)}")
        st.rerun()
    except requests.HTTPError:
        st.error(resp.text)
    except requests.RequestException as exc:
        st.error(f"Cancel failed: {exc}")

st.divider()

# --- List Bookings ---
st.subheader("Scheduled Bookings")
list_date = st.date_input("Select Date to View Bookings", value=dt.date.today(), key="list_date")

if st.button("View Bookings"):
    payload = {"date": list_date.isoformat()}
    try:
        resp = requests.post(f"{base_url}/list_bookings/", json=payload, timeout=10)
        resp.raise_for_status()
        st.dataframe(resp.json(), use_container_width=True, hide_index=True)
    except requests.RequestException as exc:
        st.warning(f"Could not load appointments: {exc}")