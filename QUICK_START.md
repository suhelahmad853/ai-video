# 🚀 AI Video Creator Tool - Quick Start Guide

## One-Command Project Startup

We've created simple scripts to make running the project much easier!

### 🟢 Start the Project
```bash
./start-project.sh
```

This script will:
- ✅ Check if ports are available
- ✅ Create virtual environment if needed
- ✅ Install Python dependencies if needed
- ✅ Install Node.js dependencies if needed
- ✅ Start backend server (http://localhost:8001)
- ✅ Start frontend server (http://localhost:3000)
- ✅ Monitor services and show status

### 🔴 Stop the Project
```bash
./stop-project.sh
```

This script will:
- ✅ Stop all backend services
- ✅ Stop all frontend services
- ✅ Free up ports 8001 and 3000
- ✅ Clean up processes

### 📱 Access the Application

Once started, you can access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Health Check**: http://localhost:8001/health

### 🐛 Troubleshooting

If you encounter issues:

1. **Port already in use**: Run `./stop-project.sh` first
2. **Backend won't start**: Check `backend.log` for errors
3. **Frontend won't start**: Check `frontend.log` for errors
4. **Dependencies missing**: The script will auto-install them

### 🔧 Manual Commands (if needed)

If you prefer to run services manually:

**Backend:**
```bash
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```bash
cd frontend
npm start
```

### 📝 What the Scripts Do

The startup script automatically:
- Creates Python virtual environment
- Installs Python requirements
- Installs Node.js dependencies
- Starts both services in background
- Monitors service health
- Provides colored output for easy reading
- Handles errors gracefully

### 🎯 Benefits

- **No more manual setup** - everything is automated
- **One command to start** - `./start-project.sh`
- **One command to stop** - `./stop-project.sh`
- **Auto-dependency installation** - no manual pip/npm install
- **Service monitoring** - see if everything is running
- **Error handling** - clear messages if something goes wrong

---

**Happy coding! 🎉** 