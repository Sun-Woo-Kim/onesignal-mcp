#!/usr/bin/env bash
set -euo pipefail

# Health check for OneSignal MCP Server.
# Usage: PUBLIC_HOST=3.34.235.194 bash scripts/test.sh

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
PUBLIC_HOST="${PUBLIC_HOST:-}"
PYTHON_BIN="${APP_DIR}/.venv/bin/python"

cd "$APP_DIR"

PASS=0
FAIL=0

check() {
  local label="$1"
  shift
  echo -n "  ${label}... "
  if "$@" &>/dev/null; then
    echo "OK"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
}

echo "==> Health Check"

check "systemd service active" systemctl is-active --quiet "${SERVICE_NAME}"

check "python import" "$PYTHON_BIN" -c "from onesignal_refactored.server import mcp"

check "localhost:${PORT} reachable" "$PYTHON_BIN" -c "
import socket, sys
s = socket.socket()
s.settimeout(3)
s.connect(('127.0.0.1', ${PORT}))
s.close()
"

if [ -n "$PUBLIC_HOST" ]; then
  check "public ${PUBLIC_HOST}:${PORT}" curl -sf --max-time 5 "http://${PUBLIC_HOST}:${PORT}/mcp" -o /dev/null
else
  echo "  public endpoint... SKIP (set PUBLIC_HOST to test)"
fi

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "--- Recent logs ---"
  journalctl -u "${SERVICE_NAME}" -n 20 --no-pager 2>/dev/null || true
  exit 1
fi
