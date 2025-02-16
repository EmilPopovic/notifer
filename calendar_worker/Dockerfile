FROM python:3.13-slim

WORKDIR /app

# Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install shared package
COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Install calendar_worker dependencies
COPY backend-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt.txt

# Copy calendar_worker code
COPY backend-worker/app /app/app

# Command to run the calendar_worker
CMD ["python", "-m", "app.worker"]