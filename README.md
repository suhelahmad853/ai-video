# AI Video Creator Tool

An intelligent tool for transforming YouTube videos into new, original content using AI-powered analysis and generation.

## 🚀 Project Overview

**AI Video Creator Tool** is a comprehensive solution that downloads YouTube videos, analyzes their content, and transforms them into new, original videos while ensuring compliance with YouTube's AI policies and copyright requirements.

## 📋 Features

### Phase 1: Core Infrastructure ✅
- [x] YouTube video download and validation
- [x] Content analysis for AI transformation
- [x] Audio extraction and processing
- [x] Video metadata extraction
- [x] Speech-to-text transcription (In Progress)
- [x] Content structure analysis (Planned)

### Phase 2: AI Content Transformation (Planned)
- [ ] Content rewriting engine
- [ ] Voice generation system
- [ ] Video generation engine

### Phase 3: Compliance & Quality Assurance (Planned)
- [ ] Copyright compliance system
- [ ] YouTube AI policy compliance
- [ ] Advanced user interface

### Phase 4: Optimization & Advanced Features (Planned)
- [ ] Performance optimization
- [ ] Template system
- [ ] Batch processing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Models     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Various)     │
│   TypeScript    │    │   Python        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Axios** for API communication
- **Modern CSS** with responsive design

### Backend
- **FastAPI** (Python web framework)
- **yt-dlp** for YouTube video processing
- **Uvicorn** ASGI server
- **Python 3.8+** compatibility

### AI & Processing
- **OpenAI Whisper** for speech-to-text
- **FFmpeg** for video/audio processing
- **MoviePy** for video manipulation

### Development & Deployment
- **Docker** containerization
- **Docker Compose** for local development
- **Git** version control

## 📁 Project Structure

```
ai-video-creator-tool/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── pages/           # Main application pages
│   │   ├── components/      # Reusable UI components
│   │   └── types/          # TypeScript type definitions
│   ├── package.json
│   └── Dockerfile
├── backend/                  # Python FastAPI backend
│   ├── video_processor.py   # Video processing logic
│   ├── audio_processor.py   # Audio processing logic
│   ├── main.py             # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── data/                    # Data storage directory
├── temp/                    # Temporary files
├── output/                  # Processed output files
├── docker-compose.yml       # Docker services configuration
├── start-project.sh         # One-command project startup
├── stop-project.sh          # Stop all project services
├── start-services.sh        # Legacy development startup script
├── BRD_AI_Video_Creator_Tool.md    # Business Requirements Document
├── DEVELOPMENT_PLAN.md      # Detailed development roadmap
├── PROJECT_STATUS.md        # Current project status tracker
└── README.md               # This file
```

## 🚀 Quick Start

### Option 1: One-Command Startup (Recommended) 🎯
```bash
# Start the entire project
./start-project.sh

# Stop all services
./stop-project.sh
```

**Benefits:**
- ✅ **No manual setup** - everything is automated
- ✅ **Auto-dependency installation** - creates venv and installs packages
- ✅ **Service monitoring** - shows real-time status
- ✅ **Error handling** - clear messages if something goes wrong

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

### Option 2: Manual Setup
#### Prerequisites
- **Docker** and **Docker Compose**
- **Node.js 16+** (for frontend development)
- **Python 3.8+** (for backend development)

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd ai-video-creator-tool

# Start all services
./start-services.sh

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Option 2: Local Development
```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py

# Frontend setup (in another terminal)
cd frontend
npm install
npm start
```

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python3 main.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
python3 -m pytest

# Frontend tests
cd frontend
npm test
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /process-video` - Process YouTube video
- `POST /analyze-content` - Analyze video content
- `POST /extract-metadata` - Extract video metadata
- `POST /check-restrictions` - Check video restrictions

### Audio Processing
- `POST /extract-audio` - Extract audio from video
- `POST /analyze-audio` - Analyze audio content
- `POST /prepare-audio-for-ai` - Prepare audio for AI transformation

## 🔒 Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_PORT=8001
BACKEND_HOST=0.0.0.0

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8001

# AI Model Configuration
OPENAI_API_KEY=your_api_key_here
WHISPER_MODEL=base
```

## 📈 Project Status

**Current Phase**: Phase 1.3 - Content Analysis Foundation  
**Progress**: 14% Complete (8/56 tasks)  
**Next Milestone**: Speech-to-text transcription implementation

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for detailed progress tracking.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) for detailed information
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🎯 Roadmap

- **Q1 2025**: Complete Phase 1 (Core Infrastructure)
- **Q2 2025**: Complete Phase 2 (AI Content Transformation)
- **Q3 2025**: Complete Phase 3 (Compliance & Quality)
- **Q4 2025**: Complete Phase 4 (Optimization & Advanced Features)

---

**Built with ❤️ for content creators and AI enthusiasts** 