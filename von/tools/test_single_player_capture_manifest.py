#!/usr/bin/env python3
"""Contract test for original-ROM single-player capture manifests."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    runner = (root / "scripts/capture-single-player-original.sh").read_text(encoding="utf-8")
    assert "VON_CAPTURE_ENABLE_PC_TRACE" in runner
    assert "MAME_DEBUG_ARGS=(-debug -debugger none)" in runner
    assert '"$MAME_BIN" vonj -rompath "$ROM_PATH"' in runner
    assert "vonjdev" not in runner
    tool = root / "von/tools/finalize_single_player_capture.py"
    with tempfile.TemporaryDirectory(prefix="von-single-player-capture-") as directory:
        capture = Path(directory) / "capture"
        capture.mkdir()
        (capture / "events.log").write_text(
            "frame=900 phase=coin_insert event=phase_start selector_steps=3\n"
            "frame=960 phase=machine_select event=phase_start\n"
            "frame=1020 phase=takeoff event=phase_start\n"
            "frame=1080 phase=level_intro event=phase_start\n"
            "frame=1140 phase=match_entry event=complete status=match_entry_timeout\n"
        )
        (capture / "mame.log").write_text("original mame log\n")
        for region in ("workram", "tilemap", "geometry-buffer", "texture-bank0", "texture-bank1"):
            (capture / f"coin_insert-start-{region}.bin").write_bytes(b"evidence")
        binary = Path(directory) / "von"
        rom = Path(directory) / "epr-18664b.15"
        binary.write_bytes(b"mame")
        rom.write_bytes(b"rom")
        subprocess.run(
            ["python3", str(tool), "--capture-dir", str(capture), "--selector-steps", "3",
             "--mame", str(binary), "--rom", str(rom)],
            check=True,
        )
        manifest = json.loads((capture / "manifest.json").read_text())
        if manifest["schema"] != "von-single-player-capture-v1":
            raise SystemExit("unexpected manifest schema")
        if (manifest["selector_steps"] != 3 or len(manifest["artifacts"]) != 7
                or manifest["completion"] != "match_entry_timeout"
                or len(manifest["timeline"]) != 5):
            raise SystemExit("manifest did not record capture inputs")

    with tempfile.TemporaryDirectory(prefix="von-single-player-timeout-") as directory:
        capture = Path(directory) / "capture"
        capture.mkdir()
        (capture / "events.log").write_text(
            "frame=1800 phase=warmup event=snapshot name=loader-timeout\n"
            "frame=1800 phase=warmup event=complete status=loader_transition_timeout\n"
        )
        (capture / "mame.log").write_text("loader mame log\n")
        for region in ("workram", "tilemap", "geometry-buffer", "texture-bank0", "texture-bank1"):
            (capture / f"loader-timeout-{region}.bin").write_bytes(b"evidence")
        binary = Path(directory) / "von"
        rom = Path(directory) / "epr-18664b.15"
        binary.write_bytes(b"mame")
        rom.write_bytes(b"rom")
        subprocess.run(
            ["python3", str(tool), "--capture-dir", str(capture), "--selector-steps", "0",
             "--mame", str(binary), "--rom", str(rom)],
            check=True,
        )
        manifest = json.loads((capture / "manifest.json").read_text())
        if manifest["completion"] != "loader_transition_timeout":
            raise SystemExit("manifest did not preserve loader timeout")
    print("PASS: single-player capture manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
