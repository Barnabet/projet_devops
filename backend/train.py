import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.sklearn
import dagshub
import dvc.api
import os
import json

# Initialize DagsHub integration with MLflow
dagshub.init(repo_owner='barnabet', repo_name='projet_devops', mlflow=True)

print("Loading data...")
# Load data using the local DVC setup.
# Make sure to run `dvc pull` if you don't have the data locally.
with dvc.api.open(
    'data/diamonds.csv'
) as fd:
    df = pd.read_csv(fd)

print("Preprocessing data...")
# Simple feature engineering and preprocessing
df = pd.get_dummies(df, columns=['cut', 'color', 'clarity'], drop_first=True)

# Define features and target
X = df.drop('price', axis=1)
y = df['price']

# Save training columns for inference
with open("training_columns.json", "w") as f:
    json.dump(X.columns.tolist(), f)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Start an MLflow run
with mlflow.start_run(nested=True):
    print("Training model...")
    # Log parameters
    n_estimators = 100
    random_state = 42
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("random_state", random_state)

    # Train model
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Log metrics
    rmse = mean_squared_error(y_test, predictions, squared=False)
    mlflow.log_metric("rmse", rmse)
    print(f"Logged RMSE: {rmse}")

    # Log the training columns as an artifact
    mlflow.log_artifact("training_columns.json", "model_meta")

    # Log the model with a registered name
    MODEL_NAME = "diamond-price-regressor"
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="diamond-price-model",
        registered_model_name=MODEL_NAME
    )
    
    # Find the latest version of the model
    client = mlflow.tracking.MlflowClient()
    latest_versions = client.get_latest_versions(name=MODEL_NAME, stages=["None"])
    if not latest_versions:
        raise Exception(f"No versions found for model '{MODEL_NAME}' in stage 'None'.")
    
    new_version = latest_versions[0].version

    print(f"Found latest version '{new_version}' for model '{MODEL_NAME}'.")

    # Transition the new version to the Production stage
    print("Transitioning new model version to Production stage...")
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=new_version,
        stage="Production",
        archive_existing_versions=True
    )
    print("Model version successfully transitioned to Production.") 