"""Environment configuration for cooperative ant foraging."""

from dataclasses import dataclass

# Local 3×3 window: walls | food | pheromone (9 cells × 3 channels) + carrying + home vector.
LOCAL_WINDOW_SIZE = 3
LOCAL_CHANNELS = 3
OBS_INTERNAL_DIM = 1 + 2  # carrying_food, home [dx, dy]
OBS_DIM = LOCAL_WINDOW_SIZE * LOCAL_WINDOW_SIZE * LOCAL_CHANNELS + OBS_INTERNAL_DIM

N_ACTIONS = 5

# Rewards (global cooperative).
REWARD_NEST_DELIVERY = 10.0
REWARD_STEP_PENALTY = -0.01
REWARD_BATTLE_WON = 50.0

# Stigmergy.
PHEROMONE_DEPOSIT = 1.0
PHEROMONE_EVAPORATION = 0.95

# Static random obstacles: fraction of grid cells (fixed per episode at reset).
WALL_FRACTION = 0.10


@dataclass
class EnvConfig:
    n_ants: int = 8
    grid_width: int = 16
    grid_height: int = 16
    max_steps: int = 200
    n_food: int = 12
    wall_fraction: float = WALL_FRACTION
    local_window_size: int = LOCAL_WINDOW_SIZE
    n_actions: int = N_ACTIONS
    obs_dim: int = OBS_DIM
    pheromone_evaporation: float = PHEROMONE_EVAPORATION
    seed: int | None = None

    def to_gym_kwargs(self) -> dict:
        return {
            "n_ants": self.n_ants,
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "max_steps": self.max_steps,
            "n_food": self.n_food,
            "wall_fraction": self.wall_fraction,
            "local_window_size": self.local_window_size,
            "n_actions": self.n_actions,
            "obs_dim": self.obs_dim,
            "pheromone_evaporation": self.pheromone_evaporation,
            "seed": self.seed,
        }


DEFAULT_ENV_CONFIG = EnvConfig()
