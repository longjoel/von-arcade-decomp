#!/usr/bin/env python3
"""Contract tests for integration-evidence registration."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path

from register_integration import register


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "image.bin").write_bytes(b"image")
        (root / "integration-test.py").write_text("print('pass')\n", encoding="utf-8")
        unit = {"id": "unit", "stage": "integrated", "modeling": {
            "boundary": "state", "test": "integration-test.py",
            "unresolved_behavior": "device timing",
        }}
        ledger = {"images": [{"name": "maincpu", "work_units": [unit]}]}
        assert not register(ledger, "unit", "image.bin", "startup-init",
                            "integration-test.py", root, run_test=True)
        assert unit["integration"] == {
            "image": "image.bin", "checkpoint": "startup-init",
            "test": "integration-test.py",
        }
        assert any("already has" in error for error in register(
            ledger, "unit", "image.bin", "startup-init", "integration-test.py", root))
        assert any("unknown" in error for error in register(
            {"images": [{"work_units": []}]}, "unit", "image.bin",
            "startup-init", "integration-test.py", root))
        assert any("not integration-promoted" in error for error in register(
            {"images": [{"work_units": [{"id": "planned", "stage": "planned"}]}]},
            "planned", "image.bin", "startup-init", "integration-test.py", root))
        assert any("missing modeling evidence" in error for error in register(
            {"images": [{"work_units": [{"id": "raw", "stage": "integrated"}]}]},
            "raw", "image.bin", "startup-init", "integration-test.py", root))
        broken = copy.deepcopy(ledger)
        del broken["images"][0]["work_units"][0]["integration"]
        assert any("missing or unsafe integration image" in error for error in register(
            broken, "unit", "missing.bin", "startup-init", "integration-test.py", root))
        assert any("missing or unsafe integration test" in error for error in register(
            broken, "unit", "image.bin", "startup-init", "missing.py", root))
        failing = root / "failing-test.py"
        failing.write_text("raise SystemExit('failed integration')\n", encoding="utf-8")
        assert any("integration test" in error and "failed" in error for error in register(
            broken, "unit", "image.bin", "startup-init", "failing-test.py", root,
            run_test=True))
    print("PASS: integration evidence registration validates paths and lifecycle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
