<p align="center">
  <img src="docs/icon/ant.svg" width="100" alt="Ant colony"/>
</p>

<h1 align="center">Ant Colony Foraging</h1>

<p align="center">
  Teach a swarm of ants to find food, find their way home, and leave trails for each other — using multi-agent reinforcement learning.
</p>

<p align="center">
  <a href="#the-idea">The idea</a> ·
  <a href="#observations-actions-rewards">Obs &amp; rewards</a> ·
  <a href="#what-weve-seen-so-far">Results</a> ·
  <a href="#quick-start">Quick start</a>
</p>

---

## The idea

A colony of ants lives on a small grid. Food appears in random places. The nest sits in the middle. Ants can move, pick up food, and **leave pheromone** when they carry food home — so others can follow successful paths.

Everyone on the team gets the **same reward**: the colony wins when **all food is back at the nest**.

<p align="center">
  <img src="docs/figures/how-it-works.svg" width="640" alt="Ants explore, leave pheromone trails, and cooperate to deliver food to the nest"/>
</p>

Learning is done with **MAPPO** (many ants learning together) on top of [EPyMARL](https://github.com/uoe-agents/epymarl).

---

## Observations, actions, rewards

Each ant sees only its **local neighbourhood** — no global map position. Pickup, pheromone drops, and nest delivery are **automatic** when an ant moves onto the right cell (not separate actions).

### Observations (30 numbers per ant)

| Part | What it tells the ant |
|------|------------------------|
| **27 values** | **3×3** patch around the ant: per cell, **wall** (0/1), **food** (0/1), **pheromone** strength |
| **1 value** | **Carrying food** (0 or 1) |
| **2 values** | **Direction home** — a path-integration vector toward the nest (updated as the ant moves; not GPS coordinates) |

Pheromone is laid automatically while carrying food and fades by **×0.95** each step. **10%** of cells are random walls, fixed for the episode.

### Actions (5 discrete)

| ID | Action |
|----|--------|
| 0 | Stay |
| 1 | Move up |
| 2 | Move down |
| 3 | Move left |
| 4 | Move right |

Walls block movement. Stepping on food **picks it up**; stepping on the nest while carrying **delivers** it.

### Rewards (one shared team score per step)

All ants get the **same** reward each step (cooperative MARL):

| Event | Reward |
|-------|--------:|
| Food delivered to the nest | **+10** per piece |
| Time (every step) | **−0.01** × number of ants |
| All food delivered (episode success) | **+50** bonus |

The step penalty encourages shorter, more efficient episodes. The big bonus appears when every piece of food is home.

---

## What we've seen so far

### First successful world: **16×16**

Eight ants, twelve food pieces, a compact map — our first run where the swarm clearly **learned the job**.

| What we measured | In plain terms |
|------------------|----------------|
| **Food home** | Almost every episode: **~12 of 12** pieces delivered |
| **Full success** | **~90%** of episodes end with the nest stocked |
| **Speed** | Episodes shrink from ~200 steps down to **~110** as ants get efficient |
| **Team score** | Stable high reward once training settles |

<p align="center">
  <img src="docs/figures/mappo_16x16_learning_curves.png" width="720" alt="Training curves for the 16x16 ant foraging run"/>
</p>

*How learning looked over time on the 16×16 world (logged during training).*

**Takeaway:** the colony goes from random wandering to **organized foraging** — higher scores, more food delivered, shorter episodes.

<details>
<summary><strong>Run setup (16×16)</strong></summary>

- Grid **16×16**, **8** ants, **12** food, **200** steps per episode  
- **MAPPO**, cooperative team reward, trained on GPU  

</details>

### Next scale: **32×32**

Larger map (32×32, 32 ants, 24 food). Training budget is **`t_max: 40_000_000`** env steps, with checkpoints every **5M** steps — scaled from 16×16 (~**5M** steps to first clear learning):

| Factor vs 16×16 | Ratio |
|-----------------|------:|
| Episode length (800 vs 200 steps) | 4× |
| Grid area (32² vs 16²) | 4× |
| Food pieces | 2× |

Combined: **5M × 4 (episodes) × 2 (map/food)** ≈ **40M** steps.

---

## Quick start

```bash
git clone https://github.com/stanimeros/ant-colony-epymarl.git
cd ant-colony-epymarl
chmod +x setup.sh train.sh
./setup.sh
./train.sh
```

Training runs in the **background** — safe to disconnect SSH. Watch progress:

```bash
tail -f logs/train-*.log
```

---

## Credits

- **Ant environment** — this repository  
- **Training framework** — [EPyMARL](https://github.com/uoe-agents/epymarl) (Apache 2.0), installed by `setup.sh`
