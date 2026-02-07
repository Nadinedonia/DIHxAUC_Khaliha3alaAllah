import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Backend imports (Person 2)
# -----------------------------
# Person 2 should implement these in backend/engine.py
# If not ready, UI still runs, but schedule tabs will show helpful errors.
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
st.title("🗓️ Shift Planning System (Forecast → Staffing → Disruptions → Impact)")

# -----------------------------
# Paths / config
# -----------------------------
DEFAULT_PROCESSED_PATH = Path("data/processed/clustered_results_places.csv")
DEFAULT_FORECAST_PATH = Path("data/forecast/forecast_results.csv")

# -----------------------------
# Helpers
# -----------------------------
@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def safe_load_or_upload(label: str, default_path: Path):
    st.sidebar.subheader(label)
    if default_path.exists():
        use_default = st.sidebar.checkbox(f"Use default: {default_path.as_posix()}", value=True)
    else:
        use_default = False
        st.sidebar.warning(f"Default not found: {default_path.as_posix()}")

    if use_default:
        df = load_csv(default_path)
        st.sidebar.success(f"Loaded: {default_path.name} ({len(df)} rows)")
        return df, default_path.as_posix()

    uploaded = st.sidebar.file_uploader(f"Upload {label} CSV", type=["csv"], key=label)
    if uploaded is None:
        return None, None

    df = pd.read_csv(uploaded)
    st.sidebar.success(f"Uploaded: {uploaded.name} ({len(df)} rows)")
    return df, uploaded.name

def show_df(title: str, df: pd.DataFrame):
    st.subheader(title)
    st.dataframe(df, use_container_width=True)

def plot_forecast(df_forecast: pd.DataFrame, date_col: str, shift_col: str, value_col: str):
    st.subheader("📈 Forecast Chart (per shift)")
    shifts = sorted(df_forecast[shift_col].unique())
    selected_shift = st.selectbox("Select shift", shifts)

    sub = df_forecast[df_forecast[shift_col] == selected_shift].copy()
    sub[date_col] = pd.to_datetime(sub[date_col])

    fig, ax = plt.subplots()
    ax.plot(sub[date_col], sub[value_col], marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Forecasted demand")
    ax.set_title(f"Forecasted demand for shift: {selected_shift}")
    st.pyplot(fig)

def require_backend():
    if not BACKEND_OK:
        st.error("Backend functions not available yet.")
        st.code(f"Import error:\n{BACKEND_IMPORT_ERR}")
        st.info(
            "Person 2 should implement these in backend/engine.py:\n"
            "- generate_schedule(processed_df, forecast_df, **params)\n"
            "- handle_call_off(schedule_df, employee_id, date, shift, **params)\n"
            "- calculate_impact_metrics(processed_df, schedule_df, forecast_df, **params)\n"
        )
        st.stop()

# -----------------------------
# Sidebar: Load inputs
# -----------------------------
st.sidebar.header("📦 Data Inputs (Pipeline Contract)")
processed_df, processed_src = safe_load_or_upload("Processed Deloitte Data", DEFAULT_PROCESSED_PATH)
forecast_df, forecast_src = safe_load_or_upload("Forecast Output (7 days)", DEFAULT_FORECAST_PATH)

st.sidebar.divider()
st.sidebar.header("⚙️ Global Controls")

# These knobs are judge-friendly; Person 2 can wire them into logic.
labor_cost_per_staff = st.sidebar.number_input("Labor cost per staff per shift", min_value=0.0, value=100.0, step=10.0)
service_level_target = st.sidebar.slider("Coverage target (%)", min_value=50, max_value=120, value=100, step=5)

# -----------------------------
# Basic validation
# -----------------------------
if processed_df is None or forecast_df is None:
    st.warning("Load both: processed Deloitte data + forecast_results.csv to continue.")
    st.stop()

# Try to infer important columns (adjust if your data contract differs)
# Forecast expected: date, shift, forecast_demand
# Processed expected: employee_id, employee_name, role/skill, availability, cost(optional)
def infer_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

fc_date = infer_col(forecast_df, ["date", "Date", "ds"])
fc_shift = infer_col(forecast_df, ["shift", "Shift", "shift_name"])
fc_val = infer_col(forecast_df, ["forecast_demand", "yhat", "demand", "prediction"])

if not all([fc_date, fc_shift, fc_val]):
    st.error("forecast_results.csv missing required columns.")
    st.write("Found columns:", list(forecast_df.columns))
    st.info("Expected something like: date, shift, forecast_demand (or Prophet ds/yhat).")
    st.stop()

# -----------------------------
# Tabs (as you requested)
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Forecast Overview",
    "🧩 Recommended Schedule",
    "⚠️ Disruption Mode (Call-off)",
    "💼 Business Impact"
])

