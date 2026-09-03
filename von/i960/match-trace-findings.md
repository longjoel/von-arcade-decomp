# Original-ROM match trace findings

Evidence source: `von/build/disasm/vonj-post-start-45s-drone0.trace`.

The trace was produced on `drone0` from the original `vonj` ROM set. The main
CPU image is `epr-18664b.15`, SHA-256
`f0b83c4751baeace121f9cefc2c2074c8cbb63e1f980c0bf57c668b0c0620f72`, matching
`von/rom_manifest.json`.

## Confirmed runtime facts

- Coin was pressed at frame 2000 and start at frame 2580.
- The final screenshot shows the active arena and match HUD.
- Post-start Lua observations run from frame 2610 through frame 5160.
- The raw trace spans emulated time 0 through 89 seconds; the post-start
  window begins at approximately 43 seconds.
- The post-start window contains 1,655 complete geometry frames and 34,256
  polygon-ROM object submissions with 109 distinct OBA values.
- Every observed polygon-ROM object submission uses opcode `0x00800101`.

## Static-to-runtime mapping

The trace fields `tpa`, `tha`, and `oba` are runtime record/object values, not
i960 program counters. The first recovery anchors are therefore the existing
static callers and services:

| ROM address | Current label | Evidence-backed role |
| --- | --- | --- |
| `0x2b430` | `geometry_object_record_dispatch` | Indexes the `0x51c5b0` object-record table, dispatches each record, and updates per-slot counts. |
| `0x2be30` | `geometry_frame_service_initialize` | Initializes the frame service and enters the twelve-arm frame dispatch. |
| `0x27550` | `geometry_record_transform_service` | Stores record transform fields and calls the geometry producer at `0x6f600`. |
| `0x6f6f0` | `geometry_float_transform_helper` | Converts the caller's transform inputs through the recovered float path. |

These labels identify the recovery path; the trace does not yet prove a
one-to-one semantic name for each OBA or transform pointer.

The transform distinction is now checked by
`von/tools/analyze_match_trace_geometry.py`. For the current capture, the
post-start window contains 34,256 object submissions and 109 distinct
polygon-ROM addresses, while the bounded matrix hook reaches its 65,536-event
limit. Every object has a latest matrix available for bookkeeping, but that
latest value is not sufficient evidence for the complete match transform
sequence. The polygon decoder oracle is therefore promoted; the `0x6f6f0`
numeric transform contract remains conservative.

Two reproducibility probes with the expanded-hook binary were intentionally
not promoted: both original-ROM runs reached the scheduled coin/start events
but remained at the pre-match `Downloading COPRO/GEO/Texture` screen and
emitted zero geometry-object or matrix events. One run used the interpreter
default and one used `VON_SHARC_DRC=1`; both had matching ROM hashes and no
stale `drone0` MAME process. These are runtime-transition diagnostics, not
counterevidence against the verified post-start trace above.

## C pipeline consequence

`recovered_polygon_rom_decode()` already models the observed OBA convention:
the low 22 bits select a four-byte word offset, followed by linked 3/4-vertex
records. The next C validation slice should feed the 109 live match OBAs into
that decoder and compare polygon counts/attributes against the corresponding
`0x00800101` submissions. Transform and object-state behavior must remain
separate until the live `tpa`/`tha` windows are correlated with the record
layout.
