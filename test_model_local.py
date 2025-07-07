#!/usr/bin/env python3
"""
Quick test script to verify DagsHub/MLflow model loading
Run this to test your credentials before using docker-compose
"""

import os
import mlflow

# Set your DagsHub credentials here
DAGSHUB_USERNAME = "Barnabet"
DAGSHUB_TOKEN = "your_token_here"  # Replace with your actual token

# Set environment variables
os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

# Set MLflow tracking URI
mlflow.set_tracking_uri("https://dagshub.com/Barnabet/projet_devops.mlflow")

try:
    print("🔍 Testing DagsHub/MLflow connection...")
    
    # Test connection
    client = mlflow.tracking.MlflowClient()
    
    # Try to get model
    model_name = "diamond-price-regressor"
    print(f"🔍 Looking for model: {model_name}")
    
    # Check for Production models
    try:
        latest_versions = client.get_latest_versions(name=model_name, stages=["Production"])
        if latest_versions:
            print(f"✅ Found Production model: version {latest_versions[0].version}")
        else:
            print("⚠️ No Production model found")
    except Exception as e:
        print(f"❌ Production model check failed: {e}")
    
    # Check for any models
    try:
        all_versions = client.get_latest_versions(name=model_name)
        if all_versions:
            print(f"✅ Found {len(all_versions)} model versions")
            for v in all_versions:
                print(f"   - Version {v.version} in stage: {v.current_stage}")
        else:
            print("❌ No models found at all")
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        
    print("✅ Connection test completed!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔧 Fix: Update DAGSHUB_TOKEN in this script with your real token from:")
    print("https://dagshub.com/user/settings/tokens") 