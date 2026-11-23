# RTI Mitra - Dockerfile
# Builds image with Chroma index pre-built inside.
# This solves the Render free tier OOM problem:
# - Uses requirements-deploy.txt (no torch/sentence-transformers)
# - Builds the Chroma index at image build time (not startup time)
# - Index is baked into the image so startup is instant

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (lightweight - no torch)
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-deploy.txt

# Copy project files
COPY . .

# Pre-build the Chroma index during image build
# This runs once at build time, not at startup
RUN python -c "from app.vectorstore import build_index; build_index(); print('Index built successfully')"

# Expose API port
EXPOSE 8000

# Start the FastAPI service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
