# test_backend.py
import pandas as pd
from backend.engine import generate_schedule

# Load your mock data
proc = pd.read_csv("data/generated_data/clustered_results_places.csv")
fore = pd.read_csv("data/forecast/forecast_results.csv")

print("Testing Schedule Generation...")
try:
    result = generate_schedule(proc, fore, service_level_target=100)
    if not result.empty:
        print("✅ SUCCESS: Schedule generated!")
        print(result.head())
    else:
        print("❌ FAIL: Schedule is empty (maybe constraints are too tight?)")
except Exception as e:
    print(f"❌ ERROR: {e}")