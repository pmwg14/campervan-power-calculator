
import streamlit as st
import pandas as pd
import math

# -- Alfred Status Theme --
st.set_page_config(page_title="Alfred Power Dashboard", layout="wide")

# -- DARK MODE TOGGLE --
dark_mode = st.sidebar.toggle("Dark Mode", value=False)
if dark_mode:
    st.markdown("<style>body { background-color: #111; color: white; }</style>", unsafe_allow_html=True)

# -- TITLE + ALFRED INTRO --
st.title("Alfred – Campervan Power Budget Calculator")

with st.expander("Meet Alfred – Your Off-Grid Power Assistant", expanded=True):
    st.markdown("""
    **Alfred** (Adventure Logistics Formulation & Renogy Energy Dashboard) is your on-board AI energy butler –  
    balancing solar, battery, and device usage so you can focus on the road ahead.

    This calculator helps you:
    - Estimate off-grid runtime based on your exact setup
    - Balance solar generation with real-world UK conditions
    - Simulate daily usage for work, mealtimes, or full-day living
    - Optimise your battery bank before heading off-grid

    _“Ready when you are, sir.”_
    """)

# -- BATTERY SELECTION --
st.sidebar.header("Battery & Power Source")

battery_option = st.sidebar.select_slider(
    "Select Renogy Battery Bank Size",
    options=["1 Battery (2.4kWh)", "2 Batteries (4.8kWh)", "3 Batteries (7.2kWh)", "4 Batteries (9.6kWh)"],
    value="3 Batteries (7.2kWh)"
)
battery_count = int(battery_option[0])
battery_wh = battery_count * 200 * 12

eco_flow_toggle = st.sidebar.checkbox("Include EcoFlow Delta Pro (3.6kWh)")
total_capacity_wh = battery_wh + (3600 if eco_flow_toggle else 0)

# -- SOLAR INPUTS --
st.sidebar.header("Solar Input")
num_panels = st.sidebar.number_input("Number of Panels", min_value=1, max_value=10, value=2)
watts_per_panel = st.sidebar.number_input("Watts per Panel", min_value=50, max_value=500, value=200)
total_solar_watts = num_panels * watts_per_panel

solar_hours = st.sidebar.slider("Estimated Sunlight Hours per Day (UK realistic range)", 0, 10, 4)
solar_input_wh = total_solar_watts * solar_hours

# -- ALTERNATOR INPUT (DC-DC CHARGING) --
st.sidebar.header("Alternator Charging")
drive_time_option = st.sidebar.radio("Driving Time", ["30 mins", "1 hour", "Custom"])
if drive_time_option == "30 mins":
    drive_hours = 0.5
elif drive_time_option == "1 hour":
    drive_hours = 1
else:
    drive_hours = st.sidebar.slider("Custom Drive Time (hours)", 0.0, 5.0, 0.5, step=0.1)

alternator_input_wh = 480 * drive_hours  # 40A × 12V = 480W

# -- DEVICE INPUT --
st.header("Device Usage")
device_count = st.number_input("Number of devices", min_value=1, max_value=10, value=3)
devices = []

for i in range(device_count):
    st.subheader(f"Device {i + 1}")
    name = st.text_input("Name", key=f"name_{i}")
    watts = st.number_input("Power draw (Watts)", key=f"watts_{i}")
    
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

# -- CALCULATIONS --
daily_consumption = sum(w * h for _, w, h in devices)
daily_input = solar_input_wh + alternator_input_wh
net_daily = daily_consumption - daily_input

# -- RESULTS DISPLAY --
st.header("Results Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Capacity", f"{total_capacity_wh} Wh")
col2.metric("Total Daily Usage", f"{daily_consumption} Wh")
col3.metric("Total Daily Input", f"{daily_input} Wh")

# Status Bar
st.subheader("Alfred System Status")

percent_used = min((daily_consumption / total_capacity_wh) * 100, 100)
runtime_days = total_capacity_wh / max(daily_consumption - daily_input, 1)
runtime_hours = runtime_days * 24

st.progress(min(percent_used / 100, 1.0))
st.write(f"**Daily usage is {percent_used:.1f}% of available capacity.**")
st.write(f"**Estimated runtime: {runtime_hours:.1f} hours ({runtime_days:.2f} days)**")

if daily_input >= daily_consumption:
    st.success("System is fully sustainable – inputs exceed usage!")
elif runtime_days >= 3:
    st.info("System is stable – good off-grid performance.")
elif runtime_days < 1:
    st.error("High consumption – consider reducing usage or increasing input.")
else:
    st.warning("Moderate consumption – check solar & alternator charging.")

# -- DEVICE TABLE --
df = pd.DataFrame(devices, columns=["Device", "Watts", "Hours per Day"])
df["Daily Wh"] = df["Watts"] * df["Hours per Day"]
st.dataframe(df)
