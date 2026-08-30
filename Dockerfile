# syntax=docker/dockerfile:1.7

###############################################################################
# Base stage: shared python environment
###############################################################################
FROM python:3.11-slim AS base

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app"

WORKDIR /app

###############################################################################
# Dependencies stage: install runtime dependencies with caching
###############################################################################
FROM base AS deps

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --requirement requirements.txt

###############################################################################
# Runtime stage: minimal, non-root image with app source only
###############################################################################
FROM base AS runtime

# Create non-root user first so files are owned correctly
RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Copy dependencies
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source
COPY app ./app

# Ensure the non-root user owns the working directory and the data dir
RUN mkdir -p /app/data && \
    chown -R app:app /app

USER app

# Graceful shutdown
STOPSIGNAL SIGINT

# Health check (executes inside the container against the API)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health', timeout=3)" || exit 1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
