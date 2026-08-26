# i960 Disassembly Annotations

This sidecar records confirmed interpretations of the generated listing at
`von/build/disasm/vonj-maincpu.lst`. Recreate the listing with:

```sh
./scripts/disasm-i960.sh
```

## Japanese Warning Text Path

### Table Walker: `0x00003c40`

Relevant listing shape:

```text
00003c40  call 0x294b0
00003c44  ld   0x00503a00,g4
00003c54  st   8,0x00884000
00003c88  ld   0x02ea2918,g4
00003c94  lda  0x02ea2918,r4
00003ca0  ldos (r4),g0
00003ca4  ldos 0x2(r4),g1
00003cac  addo r4,4,r4
00003cbc  bal  0x1cac8
00003cc4  ldob (r4),g0
00003cc8  call 0x1cc40
00003ccc  addo r4,1,r4
00003cd0  ldob (r4),g4
00003cdc  ld   (r4),g4
00003ce0  cmpible 0,g4,0x3ca0
```

`0x02ea2918` is in the i960 `main_data` window. Each record is:

```text
u16 record_id
u16 line_or_layout
char text[]    // NUL terminated ASCII
```

The table terminates with `0xffff, 0xffff`.

The first records are:

```text
0016 000c  "W A R N I N G"
000a 0010  "THIS GAME IS TO BE USED ONLY IN JAPAN."
000a 0012  "EXPORT, SALES, DISTRIBUTION AND/OR"
000a 0014  "OPERATION OUTSIDE THIS AREA MAY"
000a 0016  "CONSTITUTE A VIOLATION OF INTERNATIONAL"
000a 0018  "LAWS ON COPYRIGHTS AND/OR INDUSTRIAL"
000a 001a  "PROPERTY RIGHTS AND SUBJECT THE"
000a 001c  "VIOLATING PARTY TO LEGAL PROCEEDINGS."
000a 0020  "                   SEGA ENTERPRISES,LTD."
ffff ffff  terminator
```

### Text State Helper: `0x0001cac8`

The helper saves the current record fields into host state before returning:

```text
0001cac8  mov  g14,g2
0001cacc  mov  0,g14
0001cad0  st   g0,0x00504cdc
0001cad8  st   g0,0x00504ce0
0001cae0  st   g1,0x00504ce4
0001cae8  bx   (g2)
```

The duplicate `g0` stores are retained as observed; their separate consumers
are not yet fully labeled.

### Character Output: `0x0001cc40` and `0x0001ccd0`

`0x1ccd0` iterates a NUL-terminated string and calls `0x1cc40` for each byte.
`0x1cc40` normalizes the character and writes a 16-bit tile value into the
Model 2 tile RAM region at `0x01000000`. For printable warning text, the
address calculation is:

```text
column = state[0x00504ce0]
row    = state[0x00504ce4]
tile offset = (row << 6) + column
tile value  = 0x8000 | character
```

The writer then increments `state[0x00504ce0]`, so the first warning record
(`id=0x16`, `line=0x0c`) begins at `0x0c * 0x40 + 0x16 = 0x0316`, and the
following records begin at `0x040a`, `0x048a`, and so on. This establishes that
the `0x3c40` table is UI/message data, not geometry or decompression data.

The warning-table coordinate rule is confirmed. The control-character path in
`0x1cc40` remains separate: characters at or below the printable threshold are
handled through `0x1cbb8` and may update formatting state rather than emitting a
tile. The confirmed handlers are:

```text
TAB (9):  column = (column + 8) & ~7
          if column > 61: column = 0; row++ when row <= 46
LF  (10): column = record_id; row++ when row <= 46
other control bytes: no tile and no state update
```

Printable characters advance the column only while its prior value is at most
61. These bounds are direct consequences of the `cmpible`/`cmpibg` branches;
their presentation-level purpose remains unconfirmed.

### Formatted String Boundary

The control path is also reachable through the formatter, not only the direct
string walker. `0xf5100` creates a formatting context and dispatches to
`0xf5190`; the formatter's output loop at `0xf51b0` calls `0x1cc40` for each
expanded byte. The inline format string at `0x0c57a0` is:

```text
"Result : Node ID = %-2d\n"
```

This is static evidence that newline handling is part of the diagnostic text
path. The direct callers at `0x000012c4`, `0x000c5a98`, `0x000c5ab0`,
`0x000c5b24`, `0x000c5bd4`, `0x000f1444`, and `0x000f4628` pass ordinary
NUL-terminated strings; their surrounding state setup remains scenario
dependent.

The texture-loader path supplies a runtime vector. At `0x0002812c`, the host
formats `"Loading Texture"` at column 8, row 12; it then formats `"Bank0 ..."`
at column 25 on the same row. When the load completes, `0x00028170` formats
`"Done\n"` without resetting the text origin, and the next `Bank1` record is
initialized at column 25, row 13. The trace therefore shows:

```text
Done:  0x0323-0x0326
Bank1: 0x0359-0x0363
```

The difference is exactly `0x40`, independently confirming that LF increments
the tile row while restoring the current record's origin column.

## Geometry Upload Setup

The geometry bootstrap routine at `0x00028620` displays `"Downloading GEO prog"`
from the inline string at `0x00028600`
at column 8, row 9, then prepares the geometry boundary. At `0x2862c` it
derives these pointers:

