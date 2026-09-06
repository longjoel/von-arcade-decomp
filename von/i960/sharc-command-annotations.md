# SHARC Command Annotations (von)

> Static sidecar for the von SHARC program image
> (`von/build/disasm/vonj-sharc-bootstrap.lst`, PM `0x20000`-`0x20E5F`,
> 3,680 contiguous slots). Confidence tags follow the reconstruction
> handbook (`KNOWN` / `LIKELY` / `SPECULATIVE`); `observed:<trace>` marks
> values from original execution, `synthetic:<listing>` marks listing
> readings. The 78-entry command table lives at listing slots
> `0x99`-`0xE6` (opcodes `0x00`-`0x4D`, asserted by
> `von/tools/test_sharc_dispatch_table.py`); entries are
> `DM(I0, M0) = <handler PM>` stores with a constant-table boundary
> at slot `0xE7` (`I0 = 0x00030300`). Behavioral summaries come from
> the `recovered_sharc_opcode_*` models (`LIKELY`: black-box contract,
> not disassembly). Official Sega `Fn_*` labels do NOT transfer:
> von dispatch (78 entries, `0x20133`-`0x20CF8`) differs structurally
> from Sonic the Fighters (136 entries); see U-0010.

## Opcode `0x00` — entry `0x20133` (8 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 8 words; 1 float writes.

## Opcode `0x01` — entry `0x2013b` (8 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 8 words; 1 float writes.

## Opcode `0x02` — entry `0x20143` (8 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 8 words; 1 float writes.

## Opcode `0x03` — entry `0x2014b` (16 words)

- Behavior (`LIKELY`, `observed:<harness>`): two-word FIFO division service.
  Fed `1.0, 2.0` after an `08` init it returns to idle with no DM effects
  and queues `0.5` (`0x3f000000`) on the output FIFO: first/second. Run with
  `python3 von/tools/run_sharc_harness.py --spec "08;03:3f800000,40000000;fd:8"`.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 16 words; 8 float writes.

## Opcode `0x04` — entry `0x2015b` (18 words)

- Behavior (`LIKELY`, `observed:<harness>`): two-word FIFO service returning
  the division round-trip residual `R0 - (R0/R12)*R12`: `(1.0, 2.0)` and
  `(3.0, 2.0)` both return `0.0` with no DM effects. Bare (no args) it parks
  at its entry FLAG0 wait (`blocked-02015b`). Run with
  `python3 von/tools/run_sharc_harness.py --spec "08;04:3f800000,40000000;fd:8"`.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 18 words; 10 float writes.

## Opcode `0x05` — entry `0x2016d` (34 words)

- Behavior (`LIKELY`, `observed:<harness>`): 12-word upload-record advance.
  Copies the 12 words at the `DM(0x30101)` pointer forward by 12 (observed
  `0x30200-0x3020b` → `0x3020c-0x30217` verbatim, deterministic across boots,
  source-varying probes re-copy the new source every time). No FIFO I/O.
  Caveat: the static counter gate (`DM(0x30100) < 7`) never tripped in eight
  consecutive runs, and the counter/pointer bookkeeping stores have no
  snapshot-visible effect in steady state (boot-time stores do land), so the
  gate is statically documented but dynamically unconfirmed — suspect a MAME
  SHARC-core visibility quirk for absolute-DM bookkeeping, needs a core-level
  test. Run with `python3 von/tools/run_sharc_harness.py --spec "08;07:<12 words>;05"`.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 34 words.

## Opcode `0x06` — entry `0x2018f` (10 words)

- Behavior (`LIKELY`, `observed:<harness>` + static body): upload-counter
  decrement (`DM(0x30100) -= 1`, early RTS when already zero). Dynamically a
  no-op in every probe: no DM effects, no FIFO output, returns to idle —
  consistent with the counter reading 0 (same bookkeeping-visibility caveat
  as `0x05`). A gate-reopen probe (`05` x N, `06`, fresh-source `07`, `05`)
  could not distinguish a real decrement from a no-op because the counter is
  snapshot-invisible; the decrement is statically clear but dynamically
  unconfirmed.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 10 words.

