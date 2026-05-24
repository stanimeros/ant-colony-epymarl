"""Global cooperative reward (shared by all agents via EPyMARL ``common_reward``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from antcolony.core.colony import Colony


def compute_step_reward(
    colony: Colony, deliveries: int, *, battle_won: bool = False
) -> float:
    """Single team reward per environment step."""
    reward = deliveries * colony.reward_nest_delivery
    reward += colony.n_ants * colony.reward_step_penalty_per_ant
    if battle_won:
        reward += colony.reward_battle_won
    return reward
