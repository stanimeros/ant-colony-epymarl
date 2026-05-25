#!/usr/bin/env python3
"""Render a trained MAPPO checkpoint — grid with icons and graded pheromone."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import antcolony  # noqa: F401
import gymnasium as gym
import numpy as np
import torch as th
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for p in (_REPO, _SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
_EPYMARL_SRC = _REPO / "epymarl" / "src"
if _EPYMARL_SRC.is_dir() and str(_EPYMARL_SRC) not in sys.path:
    sys.path.insert(0, str(_EPYMARL_SRC))

from modules.agents.rnn_agent import RNNAgent  # noqa: E402
from render_icons import compose_frame  # noqa: E402

_MODEL_DIR = (
    _REPO
    / "models"
    / "mappo_seed238606856_antcolony:AntColony-v0_2026-05-24 12:10:06.952765"
)
DEFAULT_CHECKPOINT = _MODEL_DIR / "20016596" / "agent.th"

ENV_KWARGS = dict(
    n_ants=32,
    grid_width=32,
    grid_height=32,
    max_steps=800,
    n_food=24,
    wall_fraction=0.10,
    pheromone_evaporation=0.95,
)

AGENT_KWARGS = dict(hidden_dim=128, use_rnn=True, n_actions=5)


def _agent_args(n_agents: int) -> argparse.Namespace:
    return argparse.Namespace(n_agents=n_agents, **AGENT_KWARGS)


def _build_inputs(obs: list[np.ndarray], n_agents: int, device: th.device) -> th.Tensor:
    obs_t = th.tensor(np.stack(obs, axis=0), dtype=th.float32, device=device)
    agent_ids = th.eye(n_agents, device=device)
    return th.cat([obs_t, agent_ids], dim=1)


@th.no_grad()
def select_actions(
    agent: RNNAgent,
    obs: list[np.ndarray],
    hidden: th.Tensor,
    n_agents: int,
    device: th.device,
) -> tuple[list[int], th.Tensor]:
    inputs = _build_inputs(obs, n_agents, device)
    logits, hidden = agent(inputs, hidden)
    probs = F.softmax(logits, dim=-1)
    return probs.argmax(dim=-1).cpu().tolist(), hidden


def _caption_bar(frame: np.ndarray, colony, bar_px: int = 36) -> np.ndarray:
    """Step label above the grid."""
    img = Image.fromarray(frame)
    out = Image.new("RGB", (img.width, img.height + bar_px), "#ffffff")
    out.paste(img, (0, bar_px))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
    text = (
        f"Step {colony.step_count}  ·  "
        f"Food home {colony.total_deliveries}/{colony.n_food_spawned}"
    )
    draw.text((12, 8), text, fill="#000000", font=font)
    draw.text(
        (out.width - 12, 8),
        "Pheromone trail",
        fill="#000000",
        font=font,
        anchor="ra",
    )
    return np.asarray(out)


def run_episode(
    checkpoint: Path,
    seed: int,
    out_path: Path,
    fps: int,
    frame_skip: int,
    max_steps: int | None,
    cell_px: int,
) -> None:
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    n_agents = ENV_KWARGS["n_ants"]
    input_shape = 30 + n_agents

    agent = RNNAgent(input_shape, _agent_args(n_agents))
    agent.load_state_dict(
        th.load(checkpoint, map_location=device, weights_only=True)
    )
    agent.to(device)
    agent.eval()

    env = gym.make("antcolony:AntColony-v0", **ENV_KWARGS)
    obs, _ = env.reset(seed=seed)
    colony = env.unwrapped._colony
    hidden = agent.init_hidden().to(device).expand(n_agents, -1).contiguous()

    frames: list[np.ndarray] = []
    limit = max_steps or ENV_KWARGS["max_steps"]
    terminated = False
    step_i = 0

    while not terminated and step_i < limit:
        if step_i % frame_skip == 0:
            grid = compose_frame(colony, cell_px)
            frames.append(_caption_bar(grid, colony))

        actions, hidden = select_actions(agent, list(obs), hidden, n_agents, device)
        obs, _reward, terminated, _trunc, info = env.step(actions)
        step_i += 1

    env.close()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = out_path.suffix.lower()
    if suffix == ".png":
        if not frames:
            raise SystemExit("No frames captured")
        Image.fromarray(frames[-1]).save(out_path)
    elif suffix in (".gif", ".mp4"):
        try:
            import imageio.v2 as imageio
        except ImportError as exc:
            raise SystemExit("Install imageio: pip install imageio") from exc
        if suffix == ".gif":
            imageio.mimsave(out_path, frames, duration=1.0 / fps, loop=0)
        else:
            imageio.mimsave(out_path, frames, fps=fps)
    else:
        raise SystemExit(f"Unsupported output: {suffix}")

    print(f"checkpoint: {checkpoint}")
    print(f"seed: {seed}  steps: {step_i}  battle_won: {info.get('battle_won')}")
    print(f"deliveries: {info.get('total_deliveries')} / {info.get('food_spawned')}")
    print(f"saved: {out_path}  ({len(frames)} frames, cell={cell_px}px)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO / "docs" / "figures" / "mappo_32x32_demo.gif",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fps", type=int, default=2)
    parser.add_argument("--frame-skip", type=int, default=8)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument(
        "--cell-px",
        type=int,
        default=18,
        help="Pixels per grid cell (32×32 → 576px wide)",
    )
    args = parser.parse_args()

    if not args.checkpoint.is_file():
        raise SystemExit(f"Checkpoint not found: {args.checkpoint}")

    run_episode(
        args.checkpoint.resolve(),
        args.seed,
        args.out.resolve(),
        args.fps,
        args.frame_skip,
        args.max_steps,
        args.cell_px,
    )


if __name__ == "__main__":
    main()
