import pandas as pd
import numpy as np


# -----------------------------
# 1. RECOMMENDATION SERVICE
# -----------------------------
def generate_schedule(processed_df, forecast_df, **params):
    """
    Converts Forecast Demand -> Staffing Requirements -> Employee Assignments.
    """
    from ortools.sat.python import cp_model
    # Extract params from UI
    sl_target = params.get('service_level_target', 100) / 100.0
    labor_cost = params.get('labor_cost_per_staff', 100)
    
    # 1. Determine requirements: Assume 1 staff per 10 units of demand (adjust as needed)
    # We create a 'requirements' table based on forecast
    forecast_df['required_staff'] = (forecast_df['forecast_demand'] / 10 * sl_target).apply(np.ceil).astype(int)
    
    # 2. Optimization Model
    model = cp_model.CpModel()
    
    employees = processed_df.to_dict('records')
    shifts = forecast_df.to_dict('records')
    
    assignments = {}
    for e_idx, emp in enumerate(employees):
        unique_dates = set(shift['date'] for shift in shifts)
        for date in unique_dates:
            shift_indices = [s_idx for s_idx, shift in enumerate(shifts) if shift['date'] == date]
        model.Add(sum(assignments[(e_idx, s_idx)] for s_idx in shift_indices) <= 1)


    # Constraint: Skill Matching (if 'role' exists in both)
    if 'role' in processed_df.columns and 'role' in forecast_df.columns:
        for s_idx, shift in enumerate(shifts):
            for e_idx, emp in enumerate(employees):
                if emp['role'] != shift['role']:
                    model.Add(assignments[(e_idx, s_idx)] == 0)

    # Constraint: Max 1 shift per day per employee
    for e_idx, emp in enumerate(employees):
        for date in forecast_df['date'].unique():
            day_shifts = forecast_df[forecast_df['date'] == date].index.tolist()
            model.Add(sum(assignments[(e_idx, s_idx)] for s_idx in day_shifts) <= 1)

    # Constraint: Meet required staff count
    for s_idx, shift in enumerate(shifts):
        model.Add(sum(assignments[(e_idx, s_idx)] for e_idx in range(len(employees))) >= shift['required_staff'])

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # 3. Format Output
    schedule_results = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for s_idx, shift in enumerate(shifts):
            for e_idx, emp in enumerate(employees):
                if solver.Value(assignments[(e_idx, s_idx)]):
                    schedule_results.append({
                        "date": shift['date'],
                        "shift": shift['shift'],
                        "employee_id": emp.get('employee_id', e_idx),
                        "employee_name": emp.get('employee_name', f"Staff {e_idx}"),
                        "role": emp.get('role', 'Staff'),
                        "cost": labor_cost
                    })
    
    return pd.DataFrame(schedule_results)

# -----------------------------
# 2. DISRUPTION SERVICE
# -----------------------------
def handle_call_off(schedule_df, employee_id, date, shift, **params):
    """
    Finds the best replacement for a call-off.
    """
    # Identify who left
    call_off_mask = (schedule_df['employee_id'].astype(str) == str(employee_id)) & \
                    (schedule_df['date'].astype(str) == str(date)) & \
                    (schedule_df['shift'].astype(str) == str(shift))
    
    # Remove them from the schedule
    updated_schedule = schedule_df[~call_off_mask].copy()
    
    # Mock "Best Candidate" Logic:
    # In a real app, you'd filter processed_df for people NOT working this shift
    report = {
        "status": "Replacement Suggested",
        "best_candidate": "Alex Johnson (Backup Pool)",
        "estimated_impact": "+$25 (Emergency Premium)",
        "coverage_gap": "Closed"
    }
    
    return updated_schedule, report

# -----------------------------
# 3. IMPACT CALCULATOR
# -----------------------------
def calculate_impact_metrics(processed_df, schedule_df, forecast_df, **params):
    """
    Calculates KPIs for the Manager Dashboard.
    """
    labor_cost = params.get('labor_cost_per_staff', 100)
    
    # Logic: Total Cost
    total_cost = len(schedule_df) * labor_cost
    
    # Logic: Coverage Gap
    # Compare scheduled count vs required count
    scheduled_counts = schedule_df.groupby(['date', 'shift']).size().reset_index(name='actual_staff')
    
    # Simulating a metric dict for Tab 4
    metrics = {
        "coverage_rate_pct": "94%",
        "understaffed_shifts": 2,
        "overstaffed_shifts": 1,
        "total_labor_cost": f"${total_cost:,}",
        "gap_table": scheduled_counts # This shows in the UI table
    }
    
    return metrics