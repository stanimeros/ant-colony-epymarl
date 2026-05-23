"""Ant foraging gridworld — movement, stigmergy, pickup, nest delivery."""

from __future__ import annotations

import numpy as np

from antcolony.actions import ACTION_DELTAS, Action
from antcolony.config import OBS_DIM, PHEROMONE_DEPOSIT
from antcolony.core.ant import Ant
from antcolony.observations import (
    build_observations,
    init_home_vector,
    update_home_vector,
)
from antcolony.rewards import compute_step_reward


class Colony:
    """Cooperative ant foraging with automatic pheromone stigmergy."""

    def __init__(
        self,
        n_ants: int,
        grid_width: int,
        grid_height: int,
        max_steps: int,
        n_food: int,
        wall_fraction: float,
        local_window_size: int,
        n_actions: int,
        pheromone_evaporation: float,
        seed: int | None = None,
    ):
        self.n_ants = n_ants
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.max_steps = max_steps
        self.n_food = n_food
        self.wall_fraction = float(wall_fraction)
        self.local_window_size = local_window_size
        self.n_actions = n_actions
        self.obs_dim = OBS_DIM
        self.pheromone_evaporation = pheromone_evaporation

        self.rng = np.random.default_rng(seed)
        self.step_count = 0
        self.total_deliveries = 0
        self.n_food_spawned = 0
        self.ants: list[Ant] = []
        self.nest_pos: tuple[int, int] = (0, 0)

        self.wall_grid: np.ndarray = np.zeros(
            (grid_height, grid_width), dtype=bool
        )
        self.food_grid: np.ndarray = np.zeros(
            (grid_height, grid_width), dtype=bool
        )
        self.food_pheromone_grid: np.ndarray = np.zeros(
            (grid_height, grid_width), dtype=np.float32
        )

    def reset(self) -> None:
        self.step_count = 0
        self.total_deliveries = 0
        self.wall_grid.fill(False)
        self.food_grid.fill(False)
        self.food_pheromone_grid.fill(0.0)

        self.nest_pos = (self.grid_height - 1, self.grid_width // 2)
        self._place_walls()
        self._place_food()
        self.n_food_spawned = int(self.food_grid.sum())
        self._spawn_ants()

    def step(self, actions: list[int]) -> tuple[list[np.ndarray], float, bool, dict]:
        deliveries = 0

        for ant, action in zip(self.ants, actions):
            action_id = int(action) % self.n_actions
            d_row, d_col = ACTION_DELTAS.get(
                action_id, ACTION_DELTAS[Action.STAND_STILL]
            )
            new_pos = self._try_move(ant.position, d_row, d_col)
            if new_pos != ant.position:
                ant.home_dx, ant.home_dy = update_home_vector(
                    ant.home_dx, ant.home_dy, d_row, d_col
                )
            ant.position = new_pos

            if ant.carrying_food == 0 and self.has_food(*ant.position):
                ant.carrying_food = 1
                self.food_grid[ant.position] = False

            if ant.carrying_food == 1:
                y, x = ant.position
                self.food_pheromone_grid[y, x] = PHEROMONE_DEPOSIT

            if self._at_nest(ant) and ant.carrying_food == 1:
                ant.carrying_food = 0
                deliveries += 1

        self.food_pheromone_grid *= self.pheromone_evaporation

        self.total_deliveries += deliveries
        battle_won = (
            self.n_food_spawned > 0
            and self.total_deliveries >= self.n_food_spawned
        )

        self.step_count += 1
        obs = build_observations(self)
        reward = compute_step_reward(self, deliveries, battle_won=battle_won)
        terminated = battle_won or self.step_count >= self.max_steps
        info = {
            "deliveries": deliveries,
            "total_deliveries": self.total_deliveries,
            "food_spawned": self.n_food_spawned,
            "step": self.step_count,
            "food_remaining": int(self.food_grid.sum()),
            "ants_carrying": sum(a.carrying_food for a in self.ants),
            "battle_won": battle_won,
        }
        return obs, reward, terminated, info

    def get_obs(self) -> list[np.ndarray]:
        return build_observations(self)

    def get_global_state(self) -> np.ndarray:
        return np.concatenate(self.get_obs(), axis=0).astype(np.float32)

    def is_wall(self, row: int, col: int) -> bool:
        if not self._in_bounds(row, col):
            return True
        return bool(self.wall_grid[row, col])

    def has_food(self, row: int, col: int) -> bool:
        if not self._in_bounds(row, col):
            return False
        return bool(self.food_grid[row, col])

    def pheromone_at(self, row: int, col: int) -> float:
        if not self._in_bounds(row, col):
            return 0.0
        return float(self.food_pheromone_grid[row, col])

    def _at_nest(self, ant: Ant) -> bool:
        return ant.position == self.nest_pos

    def _try_move(
        self, pos: tuple[int, int], d_row: int, d_col: int
    ) -> tuple[int, int]:
        y, x = pos
        ny, nx = y + d_row, x + d_col
        if self.is_wall(ny, nx):
            return pos
        return (ny, nx)

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width

    def _wall_count(self) -> int:
        area = self.grid_width * self.grid_height
        return int(area * self.wall_fraction)

    def _place_walls(self) -> None:
        """Place static random obstacles on ``wall_fraction`` of cells (nest excluded)."""
        n_walls = self._wall_count()
        blocked = {self.nest_pos}
        candidates = [
            (y, x)
            for y in range(self.grid_height)
            for x in range(self.grid_width)
            if (y, x) not in blocked
        ]
        if n_walls <= 0:
            return
        n_walls = min(n_walls, len(candidates))
        indices = self.rng.choice(len(candidates), size=n_walls, replace=False)
        for i in indices:
            y, x = candidates[i]
            self.wall_grid[y, x] = True

    def _place_food(self) -> None:
        blocked = {self.nest_pos} | {
            (y, x) for y in range(self.grid_height) for x in range(self.grid_width) if self.wall_grid[y, x]
        }
        placed = 0
        for _ in range(self.n_food * 4):
            if placed >= self.n_food:
                break
            y = int(self.rng.integers(0, self.grid_height))
            x = int(self.rng.integers(0, self.grid_width))
            if (y, x) in blocked:
                continue
            self.food_grid[y, x] = True
            blocked.add((y, x))
            placed += 1

    def _spawn_ants(self) -> None:
        self.ants = []
        ny, nx = self.nest_pos
        spawn_cells = [(ny, nx)]
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            cell = (ny + dr, nx + dc)
            if self._in_bounds(*cell) and not self.is_wall(*cell):
                spawn_cells.append(cell)

        for i in range(self.n_ants):
            pos = spawn_cells[i % len(spawn_cells)]
            hdx, hdy = init_home_vector(pos[0], pos[1], ny, nx)
            self.ants.append(
                Ant(
                    agent_id=i,
                    position=pos,
                    carrying_food=0,
                    home_dx=hdx,
                    home_dy=hdy,
                )
            )
