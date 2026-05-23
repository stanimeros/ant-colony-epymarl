#!/usr/bin/env bash
# Start MAPPO training on the ant foraging environment.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

CONFIG="${CONFIG:-mappo}"
ENV_CONFIG="${ENV_CONFIG:-ant_colony}"
WANDB_MODE="${WANDB_MODE:-online}"
SEED="${SEED:-}"

# shellcheck disable=SC1091
source "${REPO_ROOT}/scripts/lib/common.sh"

if [[ ! -d "${REPO_ROOT}/.venv" ]] || [[ ! -f "${REPO_ROOT}/epymarl/src/main.py" ]]; then
  echo "error: run ./setup.sh first" >&2
  exit 1
fi

activate_venv
require_epymarl

PY="${REPO_ROOT}/.venv/bin/python"
check_wandb_ready "${PY}"

echo "==> MAPPO training (env-config=${ENV_CONFIG}, wandb_mode=${WANDB_MODE})"
cd "${REPO_ROOT}/epymarl/src"

ARGS=(
  main.py
  --config="${CONFIG}"
  --env-config="${ENV_CONFIG}"
  with
  wandb_mode="${WANDB_MODE}"
)

if [[ -n "${SEED}" ]]; then
  ARGS+=(seed="${SEED}")
fi

if [[ -n "${TRAIN_WITH:-}" ]]; then
  # Extra sacred overrides, e.g. TRAIN_WITH='t_max=100000 env_args.n_ants=16'
  # shellcheck disable=SC2206
  EXTRA=( ${TRAIN_WITH} )
  ARGS+=("${EXTRA[@]}")
fi

if [[ $# -gt 0 ]]; then
  ARGS+=("$@")
fi

echo "    python ${ARGS[*]}"
exec "${PY}" "${ARGS[@]}"
