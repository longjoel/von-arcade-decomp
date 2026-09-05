#!/usr/bin/env python3
"""Extract and validate the two ROM-backed coprocessor upload windows.

The i960 upload routines read these ranges directly from the assembled ROM
maps.  Keeping extraction here (rather than embedding guessed C arrays) makes
the source-window contract reproducible and gives later runtime work a stable
fixture to consume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SHARC_OFFSET = 0x16B58C
SHARC_WORDS = 0x2B1E
GEOMETRY_OFFSET = 0x00FC6290
GEOMETRY_WORDS = 0x247C


def assemble_main_data(rom_dir: Path) -> bytes:
    """Assemble the 32-bit-wide main_data ROM window in bus order."""
    image = bytearray(0x1000000)
    for name_a, name_b, base in (
        ("mpr-18648.11", "mpr-18649.12", 0x000000),
        ("mpr-18650.9", "mpr-18651.10", 0x800000),
    ):
        low = (rom_dir / name_a).read_bytes()
        high = (rom_dir / name_b).read_bytes()
        if len(low) != len(high):
            raise ValueError(f"ROM pair size mismatch: {name_a}, {name_b}")
        for index in range(0, len(low), 2):
            target = base + index * 2
            image[target:target + 2] = low[index:index + 2]
            image[target + 2:target + 4] = high[index:index + 2]
    return bytes(image)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def extract(rom_dir: Path, maincpu: Path) -> dict[str, object]:
    cpu = maincpu.read_bytes()
    sharc_end = SHARC_OFFSET + SHARC_WORDS * 2
    if sharc_end > len(cpu):
        raise ValueError(f"maincpu is too short for SHARC window: 0x{sharc_end:x}")
    main_data = assemble_main_data(rom_dir)
    geometry_end = GEOMETRY_OFFSET + GEOMETRY_WORDS * 2
    if geometry_end > len(main_data):
        raise ValueError(f"main_data is too short for geometry window: 0x{geometry_end:x}")
    sharc = cpu[SHARC_OFFSET:sharc_end]
    geometry = main_data[GEOMETRY_OFFSET:geometry_end]
    return {
        "sharc": {"offset": SHARC_OFFSET, "words": SHARC_WORDS,
                  "bytes": len(sharc), "sha256": _sha256(sharc)},
        "geometry": {"offset": GEOMETRY_OFFSET, "words": GEOMETRY_WORDS,
                      "bytes": len(geometry), "sha256": _sha256(geometry)},
        "payloads": {"sharc": sharc, "geometry": geometry},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--maincpu", type=Path,
                        default=Path("von/build/disasm/vonj-maincpu.bin"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/coprocessor-sources"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("von/build/disasm/coprocessor-sources.json"))
    args = parser.parse_args()
    result = extract(args.rom_dir, args.maincpu)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payloads = result.pop("payloads")
    assert isinstance(payloads, dict)
    for name, payload in payloads.items():
        (args.output_dir / f"{name}.bin").write_bytes(payload)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name in ("sharc", "geometry"):
        info = result[name]
        print(f"{name}: {info['words']} words, sha256={info['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
