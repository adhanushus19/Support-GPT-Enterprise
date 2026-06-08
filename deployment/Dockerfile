# Multi-stage build setup using official Python 3.12 image
FROM python:3.12-slim as builder

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into user directory
RUN pip install --user --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.12-slim as runner

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Adjust PATH variables for local python binaries
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

EXPOSE 8000

# Run FastAPI backend
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
