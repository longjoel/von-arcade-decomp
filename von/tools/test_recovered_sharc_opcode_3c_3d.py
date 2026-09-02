#!/usr/bin/env python3
"""Validate the reusable C models for SHARC opcodes 0x3c and 0x3d."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    sources = [
        ROOT / "von/i960/recovered_sharc_opcode_3c.c",
        ROOT / "von/i960/recovered_sharc_opcode_3d.c",
        ROOT / "von/i960/recovered_sharc_opcode_2b.c",
        ROOT / "von/i960/recovered_sharc_opcode_2d.c",
        ROOT / "von/i960/recovered_sharc_opcode_4d_decision.c",
        ROOT / "von/i960/recovered_sharc_opcode_4d_horizontal_seed.c",
        ROOT / "von/i960/recovered_sharc_opcode_4d_refined_bound.c",
        ROOT / "von/i960/recovered_sharc_opcode_3e.c",
        ROOT / "von/i960/recovered_sharc_opcode_3f.c",
        ROOT / "von/i960/recovered_sharc_opcode_3e.c",
        ROOT / "von/i960/recovered_sharc_opcode_3f.c",
        ROOT / "von/i960/recovered_sharc_opcode_43.c",
        ROOT / "von/i960/recovered_sharc_opcode_45.c",
        ROOT / "von/i960/recovered_sharc_opcode_47.c",
        ROOT / "von/i960/recovered_sharc_opcode_49.c",
        ROOT / "von/i960/recovered_sharc_opcode_4a.c",
        ROOT / "von/i960/recovered_sharc_opcode_4c.c",
        ROOT / "von/i960/recovered_sharc_opcode_4b.c",
        ROOT / "von/i960/recovered_sharc_opcode_25.c",
        ROOT / "von/i960/recovered_sharc_opcode_27.c",
        ROOT / "von/i960/recovered_sharc_opcode_29.c",
        ROOT / "von/i960/recovered_sharc_opcode_2a.c",
        ROOT / "von/i960/recovered_sharc_opcode_2c.c",
        ROOT / "von/i960/recovered_sharc_opcode_2e.c",
        ROOT / "von/i960/recovered_sharc_opcode_30.c",
        ROOT / "von/i960/recovered_sharc_opcode_31.c",
        ROOT / "von/i960/recovered_sharc_opcode_36.c",
        ROOT / "von/i960/recovered_sharc_opcode_37.c",
        ROOT / "von/i960/recovered_sharc_opcode_38.c",
        ROOT / "von/i960/recovered_sharc_opcode_42.c",
        ROOT / "von/i960/recovered_sharc_opcode_35.c",
        ROOT / "von/i960/recovered_sharc_opcode_32.c",
        ROOT / "von/i960/recovered_sharc_opcode_33.c",
        ROOT / "von/i960/recovered_sharc_opcode_34.c",
        ROOT / "von/i960/recovered_sharc_opcode_40.c",
        ROOT / "von/i960/recovered_sharc_opcode_41.c",
        ROOT / "von/i960/recovered_sharc_opcode_44.c",
        ROOT / "von/i960/recovered_sharc_opcode_46.c",
        ROOT / "von/i960/recovered_sharc_opcode_48.c",
        ROOT / "von/i960/recovered_sharc_opcode_39.c",
        ROOT / "von/i960/recovered_sharc_opcode_3a.c",
        ROOT / "von/i960/recovered_sharc_opcode_3b.c",
        ROOT / "von/i960/recovered_sharc_opcode_3d.c",
    ]
    with tempfile.TemporaryDirectory() as directory:
        for source in sources:
            object_file = Path(directory) / (source.stem + ".o")
            result = subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                 str(source), "-o", str(object_file)],
                capture_output=True, text=True,
            )
            if result.returncode:
                raise SystemExit(f"{source.name} failed to compile:\n{result.stderr}")
    print("PASS: reusable SHARC opcode-0x3c/0x3d C models compile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
