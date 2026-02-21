#!/usr/bin/env bash
set -euo pipefail

# OneSignal MCP bootstrap script for Lightsail (clone + deploy).
# Run on a fresh server:
#   bash scripts/lightsail-bootstrap.sh
#
# Optional overrides:
#   REPO_URL=https://github.com/Sun-Woo-Kim/onesignal-mcp.git \
#   BRANCH=main \
#   APP_DIR=/opt/onesignal-mcp \
#   PORT=8000 \
#   SERVICE_NAME=onesignal-mcp \
#   RUN_USER=ec2-user \
#   bash lightsail-bootstrap.sh

REPO_URL="${REPO_URL:-https://github.com/Sun-Woo-Kim/onesignal-mcp.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/onesignal-mcp}"
export APP_DIR
export PORT="${PORT:-8000}"
export SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
export RUN_USER="${RUN_USER:-ec2-user}"

echo "[1/5] Install base packages"
if command -v yum >/dev/null 2>&1; then
  sudo yum install -y git python3
else
  echo "[WARN] yum not found. Skipping OS package install."
fi

echo "[2/5] Prepare app directory"
sudo mkdir -p "$APP_DIR"
sudo chown -R "${RUN_USER}:${RUN_USER}" "$APP_DIR"

echo "[3/5] Clone repository"
if [ -d "$APP_DIR/.git" ]; then
  echo "Git repo already exists in $APP_DIR"
  echo "[3/5] Pulling latest from ${BRANCH}"
  git -C "$APP_DIR" fetch --all
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
else
  git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

echo "[4/5] Run deploy script"
bash "$APP_DIR/scripts/install.sh"

echo
echo "[5/5] Health check"
bash "$APP_DIR/scripts/test.sh"

echo
echo "Bootstrap complete."
echo "- Service: ${SERVICE_NAME}"
echo "- App dir: ${APP_DIR}"
echo "- Port: ${PORT}"
echo "- Status: sudo systemctl status ${SERVICE_NAME} --no-pager"
echo "- Logs:   journalctl -u ${SERVICE_NAME} -f"
echo "- Local check: sudo ss -lntp | grep :${PORT}"
echo
echo "Note: Open TCP ${PORT} in Lightsail Networking for external access."
