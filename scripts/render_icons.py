"""Grid compositor using baked PNG icons from docs/icon/png/."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
from matplotlib.colors import to_rgb
from PIL import Image

_ICON_DIR = Path(__file__).resolve().parents[1] / "docs" / "icon" / "png"
PHEROMONE_VMAX = 1.0

# Single meadow floor + rock obstacles
GROUND = to_rgb("#9dc183")
ROCK = to_rgb("#6b6e73")
ROCK_EDGE = to_rgb("#4f5256")
GRID_LINE = to_rgb("#7da868")


@lru_cache(maxsize=32)
def _load_icon(name: str, size: int) -> np.ndarray:
    """Load nearest baked PNG and resize to exact size. Returns RGBA uint8."""
    sizes = (32, 48, 64, 96, 128)
    pick = min(sizes, key=lambda s: abs(s - size))
    path = _ICON_DIR / f"{name}_{pick}.png"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Run: python scripts/bake_icons.py"
        )
    img = Image.open(path).convert("RGBA")
    if pick != size:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    return np.asarray(img, dtype=np.uint8)


def pheromone_overlay(phero: np.ndarray, cell_px: int) -> np.ndarray:
    """RGBA trail layer — pale yellow → bright golden yellow."""
    gh, gw = phero.shape
    norm = np.clip(phero / PHEROMONE_VMAX, 0.0, 1.0)
    rgba = np.zeros((gh, gw, 4), dtype=np.uint8)
    # #fff9c4 (weak) → #ffeb3b (strong)
    rgba[:, :, 0] = 255
    rgba[:, :, 1] = (249 + 6 * norm).astype(np.uint8)
    rgba[:, :, 2] = (196 * (1.0 - norm)).astype(np.uint8)
    rgba[:, :, 3] = (norm * 215).astype(np.uint8)
    img = Image.fromarray(rgba, mode="RGBA")
    img = img.resize((gw * cell_px, gh * cell_px), Image.Resampling.NEAREST)
    return np.asarray(img)


def blit_icon(canvas: np.ndarray, icon: np.ndarray, row: int, col: int, cell_px: int) -> None:
    ih, iw = icon.shape[:2]
    y0 = row * cell_px + (cell_px - ih) // 2
    x0 = col * cell_px + (cell_px - iw) // 2
    y1, x1 = y0 + ih, x0 + iw
    if y0 < 0 or x0 < 0 or y1 > canvas.shape[0] or x1 > canvas.shape[1]:
        return
    alpha = icon[:, :, 3:4].astype(np.float32) / 255.0
    rgb = icon[:, :, :3].astype(np.float32)
    region = canvas[y0:y1, x0:x1].astype(np.float32)
    canvas[y0:y1, x0:x1] = (region * (1 - alpha) + rgb * alpha).astype(np.uint8)


def _blend_rgba_under(base_rgb: np.ndarray, overlay_rgba: np.ndarray) -> np.ndarray:
    """Alpha-composite overlay onto RGB canvas."""
    base = base_rgb.astype(np.float32)
    alpha = overlay_rgba[:, :, 3:4].astype(np.float32) / 255.0
    over = overlay_rgba[:, :, :3].astype(np.float32)
    return (base * (1 - alpha) + over * alpha).astype(np.uint8)


def compose_frame(colony, cell_px: int) -> np.ndarray:
    gh, gw = colony.grid_height, colony.grid_width
    ny, nx = colony.nest_pos
    h_px, w_px = gh * cell_px, gw * cell_px

    canvas = np.zeros((h_px, w_px, 3), dtype=np.uint8)
    canvas[:, :] = (np.array(GROUND) * 255).astype(np.uint8)

    for y in range(gh):
        for x in range(gw):
            if colony.is_wall(y, x):
                y0, x0 = y * cell_px, x * cell_px
                cell = canvas[y0 : y0 + cell_px, x0 : x0 + cell_px]
                cell[:, :] = (np.array(ROCK) * 255).astype(np.uint8)
                # darker rock edge (1px inset border)
                edge = (np.array(ROCK_EDGE) * 255).astype(np.uint8)
                cell[0, :, :] = edge
                cell[-1, :, :] = edge
                cell[:, 0, :] = edge
                cell[:, -1, :] = edge

    phero_layer = pheromone_overlay(colony.food_pheromone_grid, cell_px)
    canvas[:] = _blend_rgba_under(canvas, phero_layer)

    icon_px = max(12, int(cell_px * 0.88))
    food_i = _load_icon("food", icon_px)
    nest_i = _load_icon("nest", icon_px)
    ant_i = _load_icon("ant", icon_px)
    ant_carry_i = _load_icon("ant_carrying", icon_px)

    for y in range(gh):
        for x in range(gw):
            if colony.has_food(y, x):
                blit_icon(canvas, food_i, y, x, cell_px)

    blit_icon(canvas, nest_i, ny, nx, cell_px)

    for ant in colony.ants:
        y, x = ant.position
        blit_icon(
            canvas,
            ant_carry_i if ant.carrying_food else ant_i,
            y,
            x,
            cell_px,
        )

    line = (np.array(GRID_LINE) * 255).astype(np.uint8)
    for y in range(gh + 1):
        canvas[y * cell_px : y * cell_px + 1, :, :] = line
    for x in range(gw + 1):
        canvas[:, x * cell_px : x * cell_px + 1, :] = line

    return canvas
