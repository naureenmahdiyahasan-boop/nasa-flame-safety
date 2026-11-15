import streamlit as st
import pandas as pd

st.set_page_config(page_title="Flame in Freefall | AI Fire Safety", layout="wide")

st.title("Flame in Freefall: Microgravity Combustion Insights")
st.markdown("Translating **NASA Physical Sciences Informatics (PSI)** microgravity combustion data into actionable fire safety for **Spacecraft Habitats** and **Earth Structures**.")

# 1. Load Real NASA PSI CSV Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/nasa_psi_combustion.csv")
    df = df.fillna({"Oxygen_Pct": 21, "Pressure_kPa": 101, "Flame_Spread_mm_s": 5.0, "Material": "Unspecified"})
    df["Label"] = df["Material"] + " (" + df["Experiment"] + " - " + df["Oxygen_Pct"].astype(str) + "% O2)"
    return df

df = load_data()

# 2. Sidebar: One-Click Mission Presets + Custom Sliders
st.sidebar.header("Mission & Environment Settings")

preset = st.sidebar.selectbox(
    "Quick Mission Preset",
    ["Custom Settings", "ISS Standard Cabin (21% O₂, 101 kPa)", "Artemis Lunar Habitat (34% O₂, 56 kPa)", "Earth Subway / Tunnel (21% O₂, 101 kPa)"]
)

if preset == "ISS Standard Cabin (21% O₂, 101 kPa)":
    default_mode, default_o2, default_kpa = "Spacecraft Habitat (Moon/Mars)", 21, 101
elif preset == "Artemis Lunar Habitat (34% O₂, 56 kPa)":
    default_mode, default_o2, default_kpa = "Spacecraft Habitat (Moon/Mars)", 34, 56
elif preset == "Earth Subway / Tunnel (21% O₂, 101 kPa)":
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
max_flame_spread = st.sidebar.slider("Max Safe Flame Spread (mm/s)", min_value=0.5, max_value=10.0, value=5.0, step=0.5)

# 3. Dynamic Risk Scoring Math & Color-Coded Status
o2_score = (oxygen_pct / df["Oxygen_Pct"]) * 35
spread_score = (df["Flame_Spread_mm_s"] / max_flame_spread) * 35
pressure_score = (df["Pressure_kPa"] / pressure_kpa) * 30

raw_risk = o2_score + spread_score + pressure_score

if mode == "Spacecraft Habitat (Moon/Mars)":
    df["Simulated_Risk"] = (raw_risk * 1.15).clip(1, 100).round(1)
else:
    df["Simulated_Risk"] = (raw_risk * 0.85).clip(1, 100).round(1)

def get_status(score):
    if score >= 75:
        return "🔴 CRITICAL"
    elif score >= 50:
        return "🟡 CAUTION"
    return "🟢 SAFE"

df["Status"] = df["Simulated_Risk"].apply(get_status)
ranked_df = df.sort_values(by="Simulated_Risk", ascending=False)

# 4. Top Summary KPI Strip
kpi1, kpi2, kpi3 = st.columns(3)
top_row = ranked_df.head(1).to_dict(orient="records").pop()
critical_count = int((ranked_df["Simulated_Risk"] >= 75).sum())

kpi1.metric("NASA PSI Test Points", len(ranked_df))
kpi2.metric("Critical Risk Materials (≥75)", f"{critical_count} / {len(ranked_df)}")
kpi3.metric("Highest Risk Material", top_row.get("Material"), f"{top_row.get('Simulated_Risk')} / 100", delta_color="inverse")

st.divider()

# 5. Main Dashboard Layout
col1, col2 = st.columns([1.35, 1])

with col1:
    st.subheader("Experiment Risk Ranking")
    st.caption(f"Simulated for **{mode}** at **{oxygen_pct}% O₂**, **{pressure_kpa} kPa**, and **{max_flame_spread} mm/s** spread limit.")
    
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

    st.info(f"**Selected:** {sel_mat} ({sel_exp}) — **{sel_status}** ({sel_risk}/100)")

    user_question = st.text_input("Optional: Ask a custom safety question about this material", placeholder="e.g., How should we suppress this fire in low gravity?")

    if st.button("Generate AI Risk Assessment", type="primary", use_container_width=True):
        if mode == "Spacecraft Habitat (Moon/Mars)":
            st.warning(
                f"**Spacecraft Habitat Assessment ({oxygen_pct}% O₂ | {pressure_kpa} kPa):**\n\n"
                f"In NASA **{sel_exp}** testing, **{sel_mat}** recorded a flame spread rate of **{sel_spread} mm/s**, resulting in a **{sel_status}** simulated risk score of **{sel_risk}/100** under your cabin settings. "
                f"In reduced gravity, hot gases do not rise to cool the flame, allowing fire to linger and spread along cabin surfaces.\n\n"
                f"**Recommended Action:** Isolate **{sel_mat}** near electrical wiring, shut off cabin air circulation immediately upon smoke detection, and deploy localized fire suppression."
            )
        else:
            st.success(
                f"**Earth Fire Safety Assessment ({oxygen_pct}% O₂ | {sel_spread} mm/s Spread Rate):**\n\n"
                f"Microgravity data from NASA **{sel_exp}** isolates how **{sel_mat}** burns at **{sel_spread} mm/s** when buoyant airflow is removed—mirroring hidden fires inside building wall cavities, subway tunnels, and aircraft cargo holds.\n\n"
                f"**Recommended Action:** Apply flame-retardant barriers around **{sel_mat}** and install early optical smoke sensors in low-ventilation zones."
            )
        if user_question:
            st.write(f"**Response to your query (*\"{user_question}\"*):** Based on **{sel_exp}** parameters ({sel_spread} mm/s spread at {oxygen_pct}% O₂), prioritize oxygen isolation and non-conductive extinguishing agents tailored for **{sel_mat}**.")

st.caption("Data Source: NASA Physical Sciences Informatics (PSI) Open Data Repository | Built for NASA Space Apps Challenge")
