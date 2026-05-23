"""Ant colony MARL environment (Gymnasium + EPyMARL gymma)."""

from gymnasium import register

from antcolony.config import DEFAULT_ENV_CONFIG

register(
    id="AntColony-v0",
    entry_point="antcolony.env:AntColonyEnv",
    kwargs=DEFAULT_ENV_CONFIG.to_gym_kwargs(),
)

__all__ = ["AntColonyEnv"]
