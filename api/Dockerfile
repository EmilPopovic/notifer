# Use a lightweight Python base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for SQLite and some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy shared code and install it as a package
COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Copy API code and install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the API code
COPY api/app /app/app

# Expose the API port
EXPOSE ${API_PORT}

# Run the app with UVicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${API_PORT}"]