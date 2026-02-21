#!/usr/bin/env bash
set -euo pipefail

# Standard deploy flow: git pull + install + health check.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export APP_DIR="${APP_DIR:-${SCRIPT_DIR}/..}"
export SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
export PORT="${PORT:-8000}"
export RUN_USER="${RUN_USER:-ec2-user}"
export BRANCH="${BRANCH:-}"
export PUBLIC_HOST="${PUBLIC_HOST:-}"

cd "$APP_DIR"

if [ ! -d .git ]; then
  echo "[ERROR] No git repository found in $APP_DIR"
  echo "Run these first:"
  echo "  git clone -b ${BRANCH:-master} https://github.com/Sun-Woo-Kim/onesignal-mcp.git /opt/onesignal-mcp"
  echo "  cd /opt/onesignal-mcp"
  echo "  bash scripts/deploy.sh"
  exit 1
fi

if [ -z "$BRANCH" ]; then
  BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@')"
fi
if [ -z "$BRANCH" ]; then
  BRANCH="master"
fi

export BRANCH

echo "[1/3] Sync repository (${BRANCH})"
git fetch --all --prune
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  git checkout "$BRANCH"
elif git show-ref --verify --quiet "refs/remotes/origin/${BRANCH}"; then
  git checkout -B "$BRANCH" "origin/${BRANCH}"
else
  echo "[ERROR] Branch '$BRANCH' not found in local or origin"
  exit 1
fi

git pull --ff-only origin "$BRANCH"

echo "[2/3] Install / apply runtime"
bash "$SCRIPT_DIR/install.sh"

echo "[3/3] Health check"
PUBLIC_HOST="$PUBLIC_HOST" bash "$SCRIPT_DIR/test.sh"

echo
echo "Deploy complete"
echo "- Service: ${SERVICE_NAME}"
echo "- App: ${APP_DIR}"
echo "- Port: ${PORT}"
echo "- Restarted service: sudo systemctl status ${SERVICE_NAME} --no-pager"
