"""Discrete action space for ant foraging."""

from enum import IntEnum


class Action(IntEnum):
    STAND_STILL = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4


# (d_row, d_col) — row 0 is top (up decreases row).
ACTION_DELTAS: dict[int, tuple[int, int]] = {
    Action.STAND_STILL: (0, 0),
    Action.MOVE_UP: (-1, 0),
    Action.MOVE_DOWN: (1, 0),
    Action.MOVE_LEFT: (0, -1),
    Action.MOVE_RIGHT: (0, 1),
}

N_ACTIONS = len(Action)
