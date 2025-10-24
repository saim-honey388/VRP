#!/usr/bin/env python3
"""
Test script to verify the VRP development environment setup
"""

import sys
import os

def test_environment():
    print("🧪 Testing VRP Development Environment Setup")
    print("=" * 50)
    
    # Test 1: Python virtual environment
    print("1. Testing Python virtual environment...")
    venv_path = os.path.join(os.getcwd(), '.venv')
    if os.path.exists(venv_path):
        print("   ✅ Virtual environment exists")
    else:
        print("   ❌ Virtual environment not found")
        return False
    
    # Test 2: VRP module import
    print("2. Testing VRP module import...")
    try:
        import vrp_mvp
        print("   ✅ VRP module imports successfully")
    except ImportError as e:
        print(f"   ❌ VRP module import failed: {e}")
        return False
    
    # Test 3: Backend dependencies
    print("3. Testing backend dependencies...")
    try:
        import fastapi
        import uvicorn
        print("   ✅ Backend dependencies available")
    except ImportError as e:
        print(f"   ❌ Backend dependencies missing: {e}")
        return False
    
    # Test 4: Frontend directory
    print("4. Testing frontend directory...")
    frontend_path = os.path.join(os.getcwd(), 'frontend')
    if os.path.exists(frontend_path):
        print("   ✅ Frontend directory exists")
    else:
        print("   ❌ Frontend directory not found")
        return False
    
    # Test 5: Node.js availability
    print("5. Testing Node.js availability...")
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js available: {result.stdout.strip()}")
        else:
            print("   ❌ Node.js not available")
            return False
    except FileNotFoundError:
        print("   ❌ Node.js not found in PATH")
        return False
    
    print("\n🎉 All tests passed! Environment is ready.")
    return True

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
