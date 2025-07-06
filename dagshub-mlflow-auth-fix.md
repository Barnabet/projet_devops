# DagsHub MLflow Authentication Fix for CI/CD

## Problem
DagsHub's `dagshub.init()` function triggers OAuth authentication flow in CI/CD environments, causing workflows to hang waiting for manual browser authorization. This happens even when `DAGSHUB_USERNAME` and `DAGSHUB_TOKEN` are properly set.

## Root Cause
The issue occurs because:
1. `dagshub.init()` defaults to OAuth flow instead of using provided tokens
2. DagsHub's authentication system prioritizes interactive auth over token-based auth
3. Multiple authentication methods conflict with each other

## Solution Applied

### Method 1: MLflow Environment Variables (Recommended)
```python
# Set MLflow environment variables for authentication (bypasses OAuth)
os.environ['MLFLOW_TRACKING_USERNAME'] = dagshub_username
os.environ['MLFLOW_TRACKING_PASSWORD'] = dagshub_token

# Set MLflow tracking URI (without credentials in URL to avoid double auth)
mlflow.set_tracking_uri("https://dagshub.com/Barnabet/projet_devops.mlflow")
```

### Method 2: Direct MLflow Client Authentication
```python
import mlflow
from mlflow.tracking import MlflowClient

# Create authenticated MLflow client
client = MlflowClient(
    tracking_uri="https://dagshub.com/Barnabet/projet_devops.mlflow",
    registry_uri="https://dagshub.com/Barnabet/projet_devops.mlflow"
)

# Set authentication in requests session
import requests
session = requests.Session()
session.auth = (dagshub_username, dagshub_token)
```

### Method 3: DagsHub Token Authentication (Alternative)
```python
# Use DagsHub's token authentication method
import dagshub
dagshub.auth.add_app_token(token=dagshub_token)

# Then initialize without OAuth
dagshub.init(repo_owner="Barnabet", repo_name="projet_devops", mlflow=True)
```

## Common Authentication Issues

### Issue 1: OAuth Flow in CI/CD
**Symptoms**: 
- "AUTHORIZATION REQUIRED" message
- Workflow hangs for 5+ minutes
- OAuth URL appears only after timeout

**Solution**: Use MLflow environment variables instead of `dagshub.init()`

### Issue 2: Double Authentication Headers
**Symptoms**: 
- 400 Bad Request errors
- "Authorization header already present" errors

**Solution**: Don't embed credentials in URL when using environment variables

### Issue 3: Token Permissions
**Symptoms**: 
- 403 Forbidden errors
- "Access denied" messages

**Solution**: Ensure DagsHub token has proper permissions for MLflow access

## Testing Authentication Locally

### Test Script
```python
import os
import mlflow

# Set your credentials
os.environ['DAGSHUB_USERNAME'] = 'your-username'
os.environ['DAGSHUB_TOKEN'] = 'your-token'
os.environ['MLFLOW_TRACKING_USERNAME'] = 'your-username'
os.environ['MLFLOW_TRACKING_PASSWORD'] = 'your-token'

# Test connection
mlflow.set_tracking_uri("https://dagshub.com/Barnabet/projet_devops.mlflow")

try:
    client = mlflow.MlflowClient()
    experiments = client.search_experiments()
    print(f"✅ Authentication successful! Found {len(experiments)} experiments")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

## GitHub Actions Best Practices

### 1. Use Environment Variables
```yaml
- name: Fetch Model
  env:
    DAGSHUB_USERNAME: ${{ secrets.DAGSHUB_USERNAME }}
    DAGSHUB_TOKEN: ${{ secrets.DAGSHUB_TOKEN }}
    MLFLOW_TRACKING_USERNAME: ${{ secrets.DAGSHUB_USERNAME }}
    MLFLOW_TRACKING_PASSWORD: ${{ secrets.DAGSHUB_TOKEN }}
```

### 2. Avoid OAuth in CI/CD
```python
# ❌ Don't do this in CI/CD
dagshub.init(repo_owner="owner", repo_name="repo", mlflow=True)

# ✅ Do this instead
os.environ['MLFLOW_TRACKING_USERNAME'] = username
os.environ['MLFLOW_TRACKING_PASSWORD'] = token
mlflow.set_tracking_uri("https://dagshub.com/owner/repo.mlflow")
```

### 3. Test Authentication Early
```python
# Add early authentication test
try:
    client = mlflow.MlflowClient()
    client.search_experiments(max_results=1)
    print("✅ MLflow authentication successful")
except Exception as e:
    print(f"❌ MLflow authentication failed: {e}")
    raise
```

## Troubleshooting Steps

1. **Verify Token Validity**
   ```bash
   curl -u "username:token" "https://dagshub.com/api/v1/user"
   ```

2. **Check MLflow Server Access**
   ```bash
   curl -u "username:token" "https://dagshub.com/owner/repo.mlflow/api/2.0/mlflow/experiments/search"
   ```

3. **Test Local Authentication**
   ```bash
   export MLFLOW_TRACKING_USERNAME="username"
   export MLFLOW_TRACKING_PASSWORD="token"
   python -c "import mlflow; print(mlflow.MlflowClient().search_experiments())"
   ```

## Alternative: Fallback Model Strategy

If authentication continues to fail, implement a fallback strategy:

```python
try:
    # Try to fetch from MLflow
    model = mlflow.sklearn.load_model("models:/diamond-price-regressor/Production")
    print("✅ Model loaded from MLflow")
except Exception as e:
    print(f"⚠️ MLflow failed: {e}")
    print("🔄 Using fallback model...")
    # Load a pre-trained model from artifacts or train a simple one
    model = load_fallback_model()
```

## Files Modified
- `.github/workflows/production-deploy.yml`: Updated authentication method
- `dagshub-mlflow-auth-fix.md`: This comprehensive guide

## References
- [DagsHub Authentication Docs](https://dagshub.com/docs/integration_guide/mlflow/)
- [MLflow Authentication](https://mlflow.org/docs/latest/auth/index.html)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

This fix should resolve the OAuth authentication issue and allow your CI/CD pipeline to successfully fetch models from DagsHub MLflow. 