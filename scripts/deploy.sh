#!/usr/bin/env bash
set -euo pipefail

# Deploy OneSignal MCP Server: git pull → install → health check.
# Usage: sudo PUBLIC_HOST=3.34.235.194 bash scripts/deploy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-${SCRIPT_DIR}/..}"
BRANCH="${BRANCH:-master}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
PUBLIC_HOST="${PUBLIC_HOST:-}"

export APP_DIR SERVICE_NAME PORT PUBLIC_HOST

cd "$APP_DIR"

echo "==> [1/3] Sync repository (${BRANCH})"
if [ ! -d .git ]; then
  echo "[ERROR] Not a git repo. Clone first:"
  echo "  sudo git clone https://github.com/Sun-Woo-Kim/onesignal-mcp.git /opt/onesignal-mcp"
  exit 1
fi

git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/${BRANCH}"

echo "==> [2/3] Install"
bash "$SCRIPT_DIR/install.sh"

echo "==> [3/3] Health check"
bash "$SCRIPT_DIR/test.sh"

echo ""
echo "Deploy complete."
echo "  Service: ${SERVICE_NAME}"
echo "  Port:    ${PORT}"
echo "  Host:    ${PUBLIC_HOST:-localhost}"
