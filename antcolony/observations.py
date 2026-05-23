"""Decentralised local observations (no global coordinates)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from antcolony.config import LOCAL_CHANNELS, LOCAL_WINDOW_SIZE

if TYPE_CHECKING:
    from antcolony.core.colony import Colony


def build_observations(colony: Colony) -> list[np.ndarray]:
    """One flat float vector per agent for EPyMARL ``get_obs()``."""
    return [build_agent_observation(colony, ant.agent_id) for ant in colony.ants]


def build_agent_observation(colony: Colony, agent_id: int) -> np.ndarray:
    ant = colony.ants[agent_id]
    window = colony.local_window_size
    half = window // 2
    y0, x0 = ant.position

    # Per-cell (wall, food, pheromone) in row-major order over the local patch.
    local = np.zeros(window * window * LOCAL_CHANNELS, dtype=np.float32)
    idx = 0
    for dr in range(-half, half + 1):
        for dc in range(-half, half + 1):
            cy, cx = y0 + dr, x0 + dc
            local[idx] = float(colony.is_wall(cy, cx))
            local[idx + 1] = float(colony.has_food(cy, cx))
            local[idx + 2] = colony.pheromone_at(cy, cx)
            idx += LOCAL_CHANNELS

    internal = np.array(
        [
            float(ant.carrying_food),
            np.clip(ant.home_dx, -1.0, 1.0),
            np.clip(ant.home_dy, -1.0, 1.0),
        ],
        dtype=np.float32,
    )
    return np.concatenate([local, internal], axis=0)


def init_home_vector(
    ant_row: int, ant_col: int, nest_row: int, nest_col: int
) -> tuple[float, float]:
    """Sign-based nest direction at spawn (odometer seed, not GPS in obs)."""
    dr = nest_row - ant_row
    dc = nest_col - ant_col
    return (_sign(dc), _sign(dr))


def update_home_vector(
    home_dx: float, home_dy: float, d_row: int, d_col: int
) -> tuple[float, float]:
    """Path integration: nest vector shifts opposite to executed movement."""
    dx = float(np.clip(home_dx - d_col, -1.0, 1.0))
    dy = float(np.clip(home_dy - d_row, -1.0, 1.0))
    return dx, dy


def _sign(v: int) -> float:
    if v == 0:
        return 0.0
    return 1.0 if v > 0 else -1.0
