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
is state setup, not a coprocessor dispatch. This looks like a runtime
table/command consumer rather than a bulk decompressor. The next host-code
pass should identify the record format and the callers that consume that state
block.

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

`boot-trace.cmd` contains debugger breakpoints and watchpoints for interactive
use with a MAME debugger frontend. The headless `none` backend does not process
debugger scripts, so those probes are kept separate from the reliable runtime
log.
