#!/usr/bin/env bash
set -euo pipefail

# OneSignal MCP deploy script for Amazon Linux 2 (after git clone).
# Usage:
#   cd /opt/onesignal-mcp
#   bash scripts/lightsail-deploy-after-clone.sh

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-ec2-user}"

echo "[1/6] Install base packages"
sudo yum install -y python3 git

echo "[2/6] Create virtualenv and install dependencies"
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

echo "[3/6] Create HTTP entrypoint"
cat > "$APP_DIR/run_http.py" <<PY
from onesignal_refactored.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=${PORT})
PY

echo "[4/6] Ensure optional env file exists"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENV'
LOG_LEVEL=INFO
# Keep empty if you inject all credentials per MCP tool call.
# ONESIGNAL_ORG_API_KEY=
# ONESIGNAL_APP_ID=
# ONESIGNAL_API_KEY=
ENV
fi

echo "[5/6] Register systemd service"
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

echo "[6/6] Start service"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo
echo "Done."
echo "- Service: ${SERVICE_NAME}"
echo "- Port: ${PORT}"
echo "- Status: sudo systemctl status ${SERVICE_NAME} --no-pager"
echo "- Logs:   journalctl -u ${SERVICE_NAME} -f"
echo "- Local check: curl -i http://127.0.0.1:${PORT}/"
echo
echo "Note: Open TCP ${PORT} in Lightsail Networking for external access."