## Opcode `0x07` — entry `0x20199` (38 words)

- Behavior (`LIKELY`, `observed:<harness>`): 12-word state-upload service.
  Reads twelve FIFO words into `R0-R11` and stores them verbatim at the
  `DM(0x30101)` pointer (`0x30200-0x3020b` after `08` init); feeding
  `1.0-12.0` produced exactly those twelve words in DM, deterministic across
  boots. No FIFO output. Bare-run behavior unprobed; the static body opens
  with FLAG0 waits, so it should park waiting for args like `0x04` does.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 38 words.

## Opcode `0x08` — entry `0x201bf` (5 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 5 words.

## Opcode `0x09` — entry `0x201c4` (77 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_09.c`): Recovered four-vector matrix transform for SHARC opcode 0x09.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 77 words; 43 float writes.

## Opcode `0x0a` — entry `0x20211` (10 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_0a.c`): Recovered contract for SHARC opcode 0x0a at 0x20211.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 10 words; calls 0x00020D68; 1 float writes.

## Opcode `0x0b` — entry `0x2021b` (51 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_0b.c`): Semantic model of the SHARC opcode-0x0b normalized cross-product service.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 51 words; 30 float writes.

## Opcode `0x0c` — entry `0x2024e` (31 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_0c.c`): Semantic model of the SHARC opcode-0x0c three-input normalizer.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 31 words; 21 float writes.

## Opcode `0x0d` — entry `0x2026d` (4 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_0d.c`): Model of the SHARC opcode-0x0d/helper-0x20d5d pointer initializer.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 4 words; calls 0x00020D5D.

## Opcode `0x0e` — entry `0x20271` (13 words)

- Behavior (`LIKELY`, `observed:<harness>`): four-word FIFO parameter store.
  Reads four FIFO words into `R0-R3` and stores them verbatim to absolute DM
  `0x30105-0x30108` (the last two stores sit in the RTS delay slots and still
  execute). Feeding `0x11111111-0x44444444` produced exactly those four words
  in DM, deterministic across boots; pinned by the `0e` golden. Notably, these
  absolute-DM stores ARE snapshot-visible, unlike the `0x30100/0x30101`
  bookkeeping of `0x05/0x06/0x08` — the visibility quirk is address-specific,
  not a general absolute-store failure.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 13 words.

## Opcode `0x0f` — entry `0x2027e` (16 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_0f.c`): Semantic model of the SHARC opcode-0x0f signed angle service.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 16 words; calls 0x00020D68; 3 float writes.

## Opcode `0x10` — entry `0x2028e` (16 words)

- Behavior (`LIKELY`, `observed:<harness>`): 12-word diagonal-identity
  initializer. Writes `1.0` at upload-record offsets 0, 4, 8 and `0.0` at the
  other nine words (`DM(I7+0..11)` with `I7 = DM(0x30101)`), no FIFO I/O.
  Over a garbage-prefilled record the full 12-word pattern lands verbatim;
  pinned by the `10` golden.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 16 words.

## Opcode `0x11` — entry `0x2029e` (39 words)

- Behavior (`LIKELY`, `observed:<harness>`): 12-word state readback to the
  output FIFO. Streams the twelve words at the `DM(0x30101)` pointer out
  through `I1` with FLAG1 flow control (plus a 13th delay-slot write),
  no FIFO input. Uploading `1.0-12.0` via `07` then running `11` drains those
  exact twelve words back host-side — a full FIFO→DM→FIFO round trip that
  cross-validates `07`. Run with
  `python3 von/tools/run_sharc_harness.py --spec "08;07:<12 words>;11;fd:16"`.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 39 words.

## Opcode `0x12` — entry `0x202c5` (23 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_12.c`): Semantic model of SHARC opcode-0x12 matrix-vector tail accumulation.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 23 words; 10 float writes.

## Opcode `0x13` — entry `0x202dc` (26 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_13.c`): Semantic model of SHARC opcode-0x13 row-scaled 3x3 state writeback.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 26 words; 9 float writes.

