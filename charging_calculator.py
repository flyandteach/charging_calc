import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(page_title="Electric Aircraft Charging Calculator", layout="wide")

# Title and description
st.title("Electric Aircraft Charging Calculator")
st.markdown("""
Estimate the electricity requirements for charging electric aircraft and eVTOLs at your airport.
This tool uses methodologies from the *Washington Electric Airport Feasibility Study (2022)*.
Default charging is Level 3+ (DCFC), with options for Level 1 and Level 2.
""")

# Aircraft data
aircraft_data = {
    "General Aviation": {
        "models": ["Pipistrel Alpha Electro", "Bye eFlyer 2"],
        "power_demand_kW": 56,
        "range_mi": 92.5,
        "cruise_speed_mph": 108.5
    },
    "Air Taxi": {
        "models": ["Eviation Alice"],
        "power_demand_kW": 680,
        "range_mi": 506,
        "cruise_speed_mph": 289
    },
    "eVTOL": {
        "models": ["Joby", "Wisk"],
        "power_demand_kW": 350,
        "range_mi": 100,
        "cruise_speed_mph": 150
    }
}

charging_levels = {
    "Level 1": {"power_kW": 1, "description": "120V AC, ~1 kW, slow charging"},
    "Level 2": {"power_kW": 20, "description": "240V AC, up to 20 kW"},
    "Level 3+ (DCFC)": {"power_kW": 350, "description": "DC Fast Charge, 20–350 kW"}
}

scenarios = {
    "Low": {"feasibility_rate": 0.3, "adoption_rate": 0.35, "ops_growth_years": 10},
    "Medium": {"feasibility_rate": 0.5, "adoption_rate": 0.5, "ops_growth_years": 8},
    "High": {"feasibility_rate": 0.7, "adoption_rate": 0.85, "ops_growth_years": 5}
}

# Sidebar Inputs
st.sidebar.header("Input Parameters")
operation_category = st.sidebar.selectbox("Operation Category", list(aircraft_data.keys()))
num_operations = st.sidebar.number_input("Annual Number of Operations", min_value=0, value=10000, step=1000)
charging_level = st.sidebar.selectbox("Charging Level", list(charging_levels.keys()), index=2)
charging_window = st.sidebar.slider("Daily Charging Window (hours)", 1, 24, 8)
scenario = st.sidebar.selectbox("Growth Scenario", list(scenarios.keys()))

# Calculations
def calculate_energy_demand(num_ops, category, feasibility, adoption):
    data = aircraft_data[category]
    flight_duration_hrs = data["range_mi"] / data["cruise_speed_mph"]
    energy_per_flight_kWh = data["power_demand_kW"] * flight_duration_hrs
    annual_energy_MWh = (num_ops / 2) * feasibility * adoption * energy_per_flight_kWh / 1000
    return annual_energy_MWh

def calculate_power_demand(annual_energy_MWh, charging_window_hrs):
    avg_power_kW = (annual_energy_MWh * 1000) / (365 * 24)
    seasonality = 1.7
    charging_curve = 1.8
    peak_power_MW = avg_power_kW * seasonality * charging_curve * (24 / charging_window_hrs) / 1000
    return avg_power_kW, peak_power_MW

feasibility = scenarios[scenario]["feasibility_rate"]
adoption = scenarios[scenario]["adoption_rate"]
annual_energy = calculate_energy_demand(num_operations, operation_category, feasibility, adoption)
avg_power, peak_power = calculate_power_demand(annual_energy, charging_window)

charging_power_kW = charging_levels[charging_level]["power_kW"]
if peak_power * 1000 > charging_power_kW:
    st.warning(f"Selected charging level ({charging_level}) has a max power of {charging_power_kW} kW, which may limit charging speed for peak demand of {peak_power:.2f} MW.")

# Results
st.header("Results")
st.metric("Annual Energy Demand (MWh)", f"{annual_energy:.2f}")
st.metric("Average Power Demand (kW)", f"{avg_power:.2f}")
st.metric("Peak Power Demand (MW)", f"{peak_power:.2f}")

# Assumptions
st.header("Assumptions")
st.write(f"- **Operation Category**: {operation_category}")
st.write(f"- **Number of Operations**: {num_operations}")
st.write(f"- **Charging Level**: {charging_level} ({charging_levels[charging_level]['description']})")
st.write(f"- **Charging Window**: {charging_window} hours")
st.write(f"- **Scenario**: {scenario}")
st.write(f"- **Feasibility Rate**: {feasibility * 100:.0f}%")
st.write(f"- **Adoption Rate**: {adoption * 100:.0f}%")
st.write(f"- **Aircraft Specs**: Power: {aircraft_data[operation_category]['power_demand_kW']} kW, Range: {aircraft_data[operation_category]['range_mi']} mi, Cruise Speed: {aircraft_data[operation_category]['cruise_speed_mph']} mph")
st.write("- **Seasonality**: 1.7 (70% higher in peak month)")
st.write("- **Charging Curve Factor**: 1.8 (80% higher peak vs average)")

st.markdown("""
**Note**: This calculator assumes Level 3+ (DCFC) as the default for commercial operations. Lower levels may not support rapid charging needed for high-frequency operations. Always verify with your utility provider.
""")
