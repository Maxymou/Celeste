#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: remote-install.sh --repo <git_url> [--branch <branch>] [--dest <path>] [--force]

Options:
  --repo    Git URL of the Celeste X repository (required)
  --branch  Branch, tag, or ref to checkout (default: main)
  --dest    Target directory to clone into (default: ./celestex)
  --force   Remove any existing destination directory before cloning
  -h, --help  Show this help message

Examples:
  curl -sSfL https://raw.githubusercontent.com/ORG/REPO/main/scripts/remote-install.sh \
    | bash -s -- --repo https://github.com/ORG/REPO.git

USAGE
}

print_step() {
  local msg="$1"
  printf '\n\033[1;34m==> %s\033[0m\n' "$msg"
}

error() {
  printf '\033[1;31mError:\033[0m %s\n' "$1" >&2
  exit 1
}

require_cmd() {
  local cmd="$1"
  local desc="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "$cmd ($desc) is required but not installed."
  fi
}

REPO_URL=""
BRANCH="main"
TARGET_DIR="$(pwd)/celestex"
FORCE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -lt 2 ]] && error "--repo requires a value"
      REPO_URL="$2"
      shift 2
      ;;
    --branch)
      [[ $# -lt 2 ]] && error "--branch requires a value"
      BRANCH="$2"
      shift 2
      ;;
    --dest)
      [[ $# -lt 2 ]] && error "--dest requires a value"
      TARGET_DIR="$2"
      shift 2
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$REPO_URL" ]]; then
        REPO_URL="$1"
        shift
      else
        usage >&2
        error "Unknown argument: $1"
      fi
      ;;
  esac
done

[[ -z "$REPO_URL" ]] && { usage >&2; error "--repo <git_url> is required"; }

require_cmd git "Git"
require_cmd python3 "Python runtime"
require_cmd npm "Node.js + npm"

if [[ -e "$TARGET_DIR" ]]; then
  if [[ "$FORCE" == "true" ]]; then
    print_step "Removing existing directory $TARGET_DIR"
    rm -rf "$TARGET_DIR"
  elif [[ -d "$TARGET_DIR/.git" ]]; then
    EXISTING_URL=$(git -C "$TARGET_DIR" remote get-url origin || true)
    if [[ "$EXISTING_URL" != "$REPO_URL" ]]; then
      error "Destination $TARGET_DIR already exists with remote $EXISTING_URL (expected $REPO_URL). Use --force to overwrite or specify --dest."
    fi
    print_step "Updating existing repository in $TARGET_DIR"
    git -C "$TARGET_DIR" fetch --depth 1 origin "$BRANCH"
    git -C "$TARGET_DIR" checkout "$BRANCH"
    git -C "$TARGET_DIR" reset --hard "origin/$BRANCH"
  else
    error "Destination $TARGET_DIR already exists and is not a git repository. Use --force or specify a different --dest."
  fi
else
  print_step "Cloning $REPO_URL into $TARGET_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

if [[ ! -x scripts/install.sh ]]; then
  print_step "Making install script executable"
  chmod +x scripts/install.sh
fi

print_step "Running project installer"
"${TARGET_DIR}/scripts/install.sh"

print_step "Installation finished"
cat <<'MSG'
Celeste X has been installed. Activate the environment and start the services as documented in README.md.
MSG
