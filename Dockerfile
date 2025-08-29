# Multi-stage Docker build for AI Video Creator Tool
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build (we'll build this in the next stage)
COPY frontend/ ./frontend/

# Expose ports
EXPOSE 8001 3000

# Create output directories
RUN mkdir -p /app/output/visuals /app/output/slides /app/output/graphics /app/output/videos /app/output/temp

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Default command
CMD ["python", "backend/main.py"] 