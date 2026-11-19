# RTI Mitra - Dockerfile
# Builds a single image that runs the FastAPI API.
# The Streamlit UI is a separate service in docker-compose.yml.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose API port
EXPOSE 8000

# Start the FastAPI service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
