#!/usr/bin/env python3
"""Hermetic test for the per-fighter weapon timing header generator.

Builds a small synthetic weapon-params.json (rosters and action groups),
runs emit_weapon_timing_header.py, and checks the emitted C table and the
LEFT/CENTER/RIGHT reordering. No ROMs required.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emit_weapon_timing_header import FIGHTER_ORDER, WEAPON_ORDER  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-weapon-") as directory:
        root = Path(directory)
        fighters = []
        for index, name in enumerate(FIGHTER_ORDER):
            actions = {}
            for weapon in WEAPON_ORDER:
                base = 10 * (index + 1)
                offset = {"left": 0, "center": 1, "right": 2}[weapon]
                actions[weapon] = {
                    "action": {"left": 2, "center": 3, "right": 1}[weapon],
                    "phases": [base + offset, base + 3 + offset, base + 6 + offset],
                    "cooldown_inc": base + offset,
                    "cooldown_max": base + offset + 100,
                }
            fighters.append({"fighter": name, "profile": "0x0", "actions": actions})
        params = root / "weapon-params.json"
        params.write_text(json.dumps({"fighters": fighters}))

        output = root / "weapon_timing.h"
        run = subprocess.run(
            [sys.executable, "von/tools/emit_weapon_timing_header.py",
             "--params", str(params), "--output", str(output)],
            capture_output=True, text=True, cwd=Path.cwd())
        if run.returncode != 0:
            raise SystemExit(f"generator failed: {run.stdout}\n{run.stderr}")
        text = output.read_text()

    expected_checks = [
        ("define fighters", "#define VON_WEAPON_TIMING_FIGHTERS 10" in text),
        ("table symbol", "VON_WEAPON_TIMING[VON_WEAPON_TIMING_FIGHTERS][3][3]" in text),
        ("cooldown inc", "VON_WEAPON_COOLDOWN_INC[" in text),
        ("cooldown max", "VON_WEAPON_COOLDOWN_MAX[" in text),
        # First fighter (TEMJIN), index 0: left phases base 10 -> {10,13,16}.
        ("left row", "{10, 13, 16}," in text and "/* LEFT */" in text),
        # center is weapon order index 1 -> base 11, right -> base 12.
        ("center row", "{11, 14, 17}," in text and "/* CENTER */" in text),
        ("right row", "{12, 15, 18}," in text and "/* RIGHT */" in text),
        ("last fighter label", "/* Z-GRADT */" in text),
    ]
    failures = [name for name, ok in expected_checks if not ok]
    if failures:
        raise SystemExit(f"FAILED: {failures}")
    print("PASS: weapon timing header generator (order, table, cooldowns)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
