#!/usr/bin/env python3
"""Guard the consolidated runtime-filtered SHARC diagnostics patch."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0034-von-sharc-runtime-diagnostics.patch"


def main() -> int:
    text = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "VON_SHARC_TRACE_START",
        "VON_SHARC_TRACE_END",
        "VON_SHARC_TRACE_LIMIT",
        "von_sharc_diag:",
        "m_core->opcode",
        "m_core->astat",
        "m_core->stky",
    ):
        if fragment not in text:
            raise SystemExit(f"runtime diagnostics patch missing {fragment}")
    manifest = json.loads((ROOT / "third_party/patches/patchsets.json").read_text(encoding="utf-8"))
    if PATCH.name not in resolve(manifest, "sharc-diagnostics"):
        raise SystemExit("sharc-diagnostics profile does not install the consolidated patch")
    print("PASS: consolidated runtime-filtered SHARC diagnostics patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
