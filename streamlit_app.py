import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from backend.clustering import run_clustering_pipeline

# -----------------------------
# Backend imports
# -----------------------------
try:
    from backend.engine import (
        generate_schedule,
        handle_call_off,
        calculate_impact_metrics,
    )
    BACKEND_OK = True
except Exception as e:
    BACKEND_OK = False
    BACKEND_IMPORT_ERR = str(e)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Shift Planning System", page_icon="🗓️", layout="wide")

# -----------------------------
# Paths / Initial Session State
# -----------------------------
DEFAULT_PROCESSED_PATH = Path("data/processed/clustered_results.csv")
DEFAULT_FORECAST_PATH = Path("data/forecast/forecast_results.csv")

if "processed_df" not in st.session_state:
    st.session_state.processed_df = None
if "schedule_df" not in st.session_state:
    st.session_state.schedule_df = None

# -----------------------------
# Sidebar: AI Clustering & Data Loading
# -----------------------------
st.sidebar.header("🪄 AI Clustering Pipeline")
uploaded_dim = st.sidebar.file_uploader("Upload Raw dim_places.csv", type=["csv"])

if uploaded_dim:
    if st.sidebar.button("🪄 Run AI Analysis"):
        with st.spinner("Analyzing partner segments..."):
            raw_data = pd.read_csv(uploaded_dim)
            # Run the teammate's AI code
            st.session_state.processed_df = run_clustering_pipeline(raw_data)
            # Save for backend persistence
            st.session_state.processed_df.to_csv(DEFAULT_PROCESSED_PATH, index=False)
            st.sidebar.success("AI Analysis Complete!")

# Logic to handle default data loading
if st.session_state.processed_df is None and DEFAULT_PROCESSED_PATH.exists():
    st.session_state.processed_df = pd.read_csv(DEFAULT_PROCESSED_PATH)

# Strategy Insight Display
if st.session_state.processed_df is not None:
    cluster_id = st.session_state.processed_df['cluster'].iloc[0]
    
    cluster_names = {
        0: ("🔵", "Standard Active", "Predictable demand."),
        1: ("📈", "Seasonal High", "Surge buffer applied."),
        2: ("🛑", "Inactive", "Staffing suppressed."),
        3: ("💎", "Core High", "Premium staffing prioritized."),
        4: ("🐚", "Dormant", "On-call only.")
    }
    
    icon, name, desc = cluster_names.get(cluster_id, ("❓", "Unknown", ""))
    st.sidebar.info(f"**AI Strategy:** {icon} {name}\n\n*{desc}*")

st.sidebar.divider()
st.sidebar.header("⚙️ Global Controls")
labor_cost_per_staff = st.sidebar.number_input("Labor cost per staff", min_value=0.0, value=100.0)
service_level_target = st.sidebar.slider("Coverage target (%)", 50, 120, 100)

# -----------------------------
# Main Application Tabs
# -----------------------------
st.title("🗓️ AI-Driven Shift Planning")

if st.session_state.processed_df is None:
    st.warning("Please upload `dim_places.csv` in the sidebar to begin.")
    st.stop()

# Ensure Forecast exists
if not DEFAULT_FORECAST_PATH.exists():
    st.error(f"Missing forecast file at {DEFAULT_FORECAST_PATH}")
    st.stop()
forecast_df = pd.read_csv(DEFAULT_FORECAST_PATH)

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Forecast Overview",
    "🧩 Recommended Schedule",
    "⚠️ Disruption Mode",
    "💼 Business Impact"
])

# =============================
# TAB 1: Forecast Overview
# =============================
with tab1:
    st.subheader("Regional Demand Analysis")
    col1, col2 = st.columns([1, 2])
    col1.metric("Days Forecasted", forecast_df['date'].nunique())
    col2.write("Visualizing demand data from AI Model.")
    
    shift_to_plot = st.selectbox("Select Shift to View", forecast_df['shift'].unique())
    sub_fc = forecast_df[forecast_df['shift'] == shift_to_plot]
    st.line_chart(sub_fc.set_index('date')['forecast_demand'])

# =============================
# TAB 2: Recommended Schedule
# =============================
with tab2:
    if not BACKEND_OK:
        st.error(f"Backend functions missing: {BACKEND_IMPORT_ERR}")
        st.stop()
    
    st.subheader("AI-Optimized Staffing")
    if st.button("✅ Generate Schedule", type="primary"):
        with st.spinner("Applying Cluster Multipliers..."):
            st.session_state.schedule_df = generate_schedule(
                processed_df=st.session_state.processed_df,
                forecast_df=forecast_df,
                labor_cost_per_staff=labor_cost_per_staff
            )
            st.success("Schedule Generated Successfully!")

    if st.session_state.schedule_df is not None:
        st.dataframe(st.session_state.schedule_df, use_container_width=True)

# =============================
# TAB 3: Disruption Mode
# =============================
with tab3:
    if st.session_state.schedule_df is None:
        st.info("Generate a schedule in Tab 2 first.")
    else:
        st.subheader("Simulate Staff Absence")
        emp_list = st.selectbox("Select Absent Employee", st.session_state.schedule_df['employee_name'].unique())
        if st.button("⚠️ Handle Call-off"):
            # Simple simulation call
            updated, report = handle_call_off(st.session_state.schedule_df, emp_list, "2026-02-10", "Morning")
            st.session_state.schedule_df = updated
            st.write(report)

# =============================
# TAB 4: Business Impact
# =============================
with tab4:
    if st.session_state.schedule_df is None:
        st.info("No schedule data to analyze.")
    else:
        st.subheader("Executive Dashboard")
        metrics = calculate_impact_metrics(
            st.session_state.processed_df, 
            st.session_state.schedule_df, 
            forecast_df,
            labor_cost_per_staff=labor_cost_per_staff
        )
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Labor Cost", metrics.get("total_labor_cost"))
        m2.metric("Coverage Accuracy", metrics.get("coverage_rate_pct"))
        m3.info(f"**AI Strategy Applied:**\n{metrics.get('ai_strategy_note')}")