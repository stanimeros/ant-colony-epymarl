#!/usr/bin/env python3
"""Smoke test: obs shape, global reward, pheromone deposit."""

import antcolony  # noqa: F401
import gymnasium as gym

from antcolony.actions import Action
from antcolony.config import OBS_DIM, scaled_rewards


def main() -> None:
    env = gym.make("antcolony:AntColony-v0", n_ants=4, max_steps=50)
    obs, _ = env.reset(seed=42)
    assert len(obs) == 4
    assert obs[0].shape == (OBS_DIM,) == (30,)

    colony = env.unwrapped._colony
    colony.ants[0].carrying_food = 1
    y, x = colony.ants[0].position
    obs, reward, term, trunc, info = env.step([Action.MOVE_UP] * 4)
    assert obs[0].shape == (OBS_DIM,)
    _, step_penalty, _ = scaled_rewards(4, 12)
    assert abs(reward - 4 * step_penalty) < 1e-5
    assert colony.food_pheromone_grid.max() <= 1.0

    print("obs_dim:", OBS_DIM)
    print("obs layout: 27 local (wall,food,phero) + carrying + home[dx,dy]")
    print("step reward:", reward, "info:", info)
    env.close()
    print("OK")


if __name__ == "__main__":
    main()
