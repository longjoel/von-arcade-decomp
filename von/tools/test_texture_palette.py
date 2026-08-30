#!/usr/bin/env python3
"""Test the captured Model 2 indexed-texture palette mapping."""

from __future__ import annotations

import tempfile
from pathlib import Path

from render_texture_palette import gamma, palette_rgb, parse_trace


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-palette-") as directory:
        trace = Path(directory) / "palette.trace"
        trace.write_text(
            "\n".join(
                (
                    "vonj_palette_write: time=1.000000 offset=1001 data=001f mask=ffff value=001f",
                    "vonj_palette_write: time=3.000000 offset=1001 data=03e0 mask=ffff value=03e0",
                    "vonj_luma_write: time=1.000000 offset=0008 data=40",
                    "vonj_colorxlat_write: time=1.000000 offset=1f40 data=0080 mask=ffff value=0080",
                    "vonj_colorxlat_write: time=1.000000 offset=2040 data=0090 mask=ffff value=0090",
                    "vonj_colorxlat_write: time=1.000000 offset=4040 data=00a0 mask=ffff value=00a0",
                )
            )
            + "\n"
        )
        palette, colorxlat, luma = parse_trace(trace, at_time=2.0)

    if palette_rgb(1, 1, palette, colorxlat, luma) != (
        gamma(0x80), gamma(0x90), gamma(0xA0)
    ):
        raise SystemExit("captured palette mapping mismatch")
    if palette_rgb(0, 1, palette, colorxlat, luma) != (0, 0, 0):
        raise SystemExit("missing luma entry should map to black")

    print("PASS: indexed texture palette, color-translation, and luma mapping")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
