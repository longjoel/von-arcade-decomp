#!/usr/bin/env python3
"""Contract test for the tracked evidence manifest."""

from __future__ import annotations

import json
from pathlib import Path

from evidence_manifest import validate


def main() -> int:
    root = Path.cwd()
    manifest = json.loads((root / "von/evidence/manifest.json").read_text(encoding="utf-8"))
    ledger = json.loads((root / "von/reconstruction_ledger.json").read_text(encoding="utf-8"))
    assert not validate(manifest, ledger, root)
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["outcome"] = "incomplete"
    assert any("outcome" in error for error in validate(broken, ledger, root))
    print("PASS: canonical evidence manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
