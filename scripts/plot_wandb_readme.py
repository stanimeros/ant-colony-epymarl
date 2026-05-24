#!/usr/bin/env python3
"""Download a W&B run and write README learning-curve figures."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import wandb

DEFAULT_ENTITY = "aid26006-university-of-macedonia"
DEFAULT_PROJECT = "ant-colony-foraging"
DEFAULT_RUN_ID = "x11wd1h0"  # rich-armadillo-3 — 16×16 MAPPO baseline

METRIC_PANELS = (
    ("return_mean", "test_return_mean", "Team score per episode", ""),
    ("battle_won_mean", "test_battle_won_mean", "Episodes with all food home", ""),
    (
        "total_deliveries_mean",
        "test_total_deliveries_mean",
        "Food brought home (of 12)",
        "",
    ),
    ("ep_length_mean", "test_ep_length_mean", "Steps to finish (shorter = faster)", ""),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _fetch_history(run, samples: int) -> pd.DataFrame:
    # Do not pass `keys=` — W&B often returns empty frames when key-filtering.
    df = run.history(samples=samples, pandas=True)
    if df.empty:
        raise SystemExit(f"No history for run {run.url}")
    x_col = "t_env" if "t_env" in df.columns else "_step"
    df = df.dropna(subset=[x_col]).sort_values(x_col)
    df = df.rename(columns={x_col: "x_step"})
    return df


def _smooth(series: pd.Series, window: int) -> pd.Series:
    if window <= 1 or len(series) < 2:
        return series
    return series.rolling(window, min_periods=1).mean()


def _plot_panel(ax, df: pd.DataFrame, train_key: str, test_key: str, title: str, suffix: str, smooth: int):
    x = df["x_step"] / 1e6
    if train_key in df.columns and df[train_key].notna().any():
        y = _smooth(df[train_key], smooth)
        ax.plot(x, y, label="Train", color="#2563eb", linewidth=1.8, alpha=0.95)
    if test_key in df.columns and df[test_key].notna().any():
        y = _smooth(df[test_key], smooth)
        ax.plot(x, y, label="Test (greedy)", color="#dc2626", linewidth=1.8, alpha=0.95)
    ax.set_title(title)
    ax.set_xlabel("Training progress (millions of steps)")
    ylab = title + suffix
    if "of 12" in ylab:
        ax.set_ylim(0, 12.5)
    if "Episodes with all food" in ylab:
        ax.set_ylim(0, 1.05)
    ax.set_ylabel(ylab)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="best", fontsize=8)


def plot_learning_curves(
    run_path: str,
    out_dir: Path,
    samples: int,
    smooth: int,
    dpi: int,
) -> Path:
    api = wandb.Api()
    run = api.run(run_path)
    df = _fetch_history(run, samples)

    env = run.config.get("env_args") or {}
    grid = env.get("grid_width", "?")
    ants = env.get("n_ants", "?")
    food = env.get("n_food", "?")
    title = f"Learning on a {grid}×{grid} world — {ants} ants, {food} food pieces"

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    fig.suptitle(title, fontsize=11, fontweight="medium")

    for ax, panel in zip(axes.flat, METRIC_PANELS):
        _plot_panel(ax, df, *panel, smooth=smooth)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "mappo_16x16_learning_curves.png"
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        default=os.environ.get(
            "WANDB_RUN_PATH",
            f"{DEFAULT_ENTITY}/{DEFAULT_PROJECT}/{DEFAULT_RUN_ID}",
        ),
        help="entity/project/run_id",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_repo_root() / "docs" / "figures",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=800,
        help="W&B history rows to sample (higher = slower download)",
    )
    parser.add_argument(
        "--smooth",
        type=int,
        default=15,
        help="Rolling mean window over logged points",
    )
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    if not os.environ.get("WANDB_API_KEY") and not Path.home().joinpath(".netrc").exists():
        raise SystemExit(
            "Set WANDB_API_KEY or run `wandb login` before generating figures."
        )

    out_path = plot_learning_curves(
        args.run, args.out_dir, args.samples, args.smooth, args.dpi
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
