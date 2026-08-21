---
name: von-i960-reverse-engineering
description: Use ONLY when reverse-engineering the Cyber Troopers Virtual-On Model 2 i960 host ROM in this project, including ROM extraction, disassembly, MAME tracing, main_data analysis, prototype-ROM reproduction, or differential validation.
---

# Virtual-On i960 Reverse Engineering

Use this workflow for the arcade Model 2 i960 host ROM in this repository. Work
in small behavioral slices and preserve a direct path from original ROM bytes
to a reproducible prototype test.

## Core Loop

1. Choose one bounded slice: a routine, data table, hardware register group,
   or observable output.
2. Extract the correct ROM region and disassemble it at stable addresses.
3. Identify callers, literals, memory-map references, inputs, and outputs.
4. Instrument the MAME boundary involved in the slice rather than tracing the
   entire CPU instruction stream.
5. Capture a bounded original trace under a named scenario.
6. Annotate confirmed facts, strong hypotheses, and unresolved behavior.
7. Reproduce only the observed slice in the i960 prototype.
8. Compare normalized original and prototype events exactly.
9. Document the result and add a regression command before moving on.

## Project Commands

Run from the repository root:

```sh
./scripts/disasm-i960.sh
./scripts/trace-i960-boot.sh
./scripts/i960-build.sh
./scripts/run-i960.sh -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
python3 von/tools/analyze_i960_refs.py
python3 von/tools/analyze_geo_upload.py
python3 von/tools/compare_tile_trace.py --original <trace> --prototype <trace>
./scripts/test.sh
```

ROMs remain local under `von/artifacts/` and must not be committed. Generated
disassemblies, traces, builds, and staging directories belong under ignored
`von/build/` paths.

## Evidence Rules

- Treat the pinned `vonj` MAME ROM mapping as the source of address layout.
- Preserve original byte ordering and loader interleave when extracting data.
- Label interpretations as confirmed, probable, or unknown.
- Prefer exact bus writes, register values, and memory contents over visual
  similarity.
- Do not implement guessed hardware side effects merely to suppress warnings.
- Keep deferred coprocessor or geometry behavior documented rather than
  replacing it with speculative emulation.
- A slice is complete only when the prototype reproduces an original event
  vector or an independently verifiable state result.

## Current Anchors

- i960 reset entry candidate: `0x00000930`
- Host work RAM: `0x00500000`
- Tile RAM: `0x01000000`
- Japanese warning table: `0x02ea2918`
- Text state helper: `0x0001cac8`
- Tile writer: `0x0001cc40`
- String walker: `0x0001ccd0`
- Geometry upload source: `main_data + 0x00fc6290`
- Geometry upload destination: `0x00804000`

## Documentation

Maintain durable findings in:

- `von/i960/disassembly-annotations.md` for address-level annotations and
  differential vectors.
- `von/i960/boot-path.md` for boot order, memory ownership, and hypotheses.
- `von/chip-map.md` for hardware and address-map ownership.

Keep generated listings and traces out of commits. Commit the extractor,
instrumentation, prototype code, comparison tool, and concise annotation.
