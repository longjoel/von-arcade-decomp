#!/usr/bin/env python3
"""Resolve ordered MAME patch profiles from the tracked patchset manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def resolve(manifest: dict, profile: str) -> list[str]:
    profile = manifest.get("aliases", {}).get(profile, profile)
    profiles = manifest.get("profiles", {})
    if profile not in profiles:
        raise ValueError(f"unknown patch profile {profile!r}; expected {', '.join(sorted(profiles))}")
    selected: set[str] = set()
    active: set[str] = set()

    def visit(name: str) -> None:
        if name in active:
            raise ValueError(f"cyclic patch profile involving {name}")
        if name in profiles:
            active.add(name)
            for child in profiles[name]:
                visit(child)
            active.remove(name)
        else:
            selected.add(name)

    visit(profile)
    order = manifest.get("order", [])
    unknown = selected - set(order)
    if unknown:
        raise ValueError(f"patches absent from order: {', '.join(sorted(unknown))}")
    return [name for name in order if name in selected]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--manifest", type=Path, default=Path("third_party/patches/patchsets.json"))
    parser.add_argument("--paths", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    try:
        patches = resolve(manifest, args.profile)
    except ValueError as error:
        raise SystemExit(f"error: {error}")
    base = args.manifest.parent
    for patch in patches:
        path = base / patch
        if not path.is_file():
            raise SystemExit(f"error: missing patch {path}")
        print(path if args.paths else patch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
