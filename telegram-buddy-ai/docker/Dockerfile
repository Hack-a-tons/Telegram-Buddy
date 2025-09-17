FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY telegram_runner.py .

# Create data directory for persistence
RUN mkdir -p /app/data

# Default command runs web interface with PORT from environment
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
