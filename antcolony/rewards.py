"""Global cooperative reward (shared by all agents via EPyMARL ``common_reward``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from antcolony.config import (
    REWARD_BATTLE_WON,
    REWARD_NEST_DELIVERY,
    REWARD_STEP_PENALTY,
)

if TYPE_CHECKING:
    from antcolony.core.colony import Colony


def compute_step_reward(
    colony: Colony, deliveries: int, *, battle_won: bool = False
) -> float:
    """Single team reward per environment step."""
    reward = deliveries * REWARD_NEST_DELIVERY
    reward += colony.n_ants * REWARD_STEP_PENALTY
    if battle_won:
        reward += REWARD_BATTLE_WON
    return reward
