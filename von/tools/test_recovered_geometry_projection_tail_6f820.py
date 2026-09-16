#!/usr/bin/env python3
import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_projection_tail_6f820.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

MAP_BANK_SIZE = 4096
SENTINEL = 0x47C34F80
CALLBACK_TABLE = 0x0006EB70


class TailState(ctypes.Structure):
    _fields_ = [
        ("cell", ctypes.c_uint32),
        ("map_byte", ctypes.c_uint32),
        ("quadrant", ctypes.c_uint32),
        ("callback_address", ctypes.c_uint32),
        ("dispatched", ctypes.c_int),
        ("route", ctypes.c_int),
        ("output", ctypes.c_uint32),
    ]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "projection_tail.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        dll = ctypes.CDLL(str(library))

        cell = dll.recovered_geometry_projection_tail_cell
        cell.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cell.restype = ctypes.c_int

        map_byte = dll.recovered_geometry_projection_tail_map_byte
        map_byte.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ]
        map_byte.restype = ctypes.c_int

        gate = dll.recovered_geometry_projection_tail_gate
        gate.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        gate.restype = ctypes.c_int

        callback_offset = dll.recovered_geometry_projection_tail_callback_offset
        callback_offset.argtypes = [ctypes.c_uint32]
        callback_offset.restype = ctypes.c_uint32
        callback_address = dll.recovered_geometry_projection_tail_callback_address
        callback_address.argtypes = [ctypes.c_uint32]
        callback_address.restype = ctypes.c_uint32

        mask_output = dll.recovered_geometry_projection_tail_mask_output
        mask_output.argtypes = [ctypes.c_uint16, ctypes.c_uint32]
        mask_output.restype = ctypes.c_uint32

        route = dll.recovered_geometry_projection_tail_route
        route.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_int

        reject = dll.recovered_geometry_projection_tail_reject
        reject.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        reject.restype = ctypes.c_uint32

        tail = dll.recovered_geometry_projection_tail_6f820
        tail.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32,
            ctypes.POINTER(TailState),
        ]
        tail.restype = ctypes.c_int

        value = ctypes.c_uint32(0xdeadbeef)

        # 0x6f82c-0x6f834: ((z/40) << 5) + (x/40) over the 640.0-biased quotients.
        assert cell(bits(0.0), bits(0.0), ctypes.byref(value)) == 1
        assert value.value == 528  # (16 << 5) + 16
        assert cell(bits(40.0), bits(80.0), ctypes.byref(value)) == 1
        assert value.value == 593  # (18 << 5) + 17
        assert cell(bits(-640.0), bits(-640.0), ctypes.byref(value)) == 1
        assert value.value == 0
        assert cell(bits(640.0), bits(640.0), ctypes.byref(value)) == 1
        assert value.value == 1056  # (32 << 5) + 32

        bank = (ctypes.c_uint8 * MAP_BANK_SIZE)()
        bank[528] = 0xAB
        bank[593] = 0x60
        bank[1056] = 0xFF
        assert map_byte(bank, 528, ctypes.byref(value)) == 1
        assert value.value == 0xAB
        assert map_byte(bank, 1056, ctypes.byref(value)) == 1
        assert value.value == 0xFF
        assert map_byte(None, 0, ctypes.byref(value)) == 0

        # 0x6f838-0x6f848: reject 0xff and entries without map bit 5.
        quadrant = ctypes.c_uint32(99)
        for byte in range(256):
            eligible = bool(byte != 0xFF and (byte & 0x20))
            assert gate(byte, ctypes.byref(quadrant)) == eligible
            if eligible:
                assert quadrant.value == (byte - 0x20) >> 6
        for byte, expected in ((0x20, 0), (0x3F, 0), (0x60, 1), (0xA0, 2), (0xE0, 3)):
            assert gate(byte, ctypes.byref(quadrant)) == 1
            assert quadrant.value == expected
        assert gate(0xFF, ctypes.byref(quadrant)) == 0
        assert gate(0x1F, ctypes.byref(quadrant)) == 0

        # 0x6f84c-0x6f864: table entries are 24 bytes at 0x6eb70.
        assert callback_offset(0) == 0
        assert callback_offset(1) == 24
        assert callback_offset(3) == 72
        assert callback_address(2) == CALLBACK_TABLE + 48

        # 0x6f8b8-0x6f8d4: extract the two-bit field and place it at bit 14.
        assert mask_output(0xC000, 15) == 0xFFFFC000
        assert mask_output(0x4000, 15) == 0x00004000
        assert mask_output(0x8000, 15) == 0xFFFF8000
        assert mask_output(0x0001, 1) == 0x00004000
        assert mask_output(0x000C, 3) == 0x0000C000
        assert mask_output(0x0003, 3) == 0
        assert mask_output(0x0001, 3) == 0
        assert mask_output(0xFFFF, 17) == 0  # shift 14 - 16 underflows to zero
        assert mask_output(0xFFFF, 33) == 0  # slot 32 is out of range

        # 0x6f87c-0x6f8fc: >= 1000.0 publishes map << 8; the bl target selects
        # the special mask, the general mask, or the runtime fallback.
        out = ctypes.c_uint32(0xdeadbeef)
        assert route(bits(2000.0), 0xAB, 0x1000, 0, 15,
                     0xC000, 0x4000, 0, ctypes.byref(out)) == 0
        assert out.value == 0xAB00
        assert route(bits(1000.0), 0x01, 0x1000, 0, 15,
                     0xC000, 0x4000, 0, ctypes.byref(out)) == 0
        assert out.value == 0x0100
        assert route(bits(999.0), 0xAB, 0x503AD0, 0, 15,
                     0xC000, 0x4000, 0, ctypes.byref(out)) == 1
        assert out.value == 0xFFFFC000
        assert route(bits(4.0), 0xAB, 0x1000, 0, 15,
                     0xC000, 0x4000, 0, ctypes.byref(out)) == 2
        assert out.value == 0x00004000
        assert route(bits(4.0), 0xAB, 0x1000, 1, 15,
                     0xC000, 0x4000, 0xDEADBEEF, ctypes.byref(out)) == 3
        assert out.value == 0xDEADBEEF

        # 0x6f74c: sibling reject route publishes the 99999.0 sentinel and *out=0.
        assert reject(ctypes.byref(out)) == SENTINEL
        assert out.value == 0

        # Whole tail: cell 593 -> map 0x60 -> quadrant 1 -> callback 0x6eb70+48.
        state = TailState()
        result_bits = bits(2000.0)
        assert tail(bits(40.0), bits(80.0),
                    ctypes.cast(bank, ctypes.POINTER(ctypes.c_uint8)), 2,
                    0x1000, 0, 15, result_bits, 0xC000, 0x4000, 0,
                    ctypes.byref(state)) == 1
        assert (state.cell, state.map_byte, state.quadrant) == (593, 0x60, 1)
        assert state.dispatched == 1
        assert state.callback_address == CALLBACK_TABLE + 48
        assert state.route == 0
        assert state.output == 0x6000

        state = TailState()
        assert tail(bits(40.0), bits(80.0),
                    ctypes.cast(bank, ctypes.POINTER(ctypes.c_uint8)), 2,
                    0x503AD0, 0, 15, bits(4.0), 0x8000, 0x4000, 0,
                    ctypes.byref(state)) == 1
        assert state.route == 1
        assert state.output == 0xFFFF8000
        assert tail(bits(0.0), bits(0.0), None, 0, 0x1000, 0, 15, bits(4.0),
                    0, 0, 0, ctypes.byref(state)) == 0

        listing = LISTING.read_text(encoding="utf-8")
        block = listing[listing.index("   6f820:"):listing.index("   6f900:")]
        packet_core = listing[listing.index("   6f6f0:"):listing.index("   6f820:")]
        for evidence in ("lda\t0x47c34f80,g0", "stos\tg14,(g3)"):
            if evidence not in packet_core:
                raise AssertionError(f"projection reject evidence missing: {evidence}")

        for evidence in (
                "ld\t0x51bb20,g0", "st\tr8,0x40(fp)", "shlo\t5,g13,g4",
                "addo\tr4,g4,g4", "ldob\t(g0)[g4],g4", "lda\t0xff,r9",
                "cmpibe\tg5,r9,0x6f87c", "bbc\t5,r4,0x6f87c",
                "ld\t0x5770f0,g4", "ld\t0x6eb70[g4*8],g13", "shri\t6,g4,g2",
                "callx\t(g13)", "ld\t0x40(fp),g0", "movr\tg0,fp0", "mov\t0,r8",
                "lda\t0x408f4000,r9", "cmprl\tfp0,r8", "bl\t0x6f8a4",
                "shlo\t8,r4,g4", "stos\tg4,(r6)", "lda\t0x503ad0,r9",
                "ldos\t0x562c80,g4", "subo\t1,r5,g5", "clrbit\t0,g5,g5",
                "subo\tg5,14,g5", "shri\t16,g4,g4", "ld\t0x503a7c,g4",
                "ldos\t0x562c84,g4", "stos\tg14,(r6)"):
            if evidence not in block:
                raise AssertionError(f"projection tail listing evidence missing: {evidence}")

    print("recovered geometry projection tail 6f820 vectors: ok")


if __name__ == "__main__":
    main()