```text
r4 = 0x00900000   // host-side geometry staging/buffer window
r5 = 0x00840000   // Geo/SHARC IOP register window
r6 = 0x02fc6290   // main_data upload source
```

The confirmed IOP setup writes are:

```text
0x00840000 <- 0x00003100
0x00840004 <- 0x00000000
0x00840008 <- 0x0000c400
0x00840070 <- 0x00000000
0x00840100 <- 0x00020000
0x00840104 <- 0x00000001
0x00840108 <- 0x00000c29
0x00840000 <- 0x00003110
0x00840070 <- 0x000000a1
0x00840070 <- 0x00000000
```

The following loop reads 16-bit values from `0x02fc6290`, masks them to
unsigned 16-bit payloads, and writes them through the geometry program port at
`0x00804000`. The original trace captures 9,340 writes. The uploaded bytes are
an exact little-endian match for `main_data` offset `0x00fc6290`; no geometry
processor execution or register side effect is inferred yet.

### Ghidra Static Confirmation

The Ghidra report now decompiles the complete host routine from `0x00028620`
through `0x00028754`. The inline string at `0x00028600` is separate from the
executable entry. Static values recovered from the routine are:

```text
r4 = 0x00900000
r5 = 0x00840000       // r4 - 0x000c0000
r6 = 0x02fc6290       // r4 + 0x026c6290
staging fill value = 0x07800f0f
staging count = 0x8000 (32768)
program count = 0x247c (9340)
program mask = 0xffff
program port = 0x00804000
```

The decompiler recovers both loops and the ten IOP setup writes, including the
`0x00840100`, `0x00840104`, and `0x00840108` fields. This independently
confirms the runtime boundary trace; the remaining unknown is processor-side
interpretation, not host-side reconstruction.

The upstream i960 Ghidra module originally modeled `bal` as a terminal branch.
The ROM uses it as branch-and-link at `0x00028628`, storing return address
`0x0002862c` in `g14` before calling `0x0001cac8`. The local processor patch
models this as a call, allowing the decompiler to reach the upload body. The
same pattern appears in the UI helper path and must be retained when reviewing
future decompilations.

The reset entry at `0x00000930` also now decompiles through `ret` at `0x000009e4`
and matches the GNU listing's instruction boundaries. Ghidra's generated C
still renders i960 register-stack and condition-code details as synthetic
`ac`, `fp`, and stack variables; those are presentation artifacts until the
calling convention is refined.

### First Recovered Source Slice

`von/i960/recovered_geometry.c` is the first checked-in C reconstruction from
the Ghidra output. `recovered_geometry_program_upload()` preserves the
confirmed staging fill, control pulses, IOP setup fields, masked 16-bit source
stream, and final read/write of `0x00803008`. It is linked into the i960
prototype by `scripts/i960-build.sh`, but is not called by the smoke-test entry
point yet. This keeps the current runnable prototype stable while proving that
the recovered routine compiles with the pinned i960 toolchain.

The source deliberately does not implement the geometry processor's response
to those writes. That boundary remains a hardware stub until independently
decoded.

### Fresh Boot Boundary Trace

The rebuilt MAME instrumentation confirms one coprocessor FIFO command during
the bounded one-second boot window:

```text
PC 0x0002840c: coprocessor FIFO <- 0x00000008
```

It also reproduces all ten Geo/SHARC IOP setup writes listed above. No function
port writes were observed during this boot window. The host then reaches the
`0x00800000` command window, first clearing its 16-byte slots and then writing
the nonzero initialization fields documented below. This separates the startup
FIFO command from the later geometry command-window protocol, but does not
establish the FIFO command's meaning.

A five-second trace extends this result without changing the startup
interpretation. It records one later FIFO write from `0x000bd690`:

```text
PC 0x000bd690: coprocessor FIFO <- 0x00000044
```

There are still no function-port writes. The geometry command window repeats
function-word writes at offsets `0x00f0`, `0x0040`, `0x0100`, and `0x0140`,
with bus values `0x00000f0f`, `0x00000404`, `0x00001010`, and `0x00001414`.
This confirms recurring host-side command traffic, while the SHARC/FIFO
consumption and the command-word meanings remain unresolved.

### First Command-Window Vector

After the program upload, routine `0x000284b0` clears 16-byte slots in a
separate command window at `0x00800000`. The fall-through/table-copy entry at
`0x000284e8` then consumes 64 bytes from the inline table at `0x00028470`,
copying two bytes into the `+4` and `+8` words of each of 32 slots. The first
nonzero writes observed after the upload are:

```text
0x00800014 <- 0x00000004
0x00800024 <- 0x00000008
0x00800028 <- 0x00000088
0x00800034 <- 0x00000006
0x00800044 <- 0x00000001
0x00800048 <- 0x00000001
```

The 16-byte stride and table copy are confirmed. The fields' command-length,
data, and processor-control meanings remain unknown; the trace is intentionally
kept at the bus-write level.

`von/i960/recovered_geometry_commands.c` now reconstructs the two confirmed
operations separately: clearing the `+4`/`+8` fields of 64 slots and copying
the 64-byte inline initialization table into 32 slots. The functions are
linked into the prototype but are not called by the smoke-test entry point.

The same source file also contains two further host-side slices:

- `recovered_geometry_function_command_submit()` reproduces the probable
  `(source, command, count)` register mapping at `0x28e88`, including the
  `0x00800040 <- 0x404`, normalized program word, count word, masked 16-bit
  stream, `0x00800100 <- 0x1010`, and terminating zero write.
