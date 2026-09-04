#!/usr/bin/env python3
"""Contract tests for MAME runner capture-root provenance."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/mame_runner.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        fake_mame = root / "fake-mame"
        fake_mame.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        fake_mame.chmod(0o755)
        roms = root / "roms"
        roms.mkdir()
        captures = root / "captures"
        result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(root), "--mame", str(fake_mame),
             "--rom-dir", str(roms), "--capture-dir", str(captures)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "Capture directory:" in result.stdout

        outside = root.parent / f"outside-roms-{root.name}"
        outside.mkdir()
        result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(root), "--mame", str(fake_mame),
             "--rom-dir", str(outside), "--capture-dir", str(captures)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 2
        assert "ROM path escapes root" in result.stderr

        linked_roms = root / "linked-roms"
        linked_roms.symlink_to(roms, target_is_directory=True)
        result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(root), "--mame", str(fake_mame),
             "--rom-dir", str(linked_roms), "--capture-dir", str(captures)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 2
        assert "ROM path must not be a symlink" in result.stderr
    print("PASS: MAME runner protects capture-root provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
