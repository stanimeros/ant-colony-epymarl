# README figures

| File | Purpose |
|------|---------|
| `how-it-works.svg` | Concept diagram (nest, food, pheromone, cooperation) |
| `mappo_16x16_learning_curves.png` | 16×16 MAPPO learning curves |

Regenerate the PNG (requires local experiment logs / API access — see `scripts/plot_wandb_readme.py` in developer docs):

```bash
source .venv/bin/activate
python scripts/plot_wandb_readme.py
```

Icon: `docs/icon/ant.svg`
