#!/usr/bin/env bash
set -euo pipefail

# Install runtime and register systemd service for OneSignal MCP Server.
# Requires: Amazon Linux 2 with sudo access.
# Usage: sudo bash scripts/install.sh

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-ec2-user}"

cd "$APP_DIR"

echo "==> [1/5] Install Python 3.11"
if command -v python3.11 &>/dev/null; then
  echo "    python3.11 already installed: $(python3.11 --version)"
else
  if command -v amazon-linux-extras &>/dev/null; then
    amazon-linux-extras install python3.8 -y 2>/dev/null || true
    yum install -y python311 python3.11 2>/dev/null || {
      echo "    Trying amazon-linux-extras for python3.11..."
      amazon-linux-extras enable python3.11 2>/dev/null || true
      yum install -y python3.11 2>/dev/null || true
    }
  fi

  if ! command -v python3.11 &>/dev/null; then
    echo "[ERROR] Failed to install python3.11."
    echo "        Install manually: sudo yum install -y python3.11"
    echo "        Or on AL2: sudo amazon-linux-extras install python3.8 && sudo yum install -y python3.11"
    exit 1
  fi
  echo "    Installed: $(python3.11 --version)"
fi

echo "==> [2/5] Create virtualenv"
rm -rf "$APP_DIR/.venv"
python3.11 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip --quiet

echo "==> [3/5] Install dependencies"
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt" --quiet
echo "    Dependencies installed."

echo "==> [4/5] Setup .env"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENV'
MCP_HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
ENV
  echo "    Created .env (edit to add your API keys)"
else
  echo "    .env already exists, skipping."
fi

chown -R "$RUN_USER:$RUN_USER" "$APP_DIR/.venv" "$APP_DIR/.env"

echo "==> [5/5] Register systemd service"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<SERVICE
[Unit]
Description=OneSignal MCP Server
After=network.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/python ${APP_DIR}/run_http.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo ""
echo "Install complete. Service: ${SERVICE_NAME}"
echo "  Status:  sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
