# ===================================================================
# WMS Barcode Scanner - Web Application Dockerfile
# ===================================================================
# Multi-stage build for optimized production image
# ===================================================================

# ===================================================================
# Stage 1: Builder
# ===================================================================
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies to a temporary location
RUN pip install --no-cache-dir --prefix=/install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===================================================================
# Stage 2: Runtime
# ===================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install SQL Server ODBC Driver 17
# This is required for pyodbc to connect to SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get purge -y curl gnupg2 apt-transport-https \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN useradd -m -u 1000 wmsuser && \
    chown -R wmsuser:wmsuser /app

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R wmsuser:wmsuser /app/logs

# Copy application code
COPY --chown=wmsuser:wmsuser . .

# Switch to non-root user
USER wmsuser

# Environment variables with default values
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=src/web/app.py \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Run the web application
CMD ["python", "src/web/app.py"]
