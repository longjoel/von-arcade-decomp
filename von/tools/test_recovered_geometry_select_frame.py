#!/usr/bin/env python3
"""Guard the evidence-backed 40-slot player-select geometry fixture."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_select_frame.inc"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    matrix = re.search(r"select_matrices\[(\d+)\]\[12\]", text)
    objects = re.search(r"select_objects\[(\d+)\]\[4\]", text)
    mapping = re.search(r"select_object_matrix\[(\d+)\]", text)
    if not (matrix and objects and mapping):
        raise SystemExit("select-frame fixture declarations are incomplete")
    counts = tuple(int(match.group(1)) for match in (matrix, objects, mapping))
    if counts != (37, 40, 40):
        raise SystemExit(f"unexpected select-frame fixture sizes: {counts}")
    if "0x0084553fU" not in text or "0x00a663abU" not in text:
        raise SystemExit("select-frame fixture lost its first or last traced object")
    if "{0,1,1,1,2,2,3" not in text:
        raise SystemExit("select-frame matrix/object event mapping changed")
    print("PASS: 37 select matrices and 40 ordered player-model objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
