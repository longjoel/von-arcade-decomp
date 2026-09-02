#!/usr/bin/env python3
"""Guard the generic MAME SHARC STKY state exposure patch."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0029-von-sharc-expose-stky-state.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "SHARC_STKY",
        '"STKY"',
        "m_core->stky",
        '.formatstr("%08X")',
    ):
        if fragment not in patch:
            raise SystemExit(f"STKY state patch missing {fragment}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if PATCH.name not in resolve(manifest, "sharc-diagnostics"):
        raise SystemExit("sharc-diagnostics profile does not install the STKY state patch")
    print("PASS: SHARC STKY architectural-state patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
