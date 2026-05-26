# Reward settings & W&B milestones

Cooperative team reward (one scalar per env step, shared by all ants).  
Constants live in `antcolony/config.py`; scaled values use `scaled_rewards(n_ants, n_food)`.

W&B logs **episode returns** as `return_mean` / `test_return_mean` — **not** the three constants below (those are only in code).

---

## 1. Sixteen × sixteen baseline

**Run:** [rich-armadillo-3](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/x11wd1h0) (`x11wd1h0`)

| Env | Value |
|-----|------:|
| Grid | 16×16 |
| Ants | 8 |
| Food | 12 |
| Max steps / episode | 200 |
| `t_max` (config) | 20 050 000 |

### Reward rates (fixed in code)

| Event | Per step / event |
|-------|-----------------:|
| Food delivered to nest | **+10** per piece |
| Time | **−0.01 × n_ants** → **−0.08** team per step |
| All food home | **+50** bonus (once, on that step) |

**Max theoretical return** (all food, instant last delivery, 200 steps):  
`12×10 + 50 − 200×8×0.01` ≈ **154**

### W&B learning (train `battle_won_mean`)

| Milestone | ~`t_env` |
|-----------|----------|
| First **≥50%** full success | **1.85M** |
| First **≥80%** full success | **3.54M** |
| First **≥90%** full success | **4.28M** |
| Final summary (run logged to ~17.2M) | **~93%** success, **~158** return, **~103** ep length |

---

## 2. Thirty-two × thirty-two — first training (unscaled rewards)

**Run:** [zesty-firefly-8](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/zlsz6f4l) (`zlsz6f4l`)

Same **+10 / −0.01 per ant / +50** as 16×16 — **not** scaled for more ants or food.

| Env | Value |
|-----|------:|
| Grid | 32×32 |
| Ants | 32 |
| Food | 24 |
| Max steps / episode | 800 |
| `t_max` (config) | 40 000 000 |

### Reward rates (same numbers as 16×16 — problem)

| Event | Per step / event |
|-------|-----------------:|
| Food delivered to nest | **+10** per piece |
| Time | **−0.01 × 32** → **−0.32** team per step |
| All food home | **+50** bonus |

**Max theoretical return** (all food, 800 steps):  
`24×10 + 50 − 800×32×0.01` ≈ **34** (much lower ceiling than 16×16 despite more food)

### W&B learning (train `battle_won_mean`)

Checked against W&B history (May 2026):

| Milestone | ~`t_env` | Notes |
|-----------|----------|--------|
| First **≥50%** | **~1.9M** | (similar onset to 16×16) |
| **≥80%** full success | **Not reached** | — |
| **Peak** success in logs | **~69.8%** at **~20.2M** | best single train window |
| ~20M checkpoint (typical) | **~58%** | return ~+63, ep length ~588 |
| Latest logged (~22M) | **~57%** | still below 80% |

So the **first 32×32 run had not hit 80%** train success as of ~22M `t_env`; learning was real but slow, partly due to harsh per-step penalty and low win/delivery scale.

---

## 3. Thirty-two × thirty-two — new setup (scaled rewards)

**For the next training run** after syncing repo + `./setup.sh` (patches applied).

Uses `scaled_rewards(32, 24)`:

| Event | Rate | Team per step (32 ants) |
|-------|-----:|------------------------:|
| Food delivered to nest | **+20** per piece | — |
| Time | **−0.0025** per ant | **−0.08** (matches 16×16) |
| All food home | **+100** bonus | — |

Scaling rules (from baseline 8 ants / 12 food):

- Delivery & win bonus: `× (n_food / 12)` → **2×** on 32×32  
- Per-ant step rate: `× (8 / n_ants)` → **¼** per ant so team step cost stays **−0.08**

**Max theoretical return** (all food, 800 steps):  
`24×20 + 100 − 800×0.08` ≈ **516** (if episodes stay long; shorter episodes score higher)

| Training | Value |
|----------|------:|
| `t_max` | 40 000 000 |
| `save_model_interval` | 1 000 000 |
| Best test checkpoint | `.../models/<run>/best/agent.th` (+ `best.json` with `t_env`, metric) |
| Interval checkpoints | `.../models/<run>/<timestep>/agent.th` |

**W&B:** start a **new** run after deploy; tag it e.g. `scaled-rewards` so it is not confused with `zlsz6f4l`.

---

## What W&B stores

| In config | In metrics (`t_env`) |
|-----------|----------------------|
| `common_reward`, `reward_scalarisation`, `standardise_rewards` | `return_mean`, `return_std` |
| `t_max`, `env_args.*` | `battle_won_mean`, `total_deliveries_mean`, `ep_length_mean` |
| **Not** `+10` / `+20` / step penalty constants | — |

To reproduce a run’s reward table, use this file + git commit on Titan, not the W&B config UI alone.
