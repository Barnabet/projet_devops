#!/usr/bin/env python3
"""
Test script to verify Docker containers are running correctly.
"""
import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint."""
    try:
        response = requests.get('http://localhost:5001/health')
        print(f"Backend Health Status: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Backend health check failed: {e}")
        return False

def test_frontend_health():
    """Test frontend health endpoint."""
    try:
        response = requests.get('http://localhost:8080/health')
        print(f"Frontend Health Status: {response.status_code}")
        print(f"Frontend Response: {response.text.strip()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Frontend health check failed: {e}")
        return False

def test_frontend_main_page():
    """Test frontend main page."""
    try:
        response = requests.get('http://localhost:8080/')
        print(f"Frontend Main Page Status: {response.status_code}")
        print(f"Frontend contains 'Diamond Price Prediction': {'Diamond Price Prediction' in response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Frontend main page test failed: {e}")
        return False

def test_backend_prediction():
    """Test backend prediction endpoint."""
    try:
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
        
        response = requests.post(
            'http://localhost:5001/predict',
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        print(f"Backend Prediction Status: {response.status_code}")
        print(f"Backend Prediction Response: {response.json()}")
        
        # We expect either a successful prediction or a model not loaded error
        return response.status_code == 200
    except Exception as e:
        print(f"Backend prediction test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🐳 Testing Docker Containers")
    print("=" * 50)
    
    # Wait a moment for containers to fully start
    print("Waiting for containers to initialize...")
    time.sleep(2)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Health", test_frontend_health),
        ("Frontend Main Page", test_frontend_main_page),
        ("Backend Prediction", test_backend_prediction),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print(f"✅ PASSED" if result else f"❌ FAILED")
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Docker containers are working correctly!")
        print("\n📱 Access the application:")
        print("   Frontend: http://localhost:8080")
        print("   Backend API: http://localhost:5001")
        print("   Health Checks:")
        print("     - Frontend: http://localhost:8080/health")
        print("     - Backend: http://localhost:5001/health")
    else:
        print("⚠️  Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 