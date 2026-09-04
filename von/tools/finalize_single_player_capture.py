#!/usr/bin/env python3
"""Write and validate a portable manifest for one original-ROM capture."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--selector-steps", type=int, required=True)
    parser.add_argument("--mame", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    root = args.capture_dir
    required = [root / "events.log", root / "mame.log"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("missing required capture artifacts: " + ", ".join(missing))
    for region in ("workram", "tilemap", "geometry-buffer", "texture-bank0", "texture-bank1"):
        if not any(root.glob(f"*-{region}.bin")):
            raise SystemExit(f"missing raw memory evidence for region: {region}")
    timeline = []
    completion = "incomplete"
    event_pattern = re.compile(r"frame=(\d+) phase=(\S+) event=(\S+)(?: (.*))?$")
    for line in (root / "events.log").read_text(encoding="utf-8").splitlines():
        match = event_pattern.fullmatch(line)
        if not match:
            continue
        frame, phase, event, detail = match.groups()
        entry = {"frame": int(frame), "phase": phase, "event": event}
        if detail:
            entry["detail"] = detail
        timeline.append(entry)
        if event == "complete" and detail:
            completion = detail.removeprefix("status=")
    phases = {entry["phase"] for entry in timeline}
    required_phases = {"coin_insert", "machine_select", "takeoff", "level_intro", "match_entry"}
    timeout_boundaries = {
        entry.get("detail", "") for entry in timeline if entry["event"] == "snapshot"
    }
    if completion == "loader_transition_timeout":
        if "name=loader-timeout" not in timeout_boundaries:
            raise SystemExit("loader timeout capture is missing its diagnostic boundary")
    elif not required_phases.issubset(phases):
        raise SystemExit("capture did not reach all required phase boundaries")
    files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "schema": "von-single-player-capture-v1",
        "selector_steps": args.selector_steps,
        "completion": completion,
        "timeline": timeline,
        "mame": {"path": str(args.mame), "sha256": sha256(args.mame)},
        "maincpu_rom": {"path": str(args.rom), "sha256": sha256(args.rom), "bytes": args.rom.stat().st_size},
        "artifacts": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files
        ],
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"finalized {root / 'manifest.json'} ({len(files)} artifacts)")


if __name__ == "__main__":
    main()
