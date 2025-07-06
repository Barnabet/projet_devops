import os
import mlflow
import dagshub
import pandas as pd
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# DagsHub and MLflow configuration
DAGSHUB_REPO_OWNER = 'barnabet'
DAGSHUB_REPO_NAME = 'projet_devops'
MODEL_NAME = 'diamond-price-regressor'
MODEL_STAGE = 'Production' # Or 'Staging', depending on what you set in DagsHub

model = None
training_columns = None

def load_model():
    """Load the latest model and training columns from MLflow."""
    global model, training_columns
    
    print("Initializing DagsHub...")
    dagshub.init(repo_owner=DAGSHUB_REPO_OWNER, repo_name=DAGSHUB_REPO_NAME, mlflow=True)
    
    # Construct the model URI
    model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
    print(f"Loading model from URI: {model_uri}")
    
    # Load the model
    model = mlflow.sklearn.load_model(model_uri)
    print("Model loaded successfully.")

    # Download the training columns artifact
    client = mlflow.tracking.MlflowClient()
    latest_versions = client.get_latest_versions(name=MODEL_NAME, stages=[MODEL_STAGE])
    if not latest_versions:
        raise Exception(f"No model version found for stage '{MODEL_STAGE}'")
    
    latest_version = latest_versions[0]
    run_id = latest_version.run_id
    
    print(f"Downloading artifact from run_id: {run_id}")
    local_path = client.download_artifacts(run_id, "model_meta", ".")
    
    # Load the columns
    with open(os.path.join(local_path, 'training_columns.json'), 'r') as f:
        training_columns = json.load(f)
    print("Training columns loaded successfully.")

@app.route('/predict', methods=['POST'])
def predict():
    """Receive prediction data, preprocess, and return prediction."""
    if model is None or training_columns is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get data from request
        data = request.get_json()
        df = pd.DataFrame(data)

        # Preprocess the data to match training format
        # One-hot encode categorical features
        df_processed = pd.get_dummies(df)
        
        # Reindex to match training columns
        # This adds missing columns with 0 and removes extra columns
        df_aligned = df_processed.reindex(columns=training_columns, fill_value=0)

        # Make prediction
        prediction = model.predict(df_aligned)
        
        return jsonify({"predicted_price": prediction.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    load_model()
    # To run locally: flask run
    # For production, use a Gunicorn server
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000)) 