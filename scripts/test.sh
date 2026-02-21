#!/usr/bin/env bash
set -euo pipefail

# Health check for OneSignal MCP after install/start.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
PUBLIC_HOST="${PUBLIC_HOST:-}"

cd "$APP_DIR"

echo "[1/5] Service status"
if ! sudo systemctl status "${SERVICE_NAME}" --no-pager; then
  echo "[WARN] systemctl requires sudo privileges. Check via: sudo systemctl status ${SERVICE_NAME}"
fi

echo "[2/5] Import check"
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
  if ! python -c "from onesignal_refactored.server import mcp; print('onesignal_refactored.server import ok')"; then
    echo "[ERROR] Python import failed"
    echo "--- Last 120 lines of service log ---"
    journalctl -u "${SERVICE_NAME}" -n 120 --no-pager
    exit 1
  fi
else
  echo "[ERROR] .venv not found. Run install.sh first."
  exit 1
fi

echo "[3/5] Port check (127.0.0.1:${PORT})"
python - "$PORT" <<'PY'
import socket
import sys

port = int(sys.argv[1])
s = socket.socket()
s.settimeout(3)
try:
    s.connect(("127.0.0.1", port))
    print(f"Port {port} is reachable from localhost.")
except Exception as exc:
    print(f"[ERROR] Port {port} is not reachable: {exc}")
    sys.exit(1)
finally:
    s.close()
PY

echo "[3.5/5] Socket bind check (0.0.0.0:${PORT})"
if ss -lntp | grep -E "0.0.0.0:${PORT}|\\*: ${PORT}" >/dev/null 2>&1; then
  echo "Service is bound to 0.0.0.0 for external access."
else
  echo "[WARN] Service is not bound to 0.0.0.0:${PORT}. This blocks external access."
fi

echo "[4/5] Public endpoint check"
if [ -n "${PUBLIC_HOST}" ]; then
  if curl -isS --max-time 5 "http://${PUBLIC_HOST}:${PORT}/sse" | head -n 1 | tee /tmp/onesignal-mcp-sse-check.txt >/dev/null; then
    echo "Public endpoint is reachable at http://${PUBLIC_HOST}:${PORT}/sse"
  else
    echo "[ERROR] Public endpoint check failed: http://${PUBLIC_HOST}:${PORT}/sse"
    echo "Check Lightsail firewall (TCP ${PORT}) and server bind host."
    echo "--- Last 120 lines of service log ---"
    journalctl -u "${SERVICE_NAME}" -n 120 --no-pager
    exit 1
  fi
else
  echo "PUBLIC_HOST not set. Skip public endpoint check."
  echo "Set PUBLIC_HOST=3.34.235.194 and rerun to validate external access."
fi

echo "[5/5] Logs (last 40 lines)"
journalctl -u "${SERVICE_NAME}" -n 40 --no-pager

echo
echo "Test complete."
