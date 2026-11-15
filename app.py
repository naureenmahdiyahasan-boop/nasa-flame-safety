import streamlit as st
import pandas as pd

st.set_page_config(page_title="Flame in Freefall | AI Fire Safety", layout="wide")

st.title("Flame in Freefall: Microgravity Combustion Insights")
st.markdown("Translating **NASA Physical Sciences Informatics (PSI)** microgravity combustion data into actionable fire safety for **Spacecraft Habitats** and **Earth Structures**.")

# 1. Load Curated 35-Row NASA PSI CSV Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/nasa_psi_combustion.csv")
    df.columns = df.columns.str.strip()
    for col in ["Oxygen_Pct", "Pressure_kPa", "Airflow_cm_s", "Burn_Or_Spread_Rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.fillna({"Oxygen_Pct": 21.0, "Pressure_kPa": 101.3, "Airflow_cm_s": 0.0, "Burn_Or_Spread_Rate": 0.0})
    df["Label"] = df["Material"] + " [" + df["Record_ID"] + "]"
    df = df.drop_duplicates(subset=["Label"]).reset_index(drop=True)
    return df

df = load_data()

# 2. Sidebar: One-Click Mission Presets + Cabin Environment Controls (Includes Airflow)
st.sidebar.header("Mission & Environment Settings")

preset = st.sidebar.selectbox(
    "Quick Mission Preset",
    ["Custom Settings", "ISS Standard Cabin (21% O2, 101 kPa, 15 cm/s)", "Artemis Lunar Habitat (34% O2, 56 kPa, 20 cm/s)", "Earth Subway / Tunnel (21% O2, 101 kPa, 5 cm/s)"]
)

if preset == "ISS Standard Cabin (21% O2, 101 kPa, 15 cm/s)":
    default_mode, default_o2, default_kpa, default_flow = "Spacecraft Habitat (Moon/Mars)", 21, 101, 15
elif preset == "Artemis Lunar Habitat (34% O2, 56 kPa, 20 cm/s)":
    default_mode, default_o2, default_kpa, default_flow = "Spacecraft Habitat (Moon/Mars)", 34, 56, 20
elif preset == "Earth Subway / Tunnel (21% O2, 101 kPa, 5 cm/s)":
    default_mode, default_o2, default_kpa, default_flow = "Earth Fire Safety", 21, 101, 5
else:
    default_mode, default_o2, default_kpa, default_flow = "Spacecraft Habitat (Moon/Mars)", 21, 101, 15

mode = st.sidebar.radio(
    "Application Focus",
    ["Spacecraft Habitat (Moon/Mars)", "Earth Fire Safety"],
    index=0 if default_mode == "Spacecraft Habitat (Moon/Mars)" else 1
)

if mode == "Spacecraft Habitat (Moon/Mars)":
    st.sidebar.caption("Applies strict reduced-gravity safety margins for Moon/Mars exploration cabins.")
else:
    st.sidebar.caption("Applies microgravity baseline burn rates to low-ventilation Earth spaces (tunnels, aircraft, wall cavities).")

oxygen_pct = st.sidebar.slider("Oxygen Concentration (%)", min_value=12, max_value=40, value=default_o2)
pressure_kpa = st.sidebar.slider("Cabin Pressure (kPa)", min_value=50, max_value=310, value=default_kpa)
airflow_cm_s = st.sidebar.slider("Cabin Ventilation Airflow (cm/s)", min_value=0, max_value=30, value=default_flow)

# 3. Calibrated Dynamic Risk Scoring Math (Oxygen + Burn/Spread Rate + Pressure + Airflow)
o2_term = ((oxygen_pct - 12) / 28) * 35
rate_term = ((df["Burn_Or_Spread_Rate"] / 2.0).clip(0, 1.3) / 1.3) * 32
pressure_term = max(0.0, min(1.0, (110 - pressure_kpa) / 60)) * 18
airflow_term = (airflow_cm_s / 30) * 10 + (df["Airflow_cm_s"] / 20) * 5

raw_risk = o2_term + rate_term + pressure_term + airflow_term

if mode == "Spacecraft Habitat (Moon/Mars)":
    df["Simulated_Risk"] = raw_risk.clip(1, 100).round(1)
else:
    df["Simulated_Risk"] = (raw_risk * 0.78).clip(1, 100).round(1)

def get_status(score):
    if score >= 60:
        return "🔴 CRITICAL"
    elif score >= 38:
        return "🟡 CAUTION"
    return "🟢 SAFE"

df["Status"] = df["Simulated_Risk"].apply(get_status)
ranked_df = df.sort_values(by="Simulated_Risk", ascending=False)

# 4. Top Summary KPI Strip
kpi1, kpi2, kpi3 = st.columns(3)
top_row = ranked_df.head(1).to_dict(orient="records").pop()
critical_count = int((ranked_df["Simulated_Risk"] >= 60).sum())

kpi1.metric("NASA PSI Test Points", len(ranked_df))
kpi2.metric("Critical Risk Materials (>=60)", f"{critical_count} / {len(ranked_df)}")
kpi3.metric("Highest Risk Material", top_row.get("Material"), f"{top_row.get('Simulated_Risk')} / 100", delta_color="inverse")

st.divider()

# 5. Main Dashboard Layout
col1, col2 = st.columns([1.35, 1])

with col1:
    st.subheader("Experiment Risk Ranking")
    st.caption(f"Simulated for **{mode}** at **{oxygen_pct}% O2**, **{pressure_kpa} kPa**, and **{airflow_cm_s} cm/s** airflow.")
    
    st.bar_chart(ranked_df.set_index("Label")["Simulated_Risk"])
    st.dataframe(
        ranked_df[["Status", "Record_ID", "Experiment", "Material", "Oxygen_Pct", "Pressure_kPa", "Airflow_cm_s", "Burn_Or_Spread_Rate", "Simulated_Risk"]],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("AI Mission Safety Briefing")
    selected_label = st.selectbox("Inspect Specific NASA Experiment:", ranked_df["Label"].tolist())
    sel_row = ranked_df[ranked_df["Label"] == selected_label].head(1).to_dict(orient="records").pop()

    sel_id = sel_row.get("Record_ID")
    sel_mat = sel_row.get("Material")
    sel_exp = sel_row.get("Experiment")
    sel_risk = sel_row.get("Simulated_Risk")
    sel_rate = sel_row.get("Burn_Or_Spread_Rate")
    sel_flow = sel_row.get("Airflow_cm_s")
    sel_status = sel_row.get("Status")
    unit_text = "mm/s (flame spread)" if sel_exp in ["BASS", "SAFFIRE-2"] else "mm2/s (droplet burn rate)"

    st.info(f"**Selected:** {sel_mat} (`{sel_id}`) — **{sel_status}** ({sel_risk}/100)")

    if sel_exp == "SAFFIRE-2":
        st.caption("**Hardware & Focus:** Large-scale solid material flammability test conducted aboard an uncrewed Cygnus resupply spacecraft.")
    elif sel_exp == "BASS":
        st.caption("**Hardware & Focus:** Solid fuel burning and suppression testing inside the ISS Microgravity Science Glovebox (MSG).")
    elif sel_exp == "FLEX":
        st.caption("**Hardware & Focus:** Liquid fuel droplet combustion & extinguishment inside the ISS Combustion Integrated Rack (MDCA/CIR).")

    user_question = st.text_input("Optional: Ask a custom safety question about this material", placeholder="e.g., How should we suppress this fire in low gravity?")

    if st.button("Generate AI Risk Assessment", type="primary", use_container_width=True):
        if mode == "Spacecraft Habitat (Moon/Mars)":
            st.warning(
                f"**Spacecraft Habitat Assessment ({oxygen_pct}% O2 | {pressure_kpa} kPa | {airflow_cm_s} cm/s Airflow):**\n\n"
                f"In NASA **{sel_exp}** record **`{sel_id}`** (test flow {sel_flow} cm/s), **{sel_mat}** recorded a rate of **{sel_rate} {unit_text}**, resulting in a **{sel_status}** simulated risk score of **{sel_risk}/100** under your cabin settings. "
                f"In reduced gravity, cabin ventilation feeds oxygen directly to the flame front without natural buoyancy cooling.\n\n"
                f"**Recommended Action:** Shut down cabin HVAC circulation immediately upon smoke detection, isolate **{sel_mat}** near electrical wiring, and deploy localized fire suppression."
            )
        else:
            st.success(
                f"**Earth Fire Safety Assessment ({oxygen_pct}% O2 | {airflow_cm_s} cm/s Airflow | {sel_rate} {unit_text}):**\n\n"
                f"Microgravity data from NASA **{sel_exp}** (`{sel_id}`) isolates how **{sel_mat}** burns at **{sel_rate} {unit_text}** under controlled airflow ({sel_flow} cm/s)—mirroring hidden fires inside building wall cavities, HVAC ducts, subway tunnels, and aircraft cargo holds.\n\n"
                f"**Recommended Action:** Install automatic HVAC damper shutoffs and flame-retardant barriers around **{sel_mat}**."
            )
        if user_question:
            st.write(f"**Response to your query (*\"{user_question}\"*):** Based on **{sel_id}** ({sel_rate} {unit_text} at {oxygen_pct}% O2 and {airflow_cm_s} cm/s flow), prioritize immediate ventilation shutoff and non-conductive extinguishing agents tailored for **{sel_mat}**.")

st.caption("Data Source: NASA Physical Sciences Informatics (PSI) Open Data Repository | Built for NASA Space Apps Challenge")
