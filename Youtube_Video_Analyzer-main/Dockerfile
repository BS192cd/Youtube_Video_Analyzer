# Multi-stage Dockerfile for YouTube Transcript Summarizer
# Base image: Python 3.12 slim (minimal footprint)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create directory for .env (will be mounted at runtime)
RUN mkdir -p /app/config

# Expose Streamlit default port
EXPOSE 8501

# Health check for container orchestration
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit application
# Note: .env should be provided at runtime via volume mount or environment variables
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
