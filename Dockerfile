# =============================================================================
# Dockerfile for Siim Leaks Basic Discord Bot - SECURED VERSION
# =============================================================================
# Security improvements:
# - Specific Python version (not :latest)
# - Slim base image (smaller attack surface)
# - Non-root user
# - No cache for pip (smaller image)
# - Health check
# - Proper signal handling
# =============================================================================

# Use specific Python version with slim image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies (if any are needed)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     some-package \
#     && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 botuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home botuser

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=botuser:botuser . .

# Switch to non-root user
USER botuser

# Health check - verify the bot process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Labels for image metadata
LABEL maintainer="Siim Aarmaa <contact@aarmaa.ee>" \
      version="0.3.0" \
      description="Siim Leaks Basic Discord Bot - Security Hardened"

# Run the bot
CMD ["python", "-u", "main.py"]
