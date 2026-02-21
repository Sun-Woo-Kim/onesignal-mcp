#!/usr/bin/env bash
set -euo pipefail

# Health check for OneSignal MCP after install/start.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"

cd "$APP_DIR"

echo "[1/4] Service status"
sudo systemctl status "${SERVICE_NAME}" --no-pager || true

echo "[2/4] Import check"
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

echo "[3/4] Port check (127.0.0.1:${PORT})"
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

echo "[4/4] Logs (last 40 lines)"
journalctl -u "${SERVICE_NAME}" -n 40 --no-pager

echo
echo "Test complete."
