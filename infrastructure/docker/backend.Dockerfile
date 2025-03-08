# Stage 1: Builder stage
FROM python:3.11-slim AS builder

# Set working directory
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Set environment variables for better container experience
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    # WeasyPrint dependencies for PDF generation
    build-essential \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Cleanup to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file first for better layer caching
COPY src/backend/requirements.txt .
# Generate wheels for all dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt
# Install dependencies (needed for collectstatic)
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels -r requirements.txt

# Copy application code
COPY src/backend .

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Security scanning
FROM aquasec/trivy:latest AS security-scan

# Copy application code for scanning
WORKDIR /app
COPY --from=builder /app /app

# Run Trivy security scan and fail build if critical vulnerabilities are found
RUN trivy filesystem --exit-code 1 --severity CRITICAL /app

# Stage 3: Production stage with minimal dependencies
FROM python:3.11-slim AS production

# Set working directory
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    # WeasyPrint runtime dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Create non-root user for security
    && useradd -m appuser

# Copy application code
COPY --from=builder /app /app

# Copy wheels and install packages without rebuilding
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Set appropriate permissions
RUN chown -R appuser:appuser ${APP_HOME}

# Switch to non-root user
USER appuser

# Expose port for gunicorn
EXPOSE 8000

# Start gunicorn with appropriate worker configuration
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60"]