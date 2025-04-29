import streamlit as st
import pandas as pd
import datetime
import os

# Sample bus data
bus_data = [
    {"Bus ID": "B001", "Source": "Pune", "Destination": "Mumbai", "Departure": "08:00 AM", "Arrival": "12:00 PM", "Price": 500},
    {"Bus ID": "B002", "Source": "Pune", "Destination": "Mumbai", "Departure": "02:00 PM", "Arrival": "06:00 PM", "Price": 550},
    {"Bus ID": "B003", "Source": "Pune", "Destination": "Mumbai", "Departure": "06:00 PM", "Arrival": "10:00 PM", "Price": 600},
    {"Bus ID": "B004", "Source": "Pune", "Destination": "Delhi", "Departure": "09:00 AM", "Arrival": "09:00 PM", "Price": 1500},
    {"Bus ID": "B005", "Source": "Pune", "Destination": "Delhi", "Departure": "09:00 PM", "Arrival": "09:00 AM", "Price": 1600},
]

# Convert to DataFrame
df_buses = pd.DataFrame(bus_data)

# Function to load bookings
def load_bookings():
    if os.path.exists("bookings.csv"):
        return pd.read_csv("bookings.csv")
    else:
        return pd.DataFrame(columns=["Name", "Bus ID", "Date", "Booking Time"])

# Function to save a booking
def save_booking(name, bus_id, date):
    booking_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_booking = pd.DataFrame([[name, bus_id, date, booking_time]], columns=["Name", "Bus ID", "Date", "Booking Time"])
    bookings = load_bookings()
    bookings = pd.concat([bookings, new_booking], ignore_index=True)
    bookings.to_csv("bookings.csv", index=False)

# Streamlit app
st.title("🚌 Bus Ticket Booking App")

# User inputs
source = st.selectbox("Select Source", df_buses["Source"].unique())
destination = st.selectbox("Select Destination", df_buses["Destination"].unique())
travel_date = st.date_input("Select Travel Date", min_value=datetime.date.today())

# Filter available buses
available_buses = df_buses[(df_buses["Source"] == source) & (df_buses["Destination"] == destination)]

if not available_buses.empty:
    st.subheader("Available Buses")
    st.dataframe(available_buses.reset_index(drop=True))

    # Select a bus
    bus_ids = available_buses["Bus ID"].tolist()
    selected_bus_id = st.selectbox("Select Bus ID to Book", bus_ids)

    # Enter user name
    name = st.text_input("Enter Your Name")

    if st.button("Book Ticket"):
        if name:
            save_booking(name, selected_bus_id, travel_date.strftime("%Y-%m-%d"))
            st.success(f"Ticket booked successfully for {name} on {travel_date.strftime('%Y-%m-%d')} in Bus {selected_bus_id}")
        else:
            st.error("Please enter your name to book a ticket.")
else:
    st.warning("No buses available for the selected route.")
