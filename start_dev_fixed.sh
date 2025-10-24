#!/bin/bash

# VRP Optimizer Development Startup Script (Fixed)
echo "🚀 Starting VRP Optimizer Development Environment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the VRP project root directory"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source .venv/bin/activate

# Install main project dependencies in venv
echo "📦 Installing main project dependencies in virtual environment..."
pip install -r requirements.txt

# Install backend dependencies in venv
echo "📦 Installing backend dependencies in virtual environment..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies (Node.js, no venv needed)
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "🌐 Starting development servers..."
echo ""
echo "Backend API: http://localhost:8000 (Python venv)"
echo "Frontend App: http://localhost:5173 (Node.js)"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start backend server (in virtual environment)
echo "🔧 Starting backend API server (in Python venv)..."
cd backend
source ../.venv/bin/activate && python3 -m uvicorn main_integrated:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend server
echo "🎨 Starting frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
echo "🎉 Development environment is running!"
echo "Open http://localhost:5173 in your browser"
echo ""
echo "Environment status:"
echo "- Python venv: $(which python)"
echo "- Node.js: $(which node)"
echo ""
wait
