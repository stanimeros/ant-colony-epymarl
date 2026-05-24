# README figures

| File | Purpose |
|------|---------|
| `how-it-works.svg` | Concept diagram (nest, food, pheromone, cooperation) |
| `mappo_16x16_learning_curves.png` | Learning curves from W&B run `x11wd1h0` |

Regenerate the PNG from W&B:

```bash
source .venv/bin/activate
python scripts/plot_wandb_readme.py
```

Icon: `docs/icon/ant.svg`
