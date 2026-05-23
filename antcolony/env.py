"""Gymnasium environment for EPyMARL ``gymma`` (homogeneous parameter sharing)."""

from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium.spaces import Box, Discrete, Tuple

from antcolony.config import DEFAULT_ENV_CONFIG, EnvConfig, N_ACTIONS, OBS_DIM
from antcolony.core.colony import Colony


class AntColonyEnv(gym.Env):
    """Cooperative ant foraging on a grid with automatic food-pheromone stigmergy."""

    metadata = {"render_modes": ["human"], "name": "AntColony-v0"}

    def __init__(
        self,
        n_ants: int = 8,
        grid_width: int = 16,
        grid_height: int = 16,
        max_steps: int = 200,
        n_food: int = 12,
        wall_fraction: float = 0.10,
        local_window_size: int = 3,
        n_actions: int = N_ACTIONS,
        obs_dim: int = OBS_DIM,
        pheromone_evaporation: float = 0.95,
        seed: int | None = None,
    ):
        super().__init__()
        self.n_agents = n_ants
        self._obs_dim = obs_dim

        self._colony = Colony(
            n_ants=n_ants,
            grid_width=grid_width,
            grid_height=grid_height,
            max_steps=max_steps,
            n_food=n_food,
            wall_fraction=wall_fraction,
            local_window_size=local_window_size,
            n_actions=n_actions,
            pheromone_evaporation=pheromone_evaporation,
            seed=seed,
        )

        low = np.zeros(obs_dim, dtype=np.float32)
        high = np.ones(obs_dim, dtype=np.float32)
        low[-2:] = -1.0
        high[-2:] = 1.0
        agent_obs = Box(low=low, high=high, dtype=np.float32)
        self.observation_space = Tuple([agent_obs] * n_ants)
        self.action_space = Tuple([Discrete(n_actions)] * n_ants)

    @property
    def state_size(self) -> int:
        return self.n_agents * self._obs_dim

    @classmethod
    def from_config(cls, config: EnvConfig) -> AntColonyEnv:
        return cls(**config.to_gym_kwargs())

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[tuple[np.ndarray, ...], dict]:
        if seed is not None:
            self._colony.rng = np.random.default_rng(seed)
        self._colony.reset()
        return tuple(self.get_obs()), {"step": 0}

    def step(
        self, actions: list[int]
    ) -> tuple[tuple[np.ndarray, ...], float, bool, bool, dict]:
        if len(actions) != self.n_agents:
            raise ValueError(
                f"Expected {self.n_agents} actions, got {len(actions)}"
            )
        obs, reward, terminated, info = self._colony.step(actions)
        return tuple(obs), float(reward), terminated, False, info

    def get_obs(self) -> list[np.ndarray]:
        return self._colony.get_obs()

    def render(self) -> None:
        h, w = self._colony.grid_height, self._colony.grid_width
        ny, nx = self._colony.nest_pos
        grid = [["." for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                if self._colony.wall_grid[y, x]:
                    grid[y][x] = "#"
                elif self._colony.has_food(y, x):
                    grid[y][x] = "f"
        grid[ny][nx] = "N"
        for ant in self._colony.ants:
            y, x = ant.position
            grid[y][x] = "A" if ant.carrying_food else "a"
        print(f"--- step {self._colony.step_count} ---")
        for row in grid:
            print("".join(row))

    def close(self) -> None:
        pass

    def seed(self, seed: int | None = None) -> list[int | None]:
        self._colony.rng = np.random.default_rng(seed)
        return [seed]
