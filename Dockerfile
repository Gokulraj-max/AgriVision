FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=10000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies using CPU index
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure sample images and weights are generated
RUN python scripts/generate_synthetic_samples.py && \
    python scripts/train_weather_model.py

EXPOSE 10000

CMD ["sh", "-c", "uvicorn agrivision.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
