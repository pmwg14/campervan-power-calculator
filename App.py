# ALFRED v8 – Dual Power System Campervan Calculator
import streamlit as st
import pandas as pd
import altair as alt
import random
import time

st.set_page_config(page_title="Alfred v8 – Campervan Power Calculator", layout="wide")

# --- Default Presets ---
renogy_presets = [
    {"name": "LED Puck Lights", "watts": 12, "hours": 6, "enabled": True},
    {"name": "Laptop (DC)", "watts": 65, "hours": 8, "enabled": True},
    {"name": "Fridge", "watts": 50, "hours": 10, "enabled": True},
    {"name": "MaxxFan", "watts": 30, "hours": 4, "enabled": True},
    {"name": "Diesel Heater", "watts": 20, "hours": 2, "enabled": True},
    {"name": "Phone Charging", "watts": 10, "hours": 2, "enabled": True},
    {"name": "Starlink", "watts": 45, "hours": 10, "enabled": True},
    {"name": "GL.iNet Router", "watts": 5, "hours": 24, "enabled": True},
    {"name": "Renogy One Core", "watts": 2, "hours": 24, "enabled": True}
]

ecoflow_presets = [
    {"name": "Air Fryer", "watts": 800, "hours": 0.5, "enabled": True},
    {"name": "Nespresso", "watts": 1200, "hours": 0.3, "enabled": True},
    {"name": "Induction Hob", "watts": 1800, "hours": 1.0, "enabled": True},
    {"name": "Hairdryer", "watts": 1000, "hours": 0.2, "enabled": False},
    {"name": "Electric Kettle", "watts": 1200, "hours": 0.3, "enabled": True},
    {"name": "Microwave", "watts": 1000, "hours": 0.5, "enabled": False},
    {"name": "Laptop Charger (AC)", "watts": 90, "hours": 4.0, "enabled": True}
]

# --- Solar Hours Presets ---
solar_efficiency_map = {"Low": 1.5, "Medium": 3.5, "High": 5.5}

# --- Sidebar ---
st.sidebar.header("System Configuration")

solar_eff_level = st.sidebar.selectbox("UK Solar Efficiency", options=list(solar_efficiency_map.keys()), index=1)
solar_hours = solar_efficiency_map[solar_eff_level]

# Renogy config
show_renogy = st.sidebar.checkbox("Enable Renogy 12V System", value=True)
if show_renogy:
    renogy_batteries = st.sidebar.slider("Renogy 200Ah Batteries", 1, 4, 3)
    renogy_wh = renogy_batteries * 200 * 12
    renogy_solar = st.sidebar.number_input("Renogy Solar (W)", value=400, step=10)
    drive_hours = st.sidebar.slider("Drive Time (hrs/day)", 0.0, 5.0, 0.5, step=0.1)
    alternator_input = 480 * drive_hours  # 40A * 12V
    renogy_input = (renogy_solar * solar_hours) + alternator_input
else:
    renogy_wh, renogy_input = 0, 0

# EcoFlow config
show_ecoflow = st.sidebar.checkbox("Enable EcoFlow 240V System", value=True)
if show_ecoflow:
    ecoflow_wh = 3600
    ecoflow_solar = st.sidebar.number_input("EcoFlow Solar (W)", value=400, step=10)
    ecoflow_input = ecoflow_solar * solar_hours
else:
    ecoflow_wh, ecoflow_input = 0, 0

# --- Tabs for Devices ---
tab1, tab2 = st.tabs(["Renogy Devices", "EcoFlow Devices"])

with tab1:
    st.subheader("Renogy 12V Devices")
    if st.button("Quick Add Renogy Presets"):
        st.session_state.renogy_devices = renogy_presets.copy()
    renogy_devices = st.session_state.get("renogy_devices", renogy_presets.copy())
    enabled_renogy = []
    with st.form("renogy_form"):
        for i, d in enumerate(renogy_devices):
            cols = st.columns([3, 1, 1, 1])
            d["name"] = cols[0].text_input("Name", d["name"], key=f"rname_{i}")
            d["watts"] = cols[1].number_input("W", 1, 5000, d["watts"], key=f"rwatts_{i}")
            d["hours"] = cols[2].number_input("Hrs", 0.0, 24.0, float(d["hours"]), step=0.5, key=f"rhrs_{i}")
            d["enabled"] = cols[3].checkbox("On?", d["enabled"], key=f"renabled_{i}")
            if d["enabled"]:
                enabled_renogy.append(d)
        st.session_state.renogy_devices = renogy_devices
        st.form_submit_button("Update Renogy Devices")

