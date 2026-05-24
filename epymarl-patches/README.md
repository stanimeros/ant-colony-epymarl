# EPyMARL patches

Files here mirror paths inside the [EPyMARL](https://github.com/uoe-agents/epymarl) repository. `setup.sh` clones upstream EPyMARL into `epymarl/` and **replaces** matching paths with these files.

Add new patches by copying the relative path from an EPyMARL checkout, e.g. `src/config/envs/my_env.yaml`.

Current patches:

- `src/config/envs/ant_colony.yaml` — **32×32**, 32 ants, `t_max: 40M`
- `src/config/algs/mappo.yaml` — smaller batches + matching `t_max` (~12GB VRAM)
- `src/envs/__init__.py` — optional `smaclite` (ant colony only needs `gymma`)
- `src/utils/logging.py` — W&B entity defaults to `wandb login` when `wandb_team` is null
