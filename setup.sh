#!/usr/bin/env bash
# Server-friendly bootstrap: sync git, clone EPyMARL + patches, venv, deps.
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
FORCE_EPYMARL_CLONE="${FORCE_EPYMARL_CLONE:-0}"
FORCE_PIP_INSTALL="${FORCE_PIP_INSTALL:-0}"
SKIP_PIP_UPGRADE="${SKIP_PIP_UPGRADE:-0}"
RECREATE_VENV="${RECREATE_VENV:-0}"
PIP_TIMEOUT="${PIP_TIMEOUT:-120}"

epymarl_present() {
  [[ -f "${EPYMARL_DIR}/src/main.py" ]]
}

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

# --- EPyMARL: clone only when missing (unless forced) ---
EPYMARL_EXISTED=0
if epymarl_present; then
  EPYMARL_EXISTED=1
fi

if [[ "${FORCE_EPYMARL_CLONE}" == "1" ]]; then
  if [[ -d "${EPYMARL_DIR}" ]]; then
    echo "==> removing existing epymarl/ (FORCE_EPYMARL_CLONE=1)"
    rm -rf "${EPYMARL_DIR}"
  fi
  EPYMARL_EXISTED=0
fi

if epymarl_present; then
  echo "==> keeping existing epymarl/"
else
  echo "==> cloning EPyMARL (${EPYMARL_REF})"
  if ! git clone --depth 1 --branch "${EPYMARL_REF}" "${EPYMARL_REPO}" "${EPYMARL_DIR}" 2>/dev/null; then
    git clone --depth 1 "${EPYMARL_REPO}" "${EPYMARL_DIR}"
    if [[ "${EPYMARL_REF}" != "main" && "${EPYMARL_REF}" != "master" ]]; then
      (cd "${EPYMARL_DIR}" && git fetch --depth 1 origin "${EPYMARL_REF}" && git checkout "${EPYMARL_REF}")
    fi
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

VENV_EXISTED=0
[[ -d "${VENV_DIR}" ]] && VENV_EXISTED=1

if [[ "${RECREATE_VENV}" == "1" && -d "${VENV_DIR}" ]]; then
  echo "==> removing existing .venv/"
  rm -rf "${VENV_DIR}"
  VENV_EXISTED=0
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "==> creating .venv"
  "${PYTHON}" -m venv "${VENV_DIR}"
fi

PIP="${VENV_DIR}/bin/pip"
PY="${VENV_DIR}/bin/python"

pip_install() {
  local pip_args=(--default-timeout="${PIP_TIMEOUT}")
  if [[ "${SKIP_PIP_UPGRADE}" != "1" ]]; then
    echo "==> upgrading pip/wheel"
    "${PIP}" install "${pip_args[@]}" -U pip wheel
  fi
  echo "==> installing requirements (already-installed packages are skipped by pip)"
  "${PIP}" install "${pip_args[@]}" -r "${REQUIREMENTS}"
}

if [[ "${FORCE_PIP_INSTALL}" == "1" ]]; then
  pip_install
elif [[ "${EPYMARL_EXISTED}" == "1" && "${VENV_EXISTED}" == "1" ]]; then
  echo "==> pip install skipped (epymarl/ and .venv/ already present; use FORCE_PIP_INSTALL=1 to reinstall)"
else
  pip_install
fi

export REPO_ROOT
# shellcheck disable=SC1091
source "${REPO_ROOT}/scripts/lib/common.sh"
export_pythonpath "${REPO_ROOT}"
echo "==> registering antcolony environment"
"${PY}" -c "import antcolony"

echo ""
echo "Setup complete."
echo "  commit:  $(git -C "${REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || echo n/a)"
echo "  epymarl: ${EPYMARL_DIR}"
echo "  venv:    ${VENV_DIR}"
echo ""
echo "Train:"
echo "  ./train.sh"
