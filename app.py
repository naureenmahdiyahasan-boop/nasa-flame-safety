import streamlit as st
import pandas as pd

st.set_page_config(page_title="Flame in Freefall | AI Fire Safety", layout="wide")

st.title("Flame in Freefall: Microgravity Combustion Insights")
st.markdown("Translating **NASA Physical Sciences Informatics (PSI)** microgravity combustion data into actionable fire safety for **Spacecraft Habitats** and **Earth Structures**.")

# 1. Load Real NASA PSI CSV Data (Deduplicated so bars never stack)
@st.cache_data
def load_data():
    df = pd.read_csv("data/nasa_psi_combustion.csv")
    df.columns = df.columns.str.strip()
    df["Experiment"] = df["Experiment"].astype(str).str.strip()
    df["Material"] = df["Material"].astype(str).str.strip()
    for col in ["Oxygen_Pct", "Pressure_kPa", "Flame_Spread_mm_s"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.fillna({"Oxygen_Pct": 21.0, "Pressure_kPa": 101.0, "Material": "Unspecified"})
    df = df.drop_duplicates(subset=["Experiment", "Material", "Oxygen_Pct", "Pressure_kPa"]).reset_index(drop=True)
    df["Label"] = df["Material"] + " (" + df["Experiment"] + " - " + df["Oxygen_Pct"].astype(str) + "% O2)"
    return df

df = load_data()

# 2. Sidebar: One-Click Mission Presets + Cabin Environment Controls
st.sidebar.header("Mission & Environment Settings")

preset = st.sidebar.selectbox(
    "Quick Mission Preset",
    ["Custom Settings", "ISS Standard Cabin (21% O2, 101 kPa)", "Artemis Lunar Habitat (34% O2, 56 kPa)", "Earth Subway / Tunnel (21% O2, 101 kPa)"]
)

if preset == "ISS Standard Cabin (21% O2, 101 kPa)":
    default_mode, default_o2, default_kpa = "Spacecraft Habitat (Moon/Mars)", 21, 101
elif preset == "Artemis Lunar Habitat (34% O2, 56 kPa)":
    default_mode, default_o2, default_kpa = "Spacecraft Habitat (Moon/Mars)", 34, 56
elif preset == "Earth Subway / Tunnel (21% O2, 101 kPa)":
    default_mode, default_o2, default_kpa = "Earth Fire Safety", 21, 101
else:
    default_mode, default_o2, default_kpa = "Spacecraft Habitat (Moon/Mars)", 21, 101

mode = st.sidebar.radio(
    "Application Focus",
    ["Spacecraft Habitat (Moon/Mars)", "Earth Fire Safety"],
    index=0 if default_mode == "Spacecraft Habitat (Moon/Mars)" else 1
)

if mode == "Spacecraft Habitat (Moon/Mars)":
    st.sidebar.caption("Applies strict reduced-gravity safety margins for Moon/Mars exploration cabins.")
else:
    st.sidebar.caption("Applies microgravity baseline burn rates to low-ventilation Earth spaces (tunnels, aircraft, wall cavities).")

oxygen_pct = st.sidebar.slider("Oxygen Concentration (%)", min_value=15, max_value=40, value=default_o2)
pressure_kpa = st.sidebar.slider("Cabin Pressure (kPa)", min_value=50, max_value=105, value=default_kpa)

# 3. Calibrated Dynamic Risk Scoring Math & Color-Coded Status
o2_term = ((oxygen_pct - 15) / 25) * 42
spread_term = (((df["Flame_Spread_mm_s"] / 2.5).clip(0, 1.5) / 1.5) * 35).fillna(0)
pressure_term = max(0.0, min(1.0, (105 - pressure_kpa) / 55)) * 23

raw_risk = o2_term + spread_term + pressure_term

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
    st.caption(f"Simulated for **{mode}** at **{oxygen_pct}% O2** and **{pressure_kpa} kPa**.")
    
    st.bar_chart(ranked_df.set_index("Label")["Simulated_Risk"])
    st.dataframe(
        ranked_df[["Status", "Experiment", "Material", "Oxygen_Pct", "Pressure_kPa", "Flame_Spread_mm_s", "Simulated_Risk"]],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("AI Mission Safety Briefing")
    selected_label = st.selectbox("Inspect Specific NASA Experiment:", ranked_df["Label"].tolist())
    sel_row = ranked_df[ranked_df["Label"] == selected_label].head(1).to_dict(orient="records").pop()

    sel_mat = sel_row.get("Material")
    sel_exp = sel_row.get("Experiment")
    sel_risk = sel_row.get("Simulated_Risk")
    sel_spread = sel_row.get("Flame_Spread_mm_s")
    sel_status = sel_row.get("Status")
    spread_text = f"{sel_spread} mm/s" if pd.notna(sel_spread) else "unreported (NaN)"

    st.info(f"**Selected:** {sel_mat} ({sel_exp}) — **{sel_status}** ({sel_risk}/100)")

    if "SAFFIRE" in sel_exp.upper():
        st.caption("**Hardware & Focus:** Large-scale solid material flammability test conducted aboard an uncrewed Cygnus resupply spacecraft.")
    elif "BASS" in sel_exp.upper():
        st.caption("**Hardware & Focus:** Solid fuel burning and suppression testing inside the ISS Microgravity Science Glovebox (MSG).")
    elif "SOFIE" in sel_exp.upper():
        st.caption("**Hardware & Focus:** Solid fuel ignition and growth testing inside the ISS Combustion Integrated Rack (CIR).")
    elif "BRE" in sel_exp.upper():
        st.caption("**Hardware & Focus:** Condensed-phase solid fuel emulation inside the ISS Combustion Integrated Rack (ACME/CIR).")
    elif "FLEX" in sel_exp.upper():
        st.caption("**Hardware & Focus:** Liquid fuel droplet combustion & extinguishment inside the ISS Combustion Integrated Rack (MDCA/CIR).")

    user_question = st.text_input("Optional: Ask a custom safety question about this material", placeholder="e.g., How should we suppress this fire in low gravity?")

    if st.button("Generate AI Risk Assessment", type="primary", use_container_width=True):
        if mode == "Spacecraft Habitat (Moon/Mars)":
            st.warning(
                f"**Spacecraft Habitat Assessment ({oxygen_pct}% O2 | {pressure_kpa} kPa):**\n\n"
                f"In NASA **{sel_exp}** testing, **{sel_mat}** recorded a flame spread rate of **{spread_text}**, resulting in a **{sel_status}** simulated risk score of **{sel_risk}/100** under your cabin settings. "
                f"In reduced gravity, hot gases do not rise to cool the flame, allowing fire to linger and spread along cabin surfaces.\n\n"
                f"**Recommended Action:** Isolate **{sel_mat}** near electrical wiring, shut off cabin air circulation immediately upon smoke detection, and deploy localized fire suppression."
            )
        else:
            st.success(
                f"**Earth Fire Safety Assessment ({oxygen_pct}% O2 | {spread_text} Spread Rate):**\n\n"
                f"Microgravity data from NASA **{sel_exp}** isolates how **{sel_mat}** burns at **{spread_text}** when buoyant airflow is removed—mirroring hidden fires inside building wall cavities, subway tunnels, and aircraft cargo holds.\n\n"
                f"**Recommended Action:** Apply flame-retardant barriers around **{sel_mat}** and install early optical smoke sensors in low-ventilation zones."
            )
        if user_question:
            st.write(f"**Response to your query (*\"{user_question}\"*):** Based on **{sel_exp}** parameters ({spread_text} spread at {oxygen_pct}% O2), prioritize oxygen isolation and non-conductive extinguishing agents tailored for **{sel_mat}**.")

st.caption("Data Source: NASA Physical Sciences Informatics (PSI) Open Data Repository | Built for NASA Space Apps Challenge")
