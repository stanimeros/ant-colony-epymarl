#!/usr/bin/env python3
"""Rasterize docs/icon/*.svg to docs/icon/png/ for the policy renderer."""

from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
ICON_DIR = _REPO / "docs" / "icon"
OUT_DIR = ICON_DIR / "png"
SIZES = (32, 48, 64, 96, 128)
SVG_NAMES = ("ant", "ant_carrying", "food", "nest")


def main() -> None:
    try:
        import cairosvg
    except ImportError as exc:
        raise SystemExit("pip install cairosvg") from exc

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in SVG_NAMES:
        svg_path = ICON_DIR / f"{name}.svg"
        if not svg_path.is_file():
            raise SystemExit(f"Missing {svg_path}")
        for size in SIZES:
            out = OUT_DIR / f"{name}_{size}.png"
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(out),
                output_width=size,
                output_height=size,
            )
            print(f"wrote {out.relative_to(_REPO)}")


if __name__ == "__main__":
    main()
