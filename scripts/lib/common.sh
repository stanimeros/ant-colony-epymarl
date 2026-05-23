#!/usr/bin/env bash
# Shared helpers for setup.sh / train.sh (source, do not execute).

repo_root() {
  local caller_dir
  caller_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
  if [[ -f "${caller_dir}/setup.sh" ]]; then
    echo "${caller_dir}"
  else
    echo "$(cd "${caller_dir}/.." && pwd)"
  fi
}

activate_venv() {
  local root
  root="$(repo_root)"
  if [[ ! -d "${root}/.venv" ]]; then
    echo "error: .venv not found. Run ./setup.sh first." >&2
    return 1
  fi
  # shellcheck disable=SC1091
  source "${root}/.venv/bin/activate"
  # shellcheck disable=SC1091
  source "${root}/scripts/env.sh"
}

require_epymarl() {
  local root
  root="$(repo_root)"
  if [[ ! -f "${root}/epymarl/src/main.py" ]]; then
    echo "error: epymarl/ missing. Run ./setup.sh first." >&2
    return 1
  fi
}

check_wandb_ready() {
  local py="${1:-python}"
  if ! "${py}" -c "import wandb" 2>/dev/null; then
    echo "error: wandb is not installed." >&2
    return 1
  fi
  if ! "${py}" -m wandb status 2>/dev/null | grep -q "Logged in"; then
    echo "error: wandb is not logged in. Run: wandb login" >&2
    return 1
  fi
  echo "wandb: OK ($("${py}" -m wandb whoami 2>/dev/null | head -1 || echo "?"))"
  return 0
}
