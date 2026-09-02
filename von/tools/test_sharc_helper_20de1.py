#!/usr/bin/env python3
"""Audit the shared streamed-geometry helper at SHARC target 0x20de1."""

from __future__ import annotations

import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
RUNTIME_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-nonzero.runtime.log"
STEP_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-nonzero-current20.trace"
SWEEP_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-helper-sweep-current45-nondegenerate.trace"
MULTI_RECORD_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-helper-sweep-current75-records.trace"
TRUE_SELECTOR_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r2-x.trace"
TRUE_SELECTOR_R3_ORIGIN_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r3-origin.trace"
TRUE_SELECTOR_R3_DIAGONAL_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r3-diagonal.trace"
TRUE_SELECTOR_R3_X_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r3-x.trace"
TRUE_SELECTOR_R3_Y_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r3-y.trace"
TRUE_SELECTOR_R4_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r4-four-points.trace"
TRUE_SELECTOR_R5_TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-true-selector-r5-four-points.trace"
TRACE_PATCH = ROOT / "third_party/patches/0015-von-sharc-20de1-tracing.patch"
SWEEP_PROBE = ROOT / "von/tools/probe_sharc_opcode_17_helper_sweep.lua"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    checks = {
        "de1": "DM(0x00030109) = R8",
        "de2": "DM(0x0003010A) = R9",
        "de3": "I4 = 0x0003010B",
        "de4": "R0 = DM(0x00000003, I4)",
        "de5": "R4 = DM(0x00000006, I4)",
        "de6": "F1 = F0 - F4",
        "de7": "R5 = DM(0x00000008, I4)",
        "de8": "F2 = F0 - F5",
        "de9": "F3 = F0 - F4",
        "dea": "F6 = F0 - F5",
        "deb": "IF EQ, JUMP (0x00020DFC) (DB)",
        "dec": "F4 = F8 - F4",
        "ded": "F5 = F9 - F5",
        "df3": "F7 = RECIPS F12",
        "df2": "F12 = F8 - F12",
        "dfa": "F15 = F0 * F7",
        "dfb": "JUMP (0x00020E05)",
        "dfc": "R12 = R2",
        "e05": "F3 = PASS F3",
        "e06": "IF EQ, JUMP (0x00020E13)",
        "e12": "JUMP (0x00020E1E)",
        "e13": "F8 = F1 * F5",
        "e14": "F12 = F4 * F2",
        "e15": "F12 = F1 * F6",
        "e22": "R0 = DM(0x00000006, I4)",
        "e23": "DM(0x00000003, I4) = R0",
        "e24": "R0 = DM(0x00000007, I4)",
        "e25": "DM(0x00000004, I4) = R0",
        "e26": "R0 = DM(0x00000008, I4)",
        "e2d": "DM(0x00000008, I4) = R0",
        "e37": "F13 = F2 * F5",
        "e38": "F1 = F8 - F13",
        "e39": "F15 = F2 * F4",
        "e3a": "IF EQ, JUMP (0x00020E50) (DB)",
        "e3b": "F3 = F10 - F15",
        "e43": "F8 = F8 - F12",
        "e45": "F7 = RECIPS F12",
        "e4d": "RTS (DB)",
        "e4e": "R8 = DM(0x00030109)",
        "e4f": "R9 = DM(0x0003010A)",
        "e50": "R0 = 0xBDCCCCCD",
        "e51": "RTS (DB)",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 slot {slot} missing {fragment}")
    if "F14 = F0 * F6" not in lines.get("e35", ""):
        raise SystemExit("SHARC helper-0x20de1 slot e35 missing equality product")
    equality_schedule = {
        "e32": "F1 = F11 - F14",
        "e33": "F6 = F11 - F15",
        "e34": "F8 = F1 * F6",
        "e35": "F14 = F0 * F6",
        "e36": "F10 = F0 * F5",
        "e37": "F13 = F2 * F5",
        "e38": "F1 = F8 - F13",
        "e39": "F15 = F2 * F4",
    }
    for slot, fragment in equality_schedule.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 equality schedule missing {slot}: {fragment}")
    trace_source = (ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharc.cpp").read_text()
    trace_patch = (ROOT / "third_party/patches/0015-von-sharc-20de1-tracing.patch").read_text()
    for name, text in (("MAME source", trace_source), ("trace patch", trace_patch)):
        if "vonj_sharc_20de1_step: pc=%06x" not in text or "f15=%08x" not in text:
            raise SystemExit(f"{name} does not expose F15 in the helper trace")
    if "R0 = DM(0x05, I4)" not in lines.get("de6", ""):
        raise SystemExit("SHARC helper-0x20de1 slot de6 missing scratch read")

    caller_checks = {
        "36f": "F1 = F1 * F4",
        "370": "F0 = F0 * F4",
        "371": "F0 = F0 - F1",
        "372": "IF EQ, JUMP (0x0002037E)",
        "378": "CALL (0x00020DE1)",
    }
    for slot, fragment in caller_checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x17 edge gate slot {slot} missing {fragment}")

    for slot in ("dee", "def", "df0", "df1", "e07", "e13", "e14", "e15"):
        if " * " not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 slot {slot} missing interpolation arithmetic")

    trace = RUNTIME_TRACE.read_text(encoding="utf-8")
    if "pc=20e4d r0=bcdd67c8" not in trace:
        raise SystemExit("runtime trace lacks the normal 0x20de1 return")
    if "vonj_sharc_output: pc=020387 address=00c00000 data=bcdd67c8" not in trace:
        raise SystemExit("runtime trace lacks the emitted normal helper result")
    if STEP_TRACE.exists():
        step_trace = STEP_TRACE.read_text(encoding="utf-8", errors="replace")
        step_pcs = [
            "pc=020de1", "pc=020de6", "pc=020df3", "pc=020e05",
            "pc=020e1e", "pc=020e3a", "pc=020e45", "pc=020e4c",
            "pc=020e4d",
        ]
        positions = []
        for pc in step_pcs:
            position = step_trace.find("vonj_sharc_20de1_step: " + pc)
            if position < 0:
                raise SystemExit(f"fresh helper step trace lacks {pc}")
            positions.append(position)
        if positions != sorted(positions):
            raise SystemExit("fresh helper step trace is out of execution order")
        if "pc=020e4c f0=bcdd67c8" not in step_trace:
            raise SystemExit("fresh helper step trace lacks refined normal result")
        if step_trace.count("vonj_sharc_20de1_step:") < 50:
            raise SystemExit("fresh helper step trace is too short to cover the normal path")
    if SWEEP_TRACE.exists():
        sweep = SWEEP_TRACE.read_text(encoding="utf-8", errors="replace")
        outputs = [
            int(data, 16)
            for data in re.findall(
                r"vonj_sharc_output: pc=020387 address=00c00000 data=([0-9a-f]+)",
                sweep,
            )
        ]
        expected_outputs = [
            0xbcdd67c8, 0x3e722983, 0x3f000000, 0x3f83759f,
            0xbf8a60dd, 0x3e983759, 0x3ee0dd67, 0x4005306e,
        ]
        if outputs[-len(expected_outputs):] != expected_outputs:
            raise SystemExit(
                "nondegenerate helper sweep does not match the affine output oracle"
            )
        sentinel_positions = [
            match.start() for match in re.finditer(
                r"vonj_sharc_20de1_step: pc=020e50 ", sweep
            )
        ]
        for position in sentinel_positions:
            window = sweep[max(0, position - 12000):position]
            if "vonj_sharc_20de1_step: pc=020e3a " not in window:
                raise SystemExit("sentinel return lacks the 0x20e3a equality branch")
        if sentinel_positions and "vonj_sharc_20de1_step: pc=020e4d " in sweep:
            # The sweep contains both branch classes, but each sentinel must
            # be locally preceded by equality rather than normal refinement.
            for position in sentinel_positions:
                window = sweep[max(0, position - 2000):position]
                if "pc=020e45 " in window:
                    raise SystemExit("sentinel return unexpectedly entered reciprocal refinement")
        equality_rows = re.findall(
            r"vonj_sharc_20de1_step: pc=020e3a (?P<fields>[^\n]+)", sweep
        )
        if not equality_rows:
            raise SystemExit("helper sweep lacks the post-schedule equality instruction")
        for fields in equality_rows:
            values = dict(re.findall(r"(f\d+)=([0-9a-f]+)", fields))
            if not all(name in values for name in ("f2", "f9", "f14")):
                raise SystemExit("helper equality trace lacks F2/F9/F14")
            f9 = struct.unpack(">f", bytes.fromhex(values["f9"]))[0]
            f14 = struct.unpack(">f", bytes.fromhex(values["f14"]))[0]
            expected = struct.unpack(">I", struct.pack(">f", f9 - f14))[0]
            if int(values["f2"], 16) != expected:
                raise SystemExit(
                    "helper equality trace does not match F2 = F9 - F14: "
                    f"f2={values['f2']} expected={expected:08x}"
                )
    if MULTI_RECORD_TRACE.exists():
        multi_record = MULTI_RECORD_TRACE.read_text(
            encoding="utf-8", errors="replace"
        )
        outputs = [
            int(data, 16)
            for data in re.findall(
                r"vonj_sharc_output: pc=020387 address=00c00000 data=([0-9a-f]+)",
                multi_record,
            )
        ]
        expected_prefix = [
            0xbcdd67c8, 0x3e722983, 0x3f000000, 0x3f83759f,
            0xbf8a60dd, 0x3e983759, 0x3ee0dd67, 0x4005306e,
            0xbf7fffff, 0xbed89d89,
        ]
        if outputs[:len(expected_prefix)] != expected_prefix:
            raise SystemExit(
                "multi-record helper sweep does not preserve the clean output prefix"
            )
    if TRUE_SELECTOR_TRACE.exists():
        true_selector = TRUE_SELECTOR_TRACE.read_text(
            encoding="utf-8", errors="replace"
        )
        if "pc=02035f" not in true_selector or "i5=00030310" not in true_selector:
            raise SystemExit("true-selector trace lacks selector-1 bank offset")
        if "vonj_sharc_20de1_step: pc=020de1" not in true_selector:
            raise SystemExit("true-selector trace lacks helper entry")
        if "vonj_sharc_output: pc=020387 address=00c00000 data=00000000" not in true_selector:
            raise SystemExit("true-selector trace lacks exact-zero helper result")
        if "vonj_sharc_output: pc=02038c address=00c00000 data=00000001" not in true_selector:
            raise SystemExit("true-selector trace lacks selected-record output")
    for path, bank_offset, result, selected in (
        (TRUE_SELECTOR_R3_ORIGIN_TRACE, "00030320", "bf7fffff", "00000002"),
        (TRUE_SELECTOR_R3_DIAGONAL_TRACE, "00030320", "bed89d89", "00000002"),
        (TRUE_SELECTOR_R3_X_TRACE, "00030320", "bd9d89d8", "00000002"),
        (TRUE_SELECTOR_R3_Y_TRACE, "00030320", "bf44ec4e", "00000002"),
    ):
        if path.exists():
            selected_trace = path.read_text(encoding="utf-8", errors="replace")
            if f"pc=02035f" not in selected_trace or f"i5={bank_offset}" not in selected_trace:
                raise SystemExit(f"{path.name} lacks selector-2 bank offset")
            if "vonj_sharc_20de1_step: pc=020de1" not in selected_trace:
                raise SystemExit(f"{path.name} lacks helper entry")
            if f"vonj_sharc_output: pc=020387 address=00c00000 data={result}" not in selected_trace:
                raise SystemExit(f"{path.name} lacks expected helper result")
            if f"vonj_sharc_output: pc=02038c address=00c00000 data={selected}" not in selected_trace:
                raise SystemExit(f"{path.name} lacks selected-record output")
    if TRUE_SELECTOR_R4_TRACE.exists():
        record4_trace = TRUE_SELECTOR_R4_TRACE.read_text(
            encoding="utf-8", errors="replace"
        )
        if record4_trace.count("pc=02035f") < 4 or "i5=00030330" not in record4_trace:
            raise SystemExit("true-selector record-4 trace lacks selector-3 bank offset")
        if record4_trace.count("vonj_sharc_20de1_step: pc=020de1") != 4:
            raise SystemExit("true-selector record-4 trace lacks four helper entries")
        for result in ("3f7914c1", "3fe45307", "3f9bacf9", "3fc00000"):
            if f"vonj_sharc_output: pc=020387 address=00c00000 data={result}" not in record4_trace:
                raise SystemExit(f"true-selector record-4 trace lacks result {result}")
        if record4_trace.count(
            "vonj_sharc_output: pc=02038c address=00c00000 data=00000003"
        ) != 4:
            raise SystemExit("true-selector record-4 trace lacks selected-record outputs")
    if TRUE_SELECTOR_R5_TRACE.exists():
        record5_trace = TRUE_SELECTOR_R5_TRACE.read_text(
            encoding="utf-8", errors="replace"
        )
        if record5_trace.count("pc=02035f") < 4 or "i5=00030340" not in record5_trace:
            raise SystemExit("true-selector record-5 trace lacks selector-4 bank offset")
        if record5_trace.count("vonj_sharc_20de1_step: pc=020de1") != 4:
            raise SystemExit("true-selector record-5 trace lacks four helper entries")
        for result in ("bf567c8a", "bcdd67c8", "bf183759", "be9f2298"):
            if f"vonj_sharc_output: pc=020387 address=00c00000 data={result}" not in record5_trace:
                raise SystemExit(f"true-selector record-5 trace lacks result {result}")
        if record5_trace.count(
            "vonj_sharc_output: pc=02038c address=00c00000 data=00000004"
        ) != 4:
            raise SystemExit("true-selector record-5 trace lacks selected-record outputs")
    trace_patch = TRACE_PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_20de1_step_trace_count",
        "m_core->pc <= 0x00020e53",
        "dm_read32(0x00030113)",
    ):
        if fragment not in trace_patch:
            raise SystemExit(f"step-trace patch missing {fragment}")
    sweep_probe = SWEEP_PROBE.read_text(encoding="utf-8")
    reset_order = (
        "command(0x0d, 0x00000000)",
        "pending_case = case_index",
        "pending_frame = frame + (true_selector and 60 or 10)",
        "if pending_case and frame == pending_frame then",
        "seed(records[test[3]], true_selector and (test[3] - 1) or 0)",
        "write_17(test[1], test[2])",
    )
    positions = [sweep_probe.find(fragment) for fragment in reset_order]
    if any(position < 0 for position in positions):
        raise SystemExit("opcode-0x17 sweep probe lacks delayed reset/seed protocol")
    if positions != sorted(positions):
        raise SystemExit("opcode-0x17 sweep probe seeds before delayed opcode-0x0d reset")
    selector_probe = (
        'true_selector = tonumber(os.getenv("VON_SHARC_17_TRUE_SELECTOR") or "0") ~= 0',
        'data_space:write_u32(0x00030201, selector or 0)',
        'if true_selector then',
        '0x00030300 + (bank - 1) * 16 + index - 1',
        'seed(records[test[3]], true_selector and (test[3] - 1) or 0)',
    )
    for fragment in selector_probe:
        if fragment not in sweep_probe:
            raise SystemExit(f"opcode-0x17 sweep probe missing selector experiment: {fragment}")
    print("PASS: SHARC helper-0x20de1 geometry interpolation/validation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
