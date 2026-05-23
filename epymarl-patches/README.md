# EPyMARL patches

Files here mirror paths inside the [EPyMARL](https://github.com/uoe-agents/epymarl) repository. `setup.sh` clones upstream EPyMARL into `epymarl/` and **replaces** matching paths with these files.

Add new patches by copying the relative path from an EPyMARL checkout, e.g. `src/config/envs/my_env.yaml`.

Current patches:

- `src/config/envs/ant_colony.yaml` — ant foraging env + W&B defaults
- `src/utils/logging.py` — W&B entity defaults to `wandb login` when `wandb_team` is null
