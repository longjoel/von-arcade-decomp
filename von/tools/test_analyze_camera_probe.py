#!/usr/bin/env python3
"""Hermetic test for the camera probe analyzer.

Builds a synthetic `f<frame> state ...` dump from known float values and checks
the parsed player/eye/target cells and the base-pose summary. No ROMs/MAME.
"""

from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_camera_probe import (EYE, PLAYER, TARGET, _pose,  # noqa: E402
                                  parse_log)


def words(values: dict[int, float]) -> str:
    count = max(values) + 1
    out = [0] * count
    for index, value in values.items():
        out[index] = struct.unpack("<I", struct.pack("<f", value))[0]
    return " ".join(f"{word:08x}" for word in out)


def state_line(frame: int, player_y: float, target_y: float,
               eye_y: float, distance: float) -> str:
    values = {PLAYER[0]: 5.0, PLAYER[1]: player_y, PLAYER[2]: -60.0,
              EYE[0]: 5.0, EYE[1]: eye_y, EYE[2]: -60.0 - distance,
              TARGET[0]: 5.0, TARGET[1]: target_y, TARGET[2]: -60.0}
    return f"f{frame} state {words(values)}"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-cam-") as directory:
        path = Path(directory) / "probe.lua.log"
        path.write_text("\n".join([
            state_line(3000, 0.0, 18.0, 29.445, 77.2),
            state_line(3001, 0.0, 18.0, 29.445, 77.2),
            state_line(3002, 26.0, 44.0, 62.2, 72.0),
        ]) + "\n")
        rows = parse_log(path)
        checks = [
            ("row-count", len(rows) == 3),
            ("player-y", abs(rows[0]["player"][1]) < 1e-4),
            ("eye-y", abs(rows[0]["eye"][1] - 29.445) < 1e-3),
            ("target-y", abs(rows[0]["target"][1] - 18.0) < 1e-3),
        ]
        grounded = [r for r in rows if abs(r["player"][1]) < 0.01]
        pose = _pose(grounded)
        checks.append(("distance", abs(pose["distance"] - 77.2) < 1e-2))
        checks.append(("offset", abs(pose["offset"] - 11.445) < 1e-2))
        failures = [name for name, ok in checks if not ok]
        if failures:
            raise SystemExit(f"FAILED: {failures}")
    print("PASS: camera probe analyzer (cells and base pose)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
