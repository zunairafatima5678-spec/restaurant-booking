import datetime as dt
import requests
import streamlit as st

st.title("Pakistan Restaurant Booking Portal")
base_url = st.text_input("Backend URL", "http://127.0.0.1:8000").rstrip("/")

customer_name = st.text_input("Customer name")
special_reason = st.text_input("Special_Reason")

# FIXED TYPO HERE: dt.timedelta
start_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))
start_time = st.time_input("Time", value=dt.time(9, 0))

if st.button("Schedule"):
    start_dt = dt.datetime.combine(start_date, start_time)
    payload = {
        "customer_name": customer_name.strip(),
        "special_reason": special_reason.strip() or None,
        "start_time": start_dt.isoformat(),
    }
    try:
        resp = requests.post(
            f"{base_url}/schedule_appointment/", json=payload, timeout=10
        )
        resp.raise_for_status()
        st.success("Scheduled")
    except requests.RequestException as exc:
        st.error(f"Schedule failed: {exc}")