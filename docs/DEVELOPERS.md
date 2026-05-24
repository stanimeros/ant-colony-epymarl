# Developer notes

Technical reference for setup, EPyMARL integration, and environment internals.

## Repository layout

| Path | In git? | Purpose |
|------|---------|---------|
| `antcolony/` | yes | Custom Gymnasium environment |
| `epymarl-patches/` | yes | Patches applied to upstream EPyMARL |
| `epymarl/` | **no** | Cloned by `setup.sh` |

Training uses [EPyMARL](https://github.com/uoe-agents/epymarl) (Apache 2.0). Cite upstream when publishing.

## `setup.sh` options

```bash
GIT_BRANCH=main ./setup.sh
SKIP_GIT_SYNC=1 ./setup.sh
CLEAN_RUNS=0 ./setup.sh
FORCE_EPYMARL_CLONE=1 ./setup.sh
FORCE_PIP_INSTALL=1 ./setup.sh
RECREATE_VENV=1 ./setup.sh
SKIP_PIP_UPGRADE=1 ./setup.sh
PIP_TIMEOUT=300 ./setup.sh
EPYMARL_REF=cbc38c0 ./setup.sh
```

**Titan / CUDA 12.2:** install `torch==2.5.1+cu121` wheels manually (`curl -4` / `wget -4`). Do not use default PyPI `torch`.

## Training overrides

```bash
WANDB_MODE=offline ./train.sh
FOREGROUND=1 ./train.sh
SEED=42 ./train.sh
TRAIN_WITH='t_max=100000 env_args.n_ants=16' ./train.sh
```

Reproduce **16×16** baseline:

```bash
TRAIN_WITH='env_args.grid_width=16 env_args.grid_height=16 env_args.n_ants=8 env_args.n_food=12 env_args.max_steps=200 env_args.time_limit=200 t_max=500000' ./train.sh
```

## Environment modules

| Module | Role |
|--------|------|
| `antcolony/env.py` | Gymnasium API |
| `antcolony/core/colony.py` | Grid, food, walls, nest, pheromone |
| `antcolony/observations.py` | 3×3 local window + carrying + home vector |
| `antcolony/actions.py` | stay, up, down, left, right |
| `antcolony/rewards.py` | +10 delivery, −0.01/step/ant, +50 all-food bonus |

Gymnasium id: `antcolony:AntColony-v0`.

### Observation (30 numbers)

| Part | Meaning |
|------|---------|
| 0–26 | 3×3 patch: wall, food, pheromone per cell |
| 27 | Carrying food (0/1) |
| 28–29 | Direction back to nest |

Pheromone deposits while carrying food; evaporation ×0.95 per step. **10%** random walls per episode.

## Tests

```bash
source .venv/bin/activate
export PYTHONPATH="${PWD}:${PWD}/epymarl/src"
python scripts/smoke_test_env.py
python scripts/test_ant_foraging.py
```

## W&B figures

```bash
python scripts/plot_wandb_readme.py
python scripts/plot_wandb_readme.py --run entity/project/run_id
```

## EPyMARL patches

1. `./setup.sh`
2. Edit under `epymarl/` or copy path into `epymarl-patches/`
3. Commit only `epymarl-patches/`
4. Re-run `./setup.sh`
