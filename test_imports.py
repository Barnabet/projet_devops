#!/usr/bin/env python3
"""
Quick import test to verify all dependencies are available
This is faster than building Docker containers
"""

import sys

def test_imports():
    """Test all the critical imports that might fail"""
    
    tests = [
        ("flask", "Flask web framework"),
        ("pandas", "Data manipulation"),
        ("sklearn", "Machine learning"),
        ("numpy", "Numerical computing"),
        ("mlflow", "MLflow main module"),
        ("dagshub", "DagsHub integration"),
        ("pydantic", "Data validation"),
        ("six", "Python 2/3 compatibility"),
        ("requests", "HTTP library"),
        ("boto3", "AWS SDK"),
        ("dvc", "Data version control"),
    ]
    
    print("🧪 Testing critical imports...")
    print("=" * 50)
    
    failed = []
    
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {module:<15} - {description}")
        except ImportError as e:
            print(f"❌ {module:<15} - FAILED: {e}")
            failed.append(module)
        except Exception as e:
            print(f"⚠️  {module:<15} - ERROR: {e}")
            failed.append(module)
    
    print("=" * 50)
    
    if failed:
        print(f"❌ {len(failed)} imports failed: {', '.join(failed)}")
        return False
    else:
        print("🎉 All imports successful!")
        return True

def test_mlflow_specific():
    """Test MLflow specific imports that often fail"""
    print("\n🔍 Testing MLflow specific imports...")
    
    mlflow_tests = [
        "mlflow.sklearn",
        "mlflow.tracking",
        "mlflow.models",
        "mlflow.artifacts",
        "databricks_cli.configure.provider",
        "pydantic.version",
        "typing_inspection.introspection",
    ]
    
    failed = []
    
    for module in mlflow_tests:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            failed.append(module)
        except Exception as e:
            print(f"⚠️  {module} - ERROR: {e}")
    
    if failed:
        print(f"❌ MLflow imports failed: {', '.join(failed)}")
        return False
    else:
        print("✅ All MLflow imports successful!")
        return True

if __name__ == "__main__":
    print("🚀 Quick Dependency Test (no Docker needed)")
    print("This tests if all imports work in your current environment\n")
    
    success1 = test_imports()
    success2 = test_mlflow_specific()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Dependencies should work in Docker.")
        sys.exit(0)
    else:
        print("\n❌ Some imports failed. Need to fix dependencies before Docker build.")
        sys.exit(1) 