#!/usr/bin/env python3
"""Verify a stable, trace-backed geometry assembly and write provenance JSON."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OBJECT = re.compile(
    r"vonj_geometry_object: (?:seq=(\d+) )?time=([0-9.e+-]+) tpa=([0-9a-f]+) tha=([0-9a-f]+) "
    r"oba=([0-9a-f]+) count=([0-9a-f]+) mode=(\d+) source=([^ ]+)(?: opcode=([0-9a-f]+))?"
)


def frames(trace: Path) -> dict[float, list[dict[str, object]]]:
    result: dict[float, list[dict[str, object]]] = {}
    for line in trace.read_text(errors="replace").splitlines():
        match = OBJECT.search(line)
        if not match:
            continue
        time = float(match[2])
        result.setdefault(time, []).append({
            "seq": int(match[1]) if match[1] is not None else None,
            "tpa": int(match[3], 16), "tha": int(match[4], 16),
            "oba": int(match[5], 16), "count": int(match[6], 16),
            "mode": int(match[7]), "source": match[8],
            "opcode": int(match[9], 16) if match[9] else None,
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--time", type=float, required=True)
    parser.add_argument("--start-slot", type=int, required=True)
    parser.add_argument("--object-count", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=.02)
    parser.add_argument("--minimum-stable-frames", type=int, default=3)
    parser.add_argument("--require-ordered-sequence", action="store_true",
                        help="require strictly increasing seq values for selected submissions")
    parser.add_argument("--expected-opcode", type=lambda value: int(value, 0), default=0x00800101)
    parser.add_argument("--snapshot-directory", type=Path,
                        help="optional emulator snapshot directory recorded as evidence")
    args = parser.parse_args()
    if args.start_slot < 0 or args.object_count <= 0 or args.minimum_stable_frames <= 0:
        raise SystemExit("slot, object count, and stable-frame count must be positive")
    all_frames = frames(args.trace)
    if not all_frames:
        raise SystemExit("trace contains no geometry objects")
    selected_time = min(all_frames, key=lambda value: abs(value - args.time))
    if abs(selected_time - args.time) > args.tolerance:
        raise SystemExit(f"no frame within {args.tolerance:g}s of {args.time:g}")
    selected = all_frames[selected_time][args.start_slot:args.start_slot + args.object_count]
    if len(selected) != args.object_count:
        raise SystemExit("selected frame does not contain the requested assembly")
    signature = [entry["oba"] for entry in selected]
    def ordered(entries: list[dict[str, object]]) -> bool:
        sequences = [entry.get("seq") for entry in entries]
        return (all(isinstance(sequence, int) for sequence in sequences)
                and all(sequences[index] < sequences[index + 1]
                        for index in range(len(sequences) - 1)))

    valid = lambda entries: (len(entries) == args.object_count and
        [entry["oba"] for entry in entries] == signature and
        all(entry["mode"] == 3 and entry["source"] == "polygon-rom" and
            entry["opcode"] == args.expected_opcode for entry in entries) and
        (not args.require_ordered_sequence or ordered(entries)))
    stable_times = [time for time, entries in sorted(all_frames.items())
                    if valid(entries[args.start_slot:args.start_slot + args.object_count])]
    if not valid(selected):
        raise SystemExit("selected assembly failed mode/source/opcode validation")
    if len(stable_times) < args.minimum_stable_frames:
        raise SystemExit(f"only {len(stable_times)} exact stable frames; need {args.minimum_stable_frames}")
    evidence = {
        "status": "verified", "trace": str(args.trace), "trace_time": selected_time,
        "start_slot": args.start_slot, "object_count": args.object_count,
        "obas": [f"{value:08x}" for value in signature],
        "sequence_validated": args.require_ordered_sequence,
        "mode": 3, "source": "polygon-rom", "opcode": f"{args.expected_opcode:08x}",
        "stable_frame_count": len(stable_times), "stable_times": stable_times,
        "part_labels": [{"part": index, "slot": args.start_slot + index,
                         "oba": f"{entry['oba']:08x}"}
                        for index, entry in enumerate(selected)],
    }
    if args.snapshot_directory:
        evidence["snapshot_directory"] = str(args.snapshot_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"verified {args.object_count}-part assembly across {len(stable_times)} stable frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
