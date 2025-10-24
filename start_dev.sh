#!/bin/bash

# VRP Optimizer Development Startup Script
echo "🚀 Starting VRP Optimizer Development Environment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the VRP project root directory"
    exit 1
fi

# Install main project dependencies
echo "📦 Installing main project dependencies..."
python3 -m pip install -r requirements.txt

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
python3 -m pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "🌐 Starting development servers..."
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend App: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start backend server
echo "🔧 Starting backend API server..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
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
wait
