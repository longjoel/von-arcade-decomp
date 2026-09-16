#!/usr/bin/env python3
"""Validate the runnable i960 object state handlers 2..9 and 11.

Compiles von/i960/recovered_state_attack_arms.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the nine entry points against a locally allocated 0x600 object plus
a config block and clip records.  The object and config live in a MAP_32BIT
mapping so the config pointer stored at object+0x6c round-trips through the
unit's 32-bit load, and the clip-record pointers stored in the config block are
also 32-bit.

Listing spans in von/build/disasm/vonj-maincpu.lst:
    state 2  0x2e450-0x2e588    state 3  0x2e590-0x2e6e4
    state 4  0x2e6f0-0x2e854    state 5  0x2e860-0x2e988
    state 6  0x2e990-0x2ea9c    state 7  0x2eaa0-0x2ebac
    state 8  0x2ebb0-0x2ecd8    state 9  0x2ece0-0x2ef80
    state 11 0x2f010-0x2f258

The attack states emit FIFO packet 31, compare the projection response cached
at object+0x7c, set +0x1b2 = 11, +0x1c4 from the cfg speed word, +0x19c = 1,
+0x1af = 3 and +0x1db = 0.  State 9 additionally selects a clip record pair and
commits +0x172 = 2 or 3; state 11 runs its three-phase clip machine and commits
+0x172 = 0/12/13 with +0x170 = 1 on exit.
"""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_attack_arms.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJECT_SIZE = 0x600
CONFIG_SIZE = 0x800
RECORD_OFFSET = 0x1000
MAP_SIZE = 0x2000

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x02
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def low_buffer(size):
    """Anonymous MAP_32BIT mapping, so a pointer fits in the u32 slot."""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_long]
    address = libc.mmap(None, size, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0)
    if not address or address == (1 << 64) - 1:
        raise OSError(ctypes.get_errno(), "mmap MAP_32BIT failed")
    if address >= (1 << 32):
        raise AssertionError("mapping above the 32-bit boundary")
    return address


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state-attack-arms.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        entry_points = {}
        for state in (2, 3, 4, 5, 6, 7, 8, 9, 11):
            function = getattr(recovered,
                               f"recovered_state_attack_{state}_run")
            function.argtypes = [ctypes.c_void_p]
            function.restype = None
            entry_points[state] = function

        base = low_buffer(MAP_SIZE)
        object_base = base
        config_base = base + 0x800
        record_base = base + RECORD_OFFSET

        def r8(address):
            return ctypes.c_uint8.from_address(address).value

        def r16(address):
            return ctypes.c_uint16.from_address(address).value

        def r32(address):
            return ctypes.c_uint32.from_address(address).value

        def w8(address, value):
            ctypes.c_uint8.from_address(address).value = value & 0xFF

        def w16(address, value):
            ctypes.c_uint16.from_address(address).value = value & 0xFFFF

        def w32(address, value):
            ctypes.c_uint32.from_address(address).value = value & 0xFFFFFFFF

        def cfg_word(offset):
            return 0xA5A50000 | offset

        def clear(address, size):
            for offset in range(0, size, 4):
                w32(address + offset, 0)

        def reset_object():
            clear(object_base, OBJECT_SIZE)
            w32(object_base + 0x6c, config_base)

        def setup_config():
            clear(config_base, CONFIG_SIZE)
            for offset in (0x59c, 0x5a0, 0x5a4):
                w32(config_base + offset, cfg_word(offset))
            # Clip records for state 9 (cfg+0x1d8/0x1dc and 0x1e0/0x1e4) and
            # state 11 (cfg+0x350/0x354, 0x358/0x35c, 0x360/0x364).
            for slot in (0x1d8, 0x1dc, 0x1e0, 0x1e4):
                for index in range(4):
                    w32(config_base + slot + 40 * index, record_base)
            w32(config_base + 0x350, 0x11110000)
            w32(config_base + 0x354, record_base)
            w32(config_base + 0x358, 0x22220000)
            w32(config_base + 0x35c, record_base)
            w32(config_base + 0x360, 0x33330000)
            w32(config_base + 0x364, record_base)

        def setup_attack(error_context):
            reset_object()
            setup_config()
            w8(object_base + 0xa0, 1)          # -> seed +0x17e = 0
            w16(object_base + 0x17a, 0)        # -> +0x1b2 = 11
            w16(object_base + 0x1db, 0xAB)     # must be cleared to 0
            w32(object_base + 0x1b4, 0)        # disable the finish bump
            w32(object_base + 0x7c, bits(1.0))  # nonnegative projection
            w32(object_base + 0x1c4, 0xDEADBEEF)
            w16(object_base + 0x1b2, 0)
            w16(record_base + 0x4, 5)
            return error_context

        # --- states 2..9: shared attack arming -------------------------------
        attack_table = [
            (2, 0x59c, None),
            (3, 0x59c, 0x5a0),
            (4, 0x5a4, None),
            (5, 0x59c, 0x5a0),
            (6, 0x59c, None),
            (7, 0x59c, None),
            (8, 0x59c, 0x5a0),
            (9, 0x59c, None),
        ]
        for state, speed, alternate in attack_table:
            setup_attack(state)
            entry_points[state](ctypes.c_void_p(object_base))
            assert r16(object_base + 0x1b2) == 11, \
                f"state {state}: +0x1b2 != 11"
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                f"state {state}: +0x1c4 = 0x{r32(object_base + 0x1c4):08x}"
            assert r16(object_base + 0x19c) == 1, \
                f"state {state}: +0x19c != 1"
            assert r8(object_base + 0x1af) == 3, \
                f"state {state}: +0x1af != 3"
            assert r8(object_base + 0x1db) == 0, \
                f"state {state}: +0x1db != 0"
            assert r32(object_base + 0x1b4) == 0

            if alternate is not None:
                setup_attack(state)
                w32(object_base + 0x64, 5)
                entry_points[state](ctypes.c_void_p(object_base))
                assert r32(object_base + 0x1c4) == cfg_word(alternate), \
                    (f"state {state}: +0x64 alternate +0x1c4 = "
                     f"0x{r32(object_base + 0x1c4):08x}")

        # --- attack retry: negative projection bumps +0x17e ------------------
        setup_attack("retry")
        w32(object_base + 0x7c, bits(-1.0))
        entry_points[2](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17e) == 1, \
            "state 2 negative response did not bump +0x17e"
        assert r32(object_base + 0x1c4) == cfg_word(0x59c)

        # --- attack finish: +0x1b4 set bumps +0x17e and zeroes +0x1c4 --------
        setup_attack("finish")
        w32(object_base + 0x1b4, 1)
        entry_points[2](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17e) == 1, \
            "state 2 finish did not bump +0x17e"
        assert r32(object_base + 0x1c4) == 0, \
            "state 2 finish did not zero +0x1c4"

        # --- state 2: +0x17a > 0x14 clears +0x1aa ----------------------------
        setup_attack("gate-1aa")
        w16(object_base + 0x17a, 0x20)
        w16(object_base + 0x1b2, 0x1234)
        entry_points[2](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x1b2) == 0x1234, \
            "state 2 wrote +0x1b2 with +0x17a != 0"
        assert r8(object_base + 0x1aa) == 0, \
            "state 2 +0x17a > 0x14 did not clear +0x1aa"
        assert r32(object_base + 0x1c4) == cfg_word(0x59c)

        # --- state 2: +0x17a <= 0x14 leaves +0x1aa ---------------------------
        setup_attack("gate-1aa-low")
        w8(object_base + 0x1aa, 0x55)
        entry_points[2](ctypes.c_void_p(object_base))
        assert r8(object_base + 0x1aa) == 0x55, \
            "state 2 +0x17a <= 0x14 cleared +0x1aa"

        # --- state 9: clip end selects +0x172 = 2 ----------------------------
        setup_attack("state9-2")
        w16(record_base + 0x4, 1)          # [0x17a] >= count-1
        w16(object_base + 0x174, 0)
        entry_points[9](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x172) == 2, \
            f"state 9 did not commit +0x172 = 2 (got {r16(object_base + 0x172)})"
        assert r16(object_base + 0x17a) == 21, \
            "state 9 did not commit +0x17a = 21"

        # --- state 9: +0x174 1/3 clip end selects +0x172 = 3 ------------------
        for selector in (1, 3):
            setup_attack(f"state9-3-{selector}")
            w16(record_base + 0x4, 1)
            w16(object_base + 0x174, selector)
            entry_points[9](ctypes.c_void_p(object_base))
            assert r16(object_base + 0x172) == 3, \
                f"state 9 +0x174={selector} did not commit +0x172 = 3"

        # --- state 9: +0x176 bit 15 takes the cfg+0x1d8/0x1dc pair -----------
        setup_attack("state9-alt")
        w16(record_base + 0x4, 1)
        w16(object_base + 0x176, 0x8000)
        entry_points[9](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x172) == 2, \
            "state 9 alternate pair did not commit +0x172 = 2"

        # --- state 11: it never writes the attack action fields --------------
        reset_object()
        setup_config()
        w32(object_base + 0x1b2, 0)
        w32(object_base + 0x1c4, 0xDEADBEEF)
        w8(object_base + 0x1af, 0x55)
        w16(object_base + 0x19c, 0x55)
        w8(object_base + 0x1db, 0xAB)
        w16(record_base + 0x4, 5)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x1b2) == 0, \
            "state 11 wrote +0x1b2"
        assert r32(object_base + 0x1c4) == 0xDEADBEEF, \
            "state 11 wrote +0x1c4"
        assert r8(object_base + 0x1af) == 0x55, "state 11 wrote +0x1af"
        assert r16(object_base + 0x19c) == 0x55, "state 11 wrote +0x19c"
        assert r8(object_base + 0x1db) == 0xAB, "state 11 wrote +0x1db"

        # --- state 11: phase 0 increment and phase-1 handoff ----------------
        reset_object()
        setup_config()
        w16(record_base + 0x4, 5)
        w16(object_base + 0x17e, 0)
        w16(object_base + 0x17a, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17a) == 1, "state 11 phase 0 did not advance"
        assert r16(object_base + 0x17e) == 0, "state 11 phase 0 changed +0x17e"

        reset_object()
        setup_config()
        w16(record_base + 0x4, 1)
        w16(object_base + 0x17e, 0)
        w16(object_base + 0x17a, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17e) == 1, \
            "state 11 phase 0 clip end did not advance +0x17e"
        assert r16(object_base + 0x17a) == 0

        # --- state 11: phase 1 increment -------------------------------------
        reset_object()
        setup_config()
        w16(record_base + 0x4, 5)
        w16(object_base + 0x17e, 1)
        w16(object_base + 0x17a, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17a) == 1, "state 11 phase 1 did not advance"
        assert r16(object_base + 0x17e) == 1, "state 11 phase 1 changed +0x17e"

        # --- state 11: phase 1 clip end commits +0x172 = 12/13 --------------
        for f180, expected in ((7, 12), (8, 13)):
            reset_object()
            setup_config()
            w16(record_base + 0x4, 0)
            w16(object_base + 0x17e, 1)
            w16(object_base + 0x180, f180)
            entry_points[11](ctypes.c_void_p(object_base))
            assert r16(object_base + 0x172) == expected, \
                (f"state 11 +0x180={f180}: +0x172 = "
                 f"{r16(object_base + 0x172)}")
            assert r16(object_base + 0x17e) == 0
            assert r16(object_base + 0x17a) == 0

        # --- state 11: sentinel gate advances to phase 2 ---------------------
        reset_object()
        setup_config()
        w16(record_base + 0x4, 0)
        w16(object_base + 0x17e, 1)
        w16(object_base + 0x180, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17e) == 2, \
            "state 11 sentinel gate did not advance to phase 2"
        assert r16(object_base + 0x17a) == 0

        # --- state 11: sentinel gate blocked by +0x13b/+0x1de bit 1 ----------
        reset_object()
        setup_config()
        w16(record_base + 0x4, 0)
        w16(object_base + 0x17e, 1)
        w8(object_base + 0x13b, 1)
        w8(object_base + 0x1de, 2)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17e) == 1, \
            "state 11 sentinel gate was not blocked"
        assert r16(object_base + 0x17a) == 0

        # --- state 11: phase 2 increment and clip end -----------------------
        reset_object()
        setup_config()
        w16(record_base + 0x4, 5)
        w16(object_base + 0x17e, 2)
        w16(object_base + 0x17a, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x17a) == 1, "state 11 phase 2 did not advance"
        assert r16(object_base + 0x172) == 0

        reset_object()
        setup_config()
        w16(record_base + 0x4, 1)
        w16(object_base + 0x17e, 2)
        w16(object_base + 0x17a, 0)
        entry_points[11](ctypes.c_void_p(object_base))
        assert r16(object_base + 0x172) == 0, \
            "state 11 phase 2 clip end did not commit +0x172 = 0"
        assert r16(object_base + 0x170) == 1, \
            "state 11 phase 2 clip end did not set +0x170 = 1"
        assert r16(object_base + 0x194) == 0
        assert r16(object_base + 0x178) == 0

    # --- source constants ---------------------------------------------------
    text = SOURCE.read_text(encoding="utf-8")
    for fragment in (
            "RECOVERED_STATE_ATTACK_CONFIG_OFFSET 0x6cU",
            "recovered_state_attack_2_run",
            "recovered_state_attack_3_run",
            "recovered_state_attack_4_run",
            "recovered_state_attack_5_run",
            "recovered_state_attack_6_run",
            "recovered_state_attack_7_run",
            "recovered_state_attack_8_run",
            "recovered_state_attack_9_run",
            "recovered_state_attack_11_run",
            "0x59cU", "0x5a0U", "0x5a4U",
            "0x1b2U", "0x1c4U", "0x19cU", "0x1afU", "0x1dbU", "0x1aaU",
            "0x7cU",
            "0x1d8U", "0x1dcU", "0x1e0U", "0x1e4U",
            "0x350U", "0x354U", "0x358U", "0x35cU", "0x360U", "0x364U",
            "0x3e4U", "0x3e8U", "0x3ecU", "0x3f0U", "0x3f4U", "0x3f8U",
            "0x3fcU",
            "0x00884000U", "0x51ab08", "0x51ab0c", "0x51ab10", "0x51ab12"):
        if fragment not in text:
            raise AssertionError(f"state-attack-arms model missing {fragment}")

    # --- listing evidence ---------------------------------------------------
    listing = LISTING.read_text(encoding="utf-8")

    def block(start, end):
        return listing[listing.index(start):listing.index(end)]

    state2 = block("   2e450:", "   2e590:")
    state3 = block("   2e590:", "   2e6f0:")
    state4 = block("   2e6f0:", "   2e860:")
    state5 = block("   2e860:", "   2e990:")
    state6 = block("   2e990:", "   2eaa0:")
    state7 = block("   2eaa0:", "   2ebb0:")
    state8 = block("   2ebb0:", "   2ece0:")
    state9 = block("   2ece0:", "   2ef90:")
    state11 = block("   2f010:", "   2f260:")

    evidence = {
        2: (state2, (
            "ldos\t0x17a(g0),g4", "cmpi\t0,g4", "bne\t0x2e47c",
            "stob\tg14,0x1db(g0)", "ldob\t0xa0(g0),g4",
            "stos\tg14,0x17e(g0)", "stos\tg3,0x17e(g0)",
            "mov\t11,g2", "stos\tg2,0x1b2(g0)", "mov\t31,g3",
            "st\tg3,0x884000", "cmpible\tg4,g2,0x2e558",
            "stob\tg14,0x1aa(g0)", "ld\t0x59c(g4),g4",
            "st\tg4,0x1c4(g0)", "stos\tg2,0x19c(g0)",
            "stob\tg3,0x1af(g0)", "ld\t0x3e4(g4),g1", "callx\t(g1)",
            "cmpibne\t0,g4,0x2e588", "st\tg14,0x1c4(r4)")),
        3: (state3, (
            "ld\t0x3e8(g4),g1", "ld\t0x64(g0),g4", "cmpi\t0,g4",
            "be\t0x2e67c", "cmpibne\t1,g4,0x2e684",
            "ld\t0x59c(g5),g5", "ld\t0x5a0(g5),g5",
            "st\tg5,0x1c4(g0)")),
        4: (state4, (
            "ld\t0x3ec(g4),g1", "ld\t0x5a4(g4),g4",
            "st\tg4,0x1c4(g0)")),
        5: (state5, (
            "ld\t0x3f0(g4),g1", "ld\t0x64(g0),g4",
            "ld\t0x59c(g5),g5", "ld\t0x5a0(g5),g5")),
        6: (state6, (
            "ld\t0x3f4(g4),g1", "ld\t0x59c(g4),g4")),
        7: (state7, (
            "ld\t0x3f8(g4),g1", "ld\t0x59c(g4),g4")),
        8: (state8, (
            "ld\t0x3fc(g4),g1", "ld\t0x64(g0),g4",
            "ld\t0x59c(g5),g5", "ld\t0x5a0(g5),g5")),
        9: (state9, (
            "lda\t0x2ef80,g14", "mov\tg14,g1", "stos\tg14,0x186(g0)",
            "stos\tg14,0x188(g0)", "shrdi\t1,g4,g4",
            "mov\t11,g2", "stos\tg2,0x1b2(g0)", "ld\t0x59c(g4),g4",
            "bbs\t15,g4,0x2ee70", "ld\t0x1e0(g7)[g4],g6",
            "ld\t0x1dc(g5)[g4*8],g4", "st\tg6,0x51ab0c",
            "st\tg4,0x51ab08", "cmpibl\tg5,g4,0x2ef40",
            "mov\t21,g2", "stos\tg2,0x17a(g0)", "mov\t3,g3",
            "stos\tg3,0x172(g0)", "cmpibne\t1,g4,0x2ef1c",
            "bx\t(g1)")),
        11: (state11, (
            "lda\t0x2f258,g14", "mov\tg14,g2", "stos\tg14,0x186(g0)",
            "shrdi\t1,g4,g4", "ld\t0x354(g4),g7", "ld\t0x350(g4),g6",
            "ld\t0x35c(g4),g7", "ld\t0x358(g4),g6",
            "ld\t0x364(g4),g7", "ld\t0x360(g4),g6",
            "cmpibne\t1,g4,0x2f1b8", "bge\t0x2f140", "cmpi\tg5,7",
            "mov\t12,g1", "cmpibne\t8,g4,0x2f188", "mov\t13,g1",
            "stos\tg1,0x172(g0)", "bbs\t1,g4,0x2f1b4", "mov\t2,g1",
            "stos\tg1,0x17e(g0)", "stos\tg1,0x170(g0)",
            "stos\tg14,0x194(g0)", "stos\tg14,0x178(g0)",
            "bx\t(g2)")),
    }
    for state, (state_block, fragments) in evidence.items():
        for fragment in fragments:
            if fragment not in state_block:
                raise AssertionError(
                    f"state {state} listing evidence missing: {fragment}")

    print("PASS: recovered state attack arms 2..9 and 11")


if __name__ == "__main__":
    main()
