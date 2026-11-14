import streamlit as st
import pandas as pd

st.set_page_config(page_title="Flame in Freefall | AI Fire Safety", layout="wide")

st.title("Flame in Freefall: Microgravity Combustion Insights")
st.markdown("Explore NASA Physical Sciences Informatics (PSI) data for spacecraft and Earth fire safety.")

# Sidebar controls for mission parameters
st.sidebar.header("Environment Parameters")
mode = st.sidebar.radio("Application Focus", ["Spacecraft Habitat (Moon/Mars)", "Earth Fire Safety"])
oxygen_pct = st.sidebar.slider("Oxygen Concentration (%)", min_value=15, max_value=40, value=21)
pressure_kpa = st.sidebar.slider("Cabin Pressure (kPa)", min_value=50, max_value=105, value=101)

# Main dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("NASA PSI Experiment Risk Ranking")
    st.info(f"Filtering combustion experiments near {oxygen_pct}% O2 and {pressure_kpa} kPa...")

with col2:
    st.subheader("AI Safety Briefing")
    if st.button("Generate AI Risk Assessment"):
        st.success(f"AI Summary ready for {mode} at {oxygen_pct}% O2.")
