<p align="center">
  <img src="docs/icon/ant.svg" width="100" alt="Ant colony"/>
</p>

<h1 align="center">Ant Colony Foraging</h1>

<p align="center">
  Teach a swarm of ants to find food, find their way home, and leave trails for each other — using multi-agent reinforcement learning.
</p>

<p align="center">
  <a href="#the-idea">The idea</a> ·
  <a href="#what-weve-seen-so-far">Results</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="docs/DEVELOPERS.md">Developer docs</a>
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

## Project layout (short)

| Folder | What it is |
|--------|------------|
| `antcolony/` | The foraging world (ants, food, nest, pheromone) |
| `epymarl-patches/` | Our tweaks to the training stack |
| `docs/figures/` | README diagrams and learning-curve images |
| `scripts/` | Tests and plot scripts |

Full setup flags, observation layout, and patch workflow → **[docs/DEVELOPERS.md](docs/DEVELOPERS.md)**.

---

## Credits

- **Ant environment** — this repository  
- **Training framework** — [EPyMARL](https://github.com/uoe-agents/epymarl) (Apache 2.0), installed by `setup.sh`
