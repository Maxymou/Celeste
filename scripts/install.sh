#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$REPO_ROOT"

print_step() {
  local msg="$1"
  printf '\n\033[1;34m==> %s\033[0m\n' "$msg"
}

require_cmd() {
  local cmd="$1"
  local desc="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '\033[1;31mError:\033[0m %s (%s) is required but not installed.\n' "$cmd" "$desc"
    exit 1
  fi
}

require_cmd python3 "Python 3.11 runtime"
require_cmd npm "Node.js + npm"

if ! python3 - <<'PY'
import sys
sys.exit(0 if sys.version_info >= (3, 11) else 1)
PY
then
  PY_VERSION=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
  printf '\033[1;31mError:\033[0m Python 3.11 or newer is required (found %s).\n' "$PY_VERSION"
  exit 1
fi

VENV_DIR="${REPO_ROOT}/.venv"

print_step "Creating Python virtual environment (.venv)"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
else
  printf "Virtual environment already exists, skipping creation.\n"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

print_step "Upgrading pip"
pip install --upgrade pip >/dev/null

print_step "Installing Python dependencies"
pip install -r requirements.txt

print_step "Installing frontend dependencies"
pushd frontend >/dev/null
npm install

print_step "Building frontend assets"
npm run build
popd >/dev/null

print_step "Setup complete"
cat <<'MSG'
Next steps:
1. source .venv/bin/activate
2. uvicorn backend.app.main:app --host 0.0.0.0 --port 6000
3. In a new shell (with the venv activated), set ADMIN_USER/ADMIN_PASS/ADMIN_SECRET and run:
   uvicorn backend.admin.main:app --host 0.0.0.0 --port 8000
MSG
