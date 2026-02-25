# NotebookLM API and Telegram Bot Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy notebooklm-mcp-cli and install it
COPY notebookLM-MCP-CLI/ ./notebookLM-MCP-CLI/
RUN pip install --no-cache-dir ./notebookLM-MCP-CLI

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create data directory for auth tokens
RUN mkdir -p /app/data

# Set permissions
RUN chmod +x scripts/*.sh 2>/dev/null || true

# Expose API port
EXPOSE 8777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8777/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "src.api.main"]
