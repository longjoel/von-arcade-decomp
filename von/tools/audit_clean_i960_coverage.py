#!/usr/bin/env python3
"""Reject a clean-image run that executes outside generated i960 code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcs", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    generated_end = int(manifest["generated_code_bytes"])
    pcs = {
        int(line, 16)
        for raw in args.pcs.read_text(encoding="ascii").splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    }
    escaped = sorted(pc for pc in pcs if pc >= generated_end)
    print(
        f"Clean i960 PC audit: {len(pcs)} visited instructions; "
        f"generated range 0x00000000-0x{generated_end:08x}"
    )
    if escaped:
        sample = ", ".join(f"0x{pc:08x}" for pc in escaped[:16])
        raise SystemExit(
            f"error: {len(escaped)} PCs escaped generated code; first: {sample}"
        )
    print("PASS: every visited PC belongs to generated code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
