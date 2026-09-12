"""Stream decoder for the i960 -> SHARC geometry FIFO opcode packets.

Exercises the token-driven packet grammar (transform and sequencer programs,
optional trailing decrement, and resync) directly on synthetic write streams.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_fifo_program import StreamDecoder, signed16


def words(seq, t=1.0, pc=0x8DE14, r6=0, g0=0, g2=0x5046D0):
    return [(t, pc, w, r6, g0, g2) for w in seq]


def run(stream):
    dec = StreamDecoder()
    out = []
    for (t, pc, data, r6, g0, g2) in stream:
        pkt = dec.feed(t, pc, data, r6, g0, g2)
        if pkt:
            out.append(pkt)
    tail = dec.flush()
    if tail:
        out.append(tail)
    return dec, out


def test_transform_packet():
    seq = [5, 47, 0x1111, 0x2222, 0x3333, 22, 0x4444, 21, 0x5555, 20, 0x6666, 58, 0x7777, 6]
    dec, out = run(words(seq))
    assert dec.packets == 1 and dec.resync == 0, (dec.packets, dec.resync)
    p = out[0]
    assert p["program"] == "transform"
    assert (p["off0"], p["off1"], p["off2"]) == (0x1111, 0x2222, 0x3333)
    assert (p["rotA"], p["rotB"], p["rotC"]) == (0x4444, 0x5555, 0x6666)
    assert p["readback"] == 0x7777
    print("ok: transform-packet")


def test_optional_trailing_decrement():
    seq = [5, 47, 1, 2, 3, 22, 4, 21, 5, 20, 6, 58, 7]  # no trailing 6
    dec, out = run(words(seq))
    assert dec.packets == 1 and out[0]["readback"] == 7, out
    print("ok: optional-trailing-decrement")


def test_two_packets_stride():
    seq = ([5, 47, 1, 2, 3, 22, 4, 21, 5, 20, 6, 58, 7, 6] +
           [5, 47, 8, 9, 10, 22, 11, 21, 12, 20, 13, 58, 14, 6])
    dec, out = run(words(seq))
    assert dec.packets == 2, out
    assert out[1]["off0"] == 8 and out[1]["readback"] == 14
    print("ok: two-packets")


def test_sequencer_packet():
    seq = [5, 18, 0xA, 0xB, 0xC, 21, 0xD, 19, 0xE, 0xF, 0x10, 6]
    dec, out = run(words(seq))
    assert dec.packets == 1 and out[0]["program"] == "sequencer", out
    assert (out[0]["a"], out[0]["b"], out[0]["c"], out[0]["d"]) == (0xA, 0xB, 0xC, 0xD)
    print("ok: sequencer-packet")


def test_resync_on_bad_opcode():
    # second opcode must be 47 or 18; garbage then a full packet must recover.
    seq = [5, 99, 5, 47, 1, 2, 3, 22, 4, 21, 5, 20, 6, 58, 7, 6]
    dec, out = run(words(seq))
    assert dec.packets == 1 and dec.resync == 0, (dec.packets, dec.resync)
    assert out[0]["off0"] == 1
    print("ok: resync-after-bad-opcode")


def test_signed16():
    assert signed16(0xFFFF) == -1
    assert signed16(0x7FFF) == 0x7FFF
    assert signed16(0x8000) == -0x8000
    print("ok: signed16")


def main():
    test_transform_packet()
    test_optional_trailing_decrement()
    test_two_packets_stride()
    test_sequencer_packet()
    test_resync_on_bad_opcode()
    test_signed16()
    print("PASS: decode_fifo_program")


if __name__ == "__main__":
    main()