- `recovered_geometry_frame_submission()` reproduces the confirmed phase
  selection at `0x28de8`: initialize `0x00803008` from the prior phase, poll
  bit 2 of `0x0098000c`, toggle `0x00511ba0`, and write the new phase to
  `0x00801008`.
- `recovered_geometry_batch_command_submit()` preserves the separate
  `0x28c00` path: function word `0x1414`, a count word, and a 32-bit source
  stream before the `0x1010` completion word. This is not interchangeable with
  the 16-bit masked stream at `0x28e88`.
- `recovered_geometry_command_batch_loop()` reconstructs `0x28c80`: four
  batches of `0x800` 32-bit words, source increments of `0x2000` bytes,
  command-offset increments of `0x800` before the i960 `<< 2` conversion, and
  the three frame handoffs between batches. The trailing `0xf0f` function-word
  pulses are retained exactly.

The Ghidra decompilation confirms these loop values directly: the source
parameter advances by `0x2000`, the command offset advances by `0x800`, and the
batch counter exits at four. It also confirms the initial frame handoff and two
final `0xf0f` pulses.

### Geometry Pipeline Startup: `0x00028d80`

The caller-side startup routine accepts a mode/status value in its first
argument. Ghidra and the listing agree on this order:

1. Call the device/status helper at `0x28840`.
2. When the argument is zero, upload the SHARC bootstrap at `0x282e0` and the
   geometry program at `0x28620`.
3. Run initialization helpers at `0x28d08`, `0x28548`, `0x284b8`, and `0x28418`.
4. In the zero-mode path, run texture/setup helpers at `0x28120` and `0x28d30`.
5. Prepare the host buffer at `0x00509ba0` through `0x28b80`.
6. Submit that buffer through the four-batch loop at `0x28c80`.
7. Store `0xffff` at `0x0181c000` before returning.

This connects the recovered upload and command routines to their first
caller-side buffer producer. The meaning of the buffer transformation in
`0x28b80` remains the next unresolved static slice; it uses the i960 floating
point conversion helper at `0x28b40` and should not yet be rewritten as guessed
C arithmetic.

### Geometry Buffer Preparation: `0x00028b80`

The Ghidra report establishes the shape of the unresolved producer without
assigning field names:

- Input parameter is the byte address `0x00509ba0` in the startup caller.
- The loop counter starts at `0x1fff` and decrements, producing `0x2000`
  iterations.
- The output pointer advances by four bytes per iteration.
- The routine calls `0x28b40` multiple times per record.
- `0x28b40` uses i960 floating-point `logbnr`, `addr`, and `cvtzri` operations,
  then clamps the result to zero or `0x80` in its boundary cases.
- The record packing combines converted values with shifts of `8`, `16`, and
  `24` bits and reads a table at `0x00017d00`.

The generated C contains synthetic register-stack objects for this routine,
but the scalar semantics are now independently recovered from MAME's i960
implementation and the runtime output vector.

### Geometry Buffer Runtime Vector

`von/tools/trace_geometry_buffer.lua` samples the output buffer directly
through the i960 program space:

```sh
VON_GEOMETRY_SECONDS=10 ./scripts/trace-geometry-buffer.sh
```

The first bounded capture produced these states:

```text
frame 30:  hash bcc31dc5, all 0x2000 words zero
frame 270: hash 9058e6e5, 8160 of 8192 words nonzero
```

The later dump begins with 32 zero words, then:

```text
index 0x0020: 0x01010000
index 0x0021+: repeated 0x01010101 values
index 0x0041+: repeated 0x02020202 values
...
tail: repeated 0x7f7f7f7f values
```

This is a generated byte-packed ramp, not a direct copy of the input address.
It gives us a concrete output oracle for the eventual `0x28b40`/`0x28b80`
reconstruction. `von/tools/verify_geometry_buffer.py` reproduces all 8192
words exactly. `recovered_geometry_buffer_prepare()` in
`von/i960/recovered_geometry.c` implements the same raw IEEE-754 exponent
logic without relying on host floating-point behavior.

`recovered_geometry_buffer_and_batch_chain()` now connects that generator to
the recovered four-batch submitter using the original host address
`0x00509ba0`. `von/tools/verify_geometry_chain.py` verifies the complete
buffer shape and reports the four `0x800`-word source/command strides. The
chain is linked into the prototype but remains opt-in rather than being called
by the smoke-test entry point.

`recovered_geometry_pipeline_buffer_phase()` captures the confirmed suffix of
`0x28d80`: it runs the buffer/batch chain and writes `0xffff` to
`0x0181c000`. The preceding device, SHARC, texture, and board helper calls are
intentionally not folded into this function until their signatures and side
effects are recovered.

Two small startup helpers are now recovered in
`recovered_geometry_commands.c`: `recovered_geometry_initial_handshake()`
preserves the `0x28418` control/phase reset sequence, and
`recovered_geometry_register_clear()` preserves the `0x28d08` write of
`0x4004` to `0x10000000`. The larger texture initializer at `0x28548` remains
separate. `recovered_texture_initializer()` now covers that routine: two
127-entry `floor(index / 2)` ramps at `0x11400000`, followed by an `0x2080`-byte
copy from ROM address `0x02fb1d10` into `0x11401000`.

