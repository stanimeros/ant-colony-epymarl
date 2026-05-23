# Ant Colony × EPyMARL

Cooperative multi-agent **ant foraging** gridworld for training swarm policies with [EPyMARL](https://github.com/uoe-agents/epymarl).

| Path | In git? | Purpose |
|------|---------|---------|
| `antcolony/` | yes | Custom Gymnasium environment |
| `epymarl-patches/` | yes | File replacements applied to upstream EPyMARL |
| `epymarl/` | **no** | Created by `setup.sh` (clone + patches) |

## Credits — EPyMARL

Training uses **[EPyMARL](https://github.com/uoe-agents/epymarl)** (Apache License 2.0), downloaded at setup time — not stored in this repository.

| Item | Details |
|------|---------|
| Upstream | https://github.com/uoe-agents/epymarl |
| License | Apache 2.0 (see `epymarl/LICENSE` after running `setup.sh`) |
| Our changes | `epymarl-patches/` → e.g. `src/config/envs/ant_colony.yaml` |

Please cite EPyMARL / PyMARL when using their training code (see upstream README for BibTeX).

**Ant foraging** (`antcolony/`) is original to this repository.

## Setup (local or server)

```bash
git clone https://github.com/stanimeros/ant-colony-epymarl.git
cd ant-colony-epymarl
chmod +x setup.sh train.sh
./setup.sh
./train.sh
```

Configure Weights & Biases yourself before training (e.g. `source .venv/bin/activate && wandb login`, or `WANDB_API_KEY`).

`setup.sh` will:

1. **Stop** stray `main.py` training processes for this repo and **clear** `epymarl/*/results` (Sacred logs)
2. `git fetch` + `git reset --hard origin/main` + `git clean -fd` (force match remote)
3. Clone EPyMARL **only if** `epymarl/` is missing; **always** re-apply `epymarl-patches/`
4. Create `.venv/` and install deps on first run; **skip pip** on later runs if `epymarl/` + `.venv/` exist
5. **Fix PyTorch CUDA** when needed (installs `cu121` wheels for driver CUDA 12.x — avoids CUDA 13 / driver mismatch)

Server options:

```bash
GIT_BRANCH=main ./setup.sh              # default branch to sync
SKIP_GIT_SYNC=1 ./setup.sh              # skip git reset (e.g. no remote)
CLEAN_RUNS=0 ./setup.sh                 # do not kill training PIDs or clear results/
FORCE_EPYMARL_CLONE=1 ./setup.sh        # delete and re-clone epymarl/
FORCE_PIP_INSTALL=1 ./setup.sh          # reinstall requirements even if epymarl/ exists
RECREATE_VENV=1 ./setup.sh              # rebuild venv (still runs pip unless epymarl/ existed)
SKIP_PIP_UPGRADE=1 ./setup.sh           # skip pip -U pip wheel
SKIP_CUDA_FIX=1 ./setup.sh              # skip PyTorch CUDA repair check
PIP_TIMEOUT=300 ./setup.sh              # longer PyPI timeout on slow networks (default 120)
EPYMARL_REF=cbc38c0 ./setup.sh          # pin upstream EPyMARL commit (first clone only)
```

**CUDA on Titan (driver 535 / CUDA 12.2):** default PyPI `torch` may pull CUDA 13 wheels and fail with “driver too old”. `./setup.sh` and `./train.sh` reinstall `cu121` PyTorch when `torch.cuda.is_available()` is false. If training logs `use_cuda was switched OFF`, run:

```bash
./setup.sh    # reinstalls cu121 torch if needed
./train.sh
```

Check GPU: `.venv/bin/python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"`. CPU-only training: `ALLOW_CPU=1 ./train.sh`.

On slow HPC links, `ReadTimeoutError` retries from pip are normal — let the **first** `./setup.sh` finish. Later `./setup.sh` runs only refresh patches (fast).

## Train

```bash
./train.sh
```

Runs in the **background** with `nohup` (safe to close SSH). Logs go to `logs/train-*.log`. Follow with `tail -f logs/train-*.log`.

Foreground (blocks terminal): `FOREGROUND=1 ./train.sh`

Defaults: **MAPPO**, `ant_colony` env, `wandb_mode=online`. Overrides:

```bash
WANDB_MODE=offline ./train.sh
SEED=42 ./train.sh
TRAIN_WITH='t_max=100000 env_args.n_ants=16' ./train.sh
./train.sh with env_args.grid_width=32
```

## Environment layout

| Module | Role |
|--------|------|
| `antcolony/env.py` | Gymnasium API + `get_obs()` for EPyMARL `gymma` |
| `antcolony/core/colony.py` | Grid, food, walls, nest, pheromone, step physics |
| `antcolony/observations.py` | 3×3 local window + carrying + path-integration vector |
| `antcolony/actions.py` | Discrete(5): stay, up, down, left, right |
| `antcolony/rewards.py` | Global cooperative reward (+10 delivery, −0.01/step/ant) |
| `antcolony/config.py` | Sizes, reward constants, evaporation rate |

Gymnasium id: `antcolony:AntColony-v0`.

### Observation vector (dim = 30)

| Index | Content |
|-------|---------|
| 0–26 | 3×3 patch, row-major: per cell `(wall, food, pheromone)` |
| 27 | `carrying_food` ∈ {0, 1} |
| 28–29 | Path-integration nest direction `(home_dx, home_dy)` ∈ [−1, 1] |

Pheromone is deposited automatically when `carrying_food == 1`; grid evaporates ×0.95 each step.

**Static obstacles:** **10%** of cells are random walls each episode (`wall_fraction=0.10`), nest excluded.

**Victory:** episode ends when every spawned food piece has been **delivered to the nest** (`battle_won: true`, +50 team bonus). Otherwise ends at `max_steps`.

## Tests

```bash
source .venv/bin/activate
export PYTHONPATH="${PWD}:${PWD}/epymarl/src"
python scripts/smoke_test_env.py
python scripts/test_ant_foraging.py
```

## Train with EPyMARL

```bash
source .venv/bin/activate
export PYTHONPATH="${PWD}:${PWD}/epymarl/src"
cd epymarl/src
python main.py --config=qmix --env-config=ant_colony
```

MAPPO (per-agent rewards):

```bash
python main.py --config=mappo --env-config=ant_colony common_reward=False
```

### Weights & Biases

W&B is enabled in `ant_colony.yaml` (`use_wandb: True`, project `ant-colony-foraging`). Log in or set credentials yourself before training.

Train with online sync:

```bash
python main.py --config=qmix --env-config=ant_colony with wandb_mode=online
```

Optional overrides (Sacred):

```bash
python main.py --config=qmix --env-config=ant_colony \
  with wandb_team=my-team wandb_project=my-project wandb_mode=online
```

If `wandb_team` is null, runs log to the entity from `wandb login`. Offline runs upload later with `wandb sync <run_dir>`.

## Adding EPyMARL patches

1. Run `./setup.sh` once.
2. Edit a file under `epymarl/`, or copy from upstream into `epymarl-patches/` using the **same relative path**.
3. Commit only under `epymarl-patches/`.
4. Re-run `./setup.sh` to verify.
