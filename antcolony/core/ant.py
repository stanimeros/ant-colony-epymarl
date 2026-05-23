"""Single ant state."""

from dataclasses import dataclass


@dataclass
class Ant:
    agent_id: int
    position: tuple[int, int]  # (row, col)
    carrying_food: int = 0
    # Path-integration home vector (nest direction), each in [-1, 1].
    home_dx: float = 0.0
    home_dy: float = 0.0
