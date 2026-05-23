#!/usr/bin/env bash
# Log in to Weights & Biases using the project venv.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

if [[ ! -x "${VENV_DIR}/bin/wandb" ]]; then
  echo "error: .venv/bin/wandb not found. Run ./setup.sh first." >&2
  exit 1
fi

echo "==> wandb login (using ${VENV_DIR}/bin/wandb)"
exec "${VENV_DIR}/bin/wandb" login "$@"