`recovered_geometry_auxiliary_submit_select()` covers `0x28d30`: when
`0x005039f4 == 4` and `0x00503a00 == 32`, it submits `0x4e4` 16-bit words from
`0x001687a4`; otherwise it submits `0x60` words from `0x001686e4`. The command
word is zero in both paths.

The startup gate at `0x28840` is more complex than its call site suggests. It
reads backup SRAM byte `0x01d00027`, subtracts one, and dispatches through the
nine-entry table at `0x2885c` (with the default path at `0x28974`). The selected
path initializes profile-dependent floating-point constants and stores values
at `0x00512bd4`, `0x00512bd8`, and `0x00512bdc` before continuing into a larger
calculation. It is recorded as `geometry_profile_dispatch`, not reconstructed
as a boolean status function.

The direct profile constants are preserved in `recovered_geometry_profile.c`
as raw IEEE-754 bit patterns. Backup values mapping to indices `0..8` are
represented explicitly; zero and out-of-range values use the observed default
triple. The subsequent table/math calculation in `0x28840` remains separate.

The texture/profile setup at `0x28120` displays the loading messages, calls
the unresolved loader `0x27e50` for two ROM-board/texture-bank ranges, and
stores the resulting profile state in `0x005039f4` and `0x00503a00`. Its first
source pointer is `0x02c00008`; the later bank uses `0x02c77438`. The loader's
return contract and decompression behavior remain intentionally unassigned.

The loader target `0x27e50` is now labeled `texture_decompressor`. Static
analysis shows it initializes `0xfed` bytes at `0x00511bb0`, clears status at
`0x00515080`, reads a four-byte big-endian header from its source pointer, and
returns zero on the normal completion path or the status word at
`0x00515080` on the alternate path. It writes decoded halfwords through the
two destination pointers supplied by `0x28120`. The bitstream algorithm is
left for a separate slice. `von/i960/recovered_texture_decompress.c` now
contains a static candidate for the decoder: 12-bit ring-buffer references,
flag-byte token selection, literal/back-reference lengths, and the
palette-based secondary-bank test.

The source header bytes observed through MAME match the reconstructed ROM
interleave exactly, but Lua `read_u8` does not expose the same byte order as
the i960 `ldob` path for this `ROM_LOAD32_WORD` region. A clean MAME write tap
at `0x2808c`, paired with CPU source and ring-read traces, resolves the loader:
flag bits are consumed per output byte, `1` selects a literal, `0` selects a
back-reference, the ring is cleared for `0xfed` bytes, and the copy length is
the low nibble plus three. The recovered model matches all 512 traced primary
halfword writes, including the ring transition at output `0x110`; Lua texture
RAM snapshots are not suitable for final validation because they can be
mid-decompression and use a different access representation. The clean source
tracing patch is `third_party/patches/0004-von-texture-source-tracing.patch`.

The complete texture path is now bounded. The compressed sources at
`0x02c00008` and `0x02c77438` come from the `main_data` ROM region
(`mpr-18648/49/50/51`), not the four dedicated texture sockets. The loader
expands them into the two 2 MiB host texture-RAM windows at `0x11000000` and
`0x11200000`; each stream currently produces `0x80000` halfwords, with the
format-table test selecting the primary or secondary sheet. The dedicated
texture sockets (`mpr-18660/58/61/59`) form a separate 16 MiB texture-ROM
region. Model 2 raster commands read UV records and texture headers from that
region unless bit `0x800000` selects texture RAM, then sample the selected
32-byte tile sheet from texture RAM. `von/tools/extract_texture_pipeline.py`
reproduces these three ROM/RAM artifacts under `von/build/disasm`.

Palette state is dynamic and must not be treated as part of the texture ROM
itself. The 15-bit palette entries at `0x01800000` are rewritten in batches;
the long `vonj` attract trace observed hundreds of updates to the `0x1000`
palette block, including alternating model-color values. The three
color-translation planes at `0x01810000` and the luma table at `0x11400000`
are likewise initialized and refreshed. This allows one indexed texture sheet
to render level materials and alternate P1/P2 model colors.
`von/tools/render_texture_palette.py` renders a selected palette state from a
captured trace; exact scene association still requires timestamped palette and
geometry-command capture.

The attract-to-battle trace reaches the modern polygon renderer and confirms
the texture command fields in use. Observed regular materials include
`32x32`, `64x64`, `64x128`, and `128x128` sheets, with atlas origins derived
from `texheader[2]` and palette bases from `(texheader[3] >> 6) & 0x3ff`.
`texheader[0]` supplies the dimensions and renderer flags, while bit `0x1000`
of `texheader[2]` selects the alternate texture sheet. The command trace
contains level-style materials with palette bases such as `0x1d1`, `0x309`,
`0x1d0`, and `0x10e`; `von/tools/extract_texture_tiles.py` extracts the
referenced tile regions and records their atlas coordinates.

The scripted coin-to-select run confirms that player-select assets are
resident and rendered before the start pulse: coin input occurs at frame 900
(about 15 seconds), select-screen texture activity begins afterward, and the
scripted start occurs at frame 1500. During that interval the renderer uses
model-sized `64x128` and `64x64` sheets with distinct palette bases such as
`0x309`, `0x10e`, and `0x1d1`. The timestamped trace is
`von/build/disasm/vonj-select-full.trace`; it is the source for separating
selectable-model variants from level and menu materials.

