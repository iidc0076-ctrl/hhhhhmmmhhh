# Use a standard Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy your entire project into the container
COPY . .

# Optional: If you eventually add requirements, this line won't break the build
RUN if [ -f 2_core_system/requirements.txt ]; then pip install -r 2_core_system/requirements.txt; fi

# Run your main script
CMD ["python", "2_core_system/main.py"]
