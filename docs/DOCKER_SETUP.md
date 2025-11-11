# Docker Setup Guide - WMS Barcode Scanner

Complete guide for running the WMS Barcode Scanner Web Application using Docker.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Architecture](#docker-architecture)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

The WMS Barcode Scanner Web Application can be run in Docker for:
- **Consistent environment** across different systems
- **Easy deployment** to production
- **Isolated dependencies** from host system
- **Scalability** for multiple instances

### What is Dockerized?

✅ **Included:**
- Flask Web Application
- Python dependencies
- SQL Server ODBC Driver

❌ **Not Included:**
- SQL Server database (use external server)
- Desktop Tkinter application (use native installation with .venv)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Mac: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: Install via package manager
     ```bash
     # Ubuntu/Debian
     sudo apt-get install docker.io docker-compose

     # CentOS/RHEL
     sudo yum install docker docker-compose
     ```

2. **Docker Compose** (usually included with Docker Desktop)
   ```bash
   docker-compose --version
   ```

3. **SQL Server** (external)
   - Must be accessible from Docker containers
   - For local SQL Server, use `host.docker.internal` (Windows/Mac) or host IP (Linux)

### System Requirements

- **RAM**: Minimum 2GB available
- **Disk**: 500MB for Docker image
- **Network**: Access to SQL Server

---

## Quick Start

### 1. Create Environment File

```bash
# Copy example file
cp .env.example .env

# Edit .env with your configuration
# Windows: notepad .env
# Linux/Mac: nano .env
```

Minimum required variables:
```env
DB_SERVER=host.docker.internal  # or your SQL Server address
DB_DATABASE=WMS_BarcodeScanner
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### 2. Run Development Environment

**Windows:**
```bash
scripts\docker-run-dev.bat
```

**Linux/Mac:**
```bash
bash scripts/docker-run-dev.sh
```

### 3. Access Application

Open browser and navigate to:
- **Local**: http://localhost:5000
- **From other devices**: http://[YOUR_IP]:5000

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with these variables:

#### Database Configuration (Required)

```env
# SQL Server hostname or IP
DB_SERVER=localhost
# or use host.docker.internal for local SQL Server on Windows/Mac
DB_SERVER=host.docker.internal

# Database name
DB_DATABASE=WMS_BarcodeScanner

# Authentication type: 'SQL' or 'Windows'
# Note: Windows auth requires additional Docker configuration
DB_AUTH_TYPE=SQL

# SQL Authentication credentials (required if AUTH_TYPE=SQL)
DB_USERNAME=your_username
DB_PASSWORD=your_password

# ODBC Driver (default: ODBC Driver 17 for SQL Server)
DB_DRIVER=ODBC Driver 17 for SQL Server
```

#### Flask Configuration (Optional)

```env
# Environment: development or production
FLASK_ENV=development

# Debug mode: 1=enable, 0=disable
# WARNING: Never enable in production!
FLASK_DEBUG=1

# Host to bind (0.0.0.0 = all interfaces)
FLASK_HOST=0.0.0.0

# Port to listen on
FLASK_PORT=5000

# Secret key for sessions (generate new for production!)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
FLASK_SECRET_KEY=your-secret-key-here
```

#### Application Settings (Optional)

```env
# Timezone
TZ=Asia/Bangkok

# Maximum upload file size (MB)
MAX_UPLOAD_SIZE=10

# Session timeout (minutes)
SESSION_TIMEOUT=30

# CORS origins (comma-separated or * for all)
CORS_ORIGINS=*
```

#### Logging Configuration (Optional)

```env
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log directory
LOG_DIR=logs

# Enable file logging
LOG_TO_FILE=1

# Enable console logging
LOG_TO_CONSOLE=1
```

### Accessing Local SQL Server from Docker

#### Windows/Mac
Use `host.docker.internal`:
```env
DB_SERVER=host.docker.internal
```

#### Linux
Use host IP address:
```bash
# Find host IP
ip addr show docker0 | grep inet
# Usually 172.17.0.1

# In .env
DB_SERVER=172.17.0.1
```

---

## Running the Application

### Development Mode

**Features:**
- Hot-reload enabled (code changes reflected immediately)
- Debug mode ON
- Source code mounted for editing
- Logs persisted to `./logs`

**Commands:**
```bash
# Using scripts (recommended)
bash scripts/docker-run-dev.sh    # Linux/Mac
scripts\docker-run-dev.bat        # Windows

# Or manually
docker-compose up
```

**Stop:**
Press `Ctrl+C` or run:
```bash
docker-compose down
```

### Production Mode

**Features:**
- Optimized build
- Debug mode OFF
- Resource limits enabled
- Auto-restart on failure
- Structured logging

**Commands:**
```bash
# Using scripts (recommended)
bash scripts/docker-run-prod.sh   # Linux/Mac
scripts\docker-run-prod.bat       # Windows

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Stop:**
```bash
docker-compose down

# Or using script
bash scripts/docker-stop.sh       # Linux/Mac
scripts\docker-stop.bat           # Windows
```

### Building Custom Image

```bash
# Using script
bash scripts/docker-build.sh      # Linux/Mac
scripts\docker-build.bat          # Windows

# Or manually
docker build -t wms-barcode-scanner-web:latest .
```

### Viewing Logs

```bash
# Follow logs in real-time
docker-compose logs -f wms-web

# View last 100 lines
docker-compose logs --tail=100 wms-web

# View logs from file (persisted)
cat logs/app.log
```

### Accessing Container Shell

```bash
# Start a shell in running container
docker exec -it wms-web-app /bin/bash

# Or with docker-compose
docker-compose exec wms-web /bin/bash
```

---

## Docker Architecture

### Multi-Stage Dockerfile

```
Stage 1: Builder
├── Install build dependencies
├── Install Python packages
└── Prepare dependencies for final image

Stage 2: Runtime
├── Install SQL Server ODBC Driver
├── Copy Python dependencies from builder
├── Copy application code
├── Create non-root user (security)
├── Configure environment
└── Set up health check
```

**Benefits:**
- Smaller final image (~200MB vs ~500MB)
- No build tools in production image
- Better security (non-root user)

### Docker Compose Services

```yaml
wms-web:
  ├── Base configuration (docker-compose.yml)
  ├── Development overrides (docker-compose.override.yml)
  └── Production overrides (docker-compose.prod.yml)
```

**Automatic loading:**
- `docker-compose up` → Uses base + override (dev)
- `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up` → Uses base + prod

### Volumes

```
./logs:/app/logs
- Persist application logs
- Accessible on host system

./src:/app/src (dev only)
- Mount source code
- Enable hot-reload
```

### Networks

```
wms-network (bridge)
- Isolated network for services
- Can add SQL Server container if needed
```

---

## Troubleshooting

### Cannot Connect to Database

**Symptoms:**
- "Cannot connect to SQL Server"
- "Login failed for user"

**Solutions:**

1. **Check SQL Server accessibility:**
   ```bash
   # From inside container
   docker exec -it wms-web-app /bin/bash
   ping your-sql-server
   ```

2. **Verify connection string:**
   - Windows/Mac: Use `host.docker.internal`
   - Linux: Use host IP (usually `172.17.0.1`)

3. **Check SQL Server firewall:**
   - Allow connections from Docker network
   - Enable TCP/IP protocol
   - Default port: 1433

4. **Verify credentials:**
   ```bash
   # Test from host first
   sqlcmd -S localhost -U username -P password
   ```

### Container Fails to Start

**Check logs:**
```bash
docker-compose logs wms-web
docker logs wms-web-app
```

**Common issues:**

1. **Port already in use:**
   ```bash
   # Change port in .env
   FLASK_PORT=5001
   ```

2. **Missing .env file:**
   ```bash
   cp .env.example .env
   # Edit with your settings
   ```

3. **Invalid environment variables:**
   - Check for typos in .env
   - Ensure no trailing spaces
   - Use quotes for values with spaces

### Health Check Failures

**Symptoms:**
- Container shows as "unhealthy"
- `docker ps` shows status: (unhealthy)

**Solutions:**

1. **Check if app is running:**
   ```bash
   docker exec wms-web-app curl http://localhost:5000/health
   ```

2. **View detailed logs:**
   ```bash
   docker inspect wms-web-app | grep -A 20 Health
   ```

3. **Disable health check temporarily:**
   Edit `docker-compose.yml`:
   ```yaml
   healthcheck:
     disable: true
   ```

### Hot-Reload Not Working (Development)

**Verify volume mount:**
```bash
docker inspect wms-web-app | grep Mounts -A 20
```

**Ensure using development mode:**
```bash
docker-compose up
# NOT: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Permission Errors

**Symptoms:**
- "Permission denied" when writing logs
- Cannot create files

**Solutions:**

1. **Fix log directory permissions:**
   ```bash
   sudo chown -R 1000:1000 logs/
   # 1000 is the UID of wmsuser in container
   ```

2. **Run with correct user:**
   Already configured in Dockerfile (non-root user)

---

## Best Practices

### Security

1. **Never commit .env files:**
   - Already in `.gitignore`
   - Use `.env.example` as template

2. **Use strong passwords:**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Run as non-root user:**
   - Already configured in Dockerfile
   - Container runs as `wmsuser` (UID 1000)

4. **Use environment variables for secrets:**
   - Never hardcode passwords
   - Use Docker secrets in production (if using Swarm)

### Performance

1. **Resource limits (production):**
   - Already configured in `docker-compose.prod.yml`
   - Adjust based on your needs:
     ```yaml
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
     ```

2. **Multi-stage builds:**
   - Reduces image size
   - Faster deployments

3. **Log rotation:**
   - Configured in `docker-compose.prod.yml`
   - Max size: 10MB, Max files: 3

### Development Workflow

1. **Use development mode for coding:**
   ```bash
   docker-compose up
   ```

2. **Test production build before deploying:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

3. **Keep images updated:**
   ```bash
   docker-compose build --no-cache
   ```

### Maintenance

1. **Clean up unused resources:**
   ```bash
   # Remove stopped containers
   docker-compose down

   # Remove unused images
   docker system prune -a
   ```

2. **Backup logs regularly:**
   ```bash
   tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats wms-web-app
   ```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Flask in Docker](https://flask.palletsprojects.com/en/2.3.x/tutorial/deploy/)
- [SQL Server on Docker](https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker)

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker-compose logs wms-web`
3. Check application logs in `./logs/` directory
4. Contact the development team

---

**🐳 Happy Dockering!**