Geometry uses the same split between static ROM assets and runtime state. The
four polygon ROMs (`mpr-18654/55/56/57`) assemble into a 16 MiB CPU-visible
region consumed by `geo_object_data`; object addresses with bit `0x00800000`
select that ROM and the low 22 bits select a 32-bit word. The trace confirms
polygon-ROM objects with linked texture-point and texture-header addresses,
including `oba=0x0084553f`, `0x0091af12`, and `0x009e410d`. The raw region is
reproducibly generated by `von/tools/extract_geometry_rom.py`, and referenced
object windows by `von/tools/dump_geometry_objects.py`.

Animation evidence is now present in the player-select capture. From roughly
16.18 through 20.88 seconds, the same 40 polygon-ROM object addresses repeat
while thousands of distinct 3x4 transformation matrices are written. This
supports a shared-mesh, matrix-driven animation model: polygon ROM stores the
static parts, while the geometry command stream supplies per-instance
translation and rotation. The timestamped matrix instrumentation is
`third_party/patches/0008-von-geometry-matrix-tracing.patch`.

The event-sequenced trace makes an animated export possible without guessing:
each complete select-screen timestamp contains 40 object submissions, and
the latest matrix at each submission is its effective transform. The exporter
`von/tools/export_geometry_animation_gltf.py` emits 40 mesh nodes with
translation, rotation, and scale channels for 250 captured frames. Its output
is `von/build/disasm/player-select-animation.gltf`; the current animation is
the select-screen sequence, not a gameplay skeleton or a frame-swapped mesh.

The mode-3 polygon stream is exportable without applying the animation matrix:
two initial vertices are followed by attribute records, skipped normal slots,
and triangle/quad vertices; link bits in the attribute word select strip
vertex reuse. `von/tools/export_geometry_obj.py` converts a polygon-ROM object
to OBJ while preserving each record's attribute word. The largest select-screen
object tested (`oba=0x0091e76c`) produces 781 faces, confirming that the ROM
object windows contain complete mesh strips rather than isolated primitives.
`von/tools/export_geometry_gltf.py` converts those OBJ exports into
self-contained glTF 2.0 assets; the current geometry-object dump contains 40
referenced polygon-ROM objects exported this way. The animation exporter now
normalizes its matrix-derived quaternions before writing glTF rotation
accessors. `third_party/patches/0009-von-geometry-polygon-tracing.patch` adds a
trace at the MAME rasterizer boundary, after object vertices have been
transformed and before clipping, allowing the glTF mesh-plus-transform result
to be compared with the renderer's intermediate polygon stream. The trace is
limited to accepted (non-culled) polygons and includes the effective vertex
coordinates, attribute word, texture pointers, and timestamp.

The command parameter names remain probable because the ROM exposes register
roles rather than source-level types. The bus addresses, masks, counts, and
phase operations are directly confirmed.

The existing `geo_w` implementation provides a useful, but not yet independently
confirmed, field interpretation: offsets ending in `0x0` carry the command or
function word, offsets ending in `0x4` carry a command length, and offsets
ending in `0x8` carry a data length. The host initialization table supports the
slot layout but does not prove the names or units of those fields. Treat the
`+0x4`/`+0x8` labels as probable until a nonzero command stream is decoded.

### Function-Word Encoding

The first recurring nonzero command words are emitted by host routines
`0x00028c08` and `0x00028e88`. Their bus values and the normalized words
produced by the current MAME `geo_w` model are:

```text
bus write                         normalized buffer word
0x008000f0 <- 0x00000f0f         0x07800f0f
0x00800040 <- 0x00000404         0x02000404
0x00800100 <- 0x00001010         0x08001010
0x00800140 <- 0x00001414         0x0a001414
```

For low-nibble-zero command addresses, the model preserves the low 20 data
bits and places `(address >> 4) & 0x3f` in bits 23-28. The first normalized
word, `0x07800f0f`, also matches the host's earlier initialization value at
`0x00900000`, making this encoding strongly supported. The geometry processor's
interpretation of the resulting function words remains unknown.

### Frame-Synchronized Buffer Handshake

The routine at `0x00028de8` supplies the next boundary. `0x00801008` and
`0x00803008` are the geometry write-start and read-start registers exposed by
the MAME `geo_w`/`geo_r` handlers. The host uses them as buffer-pointer control,
not as geometry processor status registers. It then reads `0x0098000c`, whose
MAME handler returns video-control bits combined with the current frame number,
and polls bit 2 until it matches the prior phase. The host toggles
`0x00511ba0` and writes either `0` or `0x00010000` to `0x00801008` as the
phase changes.

This establishes a frame-synchronized command-buffer submission boundary. It
does not establish when or how the geometry processor consumes the normalized
words.

### Uploaded Stream Format Constraint

The captured upload contains 9,340 16-bit units. The sequence has one unit of
remainder modulo three, so it cannot be treated as a contiguous 48-bit
ADSP-21062 instruction image. The stream also begins with long zero/data runs
and repeated `0x0b3e` values rather than a recognizable SHARC entry sequence.
The evidence therefore supports a geometry-specific microprogram or data
stream at `0x00804000`, distinct from the separately observed SHARC bootstrap at
`0x00980000`; no SHARC disassembly is assigned to it.

## SHARC Bootstrap Upload

The separate coprocessor bootstrap begins at `0x000282e0`. The host enables
upload mode with `0x80000000` at `0x00980000`, then copies 11,038 16-bit words
from main-ROM address `0x0016b58c` to the host FIFO at `0x00884000`.

