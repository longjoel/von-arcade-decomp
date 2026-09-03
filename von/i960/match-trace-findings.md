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
| `0x3403c` | `geometry_object_profile_projection_emitter` | Emits the shared tagged object prefix, then the profile XZ-length request and response-dependent scalar request. |
| `0x346f0`/`0x34b00` | `geometry_object_state_transform_emitter`/`geometry_object_late_response_continuation` | Emits the state setup and two later transformed state-tail readbacks modeled by the recovered object-packet C contract. |
| `0x34de8` | `geometry_object_state_response_emitter` | Uses the shared tagged prefix and standalone `0x20` state-tail readback copied into the local object record. |

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

The same report correlates object identity without assigning semantic model
names: all 109 post-start OBAs have exactly one stable `tpa`/`tha` pair, and
the busiest OBA is submitted 1,785 times. This supports treating the three
trace pointers as a stable object-record submission tuple at the
`0x2b430` boundary; it does not by itself identify the record's game role.

The retained `drone0` 45-second geometry trace is a separate machine-select
capture: its Lua log contains the coin event but no START event. It still adds
a useful C boundary check, with 684 unique polygon-ROM objects, all using
`0x00800101`, decoding to 33,874 polygons in total with a 1–781 range. It is
recorded as select-screen evidence and is not conflated with the verified
post-start match trace.

Two reproducibility probes with the expanded-hook binary were intentionally
not promoted: both original-ROM runs reached the scheduled coin/start events
but remained at the pre-match `Downloading COPRO/GEO/Texture` screen and
emitted zero geometry-object or matrix events. One run used the interpreter
default and one used `VON_SHARC_DRC=1`; both had matching ROM hashes and no
stale `drone0` MAME process. These are runtime-transition diagnostics, not
counterevidence against the verified post-start trace above.

The runtime comparison also exposes source drift in the capture harness. The
retained successful 45-second trace reports 203.15% average speed and reaches
geometry, whereas the current geometry-profile rebuild reports 67.08% and
stays on the download screen under the same scripted flow. The local pinned
MAME checkout contains substantial uncommitted diagnostic/SHARC changes, so
this difference is treated as a harness-reproduction issue until a clean-base
geometry build is tested; it is not attributed to the recovered i960 C.

That clean-base control has now been run. A detached worktree at the pinned
MAME commit `569c5e9d4534cb244ff67ebbdb5f9fe69a465318`, with the geometry
patches plus their SHARC-tracing dependency, reaches the pre-match scene with
the same original ROMs and scheduled inputs. Its trace is
`von/build/disasm/vonj-clean-base-45s.trace` (SHA-256
`cbe5e9ba1707052c3b39ab7dcc78ca5a83f3b88bfb641cbb291ef22a92d1d5f8`). The
post-start two-second analysis window contains 11,611 polygon-ROM object
submissions, 8,762 matrix events, and all `0x00800101` opcodes; the matrix
stream is not saturated. This confirms the earlier stall is caused by the
dirty MAME runtime source/patch state, while also showing that object
populations and pointer-pair stability can vary with the exact capture build
and window. The clean trace is a control, not a replacement for the verified
45-second match capture.

## C pipeline consequence

`recovered_polygon_rom_decode()` already models the observed OBA convention:
the low 22 bits select a four-byte word offset, followed by linked 3/4-vertex
records. The next C validation slice should feed the 109 live match OBAs into
that decoder and compare polygon counts/attributes against the corresponding
`0x00800101` submissions. Transform and object-state behavior must remain
separate until the live `tpa`/`tha` windows are correlated with the record
layout.
