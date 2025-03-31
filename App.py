import streamlit as st
import pandas as pd

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

solar_watts = st.sidebar.number_input("Solar Panel Total (W)", value=400, step=10)
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

# --- Chart over 7 Days using Streamlit-native charts ---
st.subheader("7-Day Power Profile")

df_chart = pd.DataFrame({
    "Day": list(range(1, 8)),
    "Usage (Wh)": [daily_usage] * 7,
    "Solar Input (Wh)": [solar_input_daily] * 7,
    "Alternator Input (Wh)": [alternator_input_daily] * 7
})

df_chart["Total Input (Wh)"] = df_chart["Solar Input (Wh)"] + df_chart["Alternator Input (Wh)"]
df_chart["Net Daily Balance (Wh)"] = df_chart["Total Input (Wh)"] - df_chart["Usage (Wh)"]

st.line_chart(
    df_chart.set_index("Day")[["Usage (Wh)", "Total Input (Wh)"]],
    use_container_width=True
)

st.bar_chart(
    df_chart.set_index("Day")[["Net Daily Balance (Wh)"]],
    use_container_width=True
)