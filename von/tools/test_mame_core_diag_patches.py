#!/usr/bin/env python3
"""Guard the captured core debugger/M2COMM diagnostics patches.

Patches 0041 (debugger PC-address tracking) and 0042 (M2COMM diagnostics
logging) capture working-tree edits that used to ride to the remote builder
as raw file syncs. They must stay in the core profile so every build profile
keeps the diagnostics behavior the captures were taken with.
"""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH41 = ROOT / "third_party/patches/0041-von-debug-pc-address-tracking.patch"
PATCH42 = ROOT / "third_party/patches/0042-von-m2comm-diag-logging.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch41 = PATCH41.read_text(encoding="utf-8")
    for fragment in (
        "m_track_pc_addresses",
        "track_pc_data_clear",
        "unordered_set",
    ):
        if fragment not in patch41:
            raise SystemExit(f"debugger PC-address patch missing {fragment}")
    patch42 = PATCH42.read_text(encoding="utf-8")
    for fragment in (
        "diag listen failure",
        "diag connect failure",
        "diag sockets ready",
        "diag handshake timer",
        "m_diagnostics",
    ):
        if fragment not in patch42:
            raise SystemExit(f"M2COMM diagnostics patch missing {fragment}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    core = resolve(manifest, "core")
    for name in (PATCH41.name, PATCH42.name):
        if name not in core:
            raise SystemExit(f"core profile does not install {name}")
    print("PASS: core debugger/M2COMM diagnostics patch contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
