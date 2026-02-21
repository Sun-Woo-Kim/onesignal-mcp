#!/usr/bin/env bash
set -euo pipefail

# Install/refresh OneSignal MCP in the current repository.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-ec2-user}"
HAS_ROOT=0
SUDO_CMD=""

cd "$APP_DIR"

is_root_capable() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    HAS_ROOT=1
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
  local label="$1"
  shift

  if [ "$HAS_ROOT" -ne 1 ]; then
    echo "[WARN] No root access for ${label}. Skipping: $*"
    return 1
  fi

  if [ -n "$SUDO_CMD" ]; then
    "$SUDO_CMD" "$@"
  else
    "$@"
  fi
}

require_root() {
  local label="$1"
  if [ "$HAS_ROOT" -ne 1 ]; then
    echo "[WARN] No privilege for ${label}. Run this script with sudo or as root."
    return 1
  fi
  return 0
}

is_root_capable

echo "[1/6] Install base packages"
if command -v yum >/dev/null 2>&1; then
  run_root "base package install" yum install -y python3 git || true
else
  echo "[WARN] yum not found. Please make sure Python 3 and git are available."
fi

echo "[2/6] Resolve uv command"
if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
else
  echo "[INFO] Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  UV_BIN="${HOME}/.local/bin/uv"
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if [ ! -x "$UV_BIN" ]; then
  echo "[ERROR] uv binary not found. Searched for: $UV_BIN"
  exit 1
fi

echo "[3/6] Create virtualenv and install dependencies"
rm -rf .venv
if "$UV_BIN" venv --python 3.11 .venv; then
  :
elif "$UV_BIN" venv --python 3.11 --clear .venv; then
  :
else
  echo "[WARN] Python 3.11 venv creation failed. Falling back to default interpreter."
  "$UV_BIN" venv .venv
fi

source .venv/bin/activate
"$UV_BIN" pip install -r requirements.txt

echo "[4/6] Create HTTP entrypoint"
cat > "$APP_DIR/run_http.py" <<PY
from onesignal_refactored.server import mcp
import logging
import os
from typing import Any, Callable, Optional, Sequence, Tuple, Union


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("onesignal-mcp-runner")
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = "streamable-http"


def _resolve_uvicorn_app() -> Optional[Union[Callable[..., Any], Any]]:
    """
    Prefer explicit ASGI app attributes exported by FastMCP.
    The order is defensive and compatible across fastmcp/mcp package versions.
    """
    candidates: Sequence[str] = (
        "streamable_http_app",
        "http_app",
        "asgi_app",
        "app",
        "get_asgi_app",
    )
    for name in candidates:
        if not hasattr(mcp, name):
            continue
        value = getattr(mcp, name)
        if value is None:
            continue
        try:
            if callable(value):
                app = value()
            else:
                app = value
            if app is None:
                continue
            logger.info("Resolved ASGI app from mcp.%s", name)
            return app
        except Exception:
            logger.exception("Failed resolving mcp.%s via %s", name, value)
            continue

    return None


def _run_uvicorn():
    import uvicorn

    app = _resolve_uvicorn_app()
    if app is None and callable(mcp):
        app = mcp
        logger.info("Falling back to uvicorn with callable FastMCP instance")

    if app is None:
        raise RuntimeError("No ASGI app candidate found for uvicorn fallback.")

    logger.info("Starting via uvicorn on host=%s port=%s", HOST, PORT)
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL.lower())


def _run_fastmcp():
    """
    FastMCP.run() is still supported as fallback only.
    We pass transport first for compatibility and rely on MCP-internal defaults if present.
    """
    last_error = None
    try:
        mcp.run(transport=TRANSPORT, host=HOST, port=PORT)
        return
    except TypeError as exc:
        last_error = exc


