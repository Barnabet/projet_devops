#!/usr/bin/env python3
"""
Test Runner for Diamond Price Prediction Application

This script provides an easy way to run all tests or specific test suites.
"""

import subprocess
import sys
import os
import argparse

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def install_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, cwd=os.path.dirname(__file__))
        print("✅ Test dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install test dependencies")
        return False

def run_unit_tests():
    """Run unit tests"""
    cmd = [sys.executable, '-m', 'pytest', 'test_unit.py', '-v', '--tb=short']
    return run_command(cmd, "Unit Tests")

def run_integration_tests():
    """Run integration tests"""
    cmd = [sys.executable, '-m', 'pytest', 'test_integration.py', '-v', '--tb=short']
    return run_command(cmd, "Integration Tests")

def run_e2e_tests():
    """Run end-to-end tests"""
    cmd = [sys.executable, '-m', 'pytest', 'test_e2e.py', '-v', '--tb=short']
    return run_command(cmd, "End-to-End Tests")

def run_all_tests():
    """Run all tests"""
    cmd = [sys.executable, '-m', 'pytest', '.', '-v', '--tb=short']
    return run_command(cmd, "All Tests")

def run_tests_with_coverage():
    """Run all tests with coverage report"""
    cmd = [sys.executable, '-m', 'pytest', '.', '-v', '--tb=short', 
           '--cov=../backend', '--cov-report=html', '--cov-report=term']
    return run_command(cmd, "All Tests with Coverage")

def main():
    parser = argparse.ArgumentParser(description='Run tests for Diamond Price Prediction Application')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install test dependencies before running tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests only')
    parser.add_argument('--coverage', action='store_true', help='Run all tests with coverage report')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # Change to tests directory
    os.chdir(os.path.dirname(__file__))
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Determine which tests to run
    results = []
    
    if args.unit:
        results.append(run_unit_tests())
    elif args.integration:
        results.append(run_integration_tests())
    elif args.e2e:
        results.append(run_e2e_tests())
    elif args.coverage:
        results.append(run_tests_with_coverage())
    else:
        # Default: run all tests
        results.append(run_all_tests())
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} test suite(s) PASSED")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} out of {total} test suite(s) FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main() 