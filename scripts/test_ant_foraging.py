#!/usr/bin/env python3
"""Unit checks for obs layout, rewards, pheromone, path integration."""

import antcolony  # noqa: F401
import numpy as np

from antcolony.actions import Action
from antcolony.config import (
    OBS_DIM,
    REWARD_BATTLE_WON,
    REWARD_NEST_DELIVERY,
    REWARD_STEP_PENALTY,
)
from antcolony.core.colony import Colony
from antcolony.observations import init_home_vector, update_home_vector


def test_wall_fraction():
    c = Colony(4, 20, 20, 50, 8, 0.10, 3, 5, 0.95, seed=3)
    c.reset()
    expected = int(20 * 20 * 0.10)
    assert int(c.wall_grid.sum()) == expected


def test_obs_dim():
    c = Colony(4, 16, 16, 50, 8, 0.10, 3, 5, 0.95, seed=0)
    c.reset()
    obs = c.get_obs()
    assert len(obs) == 4
    assert obs[0].shape == (OBS_DIM,)
    assert obs[0][-3] == 0.0  # not carrying
    assert obs[0][-2:].min() >= -1.0 and obs[0][-2:].max() <= 1.0


def test_nest_delivery_reward():
    c = Colony(2, 8, 8, 50, 4, 0.10, 3, 5, 0.95, seed=1)
    c.reset()
    c.ants[0].position = c.nest_pos
    c.ants[0].carrying_food = 1
    _, r, _, info = c.step([Action.STAND_STILL, Action.STAND_STILL])
    assert info["deliveries"] == 1
    assert c.ants[0].carrying_food == 0
    expected = REWARD_NEST_DELIVERY + 2 * REWARD_STEP_PENALTY
    assert abs(r - expected) < 1e-5


def test_pheromone_deposit_and_evaporation():
    c = Colony(1, 8, 8, 50, 4, 0.10, 3, 5, 0.95, seed=2)
    c.reset()
    ant = c.ants[0]
    ant.carrying_food = 1
    # Avoid nest delivery clearing the carrier before deposit.
    if ant.position == c.nest_pos:
        ant.position = (0, 0)
    y, x = ant.position
    c.step([Action.STAND_STILL])
    assert c.food_pheromone_grid[y, x] == pytest_approx(0.95)
    c.ants[0].carrying_food = 0
    c.step([Action.STAND_STILL])
    assert c.food_pheromone_grid[y, x] == pytest_approx(0.95 * 0.95)


def test_battle_won_terminates_episode():
    c = Colony(2, 8, 8, 50, 3, 0.10, 3, 5, 0.95, seed=4)
    c.reset()
    assert c.n_food_spawned == 3
    for i in range(3):
        c.ants[0].position = c.nest_pos
        c.ants[0].carrying_food = 1
        _, r, term, info = c.step([Action.STAND_STILL, Action.STAND_STILL])
        if i < 2:
            assert not term
            assert not info["battle_won"]
        else:
            assert term
            assert info["battle_won"]
            assert info["total_deliveries"] == 3
            expected = (
                REWARD_NEST_DELIVERY
                + 2 * REWARD_STEP_PENALTY
                + REWARD_BATTLE_WON
            )
            assert abs(r - expected) < 1e-5


def test_path_integration():
    hdx, hdy = init_home_vector(5, 5, 2, 2)  # nest north-west
    assert hdx == -1.0 and hdy == -1.0
    hdx, hdy = update_home_vector(hdx, hdy, d_row=-1, d_col=0)  # move up
    assert hdy == 0.0


def pytest_approx(x):
    class A:
        def __eq__(self, other):
            return abs(other - x) < 1e-5

    return A()


if __name__ == "__main__":
    test_wall_fraction()
    test_obs_dim()
    test_nest_delivery_reward()
    test_pheromone_deposit_and_evaporation()
    test_battle_won_terminates_episode()
    test_path_integration()
    print("All tests passed.")
