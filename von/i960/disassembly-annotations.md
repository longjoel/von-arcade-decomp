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

The geometry bootstrap routine at `0x00028600` displays `"Downloading GEO prog"`
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
separate command window at `0x00800000`. Routine `0x000284e8` then copies 32
bytes from the inline table at `0x00028470` into the first two words of those
slots. The first nonzero writes observed after the upload are:

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

If a host FIFO value `0x44` is consumed as a dispatcher opcode, the table maps
it to local slot `0xbab`. That handler consumes three input words,
sign-extends two of them, converts them to floating point, calls helper
regions at `0xdbe` and `0xdc4`, and emits at least two result words through the
output FIFO. Those helpers use polynomial constants, `pi/2`-scale values, and
reciprocal refinement, making a trigonometric or angle-related operation
probable; execution-side correlation is still needed before assigning this
handler to the observed host `0x44` writes.

### Response-Side Confirmation

The bounded response instrumentation logs reads from the SHARC output FIFO as
`vonj_copro_response`. A 30-second original-ROM trace produced 256 bounded
response reads, including values with plausible IEEE-754 encodings such as:

```text
0x41cdbfa3  0xbf34fdf4  0xbf6c7957  0x3f800000
0x3e47baf0  0x3d5fffff  0x41f3014a  0x3f3504f6
```

The trace also shows repeated opcode `0x08` writes from later host routines,
but no function-port writes. The response values are not yet paired to a
specific opcode because the bounded FIFO trace reaches its cap and the host
operand path is still only partially instrumented. They do confirm that the
SHARC is actively returning computed numeric data rather than remaining a
boot-only coprocessor.

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
