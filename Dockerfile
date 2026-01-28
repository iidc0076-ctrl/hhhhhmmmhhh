# Use a standard Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Run your main script
CMD ["python", "2_core_system/main.py"]
