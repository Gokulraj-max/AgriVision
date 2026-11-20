FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-optimized PyTorch first (fast build, low RAM)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure sample images and weights are generated
RUN python scripts/generate_synthetic_samples.py && \
    python scripts/train_weather_model.py

EXPOSE 8000

CMD ["sh", "-c", "uvicorn agrivision.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
