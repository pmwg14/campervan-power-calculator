import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Alfred v5 – Power Calculator", layout="wide")

# --- Preset 12V Devices ---
preset_devices = [
    {"name": "LED Puck Lights", "watts": 12, "hours": 6, "enabled": True},
    {"name": "LED Strip Light", "watts": 6, "hours": 4, "enabled": True},
    {"name": "Reading Light", "watts": 3, "hours": 2, "enabled": False},
    {"name": "Compressor Fridge", "watts": 50, "hours": 8, "enabled": True},
    {"name": "MaxxFan", "watts": 30, "hours": 4, "enabled": True},
    {"name": "Diesel Heater", "watts": 20, "hours": 2, "enabled": True},
    {"name": "Water Pump", "watts": 50, "hours": 0.2, "enabled": False},
    {"name": "Phone Charging", "watts": 10, "hours": 2, "enabled": True},
    {"name": "Tablet Charging", "watts": 15, "hours": 1, "enabled": False},
    {"name": "Router (GL.iNet)", "watts": 5, "hours": 24, "enabled": True},
    {"name": "Renogy One Core", "watts": 2, "hours": 24, "enabled": True}
]

# --- Sidebar Config ---
st.sidebar.header("Battery & Input Settings")
battery_count = st.sidebar.slider("Renogy 200Ah Batteries", 1, 4, 3)
battery_wh = battery_count * 200 * 12

eco_flow_toggle = st.sidebar.checkbox("Add EcoFlow Delta Pro (3.6kWh)")
total_capacity = battery_wh + (3600 if eco_flow_toggle else 0)

solar_watts = st.sidebar.number_input("Solar Panel Total (W)", value=360, step=10)
solar_hours = st.sidebar.slider("Solar Hours per Day", 0, 10, 4)
solar_input_daily = solar_watts * solar_hours

drive_hours = st.sidebar.slider("Drive Time per Day (hrs)", 0.0, 5.0, 0.5, step=0.1)
alternator_input_daily = 480 * drive_hours  # 40A * 12V

# --- Main Interface ---
st.title("Alfred v5 – Campervan Power Calculator")

st.subheader("Select Devices to Include")
show_enabled_only = st.checkbox("Show only selected devices", value=False)

# --- Device Table with Toggle ---
enabled_devices = []
with st.form("device_form"):
    for i, device in enumerate(preset_devices):
        if not show_enabled_only or device["enabled"]:
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                name = st.text_input("Name", value=device["name"], key=f"name_{i}")
            with cols[1]:
                watts = st.number_input("Watts", min_value=1, value=device["watts"], key=f"watts_{i}")
            with cols[2]:
                hours = st.number_input("Hours/day", min_value=0.0, max_value=24.0, step=0.5, value=float(device["hours"]), key=f"hours_{i}")
            with cols[3]:
                enabled = st.checkbox("On?", value=device["enabled"], key=f"enabled_{i}")
            if enabled:
                enabled_devices.append({"name": name, "watts": watts, "hours": hours})
    st.form_submit_button("Update Devices")

# --- Add Custom Device ---
st.markdown("### Add Custom Device")
with st.form("custom_device"):
    c_name = st.text_input("Device Name")
    c_watts = st.number_input("Watts", min_value=1, value=10, step=1)
    c_hours = st.number_input("Hours/day", min_value=0.0, max_value=24.0, step=0.5)
    add_custom = st.form_submit_button("Add Device")
    if add_custom and c_name:
        enabled_devices.append({"name": c_name, "watts": c_watts, "hours": c_hours})
        st.success(f"Added {c_name} to your setup!")

# --- Power Calculations ---
df = pd.DataFrame(enabled_devices)
df["Daily_Wh"] = df["watts"] * df["hours"]
daily_usage = df["Daily_Wh"].sum()
daily_input = solar_input_daily + alternator_input_daily
net_daily = daily_input - daily_usage

# --- Summary ---
st.subheader("System Summary")
st.write(f"**Total Battery Capacity:** {total_capacity} Wh")
st.write(f"**Daily Usage:** {daily_usage:.0f} Wh")
st.write(f"**Daily Input (Solar + Alternator):** {daily_input:.0f} Wh")
st.write(f"**Net Daily Power Balance:** {net_daily:.0f} Wh")

# --- Daily Power Breakdown (Stacked Bar using Altair) ---
st.subheader("Daily Power Breakdown")

# Build dataframe
df_stacked = pd.DataFrame({
    "Source": ["Solar", "Alternator", "Usage"],
    "Type": ["Input", "Input", "Output"],
    "Watt-Hours": [solar_input_daily, alternator_input_daily, daily_usage]
})

# Create stacked bar chart using Altair
bar = alt.Chart(df_stacked).mark_bar().encode(
    x=alt.X('Type:N', title=None),
    y=alt.Y('Watt-Hours:Q', title="Watt-Hours"),
    color=alt.Color('Source:N', scale=alt.Scale(scheme='rainbow')),
    tooltip=['Source', 'Watt-Hours']
).properties(
    width=300,
    height=400
)

st.altair_chart(bar, use_container_width=True)