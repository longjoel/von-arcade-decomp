# Virtual-On ROM-to-C Reconstruction Roadmap

This is the long-term work list for translating the executable Virtual-On
firmware into readable, buildable C. The active delivery milestone is the
input-free, C-only i960 attract path defined in
[`attract-mode-roadmap.md`](attract-mode-roadmap.md). Byte reproduction remains
an optional research metric rather than the delivery gate.

## Progress rule

The historical strict metric is:

```text
byte-validated C code bytes / confirmed executable firmware bytes
```

The active accounting scope is the i960 host ROM. Communication-board Z80,
audio 68000, and executable SHARC regions are deferred until the i960-side
host path is substantially reconstructed. Graphics, geometry, textures,
samples, ordinary constants, padding, and not-yet-classified bytes are not
counted as executable C code.

Semantic work units are tracked as `planned`, `modeled`, `integrated`,
`trace-validated`, `byte-validated`, or `blocked`. Physical ranges are tracked
separately as `code`, `data`, `padding`, or `unknown`; only the union of
physical `code` ranges contributes byte coverage. The current status is
generated with:

```sh
./scripts/status.sh
```

The generated report is authoritative; this roadmap intentionally carries no
copied totals. The companion semantic measure reports work-unit lifecycle
stages without claiming a byte match:

```sh
./scripts/status.sh --json
```

Active completion uses attract closure and runtime checkpoints. Byte matching
remains a research metric.

## Phase 0: inventory and classification

Establish the denominator before translating code.

- Reconcile all ROM files with MAME regions.
- Disassemble the i960 `maincpu` image.
- Classify the i960 `maincpu` image as code, constant/data, padding, or unknown.
- Record reset vectors, branch targets, jump tables, and runtime PC evidence.
- Register planned i960 slices without counting them as complete.
- Defer Z80, 68000, and SHARC classification; they are not active blockers while
  MAME's `m2comm` high-level model supplies the communication board.

## Phase 1: i960 boot path

Translate in dependency order and preserve the known boot trace.

- Reset/startup routine: `0x00000930–0x000009e8`
- I/O self-test around `0x00002734`
- SHARC bootstrap upload around `0x000282e0–0x0002840c`
- Geometry startup handshake around `0x00028418`
- Command-window clear and initialization around `0x000284b0–0x000284e8`
- Texture initializer around `0x00028548`
- Geometry program upload around `0x00028620–0x00028758`
- Geometry pipeline startup around `0x00028d80`

Completion target: the C host reproduces the original boot trace and each
accepted routine byte-matches its original range.

## Phase 2: i960 data and rendering pipeline

- Geometry buffer preparation: `0x00028b80`
- Floating-point conversion helper: `0x00028b40`
- Geometry command batch loop: `0x00028c80`
- Frame-synchronized submission: `0x00028de8`
- Geometry auxiliary submit selector: `0x00028d30`
- Texture profile setup around `0x00028120`
- Texture decompressor around `0x00027e50`
- Texture command and palette paths
- Polygon/object submission paths
- Framebuffer and raster support routines

Completion target: C reproduces the observed geometry, texture, and
framebuffer traces.

## Phase 3: i960 UI, input, and game flow

- Text table walker: `0x00003c40`
- Text state helper: `0x0001cac8`
- Character output: `0x0001cc40` and `0x0001ccd0`
- String formatter: `0x000f5100` and `0x000f5190`
- Service and test menu paths
- Input polling and normalization
- Credit/start handling
- Attract-mode state machine
- Player selection and match setup
- Single-player battle loop
- Results and return-to-menu flow

Completion target: the C host independently reaches and completes a normal
single-player match.

## Phase 4: versus and link behavior

- i960 communication-board initialization
- Shared-RAM mailbox access
- Link-role selection
- Handshake packet handling
- Frame synchronization
- Menu synchronization
- Battle-state synchronization
- Twin-cabinet input ownership
- Long-duration versus stability

Completion target: two C-backed cabinets establish a stable link, start the
same battle, and remain synchronized for the documented 60-second scripted
test.

## Deferred Phase 5: communication-board firmware

- Identify Z80 reset and memory map.
- Locate shared-RAM access.
- Locate uPD72103A/HDLC setup.
- Recover packet framing and error handling.
- Translate communication routines to C.
- Byte-match accepted routines and run them against the MAME board model.

## Deferred Phase 6: audio and SHARC firmware

- Identify 68000 reset and sound command paths.
- Translate audio command handling.
- Separate SHARC bootstrap data from executable code.
- Disassemble SHARC executable regions.
- Recover the SHARC host protocol.
- Translate and byte-match validated SHARC routines.
- Verify sound and coprocessor runtime behavior.

## Phase 7: completion and cleanup

- Resolve remaining unknown code/data ranges.
- Integrate modeled C, trace-validate it, and pursue byte validation separately.
- Run boot, attract, single-player, versus, graphics, and audio regressions.
- Publish final per-firmware and overall coverage reports.
- Document intentionally unimplemented hardware and asset data.

## Work-unit routine

Each unit uses [`reconstruction_work_unit.md`](reconstruction_work_unit.md):

1. Register the planned address range and subsystem.
2. Establish code/data boundaries and static evidence.
3. Annotate the readable assembly and calling convention.
4. Implement the slice in production C; do not add comparison-only wrappers or
   no-op dependency stubs.
5. Prove its behavior with the smallest relevant static, unit, trace, or runtime
   check and mark it `modeled` only when that evidence exists.
6. Build with the pinned remote toolchain and run the runtime regression.
7. Run byte comparison only after compiler/ABI calibration supports the
   instruction family used by the slice.
8. Mark the unit at its exact lifecycle stage or `blocked`, and update both
   headline and semantic reports.

## Current adaptation gate

The i960 GCC 2.95 toolchain does not reproduce the original firmware's
register-link conventions or several native i960 instruction sequences. The
first isolated C candidates therefore matched only 3-35 bytes per routine and
no candidate reached the byte-match gate. Do not create more comparison-only
wrappers or no-op call stubs until a compiler/ABI calibration unit establishes
which source forms and instruction families can actually byte-match.

Until then, prioritize production C with direct behavioral evidence. With the
currently classified boot/pipeline slices represented, the next unit is
compiler/ABI calibration for byte validation or expansion of the executable
classification beyond the initial i960 path. The preferred calibration runner
is now the pinned Intel CTOOLS 5.0 track documented in
[`i960/ctools-reproducibility.md`](i960/ctools-reproducibility.md). Continue to validate texture
decompression writes against MAME's debug `vonj_texture_write` trace, not RAM
snapshots, because later loader calls reuse and overwrite those RAM windows.

A failed unit records its earliest failure: classification, ABI/compiler,
hardware behavior, byte comparison, or runtime behavior. It does not increase
the headline percentage.
