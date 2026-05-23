#!/usr/bin/env bash
# Shared helpers for setup.sh / train.sh (source, do not execute).

repo_root() {
  if [[ -n "${REPO_ROOT:-}" ]]; then
    echo "${REPO_ROOT}"
    return 0
  fi

  local i dir
  for ((i = ${#BASH_SOURCE[@]} - 1; i >= 0; i--)); do
    dir="$(cd "$(dirname "${BASH_SOURCE[$i]}")" && pwd)"
    while [[ "${dir}" != "/" ]]; do
      if [[ -f "${dir}/setup.sh" ]]; then
        echo "${dir}"
        return 0
      fi
      dir="$(dirname "${dir}")"
    done
  done

  echo "error: could not find repo root (no setup.sh in call stack)" >&2
  return 1
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
