# Multi-stage Dockerfile for ML Backend - TEST VERSION
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    scikit-learn \
    pandas \
    numpy \
    pydantic \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    sqlalchemy \
    psycopg2-binary \
    requests \
    && pip install --no-cache-dir -r requirements.txt || echo "Some requirements may fail"

# Copy application code
COPY app/ /app/app/

# Create directories
RUN mkdir -p /app/mlruns /app/models /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=10s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health/liveness || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]