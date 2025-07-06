import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.sklearn
import dagshub
import dvc.api
import os

# Initialize DagsHub integration with MLflow
dagshub.init(repo_owner='barnabet', repo_name='projet_devops', mlflow=True)

print("Loading data...")
# Load data using the DVC API
with dvc.api.open(
    'data/diamonds.csv',
    repo='https://github.com/Barnabet/projet_devops.git'
) as fd:
    df = pd.read_csv(fd)

print("Preprocessing data...")
# Simple feature engineering and preprocessing
df = pd.get_dummies(df, columns=['cut', 'color', 'clarity'], drop_first=True)

# Define features and target
X = df.drop('price', axis=1)
y = df['price']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Start an MLflow run
with mlflow.start_run():
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

    # Log the model and register it
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="diamond-price-model",
        registered_model_name="diamond-price-regressor"
    )
    print("Model logged and registered in MLflow on DagsHub.") 