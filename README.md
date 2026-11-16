# nasa-flame-safety
# Flame in Freefall: Microgravity Combustion Insights

**Translating NASA Physical Sciences Informatics (PSI) microgravity combustion data into actionable fire safety for Spacecraft Habitats and Earth Structures.**

Built for the **NASA Space Apps Challenge**, this interactive Streamlit dashboard enables mission planners, engineers, and safety officers to simulate fire risks across different cabin atmospheres and low-ventilation terrestrial environments using real microgravity experimental data.

---

## Features
* **One-Click Mission Presets:** Instantly switch between **ISS Standard Cabin** (21% $O_2$, 101 kPa, 15 cm/s), **Artemis Lunar Habitat** (34% $O_2$, 56 kPa, 20 cm/s), and **Earth Subway / Tunnel** (21% $O_2$, 101 kPa, 5 cm/s) profiles, or customize parameters via interactive sliders.
* **Physics-Ordered Risk Scoring Engine:** Dynamically calculates a 1–100 risk score weighted by key combustion drivers: **40% Oxygen Concentration**, **30% Baseline Material Burn/Spread Rate**, **20% Ventilation Airflow**, and **10% Cabin Pressure**.
* **Dual-Domain Application Modes:** Toggle between strict reduced-gravity margins for Moon/Mars habitats and buoyancy-limited terrestrial spaces (e.g., HVAC ducts, aircraft cargo holds, wall cavities).
* **AI Mission Safety Briefing:** Inspect individual NASA test records and generate tailored fire-suppression and mitigation recommendations.

---

## NASA Data & Resources Used
This project uses a curated 35-row dataset (`data/nasa_psi_combustion.csv`) compiled from the **NASA Physical Sciences Informatics (PSI) Open Data Repository**, covering three landmark microgravity combustion investigations:
1. **SAFFIRE-2 (Spacecraft Fire Experiment-II):** Large-scale solid material flammability testing aboard an uncrewed Cygnus resupply spacecraft.
2. **BASS (Burning and Suppression of Solids):** Solid fuel flame spread and extinguishment testing inside the ISS Microgravity Science Glovebox (MSG).
3. **FLEX (Flame Extinguishment Experiment):** Liquid fuel droplet combustion and extinguishment inside the ISS Combustion Integrated Rack (MDCA/CIR).

---

## Setup & Local Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com
   cd flame-in-freefall
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas
   ```

3. **Verify data directory:**
   Ensure `data/nasa_psi_combustion.csv` is present in the project root directory.

4. **Run Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## AI Disclosure
AI tools were used to assist with code structuring, UI layout formatting, and drafting safety assessment logic. All underlying combustion parameters and burn/spread rates are sourced directly from public NASA PSI experimental records.
