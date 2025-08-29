#!/bin/bash

# AI Video Creator Tool - Project Stop Script
# This script stops both backend and frontend services

echo "🛑 Stopping AI Video Creator Tool..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Stop backend services
echo -e "${BLUE}Stopping backend services...${NC}"
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "python3 -m uvicorn" 2>/dev/null

# Stop frontend services
echo -e "${BLUE}Stopping frontend services...${NC}"
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

# Stop any other related processes
echo -e "${BLUE}Cleaning up other processes...${NC}"
pkill -f "node.*start" 2>/dev/null

# Check if ports are free
sleep 2

if ! lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend port 8001 is free${NC}"
else
    echo -e "${RED}❌ Backend port 8001 is still in use${NC}"
fi

if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend port 3000 is free${NC}"
else
    echo -e "${RED}❌ Frontend port 3000 is still in use${NC}"
fi

echo -e "\n${GREEN}🎉 All services stopped!${NC}"
echo -e "${YELLOW}You can now run ./start-project.sh to start the project again.${NC}" 