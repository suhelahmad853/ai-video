#!/bin/bash

# AI Video Creator Tool - Project Startup Script
# This script starts both backend and frontend services

echo "🚀 Starting AI Video Creator Tool..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Port $1 is already in use!${NC}"
        return 1
    fi
    return 0
}

# Function to stop services
stop_services() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
    echo -e "${GREEN}Services stopped.${NC}"
}

# Trap to stop services on script exit
trap stop_services EXIT

# Check if ports are available
echo -e "${BLUE}Checking ports...${NC}"
if ! check_port 8001; then
    echo -e "${RED}Backend port 8001 is busy. Please stop the service using that port.${NC}"
    exit 1
fi

if ! check_port 3000; then
    echo -e "${RED}Frontend port 3000 is busy. Please stop the service using that port.${NC}"
    exit 1
fi

# Start Backend
echo -e "${BLUE}Starting Backend (Python FastAPI)...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
fi

# Start backend in background
echo -e "${GREEN}Starting backend server on http://localhost:8001${NC}"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${BLUE}Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running!${NC}"
else
    echo -e "${RED}❌ Backend failed to start. Check backend.log for details.${NC}"
    exit 1
fi

cd ..

# Start Frontend
echo -e "${BLUE}Starting Frontend (React)...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend server on http://localhost:3000${NC}"
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
echo -e "${BLUE}Waiting for frontend to start...${NC}"
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running!${NC}"
else
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log for details.${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 AI Video Creator Tool is now running!${NC}"
echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}Backend API: http://localhost:8001${NC}"
echo -e "${BLUE}API Health: http://localhost:8001/health${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep script running and monitor services
while true; do
    sleep 5
    
    # Check if services are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend service stopped unexpectedly${NC}"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend service stopped unexpectedly${NC}"
        break
    fi
done

echo -e "\n${YELLOW}One or more services stopped. Check the logs for details.${NC}"
echo -e "${BLUE}Backend log: backend.log${NC}"
echo -e "${BLUE}Frontend log: frontend.log${NC}" 