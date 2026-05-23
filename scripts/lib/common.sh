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

export_pythonpath() {
  local root="${1:-$(repo_root)}"
  export PYTHONPATH="${root}:${root}/epymarl/src"
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
  export_pythonpath "${root}"
}

require_epymarl() {
  local root
  root="$(repo_root)"
  if [[ ! -f "${root}/epymarl/src/main.py" ]]; then
    echo "error: epymarl/ missing. Run ./setup.sh first." >&2
    return 1
  fi
}
