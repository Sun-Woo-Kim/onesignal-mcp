#!/usr/bin/env bash
set -euo pipefail

# Install/refresh OneSignal MCP in the current repository.
# This script is used by lightsail-bootstrap.sh and lightsail-deploy-after-clone.sh.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-ec2-user}"

cd "$APP_DIR"

echo "[1/6] Install base packages"
if command -v yum >/dev/null 2>&1; then
  sudo yum install -y python3 git
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
if ! "$UV_BIN" venv --recreate --python 3.11 .venv; then
  echo "[WARN] Python 3.11 venv creation failed. Falling back to default python."
  "$UV_BIN" venv --recreate .venv
fi

source .venv/bin/activate
"$UV_BIN" pip install -r requirements.txt

echo "[4/6] Create HTTP entrypoint"
cat > "$APP_DIR/run_http.py" <<PY
from onesignal_refactored.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=${PORT})
PY

echo "[5/6] Ensure .env exists"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENV'
LOG_LEVEL=INFO
# Keep empty if you inject all credentials per MCP tool call.
# ONESIGNAL_ORG_API_KEY=
ENV
fi

echo "[6/6] Register systemd service"
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<SERVICE
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

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo
echo "Install complete."