```text
source = 0x0016b58c
words  = 0x2b1e (11,038)
FIFO   = 0x00884000
```

MAME's Model 2B path forwards each FIFO word to
`adsp21062_device::external_dma_write`, masking the host write to 16 bits, and
releases the ADSP halt line when the host clears the upload bit. This confirms
the transport boundary and source ownership; the uploaded payload's SHARC
instruction/data layout and execution results remain unverified.

## What the SHARC Is Doing in MAME

The Model 2B machine configuration instantiates one real `ADSP21062` at
32 MHz, selects host boot mode, maps its data space, and enables the SHARC
recompiler. The host-to-SHARC path is therefore CPU execution, not a C-side
replacement for the game algorithm:

```text
host 0x00884000 -> FIFO -> SHARC data read
host 0x008c0000 -> SHARC external I/O write
host 0x00900000 -> shared buffer RAM
SHARC external output -> FIFO -> host 0x00884000 read
```

MAME's `sharc.cpp` and `sharcdrc.cpp` implement the SHARC instruction
semantics, including arithmetic, memory access, DMA packing, and the dynamic
recompiler. Those files provide an execution reference, but they do not
translate Virtual-On's uploaded SHARC program into readable C or identify its
math routines.

The apparent C-side math in `model2.cpp` belongs to the older TGP path:
table-backed sine/cosine, atan, reciprocal, and inverse-square-root handlers
are implemented under `model2_tgp_state`. That path is not active for Model 2B.
For the active SHARC geometry path, `0x00804000` is currently a host buffer
with logging, `0x00840000` is a logging no-op for unknown IOP registers, and a
second Geo SHARC device remains commented out. Thus the current MAME source
does not yet contain a C representation of Virtual-On's geometry math.

## First SHARC Listing

The host-uploaded payload is reproducibly extracted from the assembled i960
image and disassembled with MAME's native `unidasm` SHARC backend:

```sh
./scripts/disasm-sharc.sh
```

The extractor uses the confirmed source range `maincpu + 0x16b58c` for
`0x2b1e` 16-bit words. MAME stores SHARC program memory in 64-bit slots with
48-bit instructions, and the resulting listing contains both code and embedded
tables, so every apparent routine boundary remains provisional.
The first useful observations are:

- SHARC FIFO flag polling and reads recur around program addresses `0x0ea`,
  `0x0f0`, `0x0f6`, and `0x102`, supporting a command-consumption loop.
- `RECIPS` appears at `0x0fc` and `0x108`, with surrounding multiply/subtract
  operations. These are reciprocal-style math helpers or inlined operations.
- `RSQRTS` appears at `0x7da`, `0x963`, `0x981`, `0x9c6`, and `0x9e4`.
- Long multiply/add sequences operate on groups of registers and external
  data-memory slots, consistent with vector or matrix transforms, but their
  callers and data structures are not identified yet.

These operations can ultimately be represented in C, but exact behavior should
first be validated against SHARC semantics: `RECIPS` and `RSQRTS` are not
ordinary IEEE calls, and the program mixes packed 48-bit instructions, delayed
branches, parallel memory operations, and hardware FIFO flags. MAME's SHARC
core is currently the precise execution reference; the extracted listing is
the basis for a later C routine port.

### SHARC Service Dispatcher

The corrected 6-byte-to-8-byte program packing exposes the startup dispatcher.
Initialization at program slots `0x092-0x11d` builds a table at SHARC data
memory `0x00030000`. The main loop then:

1. Waits for FIFO input flag 0 to become non-empty.
2. Reads an opcode and masks it to the low byte.
3. Loads `DM(0x00030000 + opcode)` as an indirect program address.
4. Calls that address in the `0x20000` program-memory bank.

The first table entries identify small scalar services:

```text
opcode  target  observed body
0x00    0x133   F0 = F0 + F1
0x01    0x13b   F0 = F0 - F1
0x02    0x143   F0 = F0 * F1
0x03    0x14b   reciprocal-style polynomial/Newton operation
0x04    0x15b   division-style operation using two inputs
0x08    0x1bf   service-state initialization
```

Results are written through the SHARC output FIFO at `I1 = 0x00c00000`,
matching MAME's `copro_fifo_out` mapping. This explains why the SHARC is not
just a geometry command sink: it exposes a general math service interface.

The runtime table gives more reliable assignments for the first nontrivial
command stream. The entries are indexed by the low byte of the FIFO word:

```text
opcode  target       confirmed body
0x08    0x000201bf   reset service-state index at DM(0x30100)
0x40    0x00020af2   consume one word; store a shifted/biased value at DM(0x30148)
0x41    0x00020af9   consume one word; table-based conversion; emit one result
0x44    0x00020ba1   initialize constants at DM(0x3015c..0x3015e)
0x35    0x000208f2   consume six words; reciprocal/math result
```

The first complete normal-stream fragment in the 30-second trace is:

```text
host FIFO <- 0x00000040
host FIFO <- 0x00000005
host FIFO <- 0x00000041
host FIFO <- 0x0001b100
SHARC output -> 0x00000000, 0x00000019
```

The `0x40` and `0x41` handlers therefore establish a one-word operand
convention. The later `0x35` packet and its operand block are still being
decoded. The earlier hypothesis that `0x44` dispatched a three-operand
trigonometric handler was incorrect; `0x44` is a no-payload constant
initialization command. The trigonometric-looking handlers remain present in
the service table, but must be assigned to their actual opcodes before being
used as protocol definitions.

