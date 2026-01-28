# Use a standard Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies that might be needed for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Run your main script
CMD ["python", "2_core_system/main.py"]
