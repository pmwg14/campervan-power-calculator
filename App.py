# ALFRED v8.1 – Dual System Campervan Power Calculator with System Components & Dev Mode
import streamlit as st
import pandas as pd
import altair as alt
import random
import time
import inspect

st.set_page_config(page_title="Alfred v8.1 – Campervan Power Calculator", layout="wide")

# --- Device Presets ---
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

solar_efficiency_map = {"Low": 1.5, "Medium": 3.5, "High": 5.5}

# --- Sidebar Config ---
st.sidebar.header("System Configuration")

solar_eff_level = st.sidebar.selectbox("UK Solar Efficiency", options=list(solar_efficiency_map.keys()), index=1)
solar_hours = solar_efficiency_map[solar_eff_level]

show_renogy = st.sidebar.checkbox("Enable Renogy 12V System", value=True)
if show_renogy:
    renogy_batteries = st.sidebar.slider("Renogy 200Ah Batteries", 1, 4, 3)
    renogy_wh = renogy_batteries * 200 * 12
    renogy_solar = st.sidebar.number_input("Renogy Solar (W)", value=360, step=10)
    drive_hours = st.sidebar.slider("Drive Time (hrs/day)", 0.0, 5.0, 0.5, step=0.1)
    alternator_input = 480 * drive_hours  # 40A * 12V
    renogy_input = (renogy_solar * solar_hours) + alternator_input
else:
    renogy_wh, renogy_input = 0, 0

show_ecoflow = st.sidebar.checkbox("Enable EcoFlow 240V System", value=True)
if show_ecoflow:
    ecoflow_wh = 3600
    ecoflow_solar = st.sidebar.number_input("EcoFlow Solar (W)", value=400, step=10)
    ecoflow_input = ecoflow_solar * solar_hours
else:
    ecoflow_wh, ecoflow_input = 0, 0
    
    # --- Device Tabs ---
tab1, tab2, tab3 = st.tabs(["Renogy Devices", "EcoFlow Devices", "System Components"])

# --- Renogy Devices Tab ---
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

# --- EcoFlow Devices Tab ---
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

# --- Summary Display ---
st.header("Alfred System Summary")

st.write(f"**Total System Capacity:** {total_capacity:.0f} Wh ({total_capacity / 12:.1f} Ah)")
st.write(f"**Total Daily Usage:** {total_usage:.0f} Wh ({total_usage / 12:.1f} Ah)")
st.write(f"**Total Daily Input:** {total_input:.0f} Wh ({total_input / 12:.1f} Ah)")
st.write(f"**Net Power Balance:** {net_balance:.0f} Wh ({net_balance / 12:.1f} Ah)")

# --- Battery Endurance ---
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

# --- EV Recharge Estimate ---
if show_ecoflow:
    st.subheader("EcoFlow EV Recharge Estimate")
    missing_wh = max(0, ecoflow_wh - ecoflow_input)
    ev_recharge_time = missing_wh / 7000  # 7kW EV charger
    st.write(f"To recharge your EcoFlow using a 7kW EV charger would take approx **{ev_recharge_time:.2f} hours**.")

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

# --- System Components Tab ---
with tab3:
    st.subheader("System Components")
    components = [
        {
            "name": "Renogy 200Ah Core Battery (x3)",
            "desc": "Primary 12V lithium storage bank",
            "fuse": "400A ANL main fuse",
            "wire": "2/0 AWG tinned copper",
            "placement": "Between batteries and busbar"
        },
        {
            "name": "EcoFlow Delta Pro",
            "desc": "Standalone 240V power system with internal BMS",
            "fuse": "None required",
            "wire": "Proprietary",
            "placement": "AC appliances direct via inverter"
        },
        {
            "name": "Renogy ShadowFlux 120W Panels (x3, 360W)",
            "desc": "Flat-mounted, anti-shade solar panels",
            "fuse": "20A inline MC4 fuses",
            "wire": "10 AWG solar cable",
            "placement": "Panels to MPPT input"
        },
        {
            "name": "Renogy Rover Li 40A MPPT Controller",
            "desc": "Solar charge controller for lithium system",
            "fuse": "40A on output to battery",
            "wire": "6 AWG tinned copper",
            "placement": "Between solar array and battery combiner box"
        },
        {
            "name": "Renogy 500A Combiner Box with Comms",
            "desc": "Connects solar/controller to battery, enables smart monitoring",
            "fuse": "Internal bus protection",
            "wire": "2 AWG to shunt",
            "placement": "Between MPPT and battery/shunt"
        },
        {
            "name": "Renogy Smart Shunt",
            "desc": "Monitors battery state of charge, integrates with One Core",
            "fuse": "1A inline",
            "wire": "16 AWG power wire",
            "placement": "Negative busbar"
        },
        {
            "name": "Renogy One Core Display",
            "desc": "Central monitor for all Renogy system stats",
            "fuse": "Not required (low current)",
            "wire": "16–18 AWG",
            "placement": "Inside living area"
        },
        {
            "name": "Renogy 40A DC-DC Charger",
            "desc": "Charges Renogy bank from vehicle alternator",
            "fuse": "60A on both sides",
            "wire": "4 AWG",
            "placement": "Between starter and leisure batteries"
        },
        {
            "name": "Victron Orion-Tr 12V→24V",
            "desc": "Cross-charges EcoFlow from Renogy in emergencies",
            "fuse": "40A in, 20A out",
            "wire": "8 AWG",
            "placement": "Renogy 12V to EcoFlow XT60i solar input"
        }
    ]

    for comp in components:
        with st.expander(comp["name"]):
            st.markdown(f"**Description:** {comp['desc']}")
            st.markdown(f"**Recommended Fuse:** {comp['fuse']}")
            st.markdown(f"**Wire Gauge:** {comp['wire']}")
            st.markdown(f"**Placement Notes:** {comp['placement']}")

# --- Version Timeline Footer ---
st.markdown("---")
st.markdown("### Alfred Version Timeline")
st.markdown("""
**v8.1** – *“The Wiring Whisperer”* – Apr 2025  
> System Components tab added with install notes, fuse ratings, and wire sizes.  
> Footer redesigned as a readable timeline.  
> Secret Dev Mode toggle added to reveal app code.

**v8.0** – *“Alfred Goes Dual”* – Apr 2025  
> Added EcoFlow system with solar input, power breakdown, EV charge estimates, and tabbed UI.

**v7.2** – *“Visual Vibes”* – Mar 2025  
> Introduced battery endurance visuals, quote rotation, and improved layout.

**v7.0** – *“Alfred Awakens”* – Mar 2025  
> First public version of the Renogy 12V calculator with editable device logic.
""")

# --- Dev Mode Toggle (Safe Version) ---
with st.expander("**Dev Mode: View App Code**"):
    try:
        with open(__file__, "r") as f:
            st.code(f.read())
    except:
        st.warning("Dev Mode unavailable in this environment. Try running locally.")