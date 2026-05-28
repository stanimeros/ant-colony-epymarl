# Reward settings & W&B baselines

Cooperative team reward (one scalar per env step, shared by all ants).  
Constants live in `antcolony/config.py`; scaled values use `scaled_rewards(n_ants, n_food)`.

W&B project: [ant-colony-foraging](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging)  
W&B logs **episode returns** as `return_mean` / `test_return_mean` — **not** the reward constants below (those are only in code).

**Success metric:** `battle_won` = all spawned food **delivered to the nest** (`total_deliveries >= n_food_spawned`).  
`food_remaining_mean` ≈ 0 only means the **map** is clear; food can still be on ants (see `test_ants_carrying_mean`).

---

## Baselines to beat (May 2026)

Use these when starting a new experiment. Pick **`test_battle_won_mean`** (greedy eval) as the primary score.

**Baseline** = best **`test_battle_won_mean`** seen during training (saved under `models/…/best/`). Runs were **interrupted** (manual kill / no fixed stop rule) — we do **not** treat the last W&B log as a baseline.

| Map | Best run | W&B | Peak test success | @ `t_env` (peak) | Rewards |
|-----|----------|-----|------------------:|-----------------:|---------|
| **16×16** | rich-armadillo-3 | [`x11wd1h0`](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/x11wd1h0) | **~90%** | ~17.2M | unscaled |
| **32×32** | playful-cosmos-10 | [`pnle4do2`](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/pnle4do2) | **87.5%** | **21.2M** | scaled |

Checkpoints, the demo GIF, and `models/` use the **peak** weights only.

**Checkpoint (32×32, copied locally):**  
`models/mappo_seed448693470_antcolony:AntColony-v0_2026-05-26 17:24:39.960925/best/agent.th`  
(`best.json`: **0.875** @ **21 170 797** `t_env`).

**32×32 headroom:** peak test **87.5%** vs **~90%** on 16×16 — still room to improve.

---

## All W&B runs (inventory)

| Run | ID | Grid | Rewards | Peak test success | @ `t_env` (peak) | Notes |
|-----|-----|------|---------|------------------:|-----------------:|-------|
| **rich-armadillo-3** | `x11wd1h0` | 16×16 | unscaled | **~90%** | ~17.2M | **Best 16×16** |
| **playful-cosmos-10** | `pnle4do2` | 32×32 | scaled | **87.5%** | **21.2M** | **Best 32×32**; run interrupted |
| zesty-firefly-8 | `zlsz6f4l` | 32×32 | unscaled | 31% (last log) | 24.0M | First 32×32; unscaled |
| tough-serenity-9 | `u1l4jl6i` | 32×32 | scaled? | 12% (last log) | 27.3M | Failed / unstable |

W&B state **crashed** = process killed or interrupted; use **`best/`** peak metrics for baselines, not the last log line.

---

## 1. Best 16×16 — rich-armadillo-3

**Run:** [rich-armadillo-3](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/x11wd1h0) (`x11wd1h0`)

| Env | Value |
|-----|------:|
| Grid | 16×16 |
| Ants | 8 |
| Food | 12 |
| Max steps / episode | 200 |
| `t_max` (config) | 20 050 000 |

### Reward rates (unscaled — baseline in code)

| Event | Per step / event |
|-------|-----------------:|
| Food delivered to nest | **+10** per piece |
| Time | **−0.01 × n_ants** → **−0.08** team per step |
| All food home | **+50** bonus (once, on that step) |

**Max theoretical return** (all food, instant last delivery, 200 steps):  
`12×10 + 50 − 200×8×0.01` ≈ **154**

### W&B summary (peak ~17.2M `t_env`)

| Metric | Train | Test |
|--------|------:|-----:|
| `battle_won_mean` | 93% | **90%** |
| `return_mean` | 157.8 | **155.3** |
| `ep_length_mean` | 103 | **109** |
| `total_deliveries_mean` | 11.93 | **11.9** / 12 |