with tab2:
    st.subheader("EcoFlow 240V Devices")
    if st.button("Quick Add EcoFlow Presets"):
        st.session_state.ecoflow_devices = ecoflow_presets.copy()
    ecoflow_devices = st.session_state.get("ecoflow_devices", ecoflow_presets.copy())
    enabled_ecoflow = []
    with st.form("ecoflow_form"):
        for i, d in enumerate(ecoflow_devices):
            cols = st.columns([3, 1, 1, 1])
            d["name"] = cols[0].text_input("Name", d["name"], key=f"ename_{i}")
            d["watts"] = cols[1].number_input("W", 1, 5000, d["watts"], key=f"ewatts_{i}")
            d["hours"] = cols[2].number_input("Hrs", 0.0, 24.0, float(d["hours"]), step=0.5, key=f"ehrs_{i}")
            d["enabled"] = cols[3].checkbox("On?", d["enabled"], key=f"eenabled_{i}")
            if d["enabled"]:
                enabled_ecoflow.append(d)
        st.session_state.ecoflow_devices = ecoflow_devices
        st.form_submit_button("Update EcoFlow Devices")

# --- Power Calculations ---
df_r = pd.DataFrame(enabled_renogy)
df_r["Wh"] = df_r["watts"] * df_r["hours"]
renogy_usage = df_r["Wh"].sum() if not df_r.empty else 0

df_e = pd.DataFrame(enabled_ecoflow)
df_e["Wh"] = df_e["watts"] * df_e["hours"]
ecoflow_usage = df_e["Wh"].sum() if not df_e.empty else 0

total_capacity = renogy_wh + ecoflow_wh
total_input = renogy_input + ecoflow_input
total_usage = renogy_usage + ecoflow_usage
net_balance = total_input - total_usage

# --- Combined Summary ---
st.header("Alfred System Summary")

st.write(f"**Total System Capacity:** {total_capacity:.0f} Wh ({total_capacity / 12:.1f} Ah)")
st.write(f"**Total Daily Usage:** {total_usage:.0f} Wh ({total_usage / 12:.1f} Ah)")
st.write(f"**Total Daily Input:** {total_input:.0f} Wh ({total_input / 12:.1f} Ah)")
st.write(f"**Net Power Balance:** {net_balance:.0f} Wh ({net_balance / 12:.1f} Ah)")

# --- Visual Battery Indicator ---
st.subheader("Battery Endurance")
if total_usage <= total_input:
    fill = 100
    status = "Sustainable – Infinite Runtime"
    emoji = "🔋"
else:
    days = total_capacity / (total_usage - total_input)
    fill = min((days / 5) * 100, 100)
    status = f"{round(days * 2) / 2} days of power remaining"
    emoji = "🪫" if fill < 20 else "🟨" if fill < 66 else "🟩"
st.markdown(f"**{emoji} {status}**")
st.progress(int(fill))

# --- EV Recharge Estimate (EcoFlow only) ---
if show_ecoflow:
    st.subheader("EcoFlow EV Recharge Estimate")
    missing_wh = max(0, ecoflow_wh - ecoflow_input)
    ev_recharge_time = missing_wh / 7000  # Assume 7kW charger
    st.write(f"To recharge your EcoFlow from solar input to full using a 7kW EV charger would take **{ev_recharge_time:.2f} hours**.")

# --- Daily Power Chart ---
st.subheader("Daily Power Distribution")

df_chart = pd.DataFrame({
    "Source": ["Renogy Input", "EcoFlow Input", "Renogy Usage", "EcoFlow Usage"],
    "Wh": [renogy_input, ecoflow_input, -renogy_usage, -ecoflow_usage]
})
df_chart["% of Capacity"] = (df_chart["Wh"] / total_capacity) * 100

bar = alt.Chart(df_chart).mark_bar().encode(
    x=alt.X('Source:N'),
    y=alt.Y('% of Capacity:Q'),
    color=alt.Color('Source:N', scale=alt.Scale(scheme='category20b')),
    tooltip=["Source", "Wh", "% of Capacity"]
).properties(width=600, height=400)

st.altair_chart(bar, use_container_width=True)

# --- Rotating Footer Quote ---
quotes = [
    "“Because it’s there.” – George Mallory",
    "“The best view comes after the hardest climb.” – Unknown",
    "“It is not the mountain we conquer, but ourselves.” – Sir Edmund Hillary",
    "“Getting to the top is optional. Getting down is mandatory.” – Ed Viesturs",
    "“In every walk with nature, one receives far more than he seeks.” – John Muir",
    "“Only those who risk going too far can possibly find out how far they can go.” – T.S. Eliot",
    "“Mountains teach that not everything in life can be rationally explained.” – Aleksander Lwow",
    "“Climb the mountain not to plant your flag, but to embrace the challenge.” – David McCullough Jr.",
    "“There are no shortcuts to any place worth going.” – Beverly Sills",
    "“A man does not climb a mountain without bringing some of it away with him.” – Martin Conway"
]

st.markdown("---")
if st.button("Start Quote Rotation"):
    quote_box = st.empty()
    for _ in range(100):
        quote_box.markdown(
            f"<div style='text-align: center; font-style: italic; opacity: 0.6;'>{random.choice(quotes)}</div>",
            unsafe_allow_html=True
        )
        time.sleep(5)