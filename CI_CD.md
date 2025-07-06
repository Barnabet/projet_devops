# 🚀 CI/CD Pipeline Documentation

This document describes the complete CI/CD pipeline for the Diamond Price Prediction MLOps application.

## 📋 Pipeline Overview

The CI/CD pipeline follows a **GitFlow-inspired workflow** with automated testing, building, and deployment:

```
Pull Request → dev → staging → main (production)
      ↓           ↓        ↓         ↓
   Build & Test  Auto    Full    Deploy to
   Integration  Promote  Test    Production
```

## 🔄 Workflow Stages

### 1. **Pull Request to Dev Branch**
**File**: `.github/workflows/pr-to-dev.yml`

**Triggers**: Pull requests to `dev` branch

**Actions**:
- 🏗️ Build application and install dependencies
- 🧪 Run unit and integration tests
- 🔍 Code quality checks (Black, isort, flake8)
- 🐳 Build and test Docker containers
- 🔒 Security scanning (Safety, Bandit, Trivy)
- 📊 Generate comprehensive test report

**Requirements**: All tests must pass for manual merge approval

### 2. **Dev to Staging (Auto-Promotion)**
**File**: `.github/workflows/dev-to-staging.yml`

**Triggers**: Push to `dev` branch

**Actions**:
- 🎯 Automatically promote `dev` branch to `staging`
- 🔧 Create or update staging branch
- 📢 Notify staging deployment initiation

**Result**: Staging branch updated with latest dev changes

### 3. **Staging - Full Testing & Production Promotion**
**File**: `.github/workflows/staging-to-production.yml`

**Triggers**: Push to `staging` branch

**Actions**:
- 🧪 Run comprehensive test suite (unit, integration, e2e)
- 🐳 Build and test Docker containers
- 🔒 Security and quality checks
- 📊 Upload test results as artifacts
- 🚀 Auto-promote to `main` (production) if all tests pass

**Requirements**: All tests must pass for production promotion

### 4. **Production Deployment**
**File**: `.github/workflows/production-deploy.yml`

**Triggers**: Push to `main` branch

**Actions**:
- 🤖 Fetch latest model from MLflow Production stage
- 🏗️ Build production Docker images with latest model
- 🧪 Test production images locally
- 📤 Push images to Docker Hub
- 🚂 Deploy to Railway
- 🌐 Get deployment URL and test live application
- 📊 Generate deployment report

**Result**: Live production application with latest model

## 🔧 Setup Requirements

### GitHub Secrets

Configure the following secrets in your GitHub repository:

```bash
# Docker Hub
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password

# Railway Deployment
RAILWAY_TOKEN=your_railway_token

# DagsHub/MLflow
DAGSHUB_USERNAME=your_dagshub_username
DAGSHUB_TOKEN=your_dagshub_token
```

### Repository Setup

1. **Create Branches**:
   ```bash
   git checkout -b dev
   git push origin dev
   
   # staging and main branches will be created automatically
   ```

2. **Configure Branch Protection**:
   - `main`: Require pull request reviews, require status checks
   - `dev`: Require pull request reviews
   - `staging`: Automated branch (no direct pushes)

## 🚀 Deployment Process

### Model Integration

The pipeline automatically:
1. **Fetches** the latest model from MLflow Production stage
2. **Includes** the model in the Docker image build
3. **Deploys** with the most recent model version

### Docker Hub Integration

Images are tagged with:
- `latest`: Always points to the most recent production build
- `YYYYMMDD-HHMMSS`: Timestamp-based versioning for rollbacks

### Railway Deployment

The application is deployed to Railway with:
- **Automatic scaling** based on traffic
- **Environment variables** for secure credential management
- **Health checks** for reliability monitoring
- **Custom domain** support (configurable)

## 📊 Pipeline Monitoring

### Test Results

- **Unit Tests**: Basic functionality verification
- **Integration Tests**: API and service integration
- **End-to-End Tests**: Complete user workflow testing
- **Security Scans**: Vulnerability detection
- **Docker Tests**: Container functionality verification

### Deployment Verification

- **Health Checks**: Endpoint availability
- **Model Loading**: MLflow model integration
- **API Testing**: Prediction endpoint functionality
- **Performance**: Response time monitoring

## 🔍 Troubleshooting

### Common Issues

#### 1. **Model Loading Failures**
```bash
# Check DagsHub credentials
echo $DAGSHUB_USERNAME
echo $DAGSHUB_TOKEN

# Verify model exists in Production stage
# Check DagsHub MLflow UI
```

#### 2. **Docker Build Failures**
```bash
# Check Docker Hub credentials
docker login

# Test local build
docker-compose build
```

#### 3. **Railway Deployment Issues**
```bash
# Check Railway token
railway login --token $RAILWAY_TOKEN

# Check deployment status
railway status
```

#### 4. **Test Failures**
```bash
# Run tests locally
cd tests
python -m pytest -v

# Check test dependencies
pip install -r requirements.txt
```

### Debug Commands

```bash
# Check workflow status
gh workflow list

# View workflow runs
gh run list

# Check specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

## 🔄 Manual Operations

### Force Deployment

```bash
# Trigger production deployment
git push origin main

# Or create empty commit to trigger
git commit --allow-empty -m "trigger: force deployment"
git push origin main
```

### Rollback

```bash
# Rollback to previous Docker image
docker pull username/diamond-backend:YYYYMMDD-HHMMSS
docker tag username/diamond-backend:YYYYMMDD-HHMMSS username/diamond-backend:latest
docker push username/diamond-backend:latest

# Redeploy on Railway
railway up --detach
```

### Model Updates

```bash
# Update model in MLflow
# 1. Train new model
# 2. Register in MLflow
# 3. Promote to Production stage
# 4. Push to main branch to trigger deployment
```

## 📈 Performance Optimization

### Build Time Optimization

- **Docker layer caching** for faster builds
- **Parallel test execution** where possible
- **Dependency caching** with GitHub Actions
- **Selective triggering** with path filters

### Deployment Optimization

- **Health checks** for zero-downtime deployments
- **Image optimization** with multi-stage builds
- **Resource limits** for cost efficiency
- **Auto-scaling** based on demand

## 🔒 Security Considerations

### Secrets Management

- **GitHub Secrets** for sensitive credentials
- **Environment variables** for runtime configuration
- **No hardcoded secrets** in code or Docker images

### Security Scanning

- **Dependency scanning** with Safety
- **Code security** with Bandit
- **Container scanning** with Trivy
- **Automated updates** for security patches

### Access Control

- **Branch protection** rules
- **Required reviews** for critical branches
- **Automated testing** before deployment
- **Audit logging** for all deployments

## 📚 Additional Resources

### Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Railway Documentation](https://docs.railway.app/)
- [MLflow Documentation](https://mlflow.org/docs/latest/)

### Monitoring

- **GitHub Actions**: Workflow status and logs
- **Docker Hub**: Image pulls and usage
- **Railway**: Application metrics and logs
- **DagsHub**: Model performance and experiments

### Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Setup and troubleshooting guides
- **Community**: Best practices and examples 