## Opcode `0x14` — entry `0x202f6` (28 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_14.c`): Semantic model of SHARC opcode-0x14 X-axis row-pair rotation.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 28 words; calls 0x00020DBE, 0x00020DC4; 15 float writes.

## Opcode `0x15` — entry `0x20312` (28 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_15.c`): Semantic model of SHARC opcode-0x15 Y-axis row-pair rotation.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 28 words; calls 0x00020DBE, 0x00020DC4; 15 float writes.

## Opcode `0x16` — entry `0x2032e` (28 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_16.c`): Semantic model of SHARC opcode-0x16 Z-axis row-pair rotation.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 28 words; calls 0x00020DBE, 0x00020DC4; 15 float writes.

## Opcode `0x17` — entry `0x2034a` (68 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_17.c`): Recovered selector/staging and determinant gate for SHARC opcode 0x17.
- Behavior (`LIKELY`, `recovered_sharc_opcode_17_projection.c`): Composed normal-path model for SHARC opcode 0x17 and helper 0x20de1.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 68 words; calls 0x00020DE1; 6 float writes.

## Opcode `0x18` — entry `0x2038e` (9 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_18.c`): Exact table-window transfer recovered from SHARC opcode 0x18.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 9 words; calls 0x00020E54.

## Opcode `0x19` — entry `0x20397` (4 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 4 words.

## Opcode `0x1a` — entry `0x2039b` (27 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1a.c`): Semantic model of SHARC opcode-0x1a's affine state-output service.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 27 words; 10 float writes.

## Opcode `0x1b` — entry `0x203b6` (12 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1b.c`): Recovered contract for SHARC opcode 0x1b at 0x203b6.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 12 words; calls 0x00020DC4; 2 float writes.

## Opcode `0x1c` — entry `0x203c2` (12 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1c.c`): Recovered contract for SHARC opcode 0x1c at 0x203c2.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 12 words; calls 0x00020DBE; 2 float writes.

## Opcode `0x1d` — entry `0x203ce` (14 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1d.c`): Recovered contract for SHARC opcode 0x1d at 0x203ce.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 14 words; calls 0x00020DC4; 3 float writes.

## Opcode `0x1e` — entry `0x203dc` (14 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1e.c`): Recovered contract for SHARC opcode 0x1e at 0x203dc.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 14 words; calls 0x00020DBE; 3 float writes.

## Opcode `0x1f` — entry `0x203ea` (32 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_1f.c`): Semantic model of the SHARC opcode-0x1f endpoint-distance service.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 32 words; 22 float writes.

## Opcode `0x20` — entry `0x2040a` (11 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 11 words.

## Opcode `0x21` — entry `0x20415` (20 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 20 words.

## Opcode `0x22` — entry `0x20429` (66 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_22.c`): Proven affine portion of the SHARC opcode-0x22 projection service.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 66 words; 31 float writes.

## Opcode `0x23` — entry `0x2046b` (82 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_23.c`): Proven normalized-direction portion of SHARC opcode 0x23.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 82 words; 67 float writes.

## Opcode `0x24` — entry `0x204bd` (77 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_24.c`): Proven frame-transpose update for SHARC opcode 0x24.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 77 words; 63 float writes.

## Opcode `0x25` — entry `0x2050a` (40 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_25.c`): Recovered angular projection for SHARC opcode 0x25.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 40 words; calls 0x00020D68; 20 float writes.

## Opcode `0x26` — entry `0x20532` (17 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 17 words.

## Opcode `0x27` — entry `0x20543` (47 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_27.c`): Recovered normal path for SHARC opcode 0x27.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 47 words; 21 float writes.

## Opcode `0x28` — entry `0x20572` (55 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_28.c`): Recovered finite path for the SHARC opcode-0x28 projected predicate.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 55 words; 27 float writes.

## Opcode `0x29` — entry `0x205a9` (49 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_29.c`): Recovered state initializer for SHARC opcode 0x29.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 49 words; calls 0x00020DBE, 0x00020DC4; 15 float writes.

