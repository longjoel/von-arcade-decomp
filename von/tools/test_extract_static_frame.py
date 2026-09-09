#!/usr/bin/env python3
"""Static MAME-free frame extraction over synthetic ROM fixtures.

Builds a two-part main_data table from fake chip pairs plus a tiny
geometry ROM holding one triangle strip per OBA, runs
extract_static_frame.py with no trace input, and checks the glTF
meshes, node order/names, and both pose modes. Real-ROM verification
(19/19 per-OBA triangle soups identical to the traced bed828 asset)
is recorded in the ledger; this test keeps the tool ROM-free.
"""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


TOOL = Path(__file__).resolve().parent / "extract_static_frame.py"


def triangle_words(verts):
    """One-triangle strip: p0, p1, attr(link 0), skip, p2, skip, end."""
    words = []
    words.extend(struct.unpack("<III", struct.pack("<3f", *verts[0])))
    words.extend(struct.unpack("<III", struct.pack("<3f", *verts[1])))
    words.append(0x00000002)
    words.extend((0xDEAD0001, 0xDEAD0002, 0xDEAD0003))
    words.extend(struct.unpack("<III", struct.pack("<3f", *verts[2])))
    words.extend((0xDEAD0004, 0xDEAD0005, 0xDEAD0006))
    words.append(0x00000000)
    return words


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-static-frame-") as directory:
        root = Path(directory)
        chips = root / "chips"
        chips.mkdir()
        # Interleaved chip pairs: image word = low halfword + high halfword.
        table = [0x11111111, 0x22222222, 0x00000010,
                 0, 0, 7,
                 0x33333333, 0x44444444, 0x00000040]
        table_bytes = struct.pack(f"<{len(table)}I", *table)
        half = len(table_bytes) // 2
        low = bytearray()
        high = bytearray()
        for index in range(0, len(table_bytes), 4):
            low.extend(table_bytes[index:index + 2])
            high.extend(table_bytes[index + 2:index + 4])
        assert len(low) == len(high) == half
        (chips / "mpr-18648.11").write_bytes(bytes(low))
        (chips / "mpr-18649.12").write_bytes(bytes(high))
        (chips / "mpr-18650.9").write_bytes(b"")
        (chips / "mpr-18651.10").write_bytes(b"")

        tri_a = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        tri_b = [(4.0, 0.0, 0.0), (0.0, 5.0, 0.0), (0.0, 0.0, 6.0)]
        geo = bytearray(0x200)
        for oba, tri in ((0x10, tri_a), (0x40, tri_b)):
            words = triangle_words(tri)
            raw = struct.pack(f"<{len(words)}I", *words)
            geo[oba * 4:oba * 4 + len(raw)] = raw
        rom = root / "geometry-rom.bin"
        rom.write_bytes(bytes(geo))

        for pose, spread in (("identity", 0.0), ("distribute", 10.0)):
            output = root / f"static_{pose}.gltf"
            subprocess.run(
                [sys.executable, str(TOOL), "--rom", rom.name,
                 "--rom-dir", chips.name, "--offset", "0x0",
                 "--words", str(len(table)), "--pose", pose,
                 "--spread", str(spread), "--output", output.name,
                 "--root", str(root)],
                check=True, cwd=root, capture_output=True, text=True,
            )
            document = json.loads(output.read_text())
            assert document["extras"]["parts"] == 2
            assert document["extras"]["unique_meshes"] == 2
            assert [node["name"] for node in document["nodes"]] == [
                "slot_000_oba_00000010", "slot_001_oba_00000040"]
            assert [node["translation"] for node in document["nodes"]] == [
                [0.0, 0.0, 0.0], [spread if pose == "distribute" else 0.0, 0.0, 0.0]]
            blob = document["buffers"][0]["uri"]
            assert blob.startswith("data:application/octet-stream;base64,")
            first = document["meshes"][0]
            assert first["name"] == "oba_00000010"
            assert first["primitives"][0]["attributes"]["POSITION"] == 0

        # Vertices survive the round trip exactly (identity pose).
        import base64
        document = json.loads((root / "static_identity.gltf").read_text())
        blob = base64.b64decode(document["buffers"][0]["uri"].split(",", 1)[1])
        view = document["bufferViews"][0]
        verts = struct.unpack("<9f", blob[view["byteOffset"]:view["byteOffset"] + 36])
        # parse_mesh emits (p0, p1, p2, p3=p2) for the triangle record.
        assert list(verts) == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                               0.0, 0.0, 1.0]

        # Root containment is enforced.
        outside = root.parent / "outside.gltf"
        if outside.exists():
            outside.unlink()
        result = subprocess.run(
            [sys.executable, str(TOOL), "--rom", rom.name,
             "--rom-dir", chips.name, "--offset", "0x0", "--words", "9",
             "--output", "../outside.gltf", "--root", str(root)],
            capture_output=True, text=True)
        assert result.returncode != 0
        assert not outside.exists()
        print("PASS: static MAME-free frame extraction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
