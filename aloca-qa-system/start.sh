#!/bin/bash

# ALOCA+ QA System Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting ALOCA+ QA System..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is not installed. Please install Python 3.8 or later.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js is not installed. Please install Node.js 14 or later.${NC}"
    exit 1
fi

# Start Backend
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start backend server in background
python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"

# Give backend time to start
sleep 2

# Start Frontend
echo ""
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies (this may take a minute)..."
    npm install -q
fi

# Start frontend server
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend server started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}✅ ALOCA+ QA System is running!${NC}"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "⚙️  Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for both processes
wait
