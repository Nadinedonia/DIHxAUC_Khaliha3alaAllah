import pandas as pd
import numpy as np


# -----------------------------
# 1. RECOMMENDATION SERVICE
# -----------------------------
def generate_schedule(processed_df, forecast_df, **params):
    from ortools.sat.python import cp_model
    
    # Extract Cluster ID (Default to 0 if not found)
    cluster_id = processed_df['cluster'].iloc[0] if 'cluster' in processed_df.columns else 0
    
    # --- AI BUSINESS LOGIC RULES ---
    multiplier = 1.0
    force_zero = False
    min_staff = 0

    if cluster_id == 0:   # Standard Active
        multiplier = 1.0
    elif cluster_id == 1: # Seasonal High Performers
        multiplier = 1.2  # 20% extra for surge
    elif cluster_id == 2: # Inactive/Churned
        force_zero = True # No one works here
    elif cluster_id == 3: # Core High Performers
        multiplier = 1.5  # Premium staffing
        min_staff = 2     # Always at least 2 people
    elif cluster_id == 4: # Dormant Edge Cases
        multiplier = 0.5
        max_staff_limit = 1 # Cap at 1 person

    # Apply to forecast
    if force_zero:
        forecast_df['adjusted_demand'] = 0
    else:
        forecast_df['adjusted_demand'] = (forecast_df['forecast_demand'] * multiplier).apply(lambda x: max(x, min_staff))
    
    # ... rest of the solver code ...

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