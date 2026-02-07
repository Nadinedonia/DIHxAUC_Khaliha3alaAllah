import pandas as pd
import numpy as np
import json
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run_clustering_pipeline(df):
    # Process dates
    df['contract_start'] = pd.to_datetime(df['contract_start'], errors='coerce')
    df['termination_date'] = pd.to_datetime(df['termination_date'], errors='coerce')

    # Calculate active days
    df['days_active'] = (pd.Timestamp.now() - df['contract_start']).dt.days.fillna(0)
    df['days_inactive'] = (pd.Timestamp.now() - df['termination_date']).dt.days.fillna(0)

    # Define flags for features
    flags = ['days_active', 'days_inactive', 'accepting_orders', 'dormant', 'seasonal', 
             'daily_sales_reports', 'activated', 'binding_period', 'auto_accept_delivery', 
             'auto_accept_takeaway', 'non_eu_commission', 'processing_fee', 'service_charge', 
             'vat', 'area_id', 'takeaway', 'delivery', 'eat_in', 'sales_outcome_id', 'dormant_partner']
    
    # Ensure columns exist before converting
    existing_flags = [f for f in flags if f in df.columns]
    df[existing_flags] = df[existing_flags].fillna(0).astype(int)

    # Extract hours logic
    def extract_hours(row):
        try:
            if pd.isna(row): return 0
            open_data = json.loads(row)
            total_hours = 0
            for day, schedule in open_data.items():
                if schedule['from'] != 'closed':
                    total_hours += float(schedule['to'].split('.')[0]) - float(schedule['from'].split('.')[0])
            return total_hours
        except:
            return 0

    if 'opening_hours' in df.columns:
        df['total_open_hours'] = df['opening_hours'].apply(extract_hours)

    # Clustering Logic
    X = df[existing_flags]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Applying teammate's weights
    feature_weights = {'days_active': 3.0, 'days_inactive': 2.5, 'accepting_orders': 4.0, 'activated': 3.5}
    for feature, weight in feature_weights.items():
        if feature in existing_flags:
            col_idx = existing_flags.index(feature)
            X_scaled[:, col_idx] *= weight

    # K-Means
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    return df

# This block must be at the zero-indentation level (far left)
if __name__ == "__main__":
    # 1. SET YOUR PATH HERE
    # Change this to the actual folder name where dim_places.csv lives
    # Based on our chat, it's likely 'data/dim_places.csv' or similar
    input_path = 'data/given_data/dim_places.csv' 
    output_path = 'data/processed/clustered_results.csv'
    
    # Ensure the output directory exists
    os.makedirs('data/processed', exist_ok=True)
    
    print(f"🔍 Searching for file at: {os.path.abspath(input_path)}")
    
    if os.path.exists(input_path):
        raw_df = pd.read_csv(input_path)
        print("🚀 Found file! Running AI Clustering...")
        
        result_df = run_clustering_pipeline(raw_df)
        
        result_df.to_csv(output_path, index=False)
        print(f"✅ Success! AI results saved to: {output_path}")
    else:
        print(f"❌ Error: Could not find '{input_path}'")
        print("💡 Tip: Right-click dim_places.csv in VS Code, select 'Copy Relative Path', and paste it into input_path.")