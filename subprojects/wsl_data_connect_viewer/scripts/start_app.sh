#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$ROOT_DIR/../../../data_connect_viewer" && pwd)"
cd "$PROJECT_ROOT"

if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