## Opcode `0x2a` — entry `0x205da` (22 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_2a.c`): Recovered elementwise matrix-scale service for SHARC opcode 0x2a.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 22 words; 9 float writes.

## Opcode `0x2b` — entry `0x205f0` (4 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_2b.c`): Recovered constant-success status service for SHARC opcode 0x2b.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 4 words.

## Opcode `0x2c` — entry `0x205f4` (103 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_2c.c`): Recovered translation and Euler-matrix rebuild for SHARC opcode 0x2c.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 103 words; calls 0x00020DBE, 0x00020DC4; 55 float writes.

## Opcode `0x2d` — entry `0x2065b` (6 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_2d.c`): Recovered one-word passthrough service for SHARC opcode 0x2d.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 6 words.

## Opcode `0x2e` — entry `0x20661` (128 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_2e.c`): Recovered packed translation and Euler-matrix rebuild for SHARC opcode 0x2e.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 128 words; calls 0x00020DBE, 0x00020DC4; 55 float writes.

## Opcode `0x2f` — entry `0x206e1` (48 words)

- Behavior: no recovered model (open).
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 48 words; 10 float writes.

## Opcode `0x30` — entry `0x20711` (81 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_30.c`): Recovered translation update and scaled-Z rebuild for SHARC opcode 0x30.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 81 words; calls 0x00020DBE, 0x00020DC4; 34 float writes.

## Opcode `0x31` — entry `0x20762` (102 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_31.c`): Recovered projection transform for SHARC opcode 0x31.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 102 words; calls 0x00020DBE, 0x00020DC4; 40 float writes.

## Opcode `0x32` — entry `0x207c8` (124 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_32.c`): Recovered angle/translation contract for SHARC opcode 0x32.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 124 words; calls 0x00020DBE, 0x00020DC4; 65 float writes.

## Opcode `0x33` — entry `0x20844` (76 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_33.c`): Recovered angle/translation contract for SHARC opcode 0x33.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 76 words; calls 0x00020DBE, 0x00020DC4; 40 float writes.

## Opcode `0x34` — entry `0x20890` (98 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_34.c`): Recovered two-vector/angle contract for SHARC opcode 0x34.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 98 words; calls 0x00020DBE, 0x00020DC4; 50 float writes.

## Opcode `0x35` — entry `0x208f2` (23 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_35.c`): Recovered normal-case stateful division contract for SHARC opcode 0x35.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 23 words; 12 float writes.

## Opcode `0x36` — entry `0x20909` (55 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_36.c`): Recovered translation-tail add and uniform matrix scale for opcode 0x36.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 55 words; 19 float writes.

## Opcode `0x37` — entry `0x20940` (22 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_37.c`): Recovered identity reset and direct translation-tail write for opcode 0x37.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 22 words.

## Opcode `0x38` — entry `0x20956` (52 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_38.c`): Recovered packed-vector projection for SHARC opcode 0x38.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 52 words; 10 float writes.

## Opcode `0x39` — entry `0x2098a` (34 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_39.c`): Recovered destination derivation and seeded 12-word table copy for 0x39.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 34 words.

## Opcode `0x3a` — entry `0x209ac` (36 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3a.c`): Recovered seeded table copy plus final-word output for opcode 0x3a.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 36 words.

## Opcode `0x3b` — entry `0x209d0` (39 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3b.c`): Recovered fixed-source bridge and seeded table copy for opcode 0x3b.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 39 words.

## Opcode `0x3c` — entry `0x209f7` (101 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3c.c`): Recovered normal/degenerate state update for SHARC opcode 0x3c.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 101 words; 89 float writes.

## Opcode `0x3d` — entry `0x20a5c` (101 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3d.c`): Recovered normal/degenerate state update for SHARC opcode 0x3d.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 101 words; 89 float writes.

## Opcode `0x3e` — entry `0x20ac1` (28 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3e.c`): Recovered mathematical contract for SHARC opcode 0x3e.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 28 words; 19 float writes.

## Opcode `0x3f` — entry `0x20add` (21 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_3f.c`): Recovered normal-case contract for SHARC opcode 0x3f.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 21 words; 12 float writes.

