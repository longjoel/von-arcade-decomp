#!/usr/bin/env python3
"""Verify the recovered action -> host-sound bindings.

The command words are extracted from the original i960 maincpu image at the
ten profile pointers in the 0x19360 roster table, offsets +0x488..+0x4a4.
The golden table below is that extraction; the structural checks pin the
selector rule (object+0x68: zero takes the "_a" field, nonzero the "_b"
field) and the confirmed action wrappers (jump, locomotion enter/exit,
reaction gate). See von/i960/recovered_audio_actions.c.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_audio_actions.c"

# (reaction_a, reaction_b, jump_a, jump_b, move_a, stop_a, move_b, stop_b)
PROFILES: list[tuple[int, ...]] = [
    (0x1200, 0x1228, 0x1117, 0x113B, 0x1108, 0x1123, 0x112C, 0x1147),
    (0x120A, 0x1232, 0x1118, 0x113C, 0x1108, 0x1123, 0x112C, 0x1147),
    (0x120D, 0x1235, 0x1119, 0x113D, 0x1107, 0x1122, 0x112B, 0x1146),
    (0x1206, 0x122E, 0x1118, 0x113C, 0x1107, 0x1122, 0x112B, 0x1146),
    (0x1216, 0x123E, 0x1119, 0x113D, 0x1107, 0x1122, 0x112B, 0x1146),
    (0x121D, 0x121D, 0x1118, 0x113C, 0x1108, 0x1123, 0x112C, 0x1147),
    (0x1211, 0x1239, 0x1117, 0x113B, 0x1108, 0x1123, 0x112C, 0x1147),
    (0x1218, 0x1240, 0x1119, 0x113D, 0x1107, 0x1122, 0x112B, 0x1146),
    (0x1220, 0x1220, 0x1119, 0x113D, 0x1107, 0x1122, 0x112B, 0x1146),
    (0x1200, 0x1228, 0x1119, 0x113D, 0x1107, 0x1122, 0x112B, 0x1146),
]

CFG_WEAPON_A = 0x488
CFG_JUMP_A = 0x490
CFG_DASH_A = 0x498
CFG_STOP_A = 0x49C

# Action wrappers read these fields; confirmed call sites in the listing.
WRAPPERS = {
    "recovered_audio_jump_command": (2, 3),
    "recovered_audio_dash_command": (4, 6),
    "recovered_audio_move_exit_command": (5, 7),
    "recovered_audio_weapon_command": (0, 1),
}


def load_recovered():
    directory = tempfile.TemporaryDirectory(prefix="von-audio-actions-")
    library = Path(directory.name) / "audio-actions.so"
    subprocess.run(
        [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
         str(SOURCE), "-o", str(library)],
        check=True,
    )
    recovered = ctypes.CDLL(str(library))
    recovered.recovered_audio_profile_count.restype = ctypes.c_uint32
    recovered.recovered_audio_profile_valid.argtypes = [ctypes.c_uint32]
    recovered.recovered_audio_profile_valid.restype = ctypes.c_uint32
    recovered.recovered_audio_profile_sound.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint16)]
    recovered.recovered_audio_profile_sound.restype = ctypes.c_uint32
    for name in WRAPPERS:
        fn = getattr(recovered, name)
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint16)]
        fn.restype = ctypes.c_uint32
    return directory, recovered


def main() -> int:
    directory, recovered = load_recovered()
    try:
        assert recovered.recovered_audio_profile_count() == len(PROFILES)
        for profile in range(len(PROFILES)):
            assert recovered.recovered_audio_profile_valid(profile) == 1
        for bad in (10, 11, 0xFFFFFFFF):
            assert recovered.recovered_audio_profile_valid(bad) == 0, bad
            out = ctypes.c_uint16()
            assert recovered.recovered_audio_profile_sound(
                bad, CFG_JUMP_A, 0, ctypes.byref(out)) == 0

        # Every profile/field/selector combination must match the golden
        # table, with selector zero taking the _a field and nonzero the _b
        # field. Odd field codes are not pair bases and must be rejected.
        pair_indices = ((CFG_WEAPON_A, 0, 1), (CFG_JUMP_A, 2, 3),
                        (CFG_DASH_A, 4, 6), (CFG_STOP_A, 5, 7))
        for profile, golden in enumerate(PROFILES):
            for base, index_a, index_b in pair_indices:
                for selector, expected in ((0, golden[index_a]),
                                           (1, golden[index_b]),
                                           (7, golden[index_b])):
                    out = ctypes.c_uint16()
                    ok = recovered.recovered_audio_profile_sound(
                        profile, base, selector, ctypes.byref(out))
                    assert ok == 1, (profile, hex(base), selector)
                    assert out.value == expected, (
                        profile, hex(base), selector, hex(out.value))
            out = ctypes.c_uint16()
            assert recovered.recovered_audio_profile_sound(
                profile, CFG_WEAPON_A | 1, 0, ctypes.byref(out)) == 0

        # The four confirmed action wrappers delegate to their pair.
        for name, (index_a, index_b) in WRAPPERS.items():
            fn = getattr(recovered, name)
            for profile, golden in enumerate(PROFILES):
                for selector, expected in ((0, golden[index_a]),
                                           (1, golden[index_b])):
                    out = ctypes.c_uint16()
                    assert fn(profile, selector, ctypes.byref(out)) == 1
                    assert out.value == expected, (
                        name, profile, selector, hex(out.value))

        # Cross-check the resolved asset names. The jump pair must be a
        # SDE_jump / SDE_2_jump pair and the profile weapon field must be a
        # per-roster weapon sound, which is what makes the action binding
        # meaningful rather than an anonymous word.
        mapping = json.loads(
            (ROOT / "von/sound-id-names.json").read_text())["names"]
        names = {int(key, 16): value for key, value in mapping.items()}
        assert names[PROFILES[0][2]] == "SDE_jump_01"
        assert names[PROFILES[0][3]] == "SDE_2_jump_01"
        assert names[PROFILES[0][4]] == "SDE_dash_01_loop"
        assert names[PROFILES[0][6]] == "SDE_2_dash_01_loop"
        assert names[PROFILES[0][0]] == "SDE_tem_rifle"
        assert names[PROFILES[0][1]] == "SDE_2_tem_rifle"
        for golden in PROFILES:
            assert names[golden[2]].startswith("SDE_jump_")
            assert names[golden[4]].startswith("SDE_dash_")

        # When the assembled original is present, re-derive the golden table
        # from the roster/profile pointers so the constants above cannot drift
        # from the ROM.
        binary = ROOT / "von/build/disasm/vonj-maincpu.bin"
        if binary.is_file():
            data = binary.read_bytes()
            offsets = (0x488, 0x48C, 0x490, 0x494, 0x498, 0x49C,
                       0x4A0, 0x4A4)
            table = [int.from_bytes(data[0x19360 + i * 4:0x19364 + i * 4],
                                    "little") for i in range(len(PROFILES))]
            for profile, base in enumerate(table):
                derived = tuple(
                    int.from_bytes(data[base + offset:base + offset + 2],
                                   "little") for offset in offsets)
                assert derived == PROFILES[profile], (
                    profile, [hex(v) for v in derived])

        print(f"PASS: {len(PROFILES)} profiles, "
              f"{len(WRAPPERS)} action wrappers")
    finally:
        directory.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
