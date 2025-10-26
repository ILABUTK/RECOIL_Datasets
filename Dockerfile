# Notebook-to-webapp container using Voilà
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLCONFIGDIR=/tmp/matplotlib

# System packages kept minimal; rely on manylinux wheels for geospatial deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app

# Create a non-root user
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Voilà defaults
ENV VOILA_PORT=8866 \
    VOILA_IP=0.0.0.0 \
    VOILA_NOTEBOOK=voila.ipynb

# Start script
RUN chmod +x /app/start.sh || true

EXPOSE 8866

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "/app/start.sh"]