## Opcode `0x40` — entry `0x20af2` (7 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_40.c`): Recovered base-address calculation for SHARC opcode 0x40.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 7 words.

## Opcode `0x41` — entry `0x20af9` (16 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_41.c`): Recovered byte-lane lookup for SHARC opcode 0x41.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 16 words.

## Opcode `0x42` — entry `0x20b09` (128 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_42.c`): Recovered packed-coordinate and Euler-state service for SHARC opcode 0x42.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 128 words; calls 0x00020DBE, 0x00020DC4; 55 float writes.

## Opcode `0x43` — entry `0x20b89` (24 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_43.c`): Recovered row-major matrix projection for SHARC opcode 0x43.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 24 words; 10 float writes.

## Opcode `0x44` — entry `0x20ba1` (10 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_44.c`): Recovered four-word constant initializer for SHARC opcode 0x44.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 10 words.

## Opcode `0x45` — entry `0x20bab` (35 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_45.c`): Recovered normal-case spherical projection for SHARC opcode 0x45.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 35 words; calls 0x00020DBE, 0x00020DC4; 9 float writes.

## Opcode `0x46` — entry `0x20bce` (23 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_46.c`): Recovered seven-word state upload for SHARC opcode 0x46.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 23 words; 1 float writes.

## Opcode `0x47` — entry `0x20be5` (41 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_47.c`): Recovered normal-case geometry predicate for SHARC opcode 0x47.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 41 words; 20 float writes.

## Opcode `0x48` — entry `0x20c0e` (17 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_48.c`): Recovered five-word state upload for SHARC opcode 0x48.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 17 words.

## Opcode `0x49` — entry `0x20c1f` (39 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_49.c`): Recovered normal-case 3D distance predicate for SHARC opcode 0x49.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 39 words; 22 float writes.

## Opcode `0x4a` — entry `0x20c46` (46 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_4a.c`): Recovered normal/early-branch predicate for SHARC opcode 0x4a.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 46 words; 22 float writes.

## Opcode `0x4b` — entry `0x20c74` (86 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_4b.c`): Recovered finite-path predicate for SHARC opcode 0x4b.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 86 words; calls 0x00020D68, 0x00020DBE, 0x00020DC4; 58 float writes.

## Opcode `0x4c` — entry `0x20cca` (46 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_4c.c`): Recovered normal/early-branch predicate for SHARC opcode 0x4c.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 46 words; 22 float writes.

## Opcode `0x4d` — entry `0x20cf8` (360 words)

- Behavior (`LIKELY`, `recovered_sharc_opcode_4d_decision.c`): Proven terminal decision layer of SHARC opcode 0x4d at 0x20d02-0x20d4e.
- Behavior (`LIKELY`, `recovered_sharc_opcode_4d_horizontal_seed.c`): Exact pre-refinement scalar formed by SHARC opcode 0x4d at 0x20d04-0x20d08.
- Structure (`SPECULATIVE`, `synthetic:<listing>`): size 360 words; calls 0x00020D68, 0x00020DBE, 0x00020DC4; 216 float writes.
## Vectors and reset (`KNOWN`, `synthetic:<listing>`)

- Slot `0x005`: `JUMP 0x20080 (DB)` — reset vector into init.
- Slots `0x00c`+: `RTI` sleds — interrupt vectors (unanalyzed).
- Command table: slots `0x99`-`0xE6`; constant-table boundary slot
  `0xE7` (`I7 = 0x00030300` at `0xD68`).

## Shared helpers `0x20CF8`+ (`LIKELY`, cross-referenced)

- `0x20D02`-`0x20D4E`: terminal decision layer of opcode `0x4d`
  (`recovered_sharc_opcode_4d_decision.c`); calls `0x20D68`,
  `0x20DBE`, `0x20DC4`.
- `0x20D5D`: pointer initializer used by opcode `0x0d`.
- `0x20D68`: angle/state helper used by opcodes `0x0f`, `0x25`,
  `0x4d`.
- `0x20DE1`: staging helper used by opcode `0x17`.
- Helpers address DM `0x30109`-`0x3030C` (state slots).