def _run_via_uvicorn_fallback():
    import uvicorn

    app_candidates = []
    if hasattr(mcp, "streamable_http_app"):
        app_candidates.append(("streamable_http_app", getattr(mcp, "streamable_http_app")))
    if hasattr(mcp, "http_app"):
        app_candidates.append(("http_app", getattr(mcp, "http_app")))
    if hasattr(mcp, "asgi_app"):
        app_candidates.append(("asgi_app", getattr(mcp, "asgi_app")))
    if hasattr(mcp, "app"):
        app_candidates.append(("app", getattr(mcp, "app")))
    if hasattr(mcp, "get_asgi_app"):
        app_candidates.append(("get_asgi_app()", getattr(mcp, "get_asgi_app")))

    for name, app in app_candidates:
        try:
            if callable(app):
                candidate = app()
            else:
                candidate = app
            if candidate is None:
                continue
            logger.info("Starting via uvicorn fallback from mcp.%s", name)
            uvicorn.run(candidate, host=HOST, port=PORT)
            return
        except (TypeError, RuntimeError):
            continue

    if callable(mcp):
        logger.info("Starting via uvicorn fallback from mcp object directly")
        uvicorn.run(mcp, host=HOST, port=PORT)
        return

    raise RuntimeError("No available ASGI app for uvicorn fallback.")


if __name__ == "__main__":
    logger.info("Using MCP_HOST=%s PORT=%s", HOST, PORT)
    try:
        _run_uvicorn()
        raise SystemExit(0)
    except Exception as exc:
        logger.warning("Uvicorn fallback strategy failed: %s", exc)
        try:
            _run_fastmcp()
            logger.info("Started with FastMCP.run() fallback")
            raise SystemExit(0)
        except Exception as inner:
            logger.warning("FastMCP.run() fallback failed: %s", inner)
            try:
                _run_via_uvicorn_fallback()
            except Exception:
                logger.exception("Unable to start MCP server.")
                raise RuntimeError("Unable to start FastMCP server.") from inner
PY

echo "[5/6] Ensure .env exists"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENV'
LOG_LEVEL=INFO
# Keep empty if you inject all credentials per MCP tool call.
# ONESIGNAL_ORG_API_KEY=
ENV
fi

ensure_var() {
  local key="$1"
  local value="$2"
  local tmp
  tmp="$(mktemp)"
  awk -v k="$key" -v v="$value" 'BEGIN{found=0}
    $0 ~ ("^[[:space:]]*" k "=") {
      print k "=" v
      if (!found) found=1
      next
    }
    {print}
    END {
      if (!found) print k "=" v
    }' "$APP_DIR/.env" > "$tmp"
  mv "$tmp" "$APP_DIR/.env"
}

ensure_var MCP_HOST 0.0.0.0
ensure_var PORT ${PORT}

echo "[6/6] Register systemd service"
if require_root "systemd registration"; then
  SERVICE_TMP_FILE="${APP_DIR}/.tmp.${SERVICE_NAME}.service"
  cat > "$SERVICE_TMP_FILE" <<SERVICE
[Unit]
Description=OneSignal MCP Server
After=network.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=-${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/python ${APP_DIR}/run_http.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

  if ! run_root "install unit file" cp "$SERVICE_TMP_FILE" "/etc/systemd/system/${SERVICE_NAME}.service"; then
    echo "[WARN] Failed to write /etc/systemd/system/${SERVICE_NAME}.service."
    echo "       sudo cp ${SERVICE_TMP_FILE} /etc/systemd/system/${SERVICE_NAME}.service"
    rm -f "$SERVICE_TMP_FILE"
    exit 1
  fi
  rm -f "$SERVICE_TMP_FILE"

  if ! run_root "systemctl daemon-reload" systemctl daemon-reload; then
    echo "[WARN] Failed to run systemctl daemon-reload (service restart may fail)."
  fi

  if ! run_root "systemctl enable" systemctl enable "${SERVICE_NAME}"; then
    echo "[WARN] Failed to enable service."
  fi

  if ! run_root "systemctl restart" systemctl restart "${SERVICE_NAME}"; then
    echo "[WARN] Failed to restart service (permission issue or transient runtime error)."
    echo "       sudo systemctl daemon-reload && sudo systemctl enable ${SERVICE_NAME} && sudo systemctl restart ${SERVICE_NAME}"
  fi
else
  echo "[WARN] systemd steps skipped."
  echo "[INFO] Manual service setup required:"
  echo "  sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<'SERVICE'"
  echo "  ... (run install.sh with sudo/root once to write and enable service)"
fi

echo
echo "Install complete."
