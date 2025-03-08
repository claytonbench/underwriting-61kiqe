# Use Python 3.11 slim image as the base
# python version: 3.11-slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements files
# Copying these first to leverage Docker's layer caching
COPY requirements.txt requirements-dev.txt ./

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Copy application code
COPY . .

# Expose port for the development server
EXPOSE 8000

# Command to run the application in development mode
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]