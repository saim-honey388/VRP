#!/usr/bin/env python3
"""
Comprehensive verification script for VRP development environment
"""

import sys
import os
import subprocess
import requests
import json
from datetime import datetime

def test_python_environment():
    """Test Python virtual environment and VRP modules"""
    print("🐍 Testing Python Environment")
    print("-" * 40)
    
    # Check if we're in venv
    venv_path = os.path.join(os.getcwd(), '.venv')
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found")
        return False
    
    # Check Python path
    python_path = sys.executable
    if '.venv' not in python_path:
        print("❌ Not running in virtual environment")
        print(f"   Current Python: {python_path}")
        return False
    
    print(f"✅ Virtual environment: {python_path}")
    
    # Test VRP imports
    try:
        import vrp_mvp
        from vrp_mvp.solver import solve_baseline
        from vrp_mvp.models import Instance, Depot, Factory, Shift
        print("✅ VRP modules imported successfully")
        print(f"   VRP module path: {vrp_mvp.__file__}")
        return True
    except ImportError as e:
        print(f"❌ VRP import failed: {e}")
        return False

def test_backend_dependencies():
    """Test backend API dependencies"""
    print("\n🔧 Testing Backend Dependencies")
    print("-" * 40)
    
    try:
        import fastapi
        import uvicorn
        print(f"✅ FastAPI: {fastapi.__version__}")
        print(f"✅ Uvicorn: {uvicorn.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Backend dependencies missing: {e}")
        return False

def test_backend_api():
    """Test backend API server"""
    print("\n🌐 Testing Backend API")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API responding")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   VRP Solver Available: {data.get('vrp_solver_available', 'N/A')}")
            return True
        else:
            print(f"❌ Backend API error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API not responding: {e}")
        return False

def test_frontend():
    """Test frontend server"""
    print("\n🎨 Testing Frontend")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server responding")
            if "vite" in response.text.lower() or "react" in response.text.lower():
                print("✅ Frontend content detected")
                return True
            else:
                print("⚠️  Frontend responding but content unclear")
                return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not responding: {e}")
        return False

def test_node_environment():
    """Test Node.js environment"""
    print("\n📦 Testing Node.js Environment")
    print("-" * 40)
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not available")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ Node.js test failed: {e}")
        return False

def test_project_structure():
    """Test project directory structure"""
    print("\n📁 Testing Project Structure")
    print("-" * 40)
    
    required_dirs = ['.venv', 'frontend', 'backend', 'vrp_mvp']
    required_files = ['requirements.txt', 'start_dev_fixed.sh']
    
    all_good = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ missing")
            all_good = False
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} missing")
            all_good = False
    
    return all_good

def main():
    """Run all verification tests"""
    print("🧪 VRP Development Environment Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Python Environment", test_python_environment),
        ("Backend Dependencies", test_backend_dependencies),
        ("Node.js Environment", test_node_environment),
        ("Backend API", test_backend_api),
        ("Frontend", test_frontend),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Environment is ready.")
        print("\n🚀 You can now run:")
        print("   ./start_dev_fixed.sh")
        print("\n🌐 Access the application:")
        print("   Frontend: http://localhost:5173")
        print("   Backend API: http://localhost:8000")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
