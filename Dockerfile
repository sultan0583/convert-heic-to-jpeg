# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for image processing
RUN apt-get update && apt-get install -y \
    libheif1 \
    libheif-dev \
    libde265-0 \
    libx265-dev \
    pkg-config \
    libmagic1 \
    file \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY convert_heic.py .

# Create photos directory
RUN mkdir -p /app/photos

# Make the script executable
RUN chmod +x convert_heic.py

# Set the default command
CMD ["python", "convert_heic.py"]
