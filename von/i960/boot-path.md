# i960 Boot-Path Notes

The original `vonj` host image can be reconstructed and disassembled with:

```sh
./scripts/disasm-i960.sh
```

This reads the four `maincpu` ROMs from `von/artifacts/`, applies the MAME
`ROM_LOAD32_WORD` layout, and writes ignored analysis output to
`von/build/disasm/`.

## Initial Evidence

The reconstructed image has a plausible i960 reset structure:

| Address | Value | Initial interpretation |
| ---: | ---: | --- |
| `0x00000004` | `0x000000b0` | PRCB base candidate |
| `0x0000000c` | `0x00000930` | Reset entry candidate |
| `0x00000010` | `0xfffff620` | Reset/system metadata |
| `0x000000b4` | `0x0000000c` | PRCB field used by the reset structure |
| `0x000000c4` | `0x00001c20` | PRCB table pointer candidate |
| `0x000000c8` | `0x00501400` | Interrupt stack/table pointer candidate |

The first executable-looking routine begins at `0x930`:

```text
00000930  lda 0x8f0,g5
00000938  lda 0xe00000,g6
00000940  subo 1,0,g7
00000944  ld (g5),g4
0000094c  st g4,(g6)
0000095c  bne 0x944
```

It copies a table at `0x8f0` to `0xe00000`, then copies a range beginning at
`0x00b0` into work RAM at `0x00501800`. Those destinations are the first
hardware or runtime structures to identify against the Model 2 memory map.

At `0x9c8` the routine also loads `0xff000010`, stores `0x005018b0` at
`0x00501814`, and executes `synmovq`. These operations likely establish an
early processor or bus-control state, but remain hypotheses until validated in
the MAME debugger.

The generated listing is intentionally not checked in. Future commits should
add address labels and short annotations here as runtime traces confirm the
static interpretation.

## Host-Code Cross-References

Generate a compact report of host instructions that reference documented Model
2 regions with:

```sh
python3 von/tools/analyze_i960_refs.py
```

The first boot-related sites are:

| PC | Region | Initial interpretation |
| ---: | --- | --- |
| `0x00002734` / `0x0000273c` | `0x01c00202` | I/O self-test write/read |
| `0x00028368` / `0x000283f8` | `0x00980000` | SHARC upload start/stop |
| `0x00028678` / `0x00028680` | `0x00980008` | Empty geometry control pulse |
| `0x00028690` / `0x0002873c` | `0x00980008` | Geometry upload start/stop |
| `0x00028710` | `0x00804000` | Geometry stream loop |

This gives us an initial host-code order for the next annotations: I/O board
startup, SHARC bootstrap, geometry bootstrap, then the main-data copy and
decompression callers.

The first non-bootstrap `main_data` consumer worth annotating is the routine at
`0x3c40`. When its state flag permits, it walks a table at bus address
`0x02ea2918`, consumes two 16-bit fields at a time, and passes each record
through `0x1cac8`. That helper stores the three current fields in the host
state block at `0x00504cdc`-`0x00504ce4` and returns through a saved pointer; it
is state setup, not a coprocessor dispatch.

The surrounding consumers make this a likely text/UI subsystem. `0x1cb00`
snapshots the fields into `0x00504ce8`-`0x00504cf0`, `0x1ccd0` walks a
NUL-terminated string, and `0x1cc40` emits character data to
`0x01000000`, the Model 2 tile RAM region. The table at `0x02ea2918`
therefore appears to provide formatted messages or text records rather than
bulk decompression data.

The tile writer confirms the record fields: the first field initializes the
column at `0x00504ce0`, the second initializes the row at `0x00504ce4`, and
each printable character is written at `(row << 6) + column` with `0x8000`
ORed into the character value. The column advances after each write. This
explains the warning vector without a table-specific position exception; the
remaining text-path work is to validate control characters and other tables.

Formatted diagnostics use the same writer. The formatter entry at `0xf5100`
dispatches through `0xf5190`, whose output loop calls `0x1cc40` byte by byte.
The format string at `0x0c57a0` is `"Result : Node ID = %-2d\n"`, providing
a concrete newline-bearing caller even though the warning table itself only
contains printable ASCII.

The five-second boot trace also exercises the loader's `"Done\n"` string at
`0x00028170`. It writes `Done` at offsets `0x0323`-`0x0326`; the following
`Bank1` text starts at `0x0359`, confirming a one-row (`0x40` tile) advance in
the original runtime rather than only in static disassembly.

The first table is the legal warning shown by the Japanese set:

```text
W A R N I N G
THIS GAME IS TO BE USED ONLY IN JAPAN.
EXPORT, SALES, DISTRIBUTION AND/OR
OPERATION OUTSIDE THIS AREA MAY
CONSTITUTE A VIOLATION OF INTERNATIONAL
LAWS ON COPYRIGHTS AND/OR INDUSTRIAL
PROPERTY RIGHTS AND SUBJECT THE
VIOLATING PARTY TO LEGAL PROCEEDINGS.
                   SEGA ENTERPRISES,LTD.
```

The first record is `(id=0x0016, line=0x000c)`; subsequent warning lines use
`id=0x000a` and line/layout values `0x0010` through `0x0020`. The table ends
with `(0xffff, 0xffff)`.

## Runtime Trace

Run the headless execution trace with:

```sh
./scripts/trace-i960-boot.sh
```

The trace is written to `von/build/disasm/vonj-boot.trace`. It captures the
existing MAME error/log output during one second of execution. The first run
confirms a reset path through `0x273c`, a coprocessor upload of 11,038 dwords,
and a geometry upload of 9,340 dwords. The I/O self-test at `0x01c00202` no
longer reports an unmapped access after adding a `0x200` mirror to the Model 2B
315-5649 map.

