#!/usr/bin/env python3
"""
Local Docker Container Test Script
Test Docker containers locally before pushing to GitHub Actions
"""

import subprocess
import time
import sys
import requests
import json

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def test_backend_container():
    """Test the backend container locally"""
    print("🔍 Testing backend container locally...")
    
    # Build the backend image
    print("🏗️ Building backend image...")
    build_cmd = "docker build -t test-backend -f backend/Dockerfile ."
    code, stdout, stderr = run_command(build_cmd)
    
    if code != 0:
        print(f"❌ Backend build failed:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    print("✅ Backend image built successfully")
    
    # Run the backend container
    print("🚀 Starting backend container...")
    run_cmd = """docker run -d --name test-backend --network test-network --network-alias backend -p 5001:5000 \\
        -e DAGSHUB_USERNAME=test \\
        -e DAGSHUB_TOKEN=test \\
        -e MLFLOW_TRACKING_USERNAME=test \\
        -e MLFLOW_TRACKING_PASSWORD=test \\
        test-backend"""
    
    code, stdout, stderr = run_command(run_cmd)
    
    if code != 0:
        print(f"❌ Backend container failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    container_id = stdout.strip()
    print(f"✅ Backend container started: {container_id[:12]}")
    
    # Wait for container to start
    print("⏳ Waiting for backend to start...")
    time.sleep(10)
    
    # Check if container is still running
    check_cmd = f"docker ps -q --filter id={container_id}"
    code, stdout, stderr = run_command(check_cmd)
    
    if not stdout.strip():
        print("❌ Backend container is not running")
        # Show logs
        logs_cmd = f"docker logs {container_id}"
        code, stdout, stderr = run_command(logs_cmd)
        print(f"📋 Container logs:\n{stdout}")
        if stderr:
            print(f"📋 Container errors:\n{stderr}")
        return False
    
    print("✅ Backend container is running")
    
    # Test health endpoint
    try:
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️ Health endpoint test failed: {e}")
    
    # Test prediction endpoint
    try:
        print("🔍 Testing prediction endpoint...")
        test_data = {
            "carat": 1.0,
            "cut": "Ideal",
            "color": "H",
            "clarity": "SI1",
            "depth": 61.5,
            "table": 55.0,
            "x": 6.3,
            "y": 6.54,
            "z": 4.0
        }
        response = requests.post("http://localhost:5001/predict", 
                               json=test_data, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction endpoint working! Result: {result}")
        else:
            print(f"⚠️ Prediction endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️ Prediction endpoint test failed: {e}")
    
    return True

def test_frontend_container():
    """Test the frontend container locally"""
    print("🔍 Testing frontend container locally...")
    
    # Build the frontend image
    print("🏗️ Building frontend image...")
    build_cmd = "docker build -t test-frontend -f frontend/Dockerfile frontend/"
    code, stdout, stderr = run_command(build_cmd)
    
    if code != 0:
        print(f"❌ Frontend build failed:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    print("✅ Frontend image built successfully")
    
    # Run the frontend container
    print("🚀 Starting frontend container...")
    run_cmd = "docker run -d --name test-frontend --network test-network -p 8080:80 test-frontend"
    
    code, stdout, stderr = run_command(run_cmd)
    
    if code != 0:
        print(f"❌ Frontend container failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    container_id = stdout.strip()
    print(f"✅ Frontend container started: {container_id[:12]}")
    
    # Wait for container to start
    print("⏳ Waiting for frontend to start...")
    time.sleep(5)
    
    # Check if container is still running
    check_cmd = f"docker ps -q --filter id={container_id}"
    code, stdout, stderr = run_command(check_cmd)
    
    if not stdout.strip():
        print("❌ Frontend container is not running")
        # Show logs
        logs_cmd = f"docker logs {container_id}"
        code, stdout, stderr = run_command(logs_cmd)
        print(f"📋 Container logs:\n{stdout}")
        if stderr:
            print(f"📋 Container errors:\n{stderr}")
        return False
    
    print("✅ Frontend container is running")
    
    # Test health endpoint
    try:
        print("🔍 Testing frontend health endpoint...")
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend health endpoint working!")
        else:
            print(f"⚠️ Frontend health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️ Frontend health endpoint test failed: {e}")
    
    return True

def test_integration():
    """Test frontend-backend integration through nginx proxy"""
    print("🔍 Testing frontend-backend integration...")
    
    # Test that frontend can proxy requests to backend
    try:
        print("🔍 Testing frontend proxy to backend...")
        test_data = {
            "carat": 1.0,
            "cut": "Ideal",
            "color": "H",
            "clarity": "SI1",
            "depth": 61.5,
            "table": 55.0,
            "x": 6.3,
            "y": 6.54,
            "z": 4.0
        }
        # This should be proxied to the backend through nginx
        response = requests.post("http://localhost:8080/api/predict", 
                               json=test_data, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Frontend-backend integration working! Result: {result}")
            return True
        else:
            print(f"⚠️ Frontend-backend integration returned {response.status_code}")
    except Exception as e:
        print(f"⚠️ Frontend-backend integration test failed: {e}")
    
    return False

def setup_network():
    """Set up Docker network for testing"""
    print("🔗 Setting up Docker network...")
    
    # Create network if it doesn't exist
    create_network_cmd = "docker network create test-network 2>/dev/null || true"
    run_command(create_network_cmd)
    
    print("✅ Docker network ready")

def cleanup():
    """Clean up test containers and network"""
    print("🧹 Cleaning up test containers and network...")
    
    # Stop and remove containers
    cleanup_cmds = [
        "docker stop test-backend test-frontend 2>/dev/null || true",
        "docker rm test-backend test-frontend 2>/dev/null || true",
        "docker rmi test-backend test-frontend 2>/dev/null || true",
        "docker network rm test-network 2>/dev/null || true"
    ]
    
    for cmd in cleanup_cmds:
        run_command(cmd)
    
    print("✅ Cleanup completed")

def main():
    """Main test function"""
    print("🧪 Starting local Docker container tests...")
    print("=" * 50)
    
    success = True
    
    try:
        # Set up Docker network
        setup_network()
        
        print()
        
        # Test backend
        if not test_backend_container():
            success = False
        
        print()
        
        # Test frontend
        if not test_frontend_container():
            success = False
        
        print()
        
        # Test integration (only if both containers are running)
        if success:
            if not test_integration():
                success = False
        
        print()
        print("=" * 50)
        
        if success:
            print("🎉 All tests passed! Containers are working locally.")
            print("✅ Safe to push to GitHub Actions!")
        else:
            print("❌ Some tests failed. Fix issues before pushing to GitHub.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == "__main__":
    main() 