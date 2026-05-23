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

cleanup_training_state() {
  local root="${1:-$(repo_root)}"
  local epymarl_dir="${root}/epymarl"
  local uid
  uid="$(id -u)"
  local pid

  echo "==> stopping stray training processes for this repo"
  while IFS= read -r pid; do
    [[ -z "${pid}" ]] && continue
    echo "    kill ${pid}"
    kill "${pid}" 2>/dev/null || true
  done < <(pgrep -u "${uid}" -f "${epymarl_dir}/src/main.py" 2>/dev/null || true)
  sleep 1
  while IFS= read -r pid; do
    [[ -z "${pid}" ]] && continue
    kill -9 "${pid}" 2>/dev/null || true
  done < <(pgrep -u "${uid}" -f "${epymarl_dir}/src/main.py" 2>/dev/null || true)

  local run_dir
  for run_dir in \
    "${epymarl_dir}/results" \
    "${epymarl_dir}/src/results" \
    "${root}/results"; do
    if [[ -d "${run_dir}" ]]; then
      echo "==> clearing ${run_dir}"
      rm -rf "${run_dir}"
    fi
  done
}

pytorch_cuda_broken() {
  local py="${1:?python required}"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    return 1
  fi
  if ! "${py}" -c "import torch" 2>/dev/null; then
    return 0
  fi
  if ! "${py}" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    return 0
  fi
  # PyTorch built for CUDA 13+ needs a newer driver than typical CUDA 12.2 hosts.
  if ! "${py}" -c "
import torch
v = torch.version.cuda or ''
raise SystemExit(0 if v.startswith('12.') else 1)
" 2>/dev/null; then
    return 0
  fi
  return 1
}

install_pytorch_cuda() {
  local pip="${1:?pip required}"
  local pip_args=(--default-timeout="${PIP_TIMEOUT:-120}")
  local index="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu121}"
  echo "==> installing PyTorch (CUDA 12.1 wheels via ${index})"
  "${pip}" install "${pip_args[@]}" --upgrade torch torchvision --index-url "${index}"
}

verify_pytorch_cuda() {
  local py="${1:?python required}"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "    no nvidia-smi; using CPU PyTorch"
    "${py}" -c "import torch; print('torch', torch.__version__, 'cuda build', torch.version.cuda, 'available', torch.cuda.is_available())"
    return 0
  fi
  "${py}" -c "
import torch
print('torch', torch.__version__, 'cuda build', torch.version.cuda)
print('cuda available', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device', torch.cuda.get_device_name(0))
else:
    raise SystemExit('CUDA not available to PyTorch')
"
}

ensure_pytorch_cuda() {
  local py="${1:?python required}"
  local pip="${2:?pip required}"
  if [[ "${SKIP_CUDA_FIX:-0}" == "1" ]]; then
    echo "==> CUDA PyTorch check skipped (SKIP_CUDA_FIX=1)"
    return 0
  fi
  if pytorch_cuda_broken "${py}"; then
    install_pytorch_cuda "${pip}"
  else
    echo "==> PyTorch CUDA OK"
  fi
  verify_pytorch_cuda "${py}"
}
