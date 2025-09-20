# Lightweight Ingest Service Demo
# This demonstrates how the developer console's ingest service can be containerized

FROM python:3.11-alpine

# Install system dependencies for file analysis
RUN apk add --no-cache \
    git \
    file \
    libmagic \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN adduser -D -s /bin/sh ingest

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Change ownership to non-root user
RUN chown -R ingest:ingest /app

# Switch to non-root user
USER ingest

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the service
CMD ["python", "-m", "src.main"]

# Expected size: ~50MB
# Startup time: ~2-3 seconds
# Memory usage: ~64MB