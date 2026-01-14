# ApexAurum Main Application Container
# Production-grade AI Chat Interface
#
# Build:  docker build -f Dockerfile.app -t apexaurum:latest .
# Run:    docker-compose up
#
# Note: Use docker-compose.yml for full deployment (includes volumes, sandbox access)

FROM python:3.11-slim-bookworm

LABEL maintainer="ApexAurum"
LABEL description="ApexAurum - Claude Edition: AI Chat Interface with Multi-Agent Orchestration"
LABEL version="1.0"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Python settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Streamlit settings
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials for compiling Python packages
    build-essential \
    gcc \
    g++ \
    # For git operations
    git \
    # Network tools (for healthcheck)
    curl \
    # Docker CLI (for sandbox execution)
    docker.io \
    # For Pillow/image processing
    libjpeg-dev \
    libpng-dev \
    # For OCR (optional)
    tesseract-ocr \
    ghostscript \
    # FluidSynth for MIDI (optional)
    fluidsynth \
    fluid-soundfont-gm \
    # FFmpeg for audio/video processing
    ffmpeg \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies in layers for better caching
# Layer 1: Heavy ML dependencies (biggest, changes least)
RUN pip install \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install \
    transformers \
    sentence-transformers

# Layer 2: Core dependencies
RUN pip install \
    streamlit \
    anthropic \
    chromadb \
    python-dotenv

# Layer 3: All remaining dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p sandbox sandbox/datasets

# Create non-root user for security (optional - commented for Docker socket access)
# RUN useradd -m -s /bin/bash apex && chown -R apex:apex /app
# USER apex

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["streamlit", "run", "main.py"]
