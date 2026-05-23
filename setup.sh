#!/usr/bin/env bash
# Server-friendly bootstrap: sync git, clone EPyMARL + patches, venv, deps, wandb check.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

EPYMARL_DIR="${REPO_ROOT}/epymarl"
PATCH_DIR="${REPO_ROOT}/epymarl-patches"
VENV_DIR="${REPO_ROOT}/.venv"
REQUIREMENTS="${REPO_ROOT}/requirements.txt"
EPYMARL_REPO="${EPYMARL_REPO:-https://github.com/uoe-agents/epymarl.git}"
EPYMARL_REF="${EPYMARL_REF:-main}"
GIT_BRANCH="${GIT_BRANCH:-main}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
PYTHON="${PYTHON:-python3}"
SKIP_GIT_SYNC="${SKIP_GIT_SYNC:-0}"
SKIP_WANDB_CHECK="${SKIP_WANDB_CHECK:-0}"
RECREATE_VENV="${RECREATE_VENV:-0}"

echo "==> ant-colony-epymarl setup"
echo "    repo: ${REPO_ROOT}"

# --- Force sync with remote (discard local changes) ---
if [[ "${SKIP_GIT_SYNC}" == "1" ]]; then
  echo "==> git sync skipped (SKIP_GIT_SYNC=1)"
elif [[ -d "${REPO_ROOT}/.git" ]]; then
  echo "==> git fetch ${GIT_REMOTE} and reset --hard ${GIT_REMOTE}/${GIT_BRANCH}"
  git fetch "${GIT_REMOTE}" --prune
  git reset --hard "${GIT_REMOTE}/${GIT_BRANCH}"
  git clean -fd
  echo "    at commit: $(git rev-parse --short HEAD)"
else
  echo "==> not a git repo; skipping git sync"
fi

if [[ ! -d "${PATCH_DIR}" ]]; then
  echo "error: missing ${PATCH_DIR}" >&2
  exit 1
fi

# --- EPyMARL: fresh clone + patches ---
if [[ -d "${EPYMARL_DIR}" ]]; then
  echo "==> removing existing epymarl/"
  rm -rf "${EPYMARL_DIR}"
fi

echo "==> cloning EPyMARL (${EPYMARL_REF})"
if ! git clone --depth 1 --branch "${EPYMARL_REF}" "${EPYMARL_REPO}" "${EPYMARL_DIR}" 2>/dev/null; then
  git clone --depth 1 "${EPYMARL_REPO}" "${EPYMARL_DIR}"
  if [[ "${EPYMARL_REF}" != "main" && "${EPYMARL_REF}" != "master" ]]; then
    (cd "${EPYMARL_DIR}" && git fetch --depth 1 origin "${EPYMARL_REF}" && git checkout "${EPYMARL_REF}")
  fi
fi

echo "==> applying epymarl-patches/"
while IFS= read -r -d '' patch_file; do
  rel="${patch_file#${PATCH_DIR}/}"
  [[ "${rel}" == README.md ]] && continue
  dest="${EPYMARL_DIR}/${rel}"
  mkdir -p "$(dirname "${dest}")"
  cp "${patch_file}" "${dest}"
  echo "    ${rel}"
done < <(find "${PATCH_DIR}" -type f ! -name 'README.md' -print0)

# --- Python venv + requirements ---
if [[ ! -f "${REQUIREMENTS}" ]]; then
  echo "error: missing ${REQUIREMENTS}" >&2
  exit 1
fi

if [[ "${RECREATE_VENV}" == "1" && -d "${VENV_DIR}" ]]; then
  echo "==> removing existing .venv/"
  rm -rf "${VENV_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "==> creating .venv"
  "${PYTHON}" -m venv "${VENV_DIR}"
fi

PIP="${VENV_DIR}/bin/pip"
PY="${VENV_DIR}/bin/python"
WANDB="${VENV_DIR}/bin/wandb"

echo "==> installing requirements"
"${PIP}" install -U pip wheel
"${PIP}" install -r "${REQUIREMENTS}"

export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/epymarl/src"
echo "==> registering antcolony environment"
"${PY}" -c "import antcolony"

# --- Weights & Biases (installed in .venv — not on system PATH until activated) ---
echo "==> checking wandb"
WANDB_READY=0
if ! "${PY}" -c "import wandb" 2>/dev/null; then
  echo "error: wandb package missing after install" >&2
  exit 1
fi
if [[ "${SKIP_WANDB_CHECK}" == "1" ]]; then
  echo "    check skipped (SKIP_WANDB_CHECK=1)"
elif "${WANDB}" status 2>/dev/null | grep -q "Logged in"; then
  WANDB_READY=1
  echo "    logged in as: $("${WANDB}" whoami 2>/dev/null | head -1 || echo "?")"
  "${WANDB}" status 2>/dev/null | sed 's/^/    /' || true
else
  echo "    not logged in yet (this is OK right after clone)"
fi

echo ""
echo "Setup complete."
echo "  commit:  $(git -C "${REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || echo n/a)"
echo "  epymarl: ${EPYMARL_DIR}"
echo "  venv:    ${VENV_DIR}"
echo ""
if [[ "${WANDB_READY}" -eq 0 && "${SKIP_WANDB_CHECK}" != "1" ]]; then
  echo "Next (wandb is only inside .venv — 'wandb' alone will not work yet):"
  echo "  ./wandb_login.sh"
  echo "  ./train.sh"
else
  echo "Train:"
  echo "  ./train.sh"
fi
