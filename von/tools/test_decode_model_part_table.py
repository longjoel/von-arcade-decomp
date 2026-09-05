"""Model part table at main_data 0xbed828 decodes to the 19 trace-observed triples."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_model_part_table import decode_records, load_main_data

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PARTS = [
    (0x0009aee8, 0x0009afa8, 0x009e35b7),
    (0x0009a8fc, 0x0009a980, 0x009e2ea2),
    (0x0009aab8, 0x0009ac70, 0x009e30ab),
    (0x0009ada0, 0x0009ae5c, 0x009e343a),
    (0x0009aec4, 0x0009aee4, 0x009e3588),
    (0x00442bac, 0x0044308c, 0x008964ba),
    (0x0009a994, 0x0009aa50, 0x009e2f5d),
    (0x0009aca8, 0x0009acc8, 0x009e3300),
    (0x0045787c, 0x00457d5c, 0x008ad656),
    (0x0009accc, 0x0009ad8c, 0x009e332f),
    (0x0009a74c, 0x0009a8b8, 0x009e2cb1),
    (0x0009afbc, 0x0009b280, 0x009e36c2),
    (0x0009b7e4, 0x0009b9dc, 0x009e410d),
    (0x0009b6c8, 0x0009b7d4, 0x009e3f80),
    (0x0009ba2c, 0x0009bab0, 0x009e43a8),
    (0x0009b3d8, 0x0009b5d0, 0x009e3c34),
    (0x0009b2bc, 0x0009b3c8, 0x009e3aa7),
    (0x0009b620, 0x0009b6a4, 0x009e3ecf),
    (0x0009a558, 0x0009a700, 0x009e2a84),
]


def main():
    data = load_main_data(ROOT / "artifacts")
    base, count = 0xbed828, 66
    words = list(struct.unpack(f"<{count}I", data[base:base + count * 4]))
    entries = decode_records(words)
    parts = [entry[1:] for entry in entries if entry[0] == "part"]
    assert parts == EXPECTED_PARTS, f"part mismatch: {parts!r}"
    markers = [entry[1] for entry in entries if entry[0] == "marker"]
    assert markers == [3, 2, 4], f"marker mismatch: {markers!r}"
    print(f"PASS: model part table ({len(parts)} parts, markers {markers})")


if __name__ == "__main__":
    main()
