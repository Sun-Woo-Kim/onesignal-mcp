#!/usr/bin/env bash
set -euo pipefail

# OneSignal MCP deploy script for Amazon Linux 2 (after git clone).
# Usage:
#   cd /opt/onesignal-mcp
#   bash scripts/lightsail-deploy-after-clone.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export APP_DIR="${APP_DIR:-${SCRIPT_DIR}/..}"
export SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
export PORT="${PORT:-8000}"
export RUN_USER="${RUN_USER:-ec2-user}"

echo "[1/2] Run install script"
bash "$SCRIPT_DIR/install.sh"

echo
echo "[2/2] Optional health check"
bash "$SCRIPT_DIR/test.sh"
