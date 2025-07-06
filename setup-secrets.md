# 🔐 GitHub Secrets Setup Guide

This guide helps you configure the required GitHub secrets for the CI/CD pipeline.

## 🎯 Required Secrets

### 1. Docker Hub Credentials

1. **Create Docker Hub Account**: [hub.docker.com](https://hub.docker.com)
2. **Generate Access Token**:
   - Go to Account Settings → Security → Access Tokens
   - Create New Access Token with Read/Write permissions
3. **Add to GitHub Secrets**:
   ```
   DOCKER_USERNAME: your_dockerhub_username
   DOCKER_PASSWORD: your_access_token_here
   ```

### 2. Railway Deployment Token

1. **Create Railway Account**: [railway.app](https://railway.app)
2. **Generate API Token**:
   - Go to Account Settings → Tokens
   - Create New Token
3. **Add to GitHub Secrets**:
   ```
   RAILWAY_TOKEN: your_railway_token_here
   ```

### 3. DagsHub Credentials

1. **Your DagsHub Account**: Already configured
2. **Generate Token**:
   - Go to DagsHub Settings → Access Tokens
   - Create New Token with MLflow permissions
3. **Add to GitHub Secrets**:
   ```
   DAGSHUB_USERNAME: Barnabet
   DAGSHUB_TOKEN: your_dagshub_token_here
   ```

## 🛠️ How to Add Secrets to GitHub

### Method 1: GitHub Web Interface

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Go to **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact names above

### Method 2: GitHub CLI

```bash
# Install GitHub CLI if not already installed
# brew install gh  # macOS
# apt install gh   # Ubuntu

# Login to GitHub
gh auth login

# Add secrets (replace with your actual values)
gh secret set DOCKER_USERNAME --body "your_dockerhub_username"
gh secret set DOCKER_PASSWORD --body "your_access_token"
gh secret set RAILWAY_TOKEN --body "your_railway_token"
gh secret set DAGSHUB_USERNAME --body "Barnabet"
gh secret set DAGSHUB_TOKEN --body "your_dagshub_token"
```

## ✅ Verification

After adding secrets, verify they're configured:

```bash
# List all secrets (values won't be shown for security)
gh secret list

# Should show:
# DAGSHUB_TOKEN
# DAGSHUB_USERNAME  
# DOCKER_PASSWORD
# DOCKER_USERNAME
# RAILWAY_TOKEN
```

## 🚀 Test the Pipeline

1. **Create a test PR to dev branch**:
   ```bash
   git checkout -b test-cicd
   echo "# Test CI/CD" >> test.md
   git add test.md
   git commit -m "test: trigger CI/CD pipeline"
   git push origin test-cicd
   ```

2. **Create Pull Request** to `dev` branch on GitHub

3. **Watch the Actions tab** to see the pipeline in action!

## 🔒 Security Notes

- **Never commit secrets** to your repository
- **Use environment-specific secrets** for different stages
- **Rotate tokens regularly** for security
- **Use least privilege principle** for token permissions

## 🆘 Troubleshooting

### Common Issues

1. **Invalid Docker credentials**:
   - Verify username/password are correct
   - Ensure access token has write permissions

2. **Railway deployment fails**:
   - Check Railway token is valid
   - Verify Railway CLI can authenticate

3. **DagsHub access denied**:
   - Ensure token has MLflow permissions
   - Check repository access rights

### Getting Help

- **GitHub Actions logs**: Check the Actions tab for detailed error messages
- **Docker Hub**: Verify images are being pushed successfully
- **Railway**: Check deployment logs in Railway dashboard
- **DagsHub**: Verify MLflow experiments are accessible 