### Learning milestones (train `battle_won_mean`)

| Milestone | ~`t_env` |
|-----------|----------|
| First **≥50%** full success | **1.85M** |
| First **≥80%** full success | **3.54M** |
| First **≥90%** full success | **4.28M** |

---

## 2. Best 32×32 — playful-cosmos-10 (scaled rewards)

**Run:** [playful-cosmos-10](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/pnle4do2) (`pnle4do2`)

| Env | Value |
|-----|------:|
| Grid | 32×32 |
| Ants | 32 |
| Food | 24 |
| Max steps / episode | 800 |
| `t_max` (config) | 40 000 000 |

### Reward rates (`scaled_rewards(32, 24)`)

| Event | Rate | Team per step (32 ants) |
|-------|-----:|------------------------:|
| Food delivered to nest | **+20** per piece | — |
| Time | **−0.0025** per ant | **−0.08** (matches 16×16) |
| All food home | **+100** bonus | — |

Scaling: delivery & win **× (n_food/12)**; per-ant step **× (8/n_ants)**.

**Max theoretical return** (all food, 800 steps):  
`24×20 + 100 − 800×0.08` ≈ **516**

### Baseline checkpoint (use this)

Saved when **`test_battle_won_mean`** improved; weights in `models/…/best/`. Demo GIF uses this checkpoint.

| Metric | Value |
|--------|------:|
| `test_battle_won_mean` | **87.5%** |
| `t_env` | **21 170 797** |

**Improvement target:** beat **87.5%** peak test success; aim for **≥90%** (16×16 bar). Prefer **`best/`** + early stopping when test success plateaus — runs were not stopped at a chosen budget.

| Training | Value |
|----------|------:|
| `save_model_interval` | 1 000 000 |
| Best checkpoint metric | `test_battle_won_mean` |

---

## 3. Archived 32×32 runs (do not use as baseline)

### zesty-firefly-8 — unscaled rewards

**Run:** [zesty-firefly-8](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/zlsz6f4l) (`zlsz6f4l`)

Same **+10 / −0.32 team step / +50** as 16×16 (not scaled). Run interrupted ~24M `t_env`.

| Milestone | ~`t_env` | Notes |
|-----------|----------|--------|
| First **≥50%** train | **~1.9M** | — |
| Peak train success | **~69.8%** at **~20.2M** | never reached 80% |
| Last logged test | **31%** at ~24M | return ~−14 |

Superseded by **playful-cosmos-10** (scaled rewards).

### tough-serenity-9 — failed run

**Run:** [tough-serenity-9](https://wandb.ai/aid26006-university-of-macedonia/ant-colony-foraging/runs/u1l4jl6i) (`u1l4jl6i`)

Interrupted ~27.3M `t_env`; **12%** test success (last log), long episodes (~764 steps), high `food_remaining` — do not reuse config without checking what changed.

---

## What W&B stores

| In config | In metrics (`t_env`) |
|-----------|----------------------|
| `common_reward`, `reward_scalarisation`, `standardise_rewards` | `return_mean`, `return_std` |
| `t_max`, `env_args.*` | `battle_won_mean`, `test_battle_won_mean`, `total_deliveries_mean`, `ep_length_mean` |
| **Not** `+10` / `+20` / step penalty constants | `food_remaining_mean`, `ants_carrying_mean`, … |

To reproduce a run’s reward table, use this file + git commit on Titan, not the W&B config UI alone.

---

## Starting a new experiment

1. Tag the W&B run (e.g. `scaled-rewards-v2`) so it is not confused with archived runs.  
2. Compare against **§ Baselines to beat** using **`test_battle_won_mean`**.  
3. Do **not** run `./setup.sh` on Titan to stop training — it deletes `epymarl/results/` (`CLEAN_RUNS=1`). Use `pkill` on `main.py` only.
