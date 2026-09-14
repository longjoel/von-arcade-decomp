#!/usr/bin/env python3
"""Export each fighter's match model from the same capture as its clip.

The roster models were exported from the select-screen capture, but the
animation clips are baked from gameplay captures that show a *different* part
set for the same mech, so several model nodes had no matching clip part. This
re-exports `roster_<mech>.gltf` from the clip's own capture/frame and part
list, so every model node is animated.

Usage:
    python3 von/tools/export_clip_models.py --decomp <dir> --godot <dir>
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OBJECT = re.compile(
    r"geometry_object: time=([0-9.e+-]+) *.*oba=([0-9a-f]{8})")

# fighter -> (capture relative to von/captures, emulated seconds)
SPECS = {
    "viper2":  ("attract-20260912T/mame.log", 100.0),
    "raiden":  ("fighter-raiden-20260912T/mame.log", 225.0),
    "feiyen":  ("fighter-feiyen-20260912T/mame.log", 180.0),
    "belgador": ("fighter-belgador-20260912T/mame.log", 180.0),
}


def obas_at(trace: Path, time: float, tol: float = 0.3) -> set[int]:
    found: set[int] = set()
    for line in trace.open(errors="replace"):
        if "geometry_object" not in line:
            continue
        match = OBJECT.search(line)
        if match and abs(float(match.group(1)) - time) <= tol:
            found.add(int(match.group(2), 16))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--decomp", type=Path, required=True)
    ap.add_argument("--godot", type=Path, required=True)
    args = ap.parse_args()

    exporter = args.decomp / "von" / "tools" / "export_geometry_frame_textured_gltf.py"
    texture_root = args.decomp / "von" / "build" / "disasm" / "texture-pipeline"
    anims = args.godot / "build" / "anims"
    out_dir = args.godot / "assets" / "generated" / "fighters"

    for mech, (capture, time) in SPECS.items():
        clip_path = anims / f"{mech}-idle.json"
        if not clip_path.is_file():
            clip_path = anims / f"{mech}.json"
        clip = json.loads(clip_path.read_text())
        trace = args.decomp / "von" / "captures" / capture
        present = obas_at(trace, time)
        obas = [int(p["oba"], 16) for p in clip["parts"] if int(p["oba"], 16) in present]
        if not obas:
            print(f"{mech}: no clip parts present at t={time}")
            continue
        output = out_dir / f"roster_{mech}.gltf"
        cmd = [sys.executable, str(exporter),
               "--trace", str(trace), "--time", str(time),
               "--palette-trace", str(trace),
               "--rom", str(args.decomp / "von/build/disasm/geometry-rom.bin"),
               "--texture-rom", str(texture_root / "texture-rom.bin"),
               "--bank-primary", str(texture_root / "bank0-primary.bin"),
               "--bank-secondary", str(texture_root / "bank0-secondary.bin"),
               "--output", str(output)]
        for oba in obas:
            cmd += ["--oba", f"{oba:08x}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip().splitlines()
            print(f"{mech}: FAILED: {err[-1] if err else result.returncode}")
            continue
        print(f"{mech}: wrote roster_{mech}.gltf ({len(obas)} parts from {capture})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
