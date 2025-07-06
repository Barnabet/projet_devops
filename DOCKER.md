# Docker Deployment Guide

This guide explains how to build, run, and deploy the Diamond Price Prediction application using Docker containers.

## 🏗️ Architecture

The application consists of two main containers:

- **Backend Container**: Python Flask API with MLflow model serving
- **Frontend Container**: Nginx serving static HTML/CSS/JS files

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- DagsHub credentials (for MLflow model access)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd projet_devops
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp docker.env.example .env

# Edit .env with your DagsHub credentials
nano .env
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **Health Checks**: 
  - Frontend: http://localhost/health
  - Backend: http://localhost:5000/health

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: DagsHub credentials
MLFLOW_TRACKING_USERNAME=your_dagshub_username
MLFLOW_TRACKING_PASSWORD=your_dagshub_password

# Alternative: Use token instead of username/password
DAGSHUB_USER_TOKEN=your_dagshub_token
```

### Port Configuration

Default ports can be changed in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5000:5000"  # Change first port for external access
  frontend:
    ports:
      - "80:80"      # Change first port for external access
```

## 🐳 Container Details

### Backend Container

**Base Image**: `python:3.9-slim`
**Port**: 5000
**Health Check**: `curl -f http://localhost:5000/health`

**Features**:
- Optimized Python dependencies
- Non-root user for security
- MLflow model loading
- DVC data access
- Automatic model download from DagsHub

**Volumes**:
- `./data:/app/data:ro` - Read-only data access
- `./.dvc:/app/.dvc:ro` - DVC configuration

### Frontend Container

**Base Image**: `nginx:alpine`
**Port**: 80
**Health Check**: `curl -f http://localhost/health`

**Features**:
- Optimized nginx configuration
- Gzip compression
- Security headers
- Static file caching
- CORS support for API calls

## 📝 Docker Commands

### Build Commands
```bash
# Build all containers
docker-compose build

# Build specific container
docker-compose build backend
docker-compose build frontend

# Build with no cache
docker-compose build --no-cache
```

### Run Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up backend

# View logs
docker-compose logs
docker-compose logs backend
docker-compose logs frontend
```

### Management Commands
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Scale services (if needed)
docker-compose up --scale backend=2
```

### Debug Commands
```bash
# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container status
docker-compose ps

# View resource usage
docker stats
```

## 🔍 Health Monitoring

### Health Check Endpoints

Both containers include health checks:

```bash
# Check backend health
curl http://localhost:5000/health

# Check frontend health
curl http://localhost/health

# Check via Docker
docker-compose ps
```

### Expected Health Responses

**Backend Health Check**:
```json
{
  "status": "running",
  "model_status": "loaded",
  "message": "Diamond Price Prediction API is running"
}
```

**Frontend Health Check**:
```
healthy
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Backend Model Loading Issues
```bash
# Check backend logs
docker-compose logs backend

# Common causes:
# - Missing DagsHub credentials
# - Network connectivity issues
# - Model not promoted to Production stage
```

#### 2. Frontend CORS Issues
```bash
# Check if backend is accessible
curl http://localhost:5000/health

# Verify network connectivity
docker-compose exec frontend ping backend
```

#### 3. Port Conflicts
```bash
# Check what's using the ports
lsof -i :80
lsof -i :5000

# Change ports in docker-compose.yml if needed
```

#### 4. Permission Issues
```bash
# Check container logs
docker-compose logs

# Ensure proper file permissions
chmod -R 755 frontend/
chmod -R 755 backend/
```

### Debug Mode

Run containers with debug output:

```bash
# Enable debug logging
export FLASK_ENV=development
docker-compose up --build
```

### Container Shell Access

Access container shells for debugging:

```bash
# Backend container (bash)
docker-compose exec backend bash

# Frontend container (sh - alpine)
docker-compose exec frontend sh
```

## 🔒 Security Considerations

### Production Security

1. **Non-root Users**: Both containers run as non-root users
2. **Security Headers**: Frontend includes security headers
3. **Minimal Images**: Using slim/alpine images
4. **Read-only Volumes**: Data mounted as read-only
5. **Health Checks**: Built-in container health monitoring

### Environment Security

```bash
# Use Docker secrets for production
docker secret create dagshub_username username.txt
docker secret create dagshub_password password.txt
```

### Network Security

```bash
# Use custom networks for isolation
docker network create diamond-network --driver bridge
```

## 📊 Performance Optimization

### Image Size Optimization

- **Backend**: ~200MB (Python slim + dependencies)
- **Frontend**: ~25MB (Nginx alpine + static files)

### Build Optimization

```bash
# Use multi-stage builds (if needed)
# Leverage Docker layer caching
# Minimize COPY operations

# Build with BuildKit for better performance
DOCKER_BUILDKIT=1 docker-compose build
```

### Runtime Optimization

```bash
# Set resource limits
docker-compose up --memory=512m --cpus=1.0
```

## 🌐 Production Deployment

### Docker Hub Deployment

```bash
# Tag images
docker tag diamond-backend:latest yourusername/diamond-backend:latest
docker tag diamond-frontend:latest yourusername/diamond-frontend:latest

# Push to Docker Hub
docker push yourusername/diamond-backend:latest
docker push yourusername/diamond-frontend:latest
```

### Cloud Deployment

The containers are ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**
- **Railway**
- **Render**

### Environment-specific Configs

```bash
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up
```

## 📈 Monitoring and Logging

### Container Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Monitoring

```bash
# Continuous health check
watch docker-compose ps

# Health check script
#!/bin/bash
curl -f http://localhost/health && curl -f http://localhost:5000/health
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats diamond-backend diamond-frontend

# Export metrics (if using monitoring tools)
docker-compose exec backend curl http://localhost:5000/metrics
```

## 🔄 Updates and Maintenance

### Update Process

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Check health
docker-compose ps
```

### Backup and Recovery

```bash
# Backup volumes
docker run --rm -v diamond-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore volumes
docker run --rm -v diamond-data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Nginx Documentation](https://nginx.org/en/docs/) 