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

# Expose port for web interface
EXPOSE 8000

# Default command runs web interface
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
