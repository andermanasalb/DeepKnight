FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first for layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Backend application code
COPY backend/ .

# PyTorch model (2.8 MB — lives outside backend/ so needs root build context)
COPY data/models/ data/models/

# Runtime directories
RUN mkdir -p data/raw data/processed mlruns

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
