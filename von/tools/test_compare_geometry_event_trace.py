#!/usr/bin/env python3
import tempfile
from pathlib import Path

from compare_geometry_event_prefix import compare


def test_ordered_prefix_matches_without_timestamps():
    original = "\n".join([
        "[:] vonj_geometry_matrix: time=16.2 m=1,0,0,0,1,0,0,0,1 t=0,0,0",
        "[:] vonj_geometry_object: time=16.2 tpa=1 tha=2 oba=0084553f count=1 mode=3 source=polygon-rom opcode=00800101",
    ])
    reconstructed = original.replace("time=16.2", "time=33.9")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        left = root / "original.log"
        right = root / "reconstructed.log"
        left.write_text(original + "\n")
        right.write_text(reconstructed + "\n")
        count, error = compare(left, right, 2)
    assert count == 2
    assert error is None


if __name__ == "__main__":
    test_ordered_prefix_matches_without_timestamps()
