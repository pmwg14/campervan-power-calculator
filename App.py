import streamlit as st
import pandas as pd

# Title
st.title("Campervan Power Budget Calculator")

# --- Sidebar Inputs ---
st.sidebar.header("Battery & Solar Setup")

# 1. Battery toggle (Renogy Core 200Ah units)
battery_count = st.sidebar.number_input("Number of Renogy 200Ah Batteries", min_value=1, max_value=4, value=3)
battery_wh = battery_count * 200 * 12  # 200Ah × 12V

# 2. Solar panel entry (number and wattage per panel)
num_panels = st.sidebar.number_input("Number of Solar Panels", min_value=1, max_value=10, value=2)
watts_per_panel = st.sidebar.number_input("Wattage per Panel (W)", min_value=50, max_value=500, value=200)
total_solar_watts = num_panels * watts_per_panel

# 3. Solar hour presets
solar_efficiency = st.sidebar.radio(
    "UK Solar Conditions",
    ["Low (Winter – 2 hrs)", "Medium (Spring/Autumn – 4 hrs)", "High (Summer – 6 hrs)", "Custom"]
)

if solar_efficiency == "Low (Winter – 2 hrs)":
    solar_hours = 2
elif solar_efficiency == "Medium (Spring/Autumn – 4 hrs)":
    solar_hours = 4
elif solar_efficiency == "High (Summer – 6 hrs)":
    solar_hours = 6
else:
    solar_hours = st.sidebar.slider("Custom Sunlight Hours per Day", 0, 10, 4)

solar_input_wh = total_solar_watts * solar_hours

# EcoFlow toggle
eco_flow_toggle = st.sidebar.checkbox("Include EcoFlow Delta Pro (3.6kWh)")
total_capacity_wh = battery_wh + (3600 if eco_flow_toggle else 0)

# --- Device Entry ---
st.header("Device Usage")
device_count = st.number_input("Number of devices", min_value=1, max_value=10, value=3)

devices = []
for i in range(device_count):
    st.subheader(f"Device {i + 1}")
    name = st.text_input(f"Name", key=f"name_{i}")
    watts = st.number_input(f"Power draw (Watts)", key=f"watts_{i}")

    # Quick time selector
    col1, col2 = st.columns([2, 3])
    with col1:
        hours = st.number_input("Usage (hours/day)", min_value=0.0, max_value=24.0, step=0.5, key=f"hours_{i}")
    with col2:
        preset = st.radio(
            "Quick-select:",
            ["None", "Working day (10h)", "Mealtimes (0.5h)", "Daytime (14h)", "All the time (24h)"],
            horizontal=True,
            key=f"preset_{i}"
        )
        if preset == "Working day (10h)":
            hours = 10
        elif preset == "Mealtimes (0.5h)":
            hours = 0.5
        elif preset == "Daytime (14h)":
            hours = 14
        elif preset == "All the time (24h)":
            hours = 24

    devices.append((name, watts, hours))

# --- Calculations ---
daily_consumption = sum(w * h for _, w, h in devices)
net_daily = daily_consumption - solar_input_wh

# --- Results ---
st.header("Results")
st.write(f"**Total battery capacity**: {total_capacity_wh} Wh")
st.write(f"**Total solar input per day**: {solar_input_wh} Wh")
st.write(f"**Total daily consumption**: {daily_consumption} Wh")

if net_daily <= 0:
    st.success("You're fully solar-powered! Great job.")
else:
    days_runtime = total_capacity_wh / net_daily
    st.warning(f"Estimated off-grid runtime: **{days_runtime:.2f} days** without recharge.")

# --- Device Table ---
df = pd.DataFrame(devices, columns=["Device", "Watts", "Hours per Day"])
df["Daily Wh"] = df["Watts"] * df["Hours per Day"]
st.dataframe(df)