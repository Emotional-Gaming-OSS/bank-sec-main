# BankSec Enterprise - Production Dockerfile
# Multi-stage build for security and optimization

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG APP_USER=banksec
ARG APP_UID=1000
ARG APP_GID=1000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -s /bin/bash -m ${APP_USER}

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} . .

# Production stage
FROM python:3.11-slim as production

# Set build arguments
ARG APP_USER=banksec
ARG APP_UID=1000
ARG APP_GID=1000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -s /bin/bash -m ${APP_USER}

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder --chown=${APP_USER}:${APP_USER} /app .

# Create necessary directories
RUN mkdir -p logs data config && \
    chown -R ${APP_USER}:${APP_USER} logs data config

# Switch to app user
USER ${APP_USER}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PATH=/usr/local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--config", "config/gunicorn.conf.py", "src.entrypoints.api.app:create_app()"]

# Labels for metadata
LABEL maintainer="BankSec Team <dev@banksec-enterprise.com>"
LABEL version="2.0.0"
LABEL description="BankSec Enterprise - Cybersecurity Training Platform"
LABEL org.opencontainers.image.source="https://github.com/banksec/banksec-enterprise"