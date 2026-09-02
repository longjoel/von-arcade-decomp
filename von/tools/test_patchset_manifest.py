#!/usr/bin/env python3
"""Contract checks for ordered focused MAME patch profiles."""

from __future__ import annotations

import json
from pathlib import Path

from patchset_manifest import resolve


def main() -> int:
    manifest = json.loads(Path("third_party/patches/patchsets.json").read_text(encoding="utf-8"))
    debug = resolve(manifest, "debug")
    assert debug == [item for item in manifest["order"] if item in set(debug)]
    for profile in ("core", "link", "geometry", "texture", "sharc-diagnostics", "sharc-precision"):
        patches = resolve(manifest, profile)
        assert patches and patches[0] == "0001-von-mame-support.patch"
    assert set(resolve(manifest, "sharc-diagnostics")).isdisjoint({
        "0028-von-sharc-drc-float-special-cases.patch",
        "0031-von-sharc-40bit-header.patch",
        "0032-von-sharc-40bit-register-seam.patch",
        "0033-von-sharc-drc-compound-abs-special-cases.patch",
    })
    assert resolve(manifest, "all") == debug
    print("PASS: ordered focused patch profiles and explicit debug union")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
