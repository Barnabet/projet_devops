# DagsHub Authentication Fix for GitHub Actions

## Issue Description
GitHub Actions workflow fails with "AUTHORIZATION REQUIRED" error when trying to fetch models from DagsHub MLflow, even though `DAGSHUB_USERNAME` and `DAGSHUB_TOKEN` are set as GitHub secrets.

## Root Cause
The issue occurs because:
1. Environment variables were not being passed to the Python script properly
2. DagsHub authentication wasn't being set up correctly in the MLflow client
3. The MLflow tracking URI wasn't including authentication credentials

## Solution Applied

### 1. Fixed Environment Variable Passing
Added explicit environment variable declaration in the workflow step:

```yaml
- name: 🤖 Fetch Latest Model from MLflow
  env:
    DAGSHUB_USERNAME: ${{ secrets.DAGSHUB_USERNAME }}
    DAGSHUB_TOKEN: ${{ secrets.DAGSHUB_TOKEN }}
  run: |
    # ... rest of the script
```

### 2. Added Credential Verification
Added checks to ensure the secrets are properly set:

```bash
# Verify environment variables are set
if [ -z "$DAGSHUB_USERNAME" ] || [ -z "$DAGSHUB_TOKEN" ]; then
  echo "❌ Error: DAGSHUB_USERNAME and DAGSHUB_TOKEN must be set as GitHub secrets"
  exit 1
fi
```

### 3. Updated MLflow Authentication
Modified the Python script to use authenticated MLflow tracking URI:

```python
# Set MLflow tracking URI with authentication
mlflow.set_tracking_uri(f"https://{dagshub_username}:{dagshub_token}@dagshub.com/Barnabet/projet_devops.mlflow")
```

## How to Verify the Fix

### 1. Check GitHub Secrets
Ensure these secrets are set in your GitHub repository:
- Go to `Settings` → `Secrets and variables` → `Actions`
- Verify these secrets exist:
  - `DAGSHUB_USERNAME`: Your DagsHub username
  - `DAGSHUB_TOKEN`: Your DagsHub personal access token

### 2. Generate DagsHub Token
If you don't have a DagsHub token:
1. Go to https://dagshub.com/settings/tokens
2. Click "Generate New Token"
3. Give it a descriptive name (e.g., "GitHub Actions CI/CD")
4. Copy the token and add it to GitHub secrets

### 3. Test the Authentication
The updated workflow now includes authentication verification:
- It will fail early if credentials are missing
- It will show authentication success messages
- It will use authenticated MLflow client

## Alternative Authentication Methods

### Method 1: Using dagshub.auth()
```python
import dagshub
dagshub.auth.add_app_token(token=dagshub_token)
dagshub.init(repo_owner="Barnabet", repo_name="projet_devops", mlflow=True)
```

### Method 2: Using Environment Variables
```python
import os
os.environ['MLFLOW_TRACKING_USERNAME'] = dagshub_username
os.environ['MLFLOW_TRACKING_PASSWORD'] = dagshub_token
mlflow.set_tracking_uri("https://dagshub.com/Barnabet/projet_devops.mlflow")
```

## Troubleshooting Steps

### If Authentication Still Fails:

1. **Verify Token Permissions**
   - Ensure the DagsHub token has MLflow access permissions
   - Check if the token hasn't expired

2. **Check Repository Access**
   - Verify the token has access to the specific repository
   - Ensure the repository path is correct: `Barnabet/projet_devops`

3. **Test Locally**
   ```bash
   export DAGSHUB_USERNAME="your-username"
   export DAGSHUB_TOKEN="your-token"
   python -c "
   import dagshub
   dagshub.init(repo_owner='Barnabet', repo_name='projet_devops', mlflow=True)
   print('Authentication successful')
   "
   ```

4. **Check MLflow Server Status**
   - Visit https://dagshub.com/Barnabet/projet_devops.mlflow
   - Ensure the MLflow server is accessible

## Prevention

### Best Practices:
1. Always use environment variables for sensitive credentials
2. Add credential verification at the start of scripts
3. Use authenticated URLs for MLflow tracking
4. Test authentication locally before deploying
5. Keep tokens secure and rotate them regularly

## Files Modified
- `.github/workflows/production-deploy.yml`: Updated MLflow model fetching step
- `github-dagshub-auth-fix.md`: This troubleshooting guide

## Testing
After applying this fix, the workflow should:
1. ✅ Verify DagsHub credentials are available
2. ✅ Authenticate successfully with DagsHub
3. ✅ Fetch the latest model from MLflow
4. ✅ Continue with the deployment process

The workflow will now fail early with a clear error message if credentials are missing, making debugging much easier. 