<!-- superseded protocol hypothesis:
If a host FIFO value `0x44` is consumed as a dispatcher opcode, the table maps
it to local slot `0xbab`. That handler consumes three input words,
sign-extends two of them, converts them to floating point, calls helper
regions at `0xdbe` and `0xdc4`, and emits at least two result words through the
output FIFO. Those helpers use polynomial constants, `pi/2`-scale values, and
reciprocal refinement, making a trigonometric or angle-related operation
probable; execution-side correlation is still needed before assigning this
handler to the observed host `0x44` writes.
-->

### Response-Side Confirmation

The bounded response instrumentation logs reads from the SHARC output FIFO as
`vonj_copro_response`. A 30-second original-ROM trace produced 256 bounded
response reads, including values with plausible IEEE-754 encodings such as:

```text
0x41cdbfa3  0xbf34fdf4  0xbf6c7957  0x3f800000
0x3e47baf0  0x3d5fffff  0x41f3014a  0x3f3504f6
```

The trace also shows repeated opcode `0x08` writes from later host routines,
but no function-port writes. Most response values are not yet paired to a
specific opcode because the bounded FIFO trace reaches its cap and the host
operand path is still only partially instrumented. The packet examples below
provide the first paired response vectors. They confirm that the SHARC is
actively returning computed numeric data rather than remaining a boot-only
coprocessor.

### Initial FIFO Packet Grammar

The 30-second trace provides the first operand-count vectors. These are
observed stream boundaries matched against the SHARC handlers, not guessed
message names:

```text
0x08                          reset service state; no payload
0x44                          initialize constants; no payload
0x40 <word>                   one operand; state conversion/update
0x41 <word>                   one operand; conversion and result
0x35 <word> x 6               six operands; vector/math result
0x1e <word> x 2               two operands; result observed
0x1b <word>                   one operand; result observed
0x1c <word>                   one operand; result observed
0x1d <word> x 2               two operands; result observed
```

A representative observed sequence is:

```text
0x40 00000005
0x41 0001b100        -> reads 00000000, 00000019
0x35 00000000 00000000 00000000 c2a00000 00000000 bf800000
                     -> reads 00000000, 80000000
0x1e 00000600 41d00000
                     -> reads 00000000, 41cdbfa3
```

The initial `0x08` at `0x0002840c` is therefore a service reset after
bootstrap, while the repeated `0x08` at `0x00003c5c` is a recurring reset or
phase command from the host UI path. The later `0x44` at `0x000bd690` is a
constant-table initialization command. The next implementation boundary is
to model these packet lengths and state transitions before attempting to port
the math bodies.

### Seeded Input Fuzzing

`von/tools/fuzz_input.lua` applies a reproducible LCG-generated state to all
twelve player-one controls, including both sticks, both shot/dash pairs, coin,
and one-player start. Each random control state is held for four emulation
frames, and the run exits after 600 callback frames. The seed is supplied with
`VON_FUZZ_SEED` inside the Toolbox container:

```sh
toolbox run --container von-mame bash -lc \
  'VON_FUZZ_SEED=1 exec /var/home/longjoel/Projects/von-arcade-decomp/third_party/mame-master/von vonj \
   -rompath /var/home/longjoel/Projects/von-arcade-decomp/von/build/disasm/rompath \
   -autoboot_script /var/home/longjoel/Projects/von-arcade-decomp/von/tools/fuzz_input.lua \
   -video none -sound none -oslog -seconds_to_run 12 -skip_gameinfo -nothrottle'
```

Seeds `1`, `2`, and `3` resolved all controls and produced identical filtered
`vonj_*` boundary events: `9340` Geo upload words, `256` bounded FIFO events,
`512` Geo commands, and `538` tile writes. This is a meaningful negative
result: the controls are reaching MAME's input fields, but this boot/attract
session does not yet expose input-dependent FIFO traffic. The traces are
`von/build/disasm/vonj-fuzz-start-seed{1,2,3}.trace`.

### Opcode `0x35` State Boundary

The host producer at `0x0006f600` is a useful protocol wrapper. It converts two
host fixed-point values, sends opcode `0x41`, consumes the returned value as an
index/divisor, and then sends opcode `0x35`. The six `0x35` operands are emitted
in this order:

```text
g6, g1, g7, g2, g4, bitwise_not(g5)
```

The values are derived from quotient operations and a lookup table at
`0x0051bb24`; they are not the original joystick coordinates. This means the
`0x41 -> 0x35` pair is one stateful host protocol operation.

The SHARC target for `0x35` is `0x000208f2`. Its entry reads six FIFO words as:

```text
R4, R0, R6, R2, R13, R12
```

It then combines those integer registers with floating-point registers and
service-table values, performs reciprocal refinement, and writes `R0` to the
output FIFO at instruction `0x908`. The handler uses floating-point state
prepared by the preceding service rather than loading all of its operands into
`F0..F12`; therefore it is a continuation of a stateful vector/matrix pipeline,
not a self-contained six-argument scalar routine. The first observed packet's
second operand is zero, matching its first observed output word of zero, but
the complete response pairing remains subject to the FIFO read/write timing
ambiguity in the current MAME trace.

The same trace records repeated host FIFO writes of `0x08` from later routines
at `0x000187d8` and `0x00003c5c`, plus recurring `0x44` values from several
host routines. One representative FIFO sequence is:

```text
0x00000044, 0x00000014, 0x00000b73, 0x0000003a, 0x000009d8
```

No function-port writes appear. Because the SHARC dispatcher and handlers
consume variable numbers of FIFO words, this sequence cannot yet be split into
opcode and operands from host writes alone. The numeric response stream
confirms active SHARC computation, but is not yet a complete test vector for a
named service.

### SHARC Documentation To Obtain

The most relevant external reference is the Analog Devices **ADSP-2106x SHARC
Processor User's Manual, Revision 2.1**, part number `82-000795-03`:

```text
https://www.analog.com/media/en/dsp-documentation/processor-manuals/50836807228561ADSP2106xSHARCProcessorUsersManual_Revision2_1.pdf
```

The useful sections are the instruction-set appendix, PM/DM memory model, host
interface, DMA controller, interrupt/flag inputs, boot modes, and floating-point
compute instructions. The companion ADSP-21060/21061/21062 datasheet is useful
for package-level bus and host-port details, but the processor manual is the
higher-value source for this ROM.

The local MAME sources remain essential executable documentation:

- `third_party/mame-master/src/devices/cpu/sharc/sharc_dasm.cpp`: instruction encoding and disassembly syntax.
- `third_party/mame-master/src/devices/cpu/sharc/sharc.cpp`: DMA packing, host boot, I/O, and core state.
- `third_party/mame-master/src/devices/cpu/sharc/sharcdrc.cpp`: execution behavior used by the recompiler.
- `third_party/mame-master/src/mame/sega/model2.cpp`: Model 2B FIFO, shared RAM, and host mappings.

The practical workflow is now: use the manual to decode an instruction and its
flags, use MAME to verify packing behavior, then use the extracted listing and
bounded host packet trace to identify routine inputs and outputs.

## Prototype Reproduction

The i960 prototype now contains the nine recovered warning records and applies
the recovered `(row << 6) + column` rule before writing directly to
`0x01000000`. Its output matches the original trace exactly:

```text
tile encoding: 0x8000 | ASCII
first tile:    offset 0x0316, value 0x8057 ('W')
last tile:     offset 0x0831, value 0x8044 ('D')
total writes:  299
```

Build and run the prototype with:

```sh
./scripts/i960-build.sh
./scripts/run-i960.sh -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
```

The output can be compared against a captured original trace with
`von/tools/compare_tile_trace.py`. The parser currently supports the recovered
warning table shape and line range; other text tables will require additional
position and encoding rules as they are encountered.

## Toolbox Baseline Trace

The reproducible Toolbox capture command is:

```sh
VON_TRACE_SECONDS=5 ./scripts/trace-von-toolbox.sh
```

The 5-second capture is `von/build/disasm/vonj-toolbox-5s.trace`. It contains
9,588 lines and confirms:

- Geo program upload begins during boot and reports `9340` dwords.
- Early Geo commands execute from host PCs `0x000284d4` and `0x0002851c`.
- Tile text writes continue through host PC `0x0001ccb0`.
- The first bounded non-initialization FIFO word observed is `0x44` at host PC
  `0x000bd690`.

The value `0x44` is retained as an observed packet word, not yet assigned a
SHARC service meaning.

The normalizer `von/tools/normalize_mame_trace.py` reports the same capture as:

```text
geo_prg_data: 9340
geo_sharc_iop_w: 10
vonj_copro_fifo: 2
vonj_geo_cmd: 75
vonj_tile_write: 147
FIFO: pc=0002840c data=00000008
      pc=000bd690 data=00000044
```

The text tile map can be rendered from the trace with:

```sh
python3 von/tools/dump_tile_trace.py \
  von/build/disasm/vonj-toolbox-5s.trace \
  --output von/build/disasm/vonj-toolbox-5s.tiles.txt
```

This reconstructs the latest 64-column tile state and decodes the observed
`0x8000 | ASCII` text tiles. Non-text tile codes are shown as spaces; decoding
those into pixel art will require the corresponding tile graphics data.

No FIFO response or function-port event occurred in this five-second idle
session. This makes `0x44` the first useful candidate for a controlled input

### Controlled IN1 Input Sweep

The Lua stimulus in `von/tools/synthetic_input.lua` drives each `IN1` player-one
field for 30 frames, releases it for 30 frames, and then advances to the next
field:

```text
Button 1, Button 2, Button 3, Button 4,
Joystick Down, Joystick Up, Joystick Right, Joystick Left
```

The direct port write initially tested was ineffective because it writes the
port output latch rather than the input state. Driving the `Button 1` field with
`set_value(1)` produced this 6-second vector:

```text
geo_prg_data: 9340        geo_sharc_iop_w: 10
vonj_copro_fifo: 14       vonj_geo_cmd: 284
vonj_tile_write: 538
```

The eight-field sweep completed with the same upload counts and produced:

```text
vonj_copro_fifo: 256      vonj_geo_cmd: 512
vonj_tile_write: 538
```

The FIFO sequence added after boot consists primarily of repeated `0x08`
writes from PC `0x00003c5c`, with an additional `0x08` from `0x000187d8`.
This confirms that player-one controls reach the host path and cause repeated
coprocessor work, but the aggregate sweep does not yet isolate each field's
packet shape. The trace is `von/build/disasm/vonj-toolbox-input-sweep-12s.trace`.
experiment, while the `0x08` write remains initialization traffic.