# =============================
# TAB 1: Forecast Overview
# =============================
with tab1:
    st.markdown("### What judges should understand here")
    st.write(
        "- This comes from the AI person’s model (7-day, per-shift demand forecast).\n"
        "- We visualize it and allow filtering by shift.\n"
        "- The output format is the contract between AI → Backend."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Forecast rows", len(forecast_df))
    c2.metric("Shifts", forecast_df[fc_shift].nunique())
    c3.metric("Days", pd.to_datetime(forecast_df[fc_date]).dt.date.nunique())

    plot_forecast(forecast_df, fc_date, fc_shift, fc_val)
    show_df("Forecast output (preview)", forecast_df.head(50))

# =============================
# TAB 2: Recommended Schedule
# =============================
with tab2:
    require_backend()

    st.markdown("### Schedule generation controls")
    st.write(
        "This tab calls backend logic to convert demand → required staff, then assigns employees."
    )

    # Optional: scenario settings that backend can use
    max_staff_per_shift = st.number_input("Max staff per shift (cap)", min_value=1, value=20, step=1)
    allow_overtime = st.checkbox("Allow overtime", value=False)

    if st.button("✅ Generate Schedule", type="primary"):
        with st.spinner("Generating schedule..."):
            schedule_df = generate_schedule(
                processed_df=processed_df,
                forecast_df=forecast_df,
                labor_cost_per_staff=labor_cost_per_staff,
                service_level_target=service_level_target,
                max_staff_per_shift=max_staff_per_shift,
                allow_overtime=allow_overtime,
            )
        st.session_state["schedule_df"] = schedule_df
        st.success("Schedule generated.")

    schedule_df = st.session_state.get("schedule_df")
    if schedule_df is None:
        st.info("Click **Generate Schedule** to produce staffing assignments.")
    else:
        show_df("Recommended schedule", schedule_df)

        # Download for demo
        st.download_button(
            "⬇️ Download schedule CSV",
            data=schedule_df.to_csv(index=False).encode("utf-8"),
            file_name="recommended_schedule.csv",
            mime="text/csv",
        )

# =============================
# TAB 3: Disruption Mode (Call-off)
# =============================
with tab3:
    require_backend()

    schedule_df = st.session_state.get("schedule_df")
    if schedule_df is None:
        st.warning("Generate a schedule first in **Recommended Schedule**.")
        st.stop()

    st.markdown("### Simulate a call-off and see the system respond")
    st.write("This demonstrates robustness and real-world handling.")

    # Try to infer columns in schedule_df
    sc_date = infer_col(schedule_df, ["date", "Date"])
    sc_shift = infer_col(schedule_df, ["shift", "Shift", "shift_name"])
    sc_emp = infer_col(schedule_df, ["employee_id", "emp_id", "staff_id"])

    if not all([sc_date, sc_shift, sc_emp]):
        st.error("Schedule output missing columns required for call-off simulation.")
        st.write("Found columns:", list(schedule_df.columns))
        st.info("Schedule should include at least: date, shift, employee_id.")
        st.stop()

    # User selects a row to call-off
    schedule_df[sc_date] = pd.to_datetime(schedule_df[sc_date]).dt.date

    colA, colB = st.columns(2)
    with colA:
        chosen_date = st.selectbox("Date", sorted(schedule_df[sc_date].unique()))
    with colB:
        chosen_shift = st.selectbox("Shift", sorted(schedule_df[sc_shift].unique()))

    subset = schedule_df[(schedule_df[sc_date] == chosen_date) & (schedule_df[sc_shift] == chosen_shift)]
    st.write(f"Assignments for {chosen_date} • {chosen_shift}")
    st.dataframe(subset, use_container_width=True)

    if len(subset) == 0:
        st.info("No assignments found for this date/shift.")
        st.stop()

    chosen_employee = st.selectbox("Employee to call-off", sorted(subset[sc_emp].astype(str).unique()))

    if st.button("⚠️ Apply Call-off", type="primary"):
        with st.spinner("Recomputing schedule after call-off..."):
            updated_schedule_df, disruption_report = handle_call_off(
                schedule_df=schedule_df,
                employee_id=chosen_employee,
                date=str(chosen_date),
                shift=str(chosen_shift),
                labor_cost_per_staff=labor_cost_per_staff,
                service_level_target=service_level_target,
            )

        st.session_state["schedule_df"] = updated_schedule_df
        st.session_state["disruption_report"] = disruption_report
        st.success("Call-off handled. Schedule updated.")

    disruption_report = st.session_state.get("disruption_report")
    if disruption_report is not None:
        st.subheader("📌 Disruption report")
        if isinstance(disruption_report, pd.DataFrame):
            st.dataframe(disruption_report, use_container_width=True)
        else:
            st.write(disruption_report)

# =============================
# TAB 4: Business Impact
# =============================
with tab4:
    require_backend()

    schedule_df = st.session_state.get("schedule_df")
    if schedule_df is None:
        st.warning("Generate a schedule first in **Recommended Schedule**.")
        st.stop()

    st.markdown("### Business KPIs (what the business person will narrate)")
    st.write(
        "- Coverage rate vs forecast demand\n"
        "- Understaffed / overstaffed shifts\n"
        "- Estimated labor cost\n"
        "- Gap summary for decision makers"
    )

    with st.spinner("Calculating impact metrics..."):
        metrics = calculate_impact_metrics(
            processed_df=processed_df,
            schedule_df=schedule_df,
            forecast_df=forecast_df,
            labor_cost_per_staff=labor_cost_per_staff,
            service_level_target=service_level_target,
        )

    # metrics can be dict + tables
    if isinstance(metrics, dict):
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Coverage %", metrics.get("coverage_rate_pct", "—"))
        mcol2.metric("Understaffed shifts", metrics.get("understaffed_shifts", "—"))
        mcol3.metric("Overstaffed shifts", metrics.get("overstaffed_shifts", "—"))
        mcol4.metric("Total labor cost", metrics.get("total_labor_cost", "—"))

        # Optional tables
        if "gap_table" in metrics and isinstance(metrics["gap_table"], pd.DataFrame):
            show_df("Coverage gaps (table)", metrics["gap_table"])

        if "cost_table" in metrics and isinstance(metrics["cost_table"], pd.DataFrame):
            show_df("Cost breakdown (table)", metrics["cost_table"])

    elif isinstance(metrics, pd.DataFrame):
        show_df("Impact metrics", metrics)
    else:
        st.write(metrics)

st.caption("Pipeline: Database → AI Forecast → Backend Logic → Frontend → Business Story")
