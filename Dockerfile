# Use a standard Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies that might be needed for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better layer caching
COPY requirements.txt /app/requirements.txt

# Verify requirements.txt exists and list contents
RUN echo "=== Installing dependencies ===" && \
    cat /app/requirements.txt && \
    echo "=== End of requirements ===" && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt

# Verify key dependencies are installed
RUN python -c "import pandas; import discord; import aiohttp; import flask; import matplotlib; print('✓ All dependencies installed successfully')"

# Copy the entire project into the container
COPY . /app/

# Run your main script
CMD ["python", "2_core_system/main.py"]
