#!/usr/bin/env bash
set -euo pipefail

PORT="${VOILA_PORT:-8866}"
IP="${VOILA_IP:-0.0.0.0}"
NOTEBOOK="${VOILA_NOTEBOOK:-usage.ipynb}"

# Run Voilà serving the notebook
exec voila "$NOTEBOOK" \
  --Voila.ip="$IP" \
  --Voila.port="$PORT" \
  --no-browser \
  --strip_sources=False
