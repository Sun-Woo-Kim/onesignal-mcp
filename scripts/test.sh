#!/usr/bin/env bash
set -euo pipefail

# Health check for OneSignal MCP after install/start.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
PUBLIC_HOST="${PUBLIC_HOST:-}"
HAS_ROOT=0
SUDO_CMD=""

cd "$APP_DIR"

is_root_capable() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    HAS_ROOT=1
    SUDO_CMD=""
    return 0
  fi

  if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
    HAS_ROOT=1
    SUDO_CMD="sudo"
    return 0
  fi

  HAS_ROOT=0
  return 1
}

run_root() {
  local cmd_name="$1"
  shift

  if [ "$HAS_ROOT" -ne 1 ]; then
    echo "[WARN] No privilege for ${cmd_name}. Run with sudo for full diagnostics."
    return 1
  fi

  if [ -n "$SUDO_CMD" ]; then
    "$SUDO_CMD" "$@"
  else
    "$@"
  fi
}

is_root_capable

echo "[1/5] Service status"
if ! systemctl status "${SERVICE_NAME}" --no-pager; then
  if [ "$HAS_ROOT" -eq 1 ]; then
    run_root "systemctl status" systemctl status "${SERVICE_NAME}" --no-pager
  else
    echo "[WARN] systemctl status might be hidden due permissions. Re-run with sudo to inspect details."
  fi
fi

echo "[2/5] Import check"
PYTHON_BIN="${APP_DIR}/.venv/bin/python"

if [ -x "$PYTHON_BIN" ]; then
  if ! "$PYTHON_BIN" -c "from onesignal_refactored.server import mcp; print('onesignal_refactored.server import ok')"; then
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
if ss -lntp | grep -E "0.0.0.0:${PORT}|\\*: ${PORT}|\\*: ${PORT}$|\\*: [[:space:]]*${PORT}" >/dev/null 2>&1; then
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
    if ! journalctl -u "${SERVICE_NAME}" -n 120 --no-pager; then
      echo "[WARN] journalctl access denied. Run with sudo to inspect logs."
    fi
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
