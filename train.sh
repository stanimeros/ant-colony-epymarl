#!/usr/bin/env bash
# Start MAPPO training (nohup by default — survives SSH disconnect).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export REPO_ROOT
cd "${REPO_ROOT}"

CONFIG="${CONFIG:-mappo}"
ENV_CONFIG="${ENV_CONFIG:-ant_colony}"
WANDB_MODE="${WANDB_MODE:-online}"
SEED="${SEED:-}"
FOREGROUND="${FOREGROUND:-0}"
LOG_DIR="${LOG_DIR:-${REPO_ROOT}/logs}"

# shellcheck disable=SC1091
source "${REPO_ROOT}/scripts/lib/common.sh"

if [[ ! -d "${REPO_ROOT}/.venv" ]] || [[ ! -f "${REPO_ROOT}/epymarl/src/main.py" ]]; then
  echo "error: run ./setup.sh first" >&2
  exit 1
fi

activate_venv
require_epymarl

PY="${REPO_ROOT}/.venv/bin/python"
PIP="${REPO_ROOT}/.venv/bin/pip"

require_pytorch_cuda "${PY}" "${PIP}"

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

if [[ "${FOREGROUND}" == "1" ]]; then
  echo "    python ${ARGS[*]}"
  exec "${PY}" "${ARGS[@]}"
fi

mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/train-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="${LOG_DIR}/train.pid"

echo "==> starting training in background (nohup)"
echo "    python ${ARGS[*]}"
nohup "${PY}" "${ARGS[@]}" >> "${LOG_FILE}" 2>&1 &
TRAIN_PID=$!
echo "${TRAIN_PID}" > "${PID_FILE}"

echo "    pid:  ${TRAIN_PID} (saved to ${PID_FILE})"
echo "    log:  ${LOG_FILE}"
echo "    tail: tail -f ${LOG_FILE}"
