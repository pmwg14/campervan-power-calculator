import streamlit as st
import pandas as pd

# Title
st.title("Campervan Power Budget Calculator")

# Sidebar for battery and solar settings
battery_capacity = st.sidebar.selectbox(
    "Select Your Battery Capacity",
    options=["200Ah", "400Ah", "600Ah (Default)"]
)

eco_flow_toggle = st.sidebar.checkbox("Include EcoFlow Delta Pro (3.6kWh)")

solar_hours = st.sidebar.slider("Estimated Sunlight Hours per Day", 0, 10, 4)
solar_watts = st.sidebar.number_input("Solar Panel Capacity (W)", value=400)

# Convert battery capacity to Wh
battery_wh = {
    "200Ah": 200 * 12,
    "400Ah": 400 * 12,
    "600Ah (Default)": 600 * 12
}[battery_capacity]

total_capacity_wh = battery_wh
if eco_flow_toggle:
    total_capacity_wh += 3600

# Solar input estimation
solar_input_wh = solar_hours * solar_watts

# Device entry
st.header("Device Usage")
device_count = st.number_input("Number of devices", min_value=1, max_value=10, value=3)

devices = []
for i in range(device_count):
    st.subheader(f"Device {i + 1}")
    name = st.text_input(f"Name", key=f"name_{i}")
    watts = st.number_input(f"Power draw (Watts)", key=f"watts_{i}")
    hours = st.number_input(f"Usage per day (hours)", key=f"hours_{i}")
    devices.append((name, watts, hours))

# Calculate daily usage
daily_consumption = sum(w * h for _, w, h in devices)

# Results
st.header("Results")
st.write(f"**Total daily consumption**: {daily_consumption} Wh")
st.write(f"**Battery capacity**: {total_capacity_wh} Wh")
st.write(f"**Solar contribution per day**: {solar_input_wh} Wh")

net_daily = daily_consumption - solar_input_wh
if net_daily <= 0:
    st.success("You're fully solar-powered!")
else:
    days_runtime = total_capacity_wh / net_daily
    st.write(f"**Estimated runtime without recharge**: {days_runtime:.2f} days")

# Device table
df = pd.DataFrame(devices, columns=["Device", "Watts", "Hours per Day"])
df["Daily Wh"] = df["Watts"] * df["Hours per Day"]
st.dataframe(df)
