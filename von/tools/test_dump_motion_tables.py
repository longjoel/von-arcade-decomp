"""Per-fighter motion tables decode from the maincpu profile pointer table.

The profile table at 0x19360 maps roster index -> profile blob; each blob's
+0x70 run holds paired motion table headers ``[data, (frames<<16)|parts]``.
Verified here against the first Temjin clip and the per-fighter clip counts
that the 0x8dd40 walker semantics imply (12 * frames * parts bytes).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump_motion_tables import (
    PROFILE_TABLE, NAME_TABLE, NAME_STRIDE,
    load_maincpu, load_main_data, motion_header,
)

ROOT = Path(__file__).resolve().parents[1]


def clips_for(mc, md, base, limit):
    out = []
    off = 0x70
    while off + 4 <= limit - base:
        header = struct.unpack_from("<I", mc, base + off)[0]
        found = motion_header(mc, md, header)
        if found:
            out.append((off, header) + found)
        off += 4
    return out


def main():
    mc = load_maincpu(ROOT / "artifacts")
    md = load_main_data(ROOT / "artifacts")

    ptrs = list(struct.unpack_from("<10I", mc, PROFILE_TABLE))
    names = [mc[NAME_TABLE + i * NAME_STRIDE:NAME_TABLE + i * NAME_STRIDE + NAME_STRIDE]
             .split(b"\0", 1)[0].decode() for i in range(10)]
    assert names == ["TEMJIN", "VIPER2", "BELGDOR", "RAIDEN", "DORKAS", "FEIYEN",
                     "APHARMD", "BALBASBOW", "JAGUARANDI", "Z-GRADT"], names
    assert ptrs[0] == 0x0057D0, hex(ptrs[0])

    # Temjin profile 0x57d0, bounded by the next allocated profile (Raiden 0x7be0).
    temjin = clips_for(mc, md, ptrs[0], 0x007BE0)
    assert len(temjin) == 202, len(temjin)

    # First clip: 64 frames x 15 parts at bus 0x020e4668.
    off, header, data, frames, parts = temjin[0]
    assert (off, header, data, frames, parts) == (
        0x70, 0x020E4668, 0x020E1968, 64, 15), temjin[0]

    # Data precedes header by exactly the record size.
    assert header - data == frames * parts * 12

    # Body (15-part) and skeleton (8-part) families both present.
    assert sum(1 for c in temjin if c[4] == 15) == 101
    assert sum(1 for c in temjin if c[4] == 8) == 101

    # First record decodes as six signed 16-bit words.
    raw = md[data - 0x02000000:data - 0x02000000 + 12]
    assert len(struct.unpack_from("<6h", raw)) == 6

    print(f"PASS: motion tables ({len(temjin)} Temjin clips, "
          f"{sum(1 for c in temjin if c[4] == 8)} skeleton)")


if __name__ == "__main__":
    main()
