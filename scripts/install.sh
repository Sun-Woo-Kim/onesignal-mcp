#!/usr/bin/env bash
set -euo pipefail

# Install / refresh runtime for the MCP server and (re)register the systemd service.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICE_NAME="${SERVICE_NAME:-onesignal-mcp}"
PORT="${PORT:-8000}"
RUN_USER="${RUN_USER:-${SUDO_USER:-$(id -un)}}"
UV_ROOT="${UV_ROOT:-${APP_DIR}/.local}"
UV_BIN=""
PYTHON_BIN=""

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
    return 0
  fi

  echo "[WARN] [${cmd_name}] root 권한이 없어 ${*} 건너뜀"
  return 1
}

run_as_user() {
  local cmd_name="$1"
  shift

  if [ "$(id -un)" = "$RUN_USER" ]; then
    "$@"
    return
  fi

  if is_root_available; then
    sudo -u "$RUN_USER" -H -- "$@"
    return
  fi

  echo "[WARN] [${cmd_name}] cannot switch to ${RUN_USER}: $*"
  return 1
}

echo "[1/6] Install base packages"
if command -v yum >/dev/null 2>&1; then
  run_root "yum install python3 git" yum install -y python3 git || true
else
  echo "[WARN] yum이 없어 OS 패키지 자동 설치를 건너뜁니다."
fi

echo "[2/6] Resolve uv command"
mkdir -p "$UV_ROOT/bin"

if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
fi

if [ -x "$UV_BIN" ]; then
  if [[ "$UV_BIN" == /root/.local/bin/* && "$RUN_USER" != "root" ]]; then
    UV_BIN=""
  fi
fi

if [ -z "$UV_BIN" ]; then
  if [ -x "${UV_ROOT}/bin/uv" ]; then
    UV_BIN="${UV_ROOT}/bin/uv"
  else
    if run_as_user "install uv" bash -lc "cd '${APP_DIR}' && curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR='${UV_ROOT}' sh"; then
      UV_BIN="${UV_ROOT}/bin/uv"
    fi
  fi
fi

if [ -n "$UV_BIN" ] && [ ! -x "$UV_BIN" ]; then
  UV_BIN=""
fi

if [ -z "$UV_BIN" ]; then
  echo "[WARN] uv를 사용할 수 없습니다. 기본 python venv로 진행합니다."
fi

echo "[3/6] Create virtualenv and install dependencies"
PYTHON_BIN="$(run_as_user "find python3.11" bash -lc 'command -v python3.11 || command -v python3 || true')"

if [ -z "$PYTHON_BIN" ]; then
  echo "[ERROR] Python 인터프리터를 찾을 수 없습니다. python3 또는 python3.11이 필요합니다."
  exit 1
fi

run_as_user "reset .venv" rm -rf .venv

if [ -n "$UV_BIN" ]; then
  if run_as_user "uv venv" "$UV_BIN" venv --python "$PYTHON_BIN" .venv; then
    :
  else
    UV_BIN=""
  fi
fi

if [ -z "$UV_BIN" ]; then
  run_as_user "create venv" "$PYTHON_BIN" -m venv .venv
fi

if [ -n "$UV_BIN" ]; then
  run_as_user "install requirements" "$UV_BIN" pip install --python .venv/bin/python -r requirements.txt || run_as_user "install requirements" "$UV_BIN" pip install -r requirements.txt
else
  run_as_user "upgrade pip" "${APP_DIR}/.venv/bin/python" -m pip install --upgrade pip
  run_as_user "install requirements" "${APP_DIR}/.venv/bin/python" -m pip install -r requirements.txt
fi

echo "[4/6] Validate runtime entrypoint"
if [ ! -f "$APP_DIR/run_http.py" ]; then
  echo "[ERROR] run_http.py가 없습니다. 저장소에서 파일을 확인해 주세요."
  exit 1
fi

chmod +x "$APP_DIR/run_http.py"

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

  awk -v key="$key" -v value="$value" '
    { 
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

if run_root "install systemd unit" cp "$SERVICE_TMP_FILE" "/etc/systemd/system/${SERVICE_NAME}.service"; then
  rm -f "$SERVICE_TMP_FILE"
  if ! run_root "systemctl daemon-reload" systemctl daemon-reload; then
    echo "[WARN] systemctl daemon-reload 실패. 나중에 수동 실행이 필요할 수 있습니다."
  fi
  if ! run_root "systemctl enable" systemctl enable "${SERVICE_NAME}"; then
    echo "[WARN] systemctl enable 실패."
  fi
  if ! run_root "systemctl restart" systemctl restart "${SERVICE_NAME}"; then
    echo "[WARN] systemctl restart 실패. 수동으로 재시작 해주세요."
  fi
else
  echo "[WARN] systemd unit 파일을 복사하지 못했습니다."
  echo "      권한이 있으면 직접 실행: sudo cp ${SERVICE_TMP_FILE} /etc/systemd/system/${SERVICE_NAME}.service"
  rm -f "$SERVICE_TMP_FILE"
fi

echo "Install complete."
