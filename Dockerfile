# Use a standard Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set the working directory
WORKDIR /app

# Install system dependencies that might be needed for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better layer caching
COPY requirements.txt /app/

# Verify requirements.txt exists
RUN if [ ! -f /app/requirements.txt ]; then echo "ERROR: requirements.txt not found!"; exit 1; fi

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt

# Copy the entire project into the container
COPY . /app/

# Run your main script
CMD ["python", "2_core_system/main.py"]