The `0x00840000` range is now an explicit logging no-op in the Model 2B
address map. The first observed setup sequence is:

```text
PC 0x286ac: 0x00003100 -> 0x00840000
PC 0x286bc: 0x0000c400 -> 0x00840008
PC 0x286c8: 0x00020000 -> 0x00840100
PC 0x286d0: 0x00000001 -> 0x00840104
PC 0x286d8: 0x00000c29 -> 0x00840108
```

The ROM then uploads 9,340 dwords through the normal geometry path. This is
enough evidence to preserve and observe the register setup, but not enough to
implement its side effects.

The captured stream is an exact little-endian match in the reconstructed
`main_data` region:

```text
stream size:          18,680 bytes
main_data offset:     0x00fc6290
i960 bus address:     0x02fc6290
```

Run `python3 von/tools/analyze_geo_upload.py` to reproduce this search. This
confirms that the upload is copied directly from the ROM-board data window,
not generated from the polygon or texture regions. MAME still discards the
program payload after counting it; the next emulation task is to identify the
target geometry processor memory and execute or model this uploaded program.

The `0x01c00202` access is now modeled as an alias of the 315-5649 register
space at `0x01c00002`. The ROM writes `0x4d`, reads the low byte back, and uses
the result to select its I/O initialization path. The mirror makes that
self-test complete without inventing a new device register; the physical
address-line reason for the alias remains to be confirmed.

The geometry bootstrap is bounded at the host boundary. The routine at
`0x00028620` derives source bus address `0x02fc6290` from the `main_data` window,
configures `0x00840000` with the ten observed writes listed in
`disassembly-annotations.md`, and streams 9,340 masked 16-bit values to
`0x00804000`. The source bytes match `main_data + 0x00fc6290` exactly. The
target processor memory and side effects remain unknown and are intentionally
not modeled.

The uploaded stream is 9,340 16-bit units, leaving one unit modulo a 3-word
group. It is therefore not treated as a contiguous 48-bit SHARC instruction
image. The `0x00804000` program-port stream remains a separate geometry
microprogram/data boundary from the SHARC bootstrap at `0x00980000`.

The SHARC bootstrap is independently bounded: `0x000282e0` enables upload mode
at `0x00980000`, transfers `0x2b1e` 16-bit words from main-ROM offset
`0x0016b58c` through `0x00884000`, then clears the upload bit. MAME forwards
these words to the ADSP-21062 external DMA interface and releases its halt
line. This transport is modeled; SHARC execution and payload interpretation
remain deferred.

The first post-upload command activity is separate from the program port. The
host clears 16-byte slots at `0x00800000`, then copies the inline table at
`0x00028470` into that window. The first nonzero observed fields are at
`0x00800014`, `0x00800024`, `0x00800028`, `0x00800034`, `0x00800044`, and
`0x00800048`, with values `4`, `8`, `0x88`, `6`, `1`, and `1`. This establishes
a slot-based geometry command boundary. MAME's existing handler labels slot
offsets `+4` and `+8` as command-length and data-length fields, respectively;
that interpretation is probable but remains unconfirmed until a nonzero
command stream is decoded.

The longer trace now provides that first nonzero command stream. Host writes at
`0x00028c08`/`0x00028e88` use low-nibble-zero command addresses, and the MAME
normalization produces `0x07800f0f`, `0x02000404`, `0x08001010`, and
`0x0a001414` from the observed `0x0f0f`, `0x0404`, `0x1010`, and `0x1414`
payloads. This validates the host-to-buffer encoding boundary, not the
processor-side command meanings.

The following routine at `0x00028de8` synchronizes submission to the video
frame counter at `0x0098000c`, then updates the geometry write-start/read-start
registers at `0x00801008`/`0x00803008`. These are buffer-pointer and phase
controls; they are not evidence that the uploaded program has executed.

## Scripted Gameplay Progression

`von/tools/gameplay_progress.lua` drives the game from boot into live battles
using direct ioport field writes (immune to host keyboard mapping issues) and
logs tilemap checksums, ASCII text overlays, and per-second PNG snapshots.

```sh
VON_PROGRESS_SECONDS=150 ./scripts/trace-von-progress.sh
```

Outputs (ignored): `von/build/disasm/vonj-progress-<s>.trace`,
`...s.lua.log`, and `vonj-progress-snaps/vonj/NNNN.png`.

Confirmed attract-to-battle flow at 60 fps frame timing:

| Frame | Input | Observed result |
| ---: | --- | --- |
| ~900 | Coin 1 pulse | `MACHINE SELECT / PRESS BUTTON` opens with the 1P cursor on Temjin |
| ~1500 | 1 Player Start pulse | Machine confirmed; launch animation, then battle starts |
| 1800-7000 | stick/shot combat phase | Live battle: damage numbers, enemy health depletion, round victory |
| ~7300+ | (none) | Round 2 loads on a new stage; on eventual loss, `CONTINUE?` countdown with `INSERT COIN(S)` |

The warning screen auto-dismisses; menus after it use graphics tiles, not
ASCII text tiles, so progression is verified through snapshots and tilemap
checksums rather than text decoding. The battle session raises coprocessor
FIFO traffic from ~14.1M events (idle attract) to ~15.3M events over 150
seconds and exercises host code far beyond the boot PCs. This scripted
scenario supersedes the earlier random-input fuzzing as the coverage driver:
traces from these sessions are the source of new host PCs and SHARC opcodes
to annotate.

`boot-trace.cmd` contains debugger breakpoints and watchpoints for interactive
use with a MAME debugger frontend. The headless `none` backend does not process
debugger scripts, so those probes are kept separate from the reliable runtime
log.
