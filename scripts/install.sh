#!/usr/bin/env bash
set -euo pipefail

# Install / refresh runtime for the MCP server and (re)register the systemd service.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-${SUDO_USER:-$(id -un)}}"
UV_ROOT="${UV_ROOT:-${APP_DIR}/.local}"
UV_BIN="${UV_ROOT}/bin/uv"

cd "$APP_DIR"

SCRIPT_NAME="install.sh"

is_root_available() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    return 0
  fi
  if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

run_root() {
  local cmd_name="$1"
  shift
  if is_root_available; then
    if [ "${EUID:-$(id -u)}" -eq 0 ]; then
      "$@"
    else
      sudo "$@"
    fi
  else
    echo "[WARN] [${cmd_name}] root 권한이 없어 ${*} 건너뜀"
    return 1
  fi
}

run_as_user() {
  local cmd_name="$1"
  shift
  if [ "$(id -un)" = "$RUN_USER" ]; then
    "$@"
  elif is_root_available && [ "${EUID:-$(id -u)}" -eq 0 ]; then
    sudo -u "$RUN_USER" -H -- "$@"
  elif is_root_available; then
    sudo -u "$RUN_USER" -H -- "$@"
  else
    echo "[WARN] [${cmd_name}] cannot switch user (run as ${RUN_USER} if needed): $*"
    return 1
  fi
}

echo "[1/6] Install base packages"
if command -v yum >/dev/null 2>&1; then
  run_root "yum install python3 git" yum install -y python3 git || true
else
  echo "[WARN] yum이 없어 OS 패키지 자동 설치를 건너뜁니다."
fi

echo "[2/6] Resolve uv command"
if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
else
  if [ ! -x "$UV_BIN" ]; then
    echo "[INFO] uv가 없어서 설치합니다. (${UV_ROOT})"
    mkdir -p "$UV_ROOT"
    curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="$UV_ROOT" sh
  fi
  if [ -x "${UV_ROOT}/bin/uv" ]; then
    UV_BIN="${UV_ROOT}/bin/uv"
  fi
fi

if [ ! -x "$UV_BIN" ]; then
  echo "[WARN] uv 설치 실패. 기본 python venv로 진행합니다."
  UV_BIN=""
fi

echo "[3/6] Create virtualenv and install dependencies"
run_as_user "Reset .venv" rm -rf .venv

if [ -n "$UV_BIN" ]; then
  if "$UV_BIN" venv --python 3.11 .venv; then
    :
  elif "$UV_BIN" venv .venv; then
    :
  else
    UV_BIN=""
  fi
fi

if [ -z "$UV_BIN" ]; then
  if command -v python3.11 >/dev/null 2>&1; then
    python3.11 -m venv .venv
  elif command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv
  else
    echo "[ERROR] Python 인터프리터를 찾을 수 없습니다."
    exit 1
  fi
fi

"./.venv/bin/pip" install --upgrade pip >/dev/null
"./.venv/bin/pip" install -r requirements.txt

echo "[4/6] Create HTTP entrypoint"
cat > "$APP_DIR/run_http.py" <<'PY'
from onesignal_refactored.server import mcp
import logging
import os
import inspect
import logging

from typing import Any, Callable, Optional, Sequence, Union


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = "streamable-http"

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("onesignal-mcp")


def _run_fastmcp() -> None:
    sig = inspect.signature(mcp.run)
    kwargs = {}
    for name, value in (("transport", TRANSPORT), ("host", HOST), ("port", PORT)):
        if name in sig.parameters:
            kwargs[name] = value
    mcp.run(**kwargs)


def _asgi_candidates() -> Sequence[Union[Callable[..., Any], Any]]:
    return (
        getattr(mcp, "streamable_http_app", None),
        getattr(mcp, "http_app", None),
        getattr(mcp, "asgi_app", None),
        getattr(mcp, "app", None),
        getattr(mcp, "get_asgi_app", None),
    )


def _resolve_asgi_app() -> Optional[Any]:
    for candidate in _asgi_candidates():
        if candidate is None:
            continue
        try:
            if callable(candidate):
                resolved = candidate()
            else:
                resolved = candidate
            if resolved is not None:
                return resolved
        except Exception:
            logger.exception("ASGI candidate resolution failed")
            continue

    if callable(mcp):
        return mcp
    return None


def main() -> None:
    try:
        _run_fastmcp()
        return
    except TypeError:
        logger.info("FastMCP.run() signature does not match this adapter.")

    import uvicorn  # noqa: PLC0415

    app = _resolve_asgi_app()
    if app is None:
        raise RuntimeError("No ASGI app found from fastmcp object.")
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL.lower())


if __name__ == "__main__":
    main()
PY

echo "[5/6] Ensure .env exists"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENV'
LOG_LEVEL=INFO
# Keep empty if you inject all credentials per MCP tool call.
# ONESIGNAL_ORG_API_KEY=
ENV
fi

ensure_env_var() {
  local key="$1"
  local value="$2"
  local tmp
  tmp="$(mktemp)"

  awk -v key="$key" -v value="$value" '{
    if ($0 ~ "^" key "=") {
      print key "=" value
      found = 1
      next
    }
    print
  }
  END {
    if (!found) print key "=" value
  }' "$APP_DIR/.env" > "$tmp"
  mv "$tmp" "$APP_DIR/.env"
}

ensure_env_var MCP_HOST "0.0.0.0"
ensure_env_var PORT "${PORT}"

if is_root_available && [ "$(id -un)" != "$RUN_USER" ]; then
  run_root "chown app files" chown -R "$RUN_USER:$RUN_USER" "$APP_DIR/.venv" "$APP_DIR/.env" "$APP_DIR/run_http.py"
fi

echo "[6/6] Register systemd service"
SERVICE_TMP_FILE="${APP_DIR}/.${SERVICE_NAME}.service.tmp"
cat > "$SERVICE_TMP_FILE" <<SERVICE
[Unit]
Description=OneSignal MCP Server
After=network.target

[Service]
Type=simple
User=${RUN_USER}
Group=${RUN_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=-${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/python ${APP_DIR}/run_http.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

if ! run_root "install systemd unit" cp "$SERVICE_TMP_FILE" "/etc/systemd/system/${SERVICE_NAME}.service"; then
  echo "[WARN] systemd unit 파일을 복사하지 못했습니다."
  echo "       sudo cp ${SERVICE_TMP_FILE} /etc/systemd/system/${SERVICE_NAME}.service"
  rm -f "$SERVICE_TMP_FILE"
  exit 1
fi
rm -f "$SERVICE_TMP_FILE"

if ! run_root "systemctl daemon-reload" systemctl daemon-reload; then
  echo "[WARN] systemctl daemon-reload 실패. 나중에 수동 실행이 필요할 수 있습니다."
fi

if ! run_root "systemctl enable" systemctl enable "${SERVICE_NAME}"; then
  echo "[WARN] systemctl enable 실패."
fi

if ! run_root "systemctl restart" systemctl restart "${SERVICE_NAME}"; then
  echo "[WARN] systemctl restart 실패."
  echo "       sudo systemctl daemon-reload && sudo systemctl enable ${SERVICE_NAME} && sudo systemctl restart ${SERVICE_NAME}"
  exit 1
fi

echo
echo "Install complete."
else
  echo "[WARN] systemd steps skipped."
  echo "[INFO] Manual service setup required:"
  echo "  sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<'SERVICE'"
  echo "  ... (run install.sh with sudo/root once to write and enable service)"
fi

echo
echo "Install complete."
