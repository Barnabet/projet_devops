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

model = None
training_columns = None

def load_model():
    """Load the latest model and training columns from MLflow."""
    global model, training_columns
    
    try:
        print("Initializing DagsHub...")
        dagshub.init(repo_owner=DAGSHUB_REPO_OWNER, repo_name=DAGSHUB_REPO_NAME, mlflow=True)
        
        client = mlflow.tracking.MlflowClient()
        
        # Try to load from Production stage first
        model_uri = None
        run_id = None
        
        try:
            print("Trying to load model from Production stage...")
            model_uri = f"models:/{MODEL_NAME}/Production"
            latest_versions = client.get_latest_versions(name=MODEL_NAME, stages=["Production"])
            if latest_versions:
                run_id = latest_versions[0].run_id
                print(f"Found Production model with run_id: {run_id}")
        except Exception as e:
            print(f"Production model not found: {e}")
        
        # If Production not available, try latest version
        if model_uri is None:
            try:
                print("Trying to load latest model version...")
                latest_versions = client.get_latest_versions(name=MODEL_NAME)
                if latest_versions:
                    latest_version = latest_versions[0]
                    model_uri = f"models:/{MODEL_NAME}/{latest_version.version}"
                    run_id = latest_version.run_id
                    print(f"Found latest model version {latest_version.version} with run_id: {run_id}")
            except Exception as e:
                print(f"Latest model not found: {e}")
        
        # If still no model found, raise error
        if model_uri is None or run_id is None:
            raise Exception(f"No model found for '{MODEL_NAME}'. Please ensure the model is registered in MLflow.")
        
        print(f"Loading model from URI: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)
        print("Model loaded successfully.")

        # Download the training columns artifact
        print(f"Downloading artifact from run_id: {run_id}")
        local_path = client.download_artifacts(run_id, "model_meta", ".")
        
        # Load the columns
        with open(os.path.join(local_path, 'training_columns.json'), 'r') as f:
            training_columns = json.load(f)
        print("Training columns loaded successfully.")
        print(f"Ready to serve predictions! Model loaded with {len(training_columns)} features.")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Backend will start but predictions will not work until model is available.")

@app.route('/predict', methods=['POST'])
def predict():
    """Receive prediction data, preprocess, and return prediction."""
    if model is None or training_columns is None:
        return jsonify({
            "error": "Model not loaded. Please ensure the model is registered in MLflow and promoted to Production stage in DagsHub."
        }), 500

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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    model_status = "loaded" if model is not None else "not loaded"
    return jsonify({
        "status": "running",
        "model_status": model_status,
        "message": "Diamond Price Prediction API is running"
    })

if __name__ == '__main__':
    load_model()
    print("Starting Flask server...")
    print("Backend API available at: http://127.0.0.1:5000")
    print("Health check: http://127.0.0.1:5000/health")
    print("Prediction endpoint: http://127.0.0.1:5000/predict")
    # To run locally: flask run
    # For production, use a Gunicorn server
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000), debug=True) 