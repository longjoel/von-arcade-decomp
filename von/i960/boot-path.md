# i960 Boot-Path Notes

> **Working notebook:** this file preserves accumulated address-level research,
> including historical and provisional interpretations. Use the
> [reconstruction handbook](../docs/reconstruction.md) for current workflow and
> require ledger-backed canonical evidence before treating a claim as validated.

The original `vonj` host image can be reconstructed and disassembled with:

```sh
./scripts/disasm-i960.sh
```

When local Docker access is unavailable, generate the same listing through the
configured remote builder with `./scripts/remote-disasm-i960.sh`.

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

## `_start_ip` control-flow seed

The reset continuation at `0x00000a0c` calls `_start_ip` at `0x00000a30`.
That helper has no conditional branches: it flushes the register cache, marks
`pfp`, initializes the first spill-frame fields at `fp-0x10` and `fp-0x0c`,
then returns to `0x00000a10`. The continuation establishes `fp`, `pfp`, and
`sp`, clears `g14`, and calls `0x000186f0`, labeled
`startup_main_data_entry`. The apparent code at `0x00000a60` is outside this
reachable `_start_ip` slice and is kept separate until a code reference is
confirmed.

The first startup routine at `0x000186f0` initializes the main-data state,
calls helpers at `0x186c0`, `0x18960`, and `0x18a10`, then enters a repeating
mode/device loop. Its indirect call loads a handler from the table at
`0x00018680`, indexed by the low nibble of `0x005039f4`; a zero handler takes
the default block at `0x18834`. The loop also reaches the status gate at
`0x18848` and device-write block at `0x188a0`, with back-edges to `0x18724`
and `0x187e4`. These labels identify control-flow targets without assigning
unverified subsystem names.

### Trace-promoted startup call sites

The 60-second attract trace visits these call sites. Their direct effects are
now named in the annotation script:

| Call site | Target | Observed role |
| --- | --- | --- |
| `0x18784` | `0x186c0` | controller/device initialization |
| `0x18788` | `0x18960` | broad system setup |
| `0x1878c` | `0x18a10` | hardware-mode/status check |
| `0x187c0` | `0x18ab0` | frame/timing service |
| `0x187e0` | `0xf50a8` | input/status formatting |
| `0x187e8` | `0x18538` | status service |
| `0x18800` | `0x294b0` | warning/text service |
| `0x18960` | `0x2730` | I/O self-test; result remains in `r4` |
| `0x18968` | `0x1c220` | video-control bootstrap |
| `0x18970` | `0x1bda0` | startup asset transfer |

The surrounding writes confirm state updates at `0x5039f4`, `0x503a00`,
`0x503a08`, and `0x504c84`; video bootstrap and asset transfer occur before
the geometry startup call at `0x189d4`. The setup wrapper is modeled by
`recovered_startup_system_setup_18960.c`, which preserves the result-string
selection, exposes the `0x504c84` latch gate, and records the ordered helper
targets through `0x2440` and `0x1bb8`.

### Early-I/O sieve pass

The same trace confirms a second semantic cluster:

| Entry | Evidence-backed interpretation |
| --- | --- |
| `0x2040` | compares a 4-byte value against the ROM signature at `0x2030`, then tests `0x2038` on the alternate path |
| `0x2080` | advances a pointer by 12 bytes and invokes the CRC helper at `0x3120` |
| `0x22f0` | computes an indexed offset and reads/writes the device block at `0x1d00014/16` |
| `0x2330` | derives a device-relative address from `0x1d0020c` and calls the device writer |
| `0x2440` | repeats the signature/CRC checks and clears `0x50240c` on failure |
| `0x2850` | uploads the fixed 21-byte command sequence at `0x2830` to `0x1c00000` |
| `0x2990` | uploads the indexed controller command sequence at `0x2980` to `0x1c00000` |
| `0x2c70` | selects the normal input initializer or a short fallback based on `0x5023e0` |
| `0x2cb0` | selects the failure-mode sampler or its return stub using `0x5023e0` |
| `0x2d60` | selects the input-byte averaging sampler or its return stub using `0x5023e0` |

The `0x2440` wrapper is now captured as a pure control plan in
`recovered_io_self_test_wrapper_2440.c`. It calls the `0x2c70` input
initializer, gates each `0x502408`/`0x502448` record on the adjusted CRC and
signature helpers, clears `0x50240c` on the signature-failure arm, and then
performs the second masked CRC/device-ready phase. Mapped record reads and
device-copy timing remain unresolved by design.

These names are based on executed trace targets plus direct dataflow. The
device semantics remain intentionally generic; the trace confirms execution
and call structure, not the meaning of every individual controller bit.

### Text/video sieve pass

The trace also reaches a coherent family of text rendering routines:

| Entry | Trace-supported role |
| --- | --- |
| `0x1d090` | writes special glyph pairs selected from the low character range |
| `0x1d1d0` | walks a terminated string and dispatches each byte to alternate glyph output |
| `0x1d210` | walks a string and dispatches each byte through the special-glyph writer |
| `0x1d570` | selects a glyph block and writes rows into the text plane |
| `0x1d880` | scans a string for a glyph-table match before writing it |
| `0x1dc10` | copies halfword rows into the tile plane with the `0x800000` attribute bit |
| `0x1dc90` | copies rows while ORing the alternate plane attribute bit |
| `0x1dd10` | writes patterned rows across multiple tile rows |
| `0x1df00` | clears a rectangular tile region |
| `0x1df70` | clears a multi-row plane region |
| `0x1e030` | saves the rendering context and branches into status rendering |

These labels are based on the repeated loop bounds and direct writes to the
tile-plane address derived from `0x00504ce0`/`0x00504ce4`. Higher-level UI
names remain provisional until message/table arguments are correlated.

### Audio/service initialization pass

The trace-confirmed helpers around `0x29a80` form a small audio-device setup
family. `0x29a80` clears the table at `0x51a0c0` after programming two values
through `0x1802000`; `0x29ae8` resets entries in the `0x504c30` service table;
`0x29b20` loops over 23 records, computes `(selector << (exponent & 0xffff)) &
mask`, reads a ROM halfword at that index, and stores it into the device window
at `0x1802010 + 2*record`. Its status tail skips `0x503aac == 0`, looks up
positive values in the ROM table at `0x2bf749c`, and maps negative values to
`0x7fff` at `0x180203e`. It then commits each nonzero pointer/value pair in
the `0x51a0c0` table and clears that slot’s pointer word. `0x29c08` clamps a
command value into `0x51a260` and clears its
adjacent state fields; and `0x29ca0` copies 64-word rows between the two
device windows at `0x1810000` and `0x1810100`. These names are based on direct
loops and mapped-address use, while the device protocol remains unresolved.

### Geometry/service sieve pass

The next trace-confirmed entries extend the startup chain into geometry
service setup. `0x292d8` uploads caller-provided words through `0x804000`
after programming `0x800060`. Its `0x294b0` caller supplies the fixed
profile prefix, headers `(0, 32)`, and the 64-word source table at `0x293b0`,
then emits the post-upload handshake and finishes through `0x28d30`.
`0x295d0` is an alternate profile upload variant: it uses `0x46000000`, the
same `(0, 32)`/`0x293b0` upload, then emits the `0x800030` setup and
`0x3f333333`/`0xbf000000` tail before finishing through `0x28d30`;
`0x296d0` initializes service pointer slots at `0x515098–0x5150b4`, then
calls `0x29778` for head `0x5150c0` with stride `0x100` and `0x29738` for
head `0x5190c0` with stride `0x40`; each fills 64 linked-list entries.

`0x29d50` transforms 32-bit buffer samples across mapped windows rooted at
`0x1810000`, `0x1810100`, `0x1814000`, and `0x1818000`. The trace also reaches
`0x2b430`, which indexes 0x54-byte object records, repeats for the record
`+0x08` count, dispatches to `0x6fd50` when the slot-left word is not below
the slot-right word or to the indirect table at `0x2b420` otherwise, and
increments the selected slot count. `0x2be30` calls the alternate `0x295d0`
profile upload, emits selectors `8` and `16`, clears `0x50427a`/`0x503c7a`,
calls `0x2a990(0xd000, 0)`, advances the frame counter, resets it and advances
the phase when it exceeds `0xb4`, then dispatches `phase % 12` through the
12-entry table at `0x2bee4`.
The table targets are geometry entry points into shared downstream code rather
than independent leaf functions; several paths converge on common returns in
the `0x2d9xx` region.

The subsequent trace comparison adds six boundary labels. `0x2d9a0` routes
geometry transforms back through the profile uploader; `0x2e1c8` and
`0x2e1e8` are paired status continuation trampolines; `0x27550` is a repeated geometry
record-transform service; `0x281f0` selects texture-profile entries through a
dispatch table; and `0x284b8` is the geometry command-window clear route.

The standalone emitter at `0x2e320` normalizes its selector, reads the packet
tuple table at `0x2bf0518`, programs `0x800010`, emits the tuple through
`0x804000`, and returns at `0x2e3c0`; the next continuation stub begins at
`0x2e3d0`.

The following object-state region contains eight bounded geometry variants at
`0x2e450`, `0x2e590`, `0x2e6f0`, `0x2e860`, `0x2e990`, `0x2eaa0`, `0x2ebb0`,
and `0x2ece0`. Each follows the same object-field and `0x884000` packet
skeleton, selects a distinct callback slot, and returns before the next
variant; the final variant returns at `0x2ef80`.

The following state dispatcher at `0x2ef90` selects one of four callbacks
from the object field at offset `0x174` and returns before `0x2f010`. Motion
variant `0x2f010` updates the object/frame fields and returns through its
continuation at `0x2f258`; parallel variant `0x2f260` returns at `0x2f35c`.

The paired status trampolines at `0x2e1c8` and `0x2e1e8` are fixed ABI
epilogues: each moves its preceding `lda` link (`0x2e1d4` or `0x2e1f4`) to
`g0`, clears `g14`, and returns through `bx(g0)`. The transform route at `0x2d9a0` is now bounded through its return at
`0x2dc40`. It calls the alternate profile uploader `0x295d0` and service
helper `0x2a990`, emits the fixed selector sequence
`8,16,10,31,29,30,10,20,21,18` through `0x884000`, and stores
response-derived frame values at `0x51aad0–0x51aae4`; the following
initializer begins at `0x2dc50`. The C model exposes those fixed edges and
destinations while leaving the unmapped FIFO response arithmetic as
caller-supplied values.

### Input/controller state cluster

### Additional startup/UI value sieve

Several previously unnamed trace targets can now be bounded from their
complete instruction slices:

| Entry | Values and behavior recovered |
| --- | --- |
| `0x18538` | polls the ring bounded by `0x504c70`/`0x504c74`; reads byte records at `0x504c60 + index`, writes the byte to `0x01c00008`, advances the index modulo `16`, and stores the result at `0x503312`; its empty-ring path compares `0x504c78` against `0x502512` before writing the fallback byte to the same port |
| `0x186c0` | writes command byte `3` to `0x005770b1`, clears `0x005770b0`, then passes `0x005770c0` to the 16-byte clear helper at `0xc5d48` |
| `0x186f0` | initializes startup state fields at `0x5039f8`, `0x504c84`, `0x5024d4`, `0x503a00`, `0x5039f4`, `0x5039f0`, `0x503aac`, and `0x503a7c` to zero after a one-count delay loop |
| `0x18960` | runs the I/O self-test, preserves its result in `r4`, performs video/asset/audio setup, then renders one of the literal strings `"MODEL 2L Original"`, `"MODEL 2L BCRX"`, or `"MODEL 2L"` |
| `0x18a10` | classifies `0x01d00028`: exact `0xff` selects state `2`, masked value `1` selects state `1`, and all other values select state `3`; state byte is written to `0x005770b1` and the flag to `0x503a08`; after `0xc5870` returns zero, mode `5` exits while other modes run 120 calls to `0x18ab0` |
| `0x1ef70`/`0x1f010` | set text-plane dimensions to `(16,18)` or `(10,13)`, then select clear or patterned tile writes based on the argument |
| `0x1efc0` | sets the same width `16` with height `2`; its nonzero branch uses source `0x2fd6d20`, row/column arguments `1,6`, while zero clears at `(31,6)` |
| `0x1f060` | loads tile data from `0x01004000 + 0x1fce520`, sets attribute bit `6`, and transfers it through `0x1bc90` |
| `0x1f080` | sets text-plane dimensions `(19,19)`; its nonzero branch transfers source `0x2fe077e` with arguments `(23,5)` and the zero branch clears at `(23,5)` |
| `0x1f0d0` | preserves four floating-point registers, then writes source `0x2fd8238` with `(10,6,10,3)` through the patterned writer, or clears a `(10,6,10,3)` region when the argument is zero |
| `0x20210` | clears the text-plane origin, writes a 30-row block through `0x1dc10`, then clears and fills the adjacent attributed region through `0x1de80` |

The literal strings, exact constants, register addresses, and branch outcomes
above are direct listing evidence. The names describe bounded effects only;
they do not claim the unresolved meaning of the controller status bits.

### Startup dispatcher control flow

The complete slice from `0x186f0` through `0x18900` is now treated as one
non-returning startup dispatcher. After the one-count stack-frame delay, the
entry clears the startup state block, seeds `0x504c88` with `1`, loads delay
constants `0x64` and `0x258`, and sets `0x504d10` to `-1`. It then calls the
controller initializer (`0x186c0`), system setup (`0x18960`), and hardware
mode classifier (`0x18a10`).

The deterministic entry prefix is modeled by
`recovered_startup_main_data_init_186f0.c`. It records the 13 initialization
stores in ROM order, including the one-valued `0x504c88`, timeout constants
`0x64/0x258`, and `0xffffffff` seed, followed by the three helper targets
`0x186c0 -> 0x18960 -> 0x18a10`.

Each iteration at `0x187e4` services timing and input, masks the controller
word at `0x502484` with `0xfffb`, and calls the warning/text service. The
current mode in `0x5039f4` is reduced to its low nibble and used to load an
indirect target from `0x18680`; a zero target repairs the mode to `1`. The
target is called with `callx`, so the table entries—not the dispatcher—are
the next control-flow boundary to recover. The selector contract is modeled
by `recovered_startup_mode_dispatch_187e4.c`; its null-entry arm clears
`0x503a00` and rejoins at `0x18848` without performing `callx`.

The `0x18848` continuation is modeled by
`recovered_startup_device_handshake_18848.c`: a clear startup flag plus
controller bit 2 or ready bit 0 selects mode `5` and clears phase after saving
the prior values, while the device loop emits command `4` and `0x0f0f`.
Device word `0x50` completes the handshake through the two observed services
and loops back to `0x18724`; other cases retry at `0x187e4`.

When the startup flag at `0x5039f0` is clear, the dispatcher checks bit `2`
of `0x5023f0` and bit `0` of `0x5024b4`. If that gate opens, it snapshots
the current mode/counter at `0x503a0c/0x503a10`, changes the mode to `5`, and
clears `0x503a00`. The device path writes byte `4` to `0x01400000`, writes
`0x00000f0f` to `0x008000f0`, and loops back until the startup flag and
device word at `0x5024f4` satisfy the completion condition. This is a
dispatcher/device handshake, not evidence of the coin-state transition.

The indirect table at `0x18680` resolves as follows (the index is the low
nibble of `0x5039f4`):

| Slot | Target | Listing-supported role |
| ---: | ---: | --- |
| 0 | `0x003c40` | publishes command `8`, walks `0x2ea2918` UI records through `0x1cac8/0x1cc40`, decrements `0x503a04`, and advances mode on completion |
| 1 | `0x02b9e0` | status/service dispatcher with mode-2 device tail and 32-entry subtable |
| 2 | `0x018650` | invokes `0x01ccf8(0)`, clears phase `0x503a00`, increments mode `0x5039f4` by one, and returns at `0x018678` |
| 3 | `0x0190d0` | runs setup `0x02a4e0(0x1111)`, clears nine phase/workspace fields, seeds phase bases, and increments mode `0x5039f4` |
| 4 | `0x019180` | submits `8/16` through `0x884000`, admits phase window `8..12` or special phase `27`, masks hardware `0x10000000`, and publishes phase `5` before shared tail `0x1922c` |
| 5 | `0x0f3f00` | masks the startup hardware word, seeds `0x5039f0/0x5039f4`, resets diagnostic state, builds `0xec820`, writes marker `0x50`, and advances the mode |
| 6 | `0x0f3fe0` | writes marker `0x50`, advances `0x5784fc` modulo 11, selects from `0xf3ec0`, dispatches the default/service handler, and copies `0x5024e8` across `0x1a7` bytes |
| 7 | `0x0f3d30` | initializes the text/video phase and selects one of the startup messages |
| 8 | `0x018620` | clears `0x5039f4`/`0x503a00` and branches through local return thunk `0x018644` |
| 9–14 | `0` | null entry; the dispatcher repairs the mode to `1` before `callx` |
| 15 | `0x018620` | same handler as slot 8 |

The attract trace’s slot-9 observation is therefore useful: it does not
identify a missing handler; it proves the null-entry recovery branch at
`0x1881c–0x1883c`, after which the next iteration runs slot 1. Slots 0, 5,
and 8 are now explicitly seeded as indirect-call targets in the annotation
script. Slot 8 is shared with slot 15 and is modeled as a phase/mode clear
followed by the local return thunk at `0x18644`; the higher-level UI meanings
of the surrounding startup phases remain intentionally unresolved.

The shared slot-4 tail at `0x1922c` performs a status-gated maintenance call
`0x1e030` for phases `7..18`, copies 20 bytes from `0x503832` to
`0x1d00016`, and, for phases `7..10` with both readiness and hardware-mode
bytes set, publishes three values from the `0x502a36` bank. Otherwise it uses
the fallback bytes at `0x1d00020/25/24`. It then indexes the 64-entry table
at `0x18b00` by `0x503a00 & 0x3f`; a null target clears the phase, advances
the mode, and returns at `0x19350`, while a populated target dispatches via
`callx` and returns at `0x19358`.

The first populated phase-table target, `0x18c00` (slot 0 of `0x18b00`),
initializes state `0x504c98` through `0x2a870(1)` and `0x31a8` when needed,
then checks device word `0x5024f4` against `16` and seven mapped offsets. The
`0x52` device exception omits the final `0xff02` check. A passing device
publishes progress `0x293` at `0x503a04`, records state through `0x1cac8(28,29)`,
sets ready `0x503a7c`, runs the three formatter calls, and advances phase
`0x503a00`. Failure with an active hardware mode and state below four emits
command `35` and sets phase `3`; otherwise the state counter increments. Both
paths clear `0x503a20` and rejoin at `0x18d9c`.

Slot 1, `0x18da0`, is the companion progress arm. It calls the common record
helper with `28,29`, formats `31 + g29`, decrements `0x503a04` when the
persistent counter `0x504c94` is zero, and repeats the same device-word and
seven mapped-check gate. The first status arm can request setup `0x1111` and
commands derived from the `0x52` check marker; the extended status arms can
clear or set ready and request setup `0x1100`. When `0x504c94` is already
nonzero it increments that counter, formats once, and either returns while the
counter is within `31 + g29`, or emits a phase-derived command, clears
progress, and advances phase (with the ready case selecting phase `3`).

Slot 2, `0x19030`, is a progress/command handshake. It increments
`0x503a04`; when the prior progress is zero it performs reset `0x1c618`, setup
`0x2a4e0(0x100b)`, and probe `0x201a0(1)`. It always masks input `0x5024e8`
with `8` for probe `0x1fff0`, emits `(marker + 31, 0xffffffff)` to the command
pair, and advances `0x503a00` only when device word `0x5024f4` equals the
marker-derived command. The arm returns at `0x190c4`.

Slot 3, `0xce670`, initializes the indexed startup workspace. It resets
`0x577590` to `12`, calls `0x29c08(0)` and `0x1ccf8(0x7cc1)`, advances
`0x503a00`, and runs helpers `0x6f9e8`, `0x6fa48`, and `0x6fad8`, publishing
the resulting value at `0x51c850`. It then copies 21 words from ROM
`0xc9220` into the record selected by `0x51c5b0 + 0x154 * index`, clears the
startup workspace fields, seeds the `0x577120..0x577138` area from the phase
and lookup tables, and performs setup calls `0xc9a00`, `0x2a4e0(0x100c)`, and
`0x2a4e0(0x130a)`. The bounded arm restores its saved registers and returns
at `0xce8ec`.

Slot 4, `0xce8f0`, consumes that workspace record. It normalizes the
countdown at `0x51c858`, runs record helpers `0xcd5b0`, `0xcd4f0`, and
`0xce100`, then checks record fields `+0x4c`, `+0x0c`, and `+0x04` together
with status bit `8` at `0x5024a4`. When admitted, it initializes nine entries
at `0x51bbd8` with `0x54`-byte spacing and increments their `+0x10` counts.
It then links the selected record through the `0x51bb30` workspace, updates
the record’s `+0x0c/+0x1c/+0x20/+0x24/+0x30` fields, calls `0x22c78`, increments
the record count at `+0x04`, and returns at `0xceab4`.

Slot 5, `0x19660`, resets the shared phase helper with argument zero, copies
the status halfword at `0x503a98` to `0x5032fc`, and emits `31 + g6` to
`0x5032f4` (adding one when `0x503a7c` is ready). It clears progress
`0x503a04`, advances phase `0x503a00`, and returns at `0x196b8`.

Slot 6, `0x196c0`, compares the device word first with `31 + g2`, then with
`31 + 0x503a98`, and finally with `32`. The primary match increments
`0x503a04`; zero progress performs `0x201a0(1)`, setup `3`, and setup
`0x100b`, while progress value `26` selects setup `0x1325`. It then probes
input `0x5024e8 & 8`. The status-derived match publishes ready `1`, clears
the command, advances phase, and selects pointers `0x5024fc/0x5024f8`; the
`32` match performs the corresponding ready/phase transition, and the final
fallback clears ready while retaining the phase advance. These branches return
at `0x19740`, `0x1979c`, `0x197e8`, and `0x19820` respectively.

Slot 7, `0x19830`, resets the phase/workspace helpers, clears
`0x503a70/0x503a74/0x503a6c`, mirrors their snapshots to
`0x50330a/0x50330c/0x50330e`, and runs `0x296d0`. It selects profile records
from `0x194a0` according to ready state, publishes the status byte from
`0x1d0001a` or `0x1d00016` through `0x2250` (with `0xff` selecting literal
`0xf423f`), records secondary status at `0x503a78`, updates the
`0x504ca0/0x504cb0/0x504cc0` record area, and advances `0x503a00` before
returning at `0x19b4c`.

Slot 8 begins at `0x19c30` with a bounded status/profile prefix. It marks
`0x503ab0` as `0xff`, clears `0x503a60`, requests setup `2`, and invokes
`0xc8fa0` when the `0x503a74` phase flag is zero. That flag maps to phase
codes `100`, `105`, or `110` at `0x503ab4`; status `0x503a18` is compared
against `0xf423e`, with the sentinel selecting literal `0xf423f` and other
values using table `0x2250`. The prefix publishes the secondary status at
`0x503a78`, records the `0x504ca0/0x504cb0/0x504cc0` tuple, computes the
`0x503a1c`-based arithmetic state through `0x1e9e0`, and enters the
ready/hardware continuation at `0x19d20`. Register operands are kept as
inputs in the C contract; the later `0x27550` dispatch remains separate.

Slot 9 begins at `0x1a280` with a progress/device gate. It decrements
`0x503a04`, clears `0x504cc8`, and requests setup `0x131b` when the prior
progress equals `31`. With zero ready state it admits the zero-progress path
or a hardware/device match; the ready path similarly requires zero progress.
Admitted paths publish `31 + r18` to `0x5032f4`, set `0x503a60`, and call the
record helper with `(14,16)` or `(14,18)` before probing through `0x1fbe0` and
advancing phase. Non-admitted paths enter the common continuation at
`0x1a3fc`; the full downstream service remains separate.

Slot 10, `0x1a4a0`, consumes the timing/result state from the preceding arm.
It gates on ready and hardware mode, updates `0x503a14` and `0x503a20` from
the `0xeff` threshold or fixed pointers `0x5024fe/0x502500`, publishes the
result halfwords at `0x5032fe/0x503300`, and enters the later common service
sequence. Its timing prefix returns to the caller path at `0x1a578`; the full
routine continues through record/service dispatch and returns at `0x1afd0`.

The recovered timing prefix at `0x1a4a0–0x1a578` makes the fixed hardware
case explicit: when ready is clear and hardware mode is set it selects
`0x5024fe/0x502500` without advancing `0x503a14`. Otherwise it signed-compares the
workspace timing value with `0xeff`, advances the phase word, and either
increments the timing value or clamps it to `0xf00` before publishing the two
halfwords.

The slot-10 continuation at `0x1a578` gates the signed progress word at
`0x503a94` before status processing at `0x1a5cc`. Only a negative progress
value enters the controller test: a zero controller byte calls `0x19b50` with
`progress-1`, while a byte above `64` calls it only for controller-word low
five-bit values `0` or `16`, passing that value as the argument. All other
cases rejoin without the helper call.

The following status split at `0x1a5cc` compares `0x503a18` against signed
threshold `0xf423e`. Values at or below the threshold continue at `0x1a620`;
higher values call `0x1cac8(6,3)`, then select text service `0x1d210` when
controller bit 4 at `0x5024e8` is set or `0x1d1f0` otherwise, rejoining at
`0x1a7c8`.

The slot-10 timing prefix at `0x1a4a0` skips the timing update and publication
when ready is clear and hardware mode is set, returning through `0x1a578`.
When ready and hardware mode are both clear but pending `0x504cc8` is nonzero,
it skips the timing comparison and reaches publication directly at `0x1a558`.
That publication loads the phase/timing words as signed halfwords before the
`stos` writes; the corresponding side effects are modeled by
`recovered_startup_mode4_arm_1a4a0_prefix.c`.

On the status-zero arm at `0x1a620`, slot 10 computes `31+r17` modulo and
divided by the phase divisor `0x503a14`, derives the `35x` stride from
`31+r16` and that remainder, and calls `0x1e800` with the resulting `(r5,r6)`
pair. When the original remainder is zero and `r5 <= 9`, it also requests
setup `0x1148`; the modeled continuation is `0x1a690`.

The ready/row gate at `0x1a690` is active only when ready `0x503a7c` is clear
and row `0x503a80` equals `9`. It masks phase `0x503a14` by `7`, `15`, `31`,
or `63` for `r5` ranges at most `0`, `1..2`, `3..5`, or at least `6`; a zero
masked phase requests setup `0x1340`. The subsequent low-phase tests set the
local latch used by the `0x1a778` continuation.

At `0x1a778`, the slot-10 timing gate stores a signed expression derived from
status `0x503a18` and phase `0x503a14` at `0x504ccc`. Only a negative value
whose low three bits are zero calls `0x29c58`, with the value divided by five
and argument `1`; all paths continue at `0x1a7d0`.

The ratio/latch gate at `0x1a820` compares `0x503ca8/0x503ca2` against
`0x5042a8/0x5042a2`. If latch `0x504cc4` is zero, the less-than arm emits
warning `0x97` (normal hardware) or `0x9f` (hardware mode), while the
equal/greater arm emits `0x91` or `0x99` and records the incoming callback
value; latched paths suppress the warning. The continuation is `0x1a8d0`.

The route at `0x1a8d0` first sends ready-clear to `0x1aad4`; with ready set,
hardware mode selects `0x1aa20`. Normal ready operation sends status/r5/r6
failures to `0x1a9e0` and the accepted zero-status/results case to `0x1a904`.

The accepted arm at `0x1a904` increments retry counter `0x504cc8`. Existing
counts at least `4` fall into the `0x1a9e0` selector; the first four visits
recompute the signed ratios `0x503ca2/0x503ca8` and `0x5042a2/0x5042a8`,
publish state/command `1/0x41`, callback/`0x40`, or `2/0x42`, and advance
through `0x1ac44` using phase `0x503a00`.

The zero-halfword selector at `0x1a9e0` checks `0x503ca2` before
`0x5042a2`. A zero first value publishes state `1`/command `0x41`; otherwise
a zero second value publishes the callback state/command `0x40`. Either
selected case advances phase through `0x1ac44`; two nonzero values continue
at `0x1ac50`.

The ready-side selector at `0x1aa20` partitions device word `0x5024f4`:
`0x40` publishes state `1`/command `0x41`, `0x41` publishes the callback
state/command `0x40`, `0x42` publishes state `2`/command `0x42`, and `0x43`
publishes state `5`/command `0x43`. Selected values advance phase through
`0x1ac44`; other values enter the common service path at `0x1ac50`.

The ready-clear entry at `0x1aad4` admits only status at most `0xf423e` with
both computed values `r5` and `r6` zero. At phase zero it increments
`0x503aa0`, calls `0x1fb50`, requests setup `0x1012`, publishes state `5` and
command `0x43`, and joins `0x1ac50`; a nonzero phase continues into the ratio
arm at `0x1ab40`, while rejected inputs go to `0x1abec`.

The nonzero-phase ratio arm at `0x1ab40` compares the same ratios as the
earlier latch gate. Less-than publishes state `1`/command `0x41`, equality
publishes state `2`/command `0x42`, and greater-than publishes the callback
state with command `0x40` while incrementing `0x503a90`; selected paths join
`0x1ac50`.

The completion tail at `0x1aee4` consumes the phase latch `r7`. A set latch
emits the fixed 13-word packet `[5,16,18,0,0,0x3dcccccd,19,0x41a00000,
0x41a00000,0x3f800000,31+r27,device-control,6]` to `0x884000`, publishes
`[0,0x400128,0x8f31a0,0]` at `0x804000`, writes `0x101` at `0x800010`, and
stores the `0x802008` value plus `0x34` at `0x801008` before returning at `0x1afd0`.

The shared phase advance at `0x1ac44` increments `0x503a00` modulo 32 bits
and enters the input/timer gate at `0x1ac50`. This is the common handoff for
the selected state/command arms at `0x1a904`, `0x1a9e0`, and `0x1aa20`.

The common-service dispatcher at `0x1ac8c` routes state `0` to `0x1ad14`,
state `1` to `0x1ace0`, state `2` to `0x1ad5c`, and state `5` to `0x1acac`.
Any other `0x503ab0` value enters the generic service path at `0x1ada0`.

The recognized state arms request setup `0x1314`, `0x1315`, `0x1313`, or
`0x1312` for states `0`, `1`, `2`, or `5`, respectively, except when ready is
clear and row is 9. They then emit warning `0x93/0x9b` for state 0 and
`0x97/0x9f` for the other states, selected by hardware mode, before joining
`0x1ada0`.

Before the common state dispatch, `0x1ac50` rejects nonpositive timer
`0x503ca0` values and timers reaching the logical `0x503ca8 >> 3` threshold.
For the remaining range it masks controller `0x5024e8` to six bits and
requests setup `0x1110` only when that mask is zero, then continues at
`0x1ac8c`.

The common service plan beginning at `0x1ada0` calls the record/object and
formatter services in a fixed order through `0x1ae64`, including indirect
targets loaded from `0x503ad4` and `0x5040d4`. It adds a final `0xdf070`
service on the `ready == 0` path; the call plan is modeled without assuming
the internals of those downstream routines.

The final gate at `0x1ae64` runs services `0xbece0`, `0x9b320`, `0x41f20`,
`0xc5530`, `0x6fec0(0)`, and `0x71080` on the record, then calls `0x23d60`
with argument `0` only when ready is set, the unsigned status word is at most
`0xf423e` (equality accepted), and both `r5` and `r6` are zero; all other
cases pass argument `1`. It then calls
`0x87f60` with the record and shared buffer before entering `0x1aee4`.

The ready-clear grid update at `0x1a7d0` increments `0x503a1c`, computes
`0xb40/(phase+1)`, scales the `31+r17` remainder by `35`, derives the
`(31+r29)` remainder against the quotient, and calls `0x1e9e0` with those
three values before continuing at `0x1a820`. Ready-set paths skip the update.

Slot 11 begins at `0x1afe0`. Its setup prefix clears marker `0x503a60`, then
derives a grid index from `0x503a1c` using divisor `r17+31`, the fixed bucket
divisor `0xb40`, and the `99x` remainder path formed by `3x` plus `96x`.
The `r29+31` remainder is also computed by the instruction sequence. It calls helper `0x1e9e0`
with that index, stores `0x503a1c - 0x504c90` at `0x503a30 + 4*0x503a80`,
and continues through the service/state sequence at `0x1b054`. The arithmetic
and write contract is modeled by `recovered_startup_mode4_arm_1afe0_prefix.c`.
The bridge at `0x1b054` repeats the record/buffer services, conditionally adds
`0xdf070` when ready is clear, copies signed halfwords `0x503ca2/0x5042a2`
to `0x503ca0/0x5042a0`, calls `0x23d60(0)`, and dispatches the state through
`0x8d0b8`; that bridge is modeled by
`recovered_startup_mode4_arm_1b054_service_bridge.c`. The later state sequence
through return `0x1b460` remains unresolved.

The state-0 arm at `0x1b184` publishes state `3` and increments `0x503a6c`.
When ready is clear it initializes or updates the signed halfword at `0x504242`
from row `0x504134` and `31+r10`, recording the callback at `0x50424a`. When
ready is set and the incremented signed progress exceeds signed `0x503a78`, it increments
`0x503a94` and calls `0x20060` followed by `0x19b50`; all paths save the
callback at `0x504b94` and rejoin `0x1b2fc`. This arm is modeled by
`recovered_startup_mode4_arm_1b184_state0_progress.c`.

The shared state-1/state-5 arm at `0x1b244` reads signed halfword latch
`0x503c42`. For mode `0x503b34 == 9`, latch `6` takes the special path;
otherwise the shifted latch is compared with sentinel `0x290000`, and a
mismatch replaces the latch with `31+r10` while recording the callback at
`0x503c4a`. It then publishes state `4`, increments `0x503a70`, saves the
callback at `0x504b94`, calls `0x20180`, and rejoins `0x1b2fc`. This arm is
modeled by `recovered_startup_mode4_arm_1b244_state45_latch.c`.

The state-2 arm at `0x1b2cc` saves the callback at `0x504b94`, increments
both `0x503a6c` and `0x503a70` modulo 32 bits, and rejoins `0x1b2fc`. This
counter handoff is modeled by
`recovered_startup_mode4_arm_1b2cc_state2_counters.c`.

Within that downstream sequence, the bounded counter seam at `0x1b2fc`
increments `0x503a74`, publishes its low halfword together with the low
halfwords of `0x503a6c` and `0x503a70` at `0x50330a/0x50330c/0x50330e`, and
selects command `20` at `0x5032f4` when ready is clear, the full signed
progress word is greater than signed `0x503a78`, and the signed row value is
greater than `8`. The corresponding
`0x31c0` trigger is modeled by `recovered_startup_mode4_arm_1b2fc_counter_publish.c`.
The terminal tail at `0x1b400` publishes either `31` or `31 + g2` to
`0x503a00`, conditionally republishes command `20` when signed `0x503a70 <=
0x503a78` with ready clear, sets `0x503a04` to `90`, and returns at `0x1b460`;
this is modeled by `recovered_startup_mode4_arm_1b400_return_tail.c`.

Slot 12 begins at `0x1b470` and repeats the slot-11 grid-index/helper setup.
Its ready-clear prefix uses the same `99x` remainder term, calls `0x1e9e0`,
and then enters `0x445a0` at `0x1b4b4`; ready-set paths skip that helper.
Its bounded progress gate at `0x1b598` requests setup `3` when
`0x503a04 == 1`; otherwise signed progress above `0xaf` diverts when bit 4 of
`0x5024a4` is set without decrementing, and the ordinary path decrements
`0x503a04`. A zero countdown or high-progress diversion reaches `0x1b614`,
while a nonzero countdown continues at `0x1b5d8`. This prefix is modeled by
`recovered_startup_mode4_arm_1b598_progress_gate.c`.
The following ready/device gate at `0x1b5d8` returns to `0x1b95c` when ready
is clear. With ready set, an exact sign-extended low-halfword `0x5024f4 == r19+31` match enters
completion helper `0x43ee8`; the fallback adds `0xffed` to the device word’s
low halfword, masks to 16 bits, and enters the same helper only when the
adjusted value is at most `1`. This contract is modeled by
`recovered_startup_mode4_arm_1b5d8_device_gate.c`.
The common completion bridge at `0x1b614` calls `0x43ee8` and then `0x423a8`
before entering the counter dispatcher at `0x1b61c`; this ordering is modeled
by `recovered_startup_mode4_arm_1b614_completion_bridge.c`.
After the completion helpers, the counter dispatcher at `0x1b61c` signed-compares
both `0x503a6c` and `0x503a70` against `0x503a78`. Only when both are at or
below the limit does it select state `8` and jump to `0x1b800`; otherwise a
secondary value at or below the limit routes to `0x1b780`, and the remaining
path goes through helper `0x31c0` at `0x1b650`. This branch contract is modeled by
`recovered_startup_mode4_arm_1b61c_counter_dispatch.c`.
The over-limit path at `0x1b650` calls `0x31c0`, increments the selected table
lane at `0xac` when `0x503a7c` is nonzero or at `0xb0` otherwise, then calls
`0x2330`. On the ready-clear path, a zero diagnostic status byte calls
`0x29c08` regardless of the status word; on the ready-set path, both the
status word and diagnostic byte must be zero. All other cases publish state
`15`/command `19`; the `0x29c08` case publishes command `20` and increments
the prior state. The final `0x184e8` notification
uses argument `0xf0` when `0x503a08` is zero and `0xf9` otherwise, then joins
`0x1b950`. This contract is modeled by
`recovered_startup_mode4_arm_1b650_over_limit_path.c`.
The ready branch at `0x1b780` stores `g14` at `0x503a84`, increments
`0x503a64`, and increments the `+0xac` entry in the `0x1d00000` table indexed
by `0x503a98`. A zero `0x503aa8` selects state `15` with command `19`; a
nonzero value selects state `5` with the low halfword of `31+r19`. Both paths continue at
`0x1b950`; this record-update contract is modeled by
`recovered_startup_mode4_arm_1b780_ready_path.c`.
The clear-ready branch at `0x1b818` initially publishes state `7`, increments
`0x503a64` and the selected `0xac` record entry, then increments row
`0x503a80`. If the new row is signed-below `9`, it overwrites the row with `g14`,
calls `0x31c0`, and publishes command `19`/state `17` before `0x1b940`;
otherwise it continues at the row-limit phase gate `0x1b8a8`. This is modeled
by `recovered_startup_mode4_arm_1b818_clear_ready_path.c`.

At `0x1b8a8`, row `5` enters a phase gate that signed-divides `0x503a1c` by
`0x503a8c` and publishes the low halfword of `31+r19`. A signed quotient at or below `0x690`
selects state `6` and row `6` at `0x1b924`; a larger quotient selects state
`27`, writes `g14` to `0x503a04`, sets bit 0 at `0x10000000`, and continues at
`0x1b940`. Other rows proceed to `0x1b914`. The recovered contract is in
`recovered_startup_mode4_arm_1b8a8_row5_gate.c`.
The terminal tail at `0x1b914` publishes the low halfword of `31+r19`; row `6` promotes
state to `28`, while other rows preserve the incoming state. It then publishes
the row low halfword at `0x5032f8`, calls `0x1fe90`, requests setup `3` through
`0x2a4e0`, and returns at `0x1b95c`. This contract is modeled by
`recovered_startup_mode4_arm_1b914_terminal_tail.c`.

Slot 15 at `0x1b960` is a compact complete handler: it calls `0x29c08`,
stores the low byte of `g14` at `0x5024c6`, publishes state `25` at `0x503a00`, and returns
at `0x1b97c`. Its state contract is modeled by
`recovered_startup_mode4_arm_1b960.c`.

Slot 16 at `0x1b9d0` masks `0x503a04` to bit 5 for helper `0x1fa30`, bypasses
the decrement when bit 4 of `0x5024a4` is set, and otherwise decrements the
counter. The link-publish continuation at `0x1ba08` is selected by the flag
path or an entry counter of `1`; it calls `0x2a4e0` with argument `2`, stores
flag `1` at `0x5039f4`, publishes resume link `0x1ba10` at `0x503a00`, and
returns at `0x1ba24`. These existing contracts are now connected with the
assembly annotations in `recovered_counter_dispatch_1b9d0.c` and
`recovered_link_publish_1ba08.c`.

Slot 17 at `0x1ba30` runs the service-head call sequence (`0x1c618`,
`0x1ccf8`, `0x2a4e0(0x1013)`, and `0x1fa00`), presets `0x503a04` to
`0x12c`, increments `0x503a00`, and returns at `0x1ba6c`. Slot 18 at
`0x1ba70` calls `0x2a4e0(0x1317)` only at counter `480`, then applies the
same flag-bit/decrement schedule and publishes state `22` before returning at
`0x1babc`. These existing contracts are connected by the slot annotations.
Slot 19 at `0x1bac0` checks for counter `0x118`, runs `0x1c618`, publishes
state `7`, clears the low 16 bits of `0x10000000`, and then advances the
counter through its return at `0x1bb4c`; its existing model remains the
bounded contract for that flag block.

Slot 20 at `0x86dc0` begins with two `0xf5d40` uploads of `0x600` bytes:
`0x51c9e0 -> 0x503ad0` and `0x51cfe0 -> 0x5040d0`. It then emits the exact
seven-word FIFO prelude `[31, *0x503ad8, *0x5040d8, 0, 0, *0x503ae0,
*0x5040e0]` at `0x884000` (the four entries are loaded values, not addresses);
response `1` continues at `0x86eec`, while other
responses branch to `0x873dc`. The secondary selector gates on that FIFO response, then reloads its selector value from `0x51c990`; this prelude is modeled by
`recovered_startup_mode4_arm_86dc0_fifo_prelude.c`. Its preceding timing
normalization at `0x86df0` is modeled by `recovered_stage_slot20_timing_86df0.c`;
the response word is loaded from `0x51c9d0`, and the downstream response table
and device behavior remain separate.
The response selector at `0x86eec` reloads its input from `0x51c98c` and handles value `10` separately by storing
`8` at `0x51c97c`. All other responses are masked to 8 bits; nonzero values
are reduced by `(value-1) % 6`, values above `0xaf` route to `0x878e8`, and
the remaining values index the table at `0x86f34`. The selector contract is
modeled by `recovered_startup_mode4_arm_86eec_response_selector.c`.
The recovered table defaults to `0x878e8`; its non-default entries are
`01->871f4`, `1f->87210`, `25->8722c`, `31->87248`, `37->87264`, `3d->87280`,
`49->8729c`, `4f->872d0`, `7f->8730c`, `85->87328`, `8b->87344`, `9d->87360`,
and `a9->8737c`. These mappings are now encoded directly in the C selector.
The response-`0x1f` handler at `0x87210` moves `g6` into `fp0`, prepares the
compare pair `r4=0/r5=0x40590000`, and routes the extended-real less-than case
to `0x878e8` or the other case to `0x87394`. Its wrapper contract is modeled by
`recovered_startup_mode4_arm_87210_response1f.c`; the real encoding remains an
explicit predicate input.
The response-1 wrapper at `0x871f4` supplies `r5=14`, `r4=1`, the loaded
`0x51c98c` value, and buffer `0x5040d0` before continuing at `0x87864`; this
ABI-facing wrapper is modeled by
`recovered_startup_mode4_arm_871f4_response1.c`.
The response-`0x25` wrapper at `0x8722c` uses the same loaded source and
buffer with `r5=10` and `r4=1`, then continues at `0x87738`; it is modeled by
`recovered_startup_mode4_arm_8722c_response25.c`.
At `0x87738`, that path publishes mode `11`, flag `1`, and the high byte of
`0x51c990`, calls `0x8c970` with buffer `0x503ad0`, and joins `0x878f8`.
This distinct continuation is modeled by
`recovered_startup_mode4_arm_87738_mode11_continuation.c`.
The secondary response-`0x1f` entry at `0x87704` repeats the extended-real
comparison against `0x40590000`, routing less-than to `0x878e8` and the other
case to `0x878a0`. Its predicate-preserving model is
`recovered_startup_mode4_arm_87704_secondary_compare_1f.c`.
The secondary response-`0x25` entry at `0x87720` has the same threshold
contract, routing less-than to `0x878e8` and the other case to `0x878a0`.
Its predicate-preserving model is
`recovered_startup_mode4_arm_87720_secondary_compare_25.c`.
The secondary response-`0x31` entry at `0x8775c` repeats this comparison and
branch contract; its model is
`recovered_startup_mode4_arm_8775c_secondary_compare_31.c`.
The secondary response-`0x37` entry at `0x87778` repeats the same comparison
and branch contract; its model is
`recovered_startup_mode4_arm_87778_secondary_compare_37.c`.
The secondary response-`0x49` entry at `0x8779c` compares against both
`0x40590000` and `0x4072c000`: below-first reaches `0x878e8`, the middle band
reaches mode-7 setup at `0x878a4`, and the high band reaches `0x878a0`. Its
model is `recovered_startup_mode4_arm_8779c_secondary_compare_49.c`.
The middle band enters the shared body at `0x878a4` after setting mode `7`;
it publishes that mode and flag `1`, stores the high byte of `0x51c990`, calls
`0x888f0`, forwards `0x5040d0` through `0x88af0`, and joins `0x878f8`. This
mode-7 continuation is modeled by
`recovered_startup_mode4_arm_878a4_mode7_continuation.c`.
The helper bodies now have explicit annotation anchors: `0x888f0` and
`0x88af0` perform timing-indexed paired uploads and 29-entry status scans,
and `0x88a10` performs the same shared upload/scan family for mode-specific
callers,
`0x8c970` is the response-25 upload/bookkeeping helper, `0x88380` builds the
FIFO response packet and command-31 follow-up, and `0xf5058` advances the
`0x5785d0` state before returning a bit-generator result. Their full device
side effects remain outside the caller-level C contracts.
The alternate `0x88af0` tail is now modeled separately: after its paired
uploads, a nonzero linked-record `+0x1d0` marker publishes the timing after
the additional six-unit subtraction at `0x51c9b8`; 29 zero-marker passes
publish `-1` instead.
The shared gate at `0x88bd0` follows that helper and selects the six-way table
at literal base `0x88cec`, loaded by the instruction at `0x88ce0`. It gates on `0x51d5e0/0x51c99c`, performs the timing-equality
state seed and conditional `0x51c9a0` publication, then derives the selector
from the indexed status byte and the `0x95` counter threshold. Its bounded
model is `recovered_startup_mode4_arm_88bd0_dispatch_gate.c`.
The `0x88bd0` selector hands off through the six-entry literal table at
`0x88cec`: selectors `0..5` target `0x88d04`, `0x88ea0`, `0x8903c`,
`0x8931c`, `0x89930`, and `0x89814`. The table contract is modeled by
`recovered_startup_mode4_arm_88cec_dispatch_table.c`.
The first arm at `0x88d04` reads record `+0x184`, emits command `29` with the
masked `-0x6000` transform and constant `0x42a00000`, emits command `30`
with the same transformed value, then consumes one FIFO response before continuing at
`0x88d70`; its bounded model is
`recovered_startup_mode4_arm_88d04_packet_prefix.c`.
The `0x88d70` continuation then publishes the response-derived state used by
the common `0x8878c` finalizer: response-plus-record-`+8` to `0x51c950`,
record-`+0x10` minus the second response to `0x51c954`, record `+0x184` to
`0x51c940`, and constant `0x42a00000` to `0x51c948`. Its bounded model is
`recovered_startup_mode4_arm_88d70_response_state_bridge.c`.
The later selector-0 suffix at `0x88e4c` emits command `10` with
`0x51c948` and the computed word, consumes one response, publishes the
computed/response pair at `0x51c94c/0x51c944`, and branches to `0x89ad8` when
record `+0x30` is zero or `0x89ac8` otherwise. Its bounded model is
`recovered_startup_mode4_arm_88e4c_state_packet.c`.
The selector-1 target at `0x88ea0` uses the linked record’s `+0x184` field
with a `+0x6000` transform for both command `29` and command `30`, retains
`0x42a00000`, and consumes the response before continuing at `0x88f04`.
Its bounded model is `recovered_startup_mode4_arm_88ea0_packet_prefix.c`.
The selector-2 arm at `0x8903c` extends the same command-29/30 family with
command `31`: its payload is the first response plus record `+8`, table words
at selector-relative `+0x10/+0x18`, and record `+0x10` minus the second
response, separated by two zeros. It is modeled by
`recovered_startup_mode4_arm_8903c_packet_prefix.c`.
The selector-3 arm at `0x8931c` emits the same command-29/30/31 family while
retaining the unmasked `record +0x184 - 0x6000` value in `0x51c940`; only the
command packet operand is reduced to 16 bits. It publishes the response-derived
`0x51c950/0x51c954` state and the shared float constant at `0x51c948`, then
continues at `0x89450`. Its bounded model is
`recovered_startup_mode4_arm_8931c_packet_state_prefix.c`.
The selector-4 arm at `0x89930` uses the positive `+0x6000` transform: its
command-29/30 operands are low-16-bit masked, but the full transformed value
is stored at `0x51c940`. It combines the two responses with record `+8` and
`+0x10`, publishes `0x51c948/0x51c950/0x51c954`, and reaches the timing branch
at `0x899d8`; its bounded model is
`recovered_startup_mode4_arm_89930_packet_state_prefix.c`.
The selector-4 tail at `0x899d8` consumes the `0x6ece0` result, keeps it when
nonpositive or substitutes `30.0f`, subtracts record `+0x0c` in the recovered
single-precision path, and emits command 10 with `0x51c948`. It preserves
`0x51c940`, stores the second response at `0x51c944`, publishes the selected
word at `0x51c94c`, and branches on record `+0x30` at `0x89ac4`; its bounded
model is `recovered_startup_mode4_arm_899d8_float_tail.c`.
The selector tails reconverge at `0x89ac8`, where record `+0x30` selects the
`0x51c9b4` value, record `+0x64 == 7` conditionally writes `g14` to
`0x51d5e0`, and the three current state fields roll forward into
`0x51c958/0x51c95c/0x51c960` for the next selector-5 pass. This common commit
is modeled by `recovered_startup_mode4_arm_common_state_commit_89ac8.c`.
The shared gate at `0x89b30` maps the counter thresholds to selector `g14/1/2/3`,
emits command 10 from current-versus-linked record deltas, stores its response
at `0x51c940`, and dispatches selectors `0..3` to `0x89c04/0x89e44/0x8a178/0x8a4bc`.
Its bounded model is `recovered_startup_mode4_arm_common_dispatch_89b30.c`.
Selector-0 downstream target `0x89c04` derives the `0xb4` timing delta,
transforms the prior FIFO response plus `0x1000`, emits command 29/30 with
the masked operand and computed word, and publishes the shared state fields
through the branch at `0x89cf4`. It is modeled by
`recovered_startup_mode4_arm_89c04_packet_state_prefix.c`.
The selector-0 floating continuation at `0x89cf4` calls `0x6ece0`, chooses the
nonpositive result or `30.0f`, emits the state-delta command 10 and a second
command 10 carrying `0x51c948` plus the computed float word, then publishes
`0x51c940/0x51c944/0x51c94c` before branching to `0x8a880` or `0x8a16c`.
It is modeled by `recovered_startup_mode4_arm_89cf4_float_packet_tail.c`.
Selector-1 downstream target `0x89e44` repeats the timing delta and
prior-response-plus-`0x1000` transform used by selector 0, emits command 29/30,
publishes the shared state fields, and continues into the selector-1 floating
tail at `0x89f34`. Its bounded model is
`recovered_startup_mode4_arm_89e44_packet_state_prefix.c`.
The selector-1 continuation at `0x89f34` calls `0x6ece0`, applies the same
nonpositive/`30.0f` selection, captures the timing predicate, and enters the
fixed-point continuation at `0x89f9c`. It is modeled by
`recovered_startup_mode4_arm_89f34_float_selection.c`.
Selector-2 downstream target `0x8a178` derives the shared timing delta and
prior-response-plus-`0x1000` transform, publishes `0x51c940/0x51c942`, and
continues into its floating/scale tail at `0x8a1c0`. It is modeled by
`recovered_startup_mode4_arm_8a178_packet_state_prefix.c`.
The selector-2 continuation at `0x8a1c0` calls `0x6ece0` using the published
state pair, applies the same nonpositive/`30.0f` selection, and enters the
scale tail at `0x8a234`. It is modeled by
`recovered_startup_mode4_arm_8a1c0_float_selection.c`.
The selector-2 scale tail emits its next packet sequence at `0x8a350`: command
29/30 use `0x51c940` low16 plus `0x51c948`, command 10 uses current/linked
record deltas, and command 31 carries the response/current/linked values before
the `0x8a43c` continuation. It is modeled by
`recovered_startup_mode4_arm_8a350_packet_sequence.c`.
The selector-2 response tail at `0x8a43c` subtracts linked record `+0x0c` from
the selected float and emits command 10 with the command-31 response plus that
delta. It preserves `0x51c950/0x51c954`, publishes the two command-10 responses
at `0x51c940/0x51c944`, and routes on record `+0x30` to `0x8a880` or `0x8a16c`;
its bounded model is `recovered_startup_mode4_arm_8a43c_response_tail.c`.
The selector-3 arm begins at `0x8a4bc`: it derives the timing delta, applies the
prior-response-plus-`0x1000` transform, publishes `0x51c940/0x51c942`, and
selects the `0x6ece0` result or `30.0f` before continuing at `0x8a584`. It is
modeled by `recovered_startup_mode4_arm_8a4bc_float_prefix.c`.
The selector-3 packet/state sequence at `0x8a670` emits command 29/30 using the
published low16/base words, derives response-relative rolling state, and then
emits command 31 with its response returned to `0x51c940`. It is modeled by
`recovered_startup_mode4_arm_8a670_packet_state.c`.
The selector-3 response tail at `0x8a7e4` completes the command-31 payload,
emits the final command-10 packet, stores its response at `0x51c944`, and routes
on record `+0x30` to `0x8a16c` or `0x8a880`. Its bounded model is
`recovered_startup_mode4_arm_8a7e4_response_tail.c`.
The success target at `0x8a880` forces `0x51c9b4 = 1` and returns; its bounded
model is `recovered_startup_mode4_arm_8a880_force_state.c`.
The selector-0 arm at `0x8a964` emits command 29/30 after the timing and
prior-response transform, publishes the packet/response state fields, and
continues at `0x8aa54`. Its bounded model is
`recovered_startup_mode4_arm_8a964_packet_state_prefix.c`.
The selector-0 floating tail at `0x8aa54` applies the helper-result selection
and timing-zero adjustment, emits two command-10 packets, publishes the final
response state, and routes on record `+0x30` to `0x8b604` or `0x8aecc`. Its
bounded model is `recovered_startup_mode4_arm_8aa54_float_packet_tail.c`.
The selector-1 helper-selection block at `0x8ac94` applies the shared
nonpositive/`30.0f` selection and timing-zero `2.5f` adjustment before entering
the fixed-point continuation at `0x8ad00`. Its bounded model is
`recovered_startup_mode4_arm_8ac94_float_selection.c`.
The selector-1 packet/state tail at `0x8ad00` commits the rolling state, emits
command 31 and two command-10 packets, publishes the two responses, and routes
on record `+0x30` to `0x8aecc` or `0x8b604`. Its bounded model is
`recovered_startup_mode4_arm_8ad00_packet_state_tail.c`.
The selector-2 post-dispatch prefix at `0x8aed8` applies the timing and
prior-response transform, publishes `0x51c940/0x51c942`, and enters the helper
continuation at `0x8af20`. Its bounded model is
`recovered_startup_mode4_arm_8aed8_packet_state_prefix.c`.
The selector-2 helper-selection block at `0x8af20` applies the shared helper
selection and timing-zero adjustment before entering fixed-point arithmetic at
`0x8af94`. Its bounded model is
`recovered_startup_mode4_arm_8af20_float_selection.c`.
The selector-2 scale/state block at `0x8af94` bounds the computed scale,
publishes the resulting `0x51c948/0x51c94c` pair, and reconverges at `0x8b0b0`.
Its bounded model is `recovered_startup_mode4_arm_8af94_scale_state.c`.
The selector-3 post-dispatch prefix at `0x8b21c` applies the timing and
prior-response transform, publishes the shared packet state, and enters the
helper continuation at `0x8b298`. Its bounded model is
`recovered_startup_mode4_arm_8b21c_packet_state_prefix.c`.
The selector-3 helper-selection block at `0x8b298` applies the shared helper
selection and timing-zero adjustment before entering fixed-point arithmetic at
`0x8b30c`. Its bounded model is
`recovered_startup_mode4_arm_8b298_float_selection.c`.
The selector-3 scale/state block at `0x8b30c` bounds the computed scale,
publishes the resulting `0x51c948/0x51c94c` pair, and reconverges at `0x8b3f4`.
Its bounded model is `recovered_startup_mode4_arm_8b30c_scale_state.c`.
The selector-3 packet/state builder at `0x8b3f4` emits command 29/30, commits
the response-relative rolling state and `0x51c94c`, and enters the command-10
boundary at `0x8b4e8`. Its bounded model is
`recovered_startup_mode4_arm_8b3f4_packet_state.c`.
The selector-3 response tail at `0x8b554` completes command 31, emits the final
command-10 packet, publishes the two responses, and routes on record `+0x30` to
`0x8aecc` or `0x8b604`. Its bounded model is
`recovered_startup_mode4_arm_8b554_response_tail.c`.
The selector-3 success target at `0x8b604` forces `0x51c9b4 = 1` and returns;
its bounded model is `recovered_startup_mode4_arm_8b604_force_state.c`.
The post-selector gate at `0x8b620` selects `g14` through threshold 61, then
selector 1 through `0x77`, otherwise selector 2, before continuing at
`0x8b678`; its bounded model is
`recovered_startup_mode4_arm_8b620_dispatch_gate.c`.
The shared `0x8b678` continuation reconciles the `0x51d5e0` flag and
`0x51d5e4/0x51c9b8` values, advances retry state while it is below 26, emits
command 10 from the current/linked record deltas, and publishes the response
at `0x51c940`; its bounded model is
`recovered_startup_mode4_arm_8b678_state_packet_bridge.c`.
The selector-0 packet prefix at `0x8b754` applies the `+0x1000` response
transform, emits command 29/30 with `0x42200000`, republishes the shared packet
state, and enters helper selection at `0x8b7e0`; its bounded model is
`recovered_startup_mode4_arm_8b754_packet_state_prefix.c`.
The selector-0 setup at `0x8b7e0` subtracts 3 from the masked operand, routes
ordered values below 1 through `0x8b830`, and otherwise applies the shared
helper selection and timing-zero adjustment before `0x8b85c`; its bounded
model is `recovered_startup_mode4_arm_8b7e0_float_selection.c`.
The selector-0 response tail at `0x8b85c` emits two command-10 packets,
publishes their responses at `0x51c940/0x51c944`, clears `0x51c94c`, and routes
record `+0x30` zero/nonzero to `0x8bfac` or `0x8bd60`; its bounded model is
`recovered_startup_mode4_arm_8b85c_response_tail.c`.
The selector-1 packet prefix at `0x8b944` applies the `+0x1000` response
transform, emits command 29/30 with `0x42200000`, prepares the masked `+0x5000`
follow-up word, and enters its arithmetic continuation at `0x8b9e4`; its
bounded model is `recovered_startup_mode4_arm_8b944_packet_prefix.c`.
The selector-1 helper-selection block at `0x8baf0` applies the unsigned timing
gate after subtracting 3, routes the low path through `0x8bb34`, and otherwise
uses the shared helper-result and timing-zero adjustment before `0x8bb60`; its
bounded model is `recovered_startup_mode4_arm_8baf0_float_selection.c`.
The selector-1 `0x8bb60` tail carries explicit record-delta fixed-point words
through a command-31 prefix and two command-10 packets, publishes rolling and
response state, and routes record `+0x30` to `0x8bd60` or `0x8bfac`; its bounded
model is `recovered_startup_mode4_arm_8bb60_packet_state_tail.c`.
The selector-1 success target at `0x8bd60` writes `g14` to `0x51c9b4` and
returns at `0x8bd70`; its bounded model is
`recovered_startup_mode4_arm_8bd60_force_state.c`.
The selector-2 packet prefix at `0x8bd74` applies the `+0x5000` response
transform, emits command 29/30 with `0x42200000`, republishes response-relative
state, and enters its arithmetic continuation at `0x8be00`; its bounded model
is `recovered_startup_mode4_arm_8bd74_packet_state_prefix.c`.
The alternate selector-1 success target at `0x8bfac` forces `0x51c9b4 = 1` and
returns at `0x8bfc0`; its bounded model is
`recovered_startup_mode4_arm_8bfac_force_state.c`.
The shared continuation at `0x8bfd0` promotes `0x51c9a0` when the scan values
match, derives the next `0x51c99c` selector, increments `0x51c9a8` below 9,
emits command 10 from record deltas, and continues at `0x8c0c8`; its bounded
model is `recovered_startup_mode4_common_dispatch_8bfd0.c`.
The selector-routing bridge at `0x8c0c8` honors the preceding equal gate to
`0x8c2cc`, then routes selector 0 to `0x8c0e0`, selector 2 to `0x8c660`, and
selector 1/default to `0x8c760`; its bounded model is
`recovered_startup_mode4_common_dispatch_8c0c8_selector_routes.c`.
The selector-0 arm at `0x8c0e0` applies the `-0x6000` response transform,
emits command 29/30 with `0x42200000`, republishes response-relative state,
and enters helper selection at `0x8c16c`; its bounded model is
`recovered_startup_mode4_arm_8c0e0_packet_state_prefix.c`.
The selector-0 response tail at `0x8c16c` emits two command-10 packets,
publishes `0x51c940/0x51c944/0x51c94c`, and routes record `+0x30` to
`0x8c904` or `0x8c8f4`; its bounded model is
`recovered_startup_mode4_arm_8c16c_response_tail.c`.
The selector-1 arm at `0x8c2cc` applies the `-0x6000` response transform,
emits command 29/30 with `0x42200000`, republishes response-relative state,
and enters helper selection at `0x8c358`; its bounded model is
`recovered_startup_mode4_arm_8c2cc_packet_state_prefix.c`.
The selector-1 helper-selection block at `0x8c358` applies the ordered timing
gate after subtracting 3, routes the low path through `0x8c3a4`, and otherwise
uses the shared helper-result and timing-zero adjustment before `0x8c3d0`; its
bounded model is `recovered_startup_mode4_arm_8c358_float_selection.c`.
The selector-1 scale/state checkpoint at `0x8c3d0` publishes `0x51c94c`, takes
the `<= 120` short path, updates rolling state, clamps negative `0x51c95c` to
`10.0f`, and continues at `0x8c510`; its bounded model is
`recovered_startup_mode4_arm_8c3d0_scale_state.c`.
The selector-1 command/response tail at `0x8c510` emits command 31 and two
command-10 packets, publishes `0x51c940/0x51c944`, selects selector 2 for a
zero marker, and routes record `+0x30` through `0x8c904`/`0x8c90c`; its
bounded model is `recovered_startup_mode4_arm_8c510_packet_state_tail.c`.
The selector-2 command/response tail at `0x8c660` emits command 31 and two
command-10 packets from rolling state, publishes `0x51c940/0x51c944`, and
routes record `+0x30` through `0x8c8f4`/`0x8c904`; its bounded model is
`recovered_startup_mode4_arm_8c660_packet_state_tail.c`.
The selector-3 arm at `0x8c760` applies the `+0x6000` record-`+0x184`
transform, emits command 29/30 with `0x42a00000`, republishes response-relative
state, and enters helper selection at `0x8c7f0`; its bounded model is
`recovered_startup_mode4_arm_8c760_packet_state_prefix.c`.
The selector-3 helper block at `0x8c7f0` performs the signed timing gate and
helper call, chooses the nonpositive helper result or `30.0f`, applies the two
timing-zero `2.5f` adjustments, and continues into the scale/state tail at
`0x8c840`; its bounded model is
`recovered_startup_mode4_arm_8c7f0_float_selection.c`.
The selector-3 scale/packet tail at `0x8c840` completes the float adjustment,
emits command 10 using `0x51c948`, publishes `0x51c94c/0x51c944`, routes the
record `+0x30` result through `0x8c8f4`/`0x8c904`, and snapshots the shared
state at `0x51c964–0x51c978`; its bounded model is
`recovered_startup_mode4_arm_8c840_scale_packet_tail.c`.
The selector-2 packet/state sequence at `0x8b0b0` emits command 29/30, builds
the following command-10/31 payloads, commits shared and rolling state, and
continues at `0x8b1a4`. Its bounded model is
`recovered_startup_mode4_arm_8b0b0_packet_state.c`.
The selector-2 response tail at `0x8b1a4` commits the shared state, emits the
final command-10 response, and routes on record `+0x30` to `0x8aecc` or
`0x8b604`. Its bounded model is
`recovered_startup_mode4_arm_8b1a4_response_tail.c`.
The selector-1 success target at `0x8aecc` writes `g14` to `0x51c9b4` and
returns; its bounded model is `recovered_startup_mode4_arm_8aecc_force_state.c`.
The post-selector dispatcher at `0x8a890` republishes the threshold-derived
selector, sends the current/linked record delta command 10, stores its response
at `0x51c940`, and routes selectors 0..3 to their downstream arms. Its bounded
model is `recovered_startup_mode4_arm_8a890_post_dispatch.c`.
The selector-5 arm at `0x89814` consumes the prior `0x51c958/0x51c95c/0x51c960`
state, emits command 10 and command 31 from record deltas and prior fields,
computes the second command-10 word as `0x51c95c - (record +0x0c)`, and emits it
with `0x51c948`. It stores the two responses and prior state back into the
shared `0x51c940` through `0x51c954` fields before continuing at `0x89930`; its bounded model is
`recovered_startup_mode4_arm_89814_state_packet_sequence.c`.
The generator’s arithmetic contract is modeled by
`recovered_runtime_math.c` and validated by `test_recovered_runtime_math.py`:
the product low-word bit 31 supplies the `chkbit` carry, which is folded with
the high word before bit 31 is cleared. The slot-20 failure bridge consumes
the resulting state through its low bit.
The `0x88380` packet-prefix model is now captured by
`recovered_startup_mode4_arm_88380_fifo_response_builder.c`: it preserves the
reverse-subtract deltas `5040d8-503ad8` and `5040e0-503ae0`, the command-10
three-word packet, and the following command-31 seven-word packet at FIFO
`0x884000`.
The exact upload phase of `0x888f0` is modeled by
`recovered_startup_mode4_arm_888f0_indexed_upload_phase.c`, including its
positive-timing `0x78` bias, paired `0x600`-byte source ranges, and 29-entry
scan boundary.
The corresponding `0x88a10` upload phase is modeled by
`recovered_startup_mode4_arm_88a10_indexed_upload_phase.c` with the same
positive-timing bias and paired upload geometry; its later status predicates
are modeled separately by `recovered_startup_mode4_arm_88a10_status_scan.c`:
the first zero status stores the current timing at `0x51c998`, while an
all-nonzero 29-pass scan stores `g14` at `0x51c9a0`.
The response-25 helper `0x8c970` has a distinct two-stage upload prefix,
modeled by `recovered_startup_mode4_arm_8c970_upload_phase.c`: it uploads the
current timing-indexed pair, scans 32 status slots, and retries from `0x8c9cc`
for up to 26 additional passes. Each pass advances timing by four with the
observed `>0x78` subtractive wrap, uploads the next pair, and enters the
status scan at `0x8ca1c`; the model also captures the matching-slot stores to
`0x51c998/0x51c994` and the no-match mode-zero store to `0x51c9a0`.
The scan body at `0x8ca1c` is independently modeled by
`recovered_startup_mode4_arm_8ca1c_status_scan.c`: it checks 32 entries with a
`0x20` stride, accepts masked status in `(lower, upper]` with a zero following
byte, stores the matching pointer/count, and returns to `0x8ca80` after either
the first match or bounded exhaustion.
The adjacent response-helper entry `0x8ca80`, called from dispatch-table
slots at `0x88760` and `0x88770`, first gates on `0x51c984 > 0x77`, publishes
the result at `0x51c99c`, and only the true arm enters the packet path at
`0x8ccfc`; this gate is modeled by
`recovered_startup_mode4_arm_8ca80_response_gate.c`.
Both packet arms at `0x8cac8` and `0x8ccfc` share a command-10 delta prefix,
then emit command 29 and command 30 with the masked FIFO response lane and
`0x42200000`; that bounded prefix is modeled by
`recovered_startup_mode4_arm_8ca80_packet_prefix.c`.
The selector-0 response/state bridge at `0x8cb00` consumes the command-29 FIFO
response, emits command 29/30 with the masked `+0x3000` lane and `0x42200000`,
publishes `0x51c940/0x51c948/0x51c950/0x51c954`, and enters helper selection at
`0x8cc0c`; its bounded model is
`recovered_startup_mode4_arm_8cb00_response_state_bridge.c`.
The selector-0 command-10 tail at `0x8cc0c` emits the two response packets
from explicit arithmetic words, publishes `0x51c940/0x51c944/0x51c94c`, and
routes record `+0x30` to the completion or retry paths at `0x8ccf0` and
`0x8d094`; its bounded model is
`recovered_startup_mode4_arm_8cc0c_command10_tail.c`.
The gate-1 response/state bridge at `0x8cd30` mirrors the selector-0 bridge:
it consumes the command-29 response, emits the masked `+0x3000` command 29/30
lane with `0x42200000`, publishes the shared response-relative state, and
enters helper selection at `0x8ce14`; its bounded model is
`recovered_startup_mode4_arm_8cd30_response_state_bridge.c`.
The gate-1 packet/state tail at `0x8ce14` emits command 31, command 29/30,
and two command-10 packets, publishes the response and rolling state words,
and enters the completion gate at `0x8d090`; its bounded model is
`recovered_startup_mode4_arm_8ce14_packet_state_tail.c`, with fixed-point and
FIFO-derived words retained as explicit inputs.
The response-helper tails converge on the `0x8d090` completion gate: a zero
word at record offset `0x30` publishes `1` to `0x51c9b4` and returns, while a
nonzero word retries through `0x8ccf0`; this gate is modeled by
`recovered_startup_mode4_arm_8d090_completion_gate.c`.
The nonzero completion branch at `0x8d0a4` is a one-instruction retry bridge
back to `0x8ccf0`; it is modeled explicitly by
`recovered_startup_mode4_arm_8d0a4_retry_bridge.c` before the callback cluster
at `0x8d0b0`.
The compact callback trampolines at `0x8d0b0`, `0x8d0d0`, and `0x8d100` are
also now modeled in `recovered_startup_mode4_arm_8d0b0_callback_trampolines.c`:
they publish/query `0x51c9d0`, conditionally return the `0x51d5e0` state, and
initialize `0x51d5e0/0x503a04/0x51c9c0` before their indirect callbacks.
The following `0x8d140` latch query uses the same callback shape against
`0x51c9c0`, returning one only for latch value `1` and otherwise zero.
The first-call branch at `0x87f80` invokes `0x8d170` after clearing
`0x51c9b0`; this initializer uploads the paired timing tables and fixed
records, uploads 90 indexed asset pairs, and seeds the two 12-byte tables
`0x5618f0/0x561e90` with `0xffff` at offsets `+4/+8`. Its exact schedule is
modeled by `recovered_startup_mode4_arm_8d170_asset_table_initializer.c`.
The scheduler caller at `0x849dc` invokes `0x8d2a0`; its recovered prefix
computes `(0x51c9b0 % 120) >> 2`, caps the index at `29`, and gives response
`10` the direct result `10` before the other responses enter normalization at
`0x8d2d0`. This selector is modeled by
`recovered_scheduler_response_selector_8d2a0.c` and feeds the existing
`0x849d0` frame-slot arithmetic model.
The normal response arm at `0x8d2d0` subtracts `0x25`, advances once from the
modulo-120-derived index before cycling through up to 30 rows, and performs a 32-entry
status scan at `0x20` stride for each row; a slot matches only when its masked
byte is greater than `lower+31`, at most `upper+31`, and its following byte is
zero. It returns `30-attempt` on the first match or `-1`
after exhaustion; low normalized values branch to the separate `0x8d390` arm,
which does not perform that initial advance.
This search skeleton is modeled by `recovered_scheduler_response_search_8d2d0.c`.
The separate low-response arm at `0x8d390` probes the same 30-row table in
reverse cyclic order, but tests the single column selected by the caller’s
upper response byte (`high_byte << 5`) and returns the probe count at the
first zero byte. Exhaustion returns `-1`; this path is modeled by
`recovered_scheduler_response_low_search_8d390.c`.
The secondary response-`0x4f` entry at `0x877d0` publishes mode `5`, flag `1`,
and the high byte of `0x51c990`, calls `0x88a10` with buffer `0x503ad0`, and
joins through `0x878d8`. Its model is
`recovered_startup_mode4_arm_877d0_secondary_mode5_side_effect.c`.
The secondary response-`0x7f` entry at `0x8780c` repeats the one-threshold
comparison, routing less-than to `0x878e8` and success to `0x878a0`; its model
is `recovered_startup_mode4_arm_8780c_secondary_compare_7f.c`.
The secondary response-`0x85` entry at `0x87828` repeats the same threshold
contract; its model is
`recovered_startup_mode4_arm_87828_secondary_compare_85.c`.
The secondary response-`0xa9` entry at `0x87888` repeats the same threshold
contract; its model is
`recovered_startup_mode4_arm_87888_secondary_compare_a9.c`.
The secondary response-`0x01` entry at `0x876e8` supplies mode `15`, loads
`0x51c990`, sets flag `1` with buffer `0x5040d0`, and enters `0x87864`; its
model is `recovered_startup_mode4_arm_876e8_secondary_mode15_setup.c`.
The response-`0x31` handler at `0x87248` repeats the response-`0x1f`
extended-real wrapper (`fp0←g6`, compare pair `r4=0/r5=0x40590000`) and
branches to `0x878e8` or `0x87394`; its predicate-preserving model is
`recovered_startup_mode4_arm_87248_response31.c`.
Primary responses `0x37` and `0x3d` use the same comparison contract at
`0x87264` and `0x87280`, with failure to `0x878e8` and success to `0x87394`.
Their shared predicate model is
`recovered_startup_mode4_arm_primary_compare_37_3d.c`.
Primary responses `0x7f`, `0x85`, and `0xa9` use the same one-threshold
comparison at `0x8730c`, `0x87328`, and `0x8737c`, branching to `0x878e8` or
`0x87394`; their shared model is
`recovered_startup_mode4_arm_primary_compare_7f_85_a9.c`.
Primary responses `0x8b` and `0x9d` set modes `10` and `4` respectively,
load `0x51c98c`, use buffer `0x5040d0`, and enter `0x87864`; their setup model
is `recovered_startup_mode4_arm_primary_setup_8b_9d.c`.
The response-`0x4f` handler at `0x872d0` sets `r5=4`, loads `0x51c98c`,
passes `0x5040d0` with `r4=1`, stores `4`/`1` at `0x51c97c/0x51c9a0`, stores
`g4 >> 8` at `0x51c994`, calls `0x88a10`, and continues at `0x873cc`. This
side-effect contract is modeled by
`recovered_startup_mode4_arm_872d0_response4f.c`.
The response-`0x49` handler at `0x8729c` compares the same `fp0` input against
`0x40590000` and then `0x4072c000`: below the first threshold routes to
`0x878e8`, the intermediate band sets `r5=6` and routes to `0x87398`, and the
high band routes to `0x87394`. Its predicate-preserving model is
`recovered_startup_mode4_arm_8729c_response49.c`.
The response `0x1f`, `0x31`, `0x37`, and high-band `0x49` paths converge at
`0x87394`: the shared block stores mode `4`, flag `1`, and `0x51c98c >> 8` to
`0x51c97c/0x51c9a0/0x51c994`, calls `0x888f0`, passes `0x503ad0` to
`0x88af0`, and continues at `0x878f8`. This shared continuation is modeled by
`recovered_startup_mode4_arm_87394_common_response.c`.
The non-`1` FIFO response path enters a second selector at `0x873dc`: a
nonzero status immediately joins the failure bridge, response `10` stores park
mode `9` and continues at `0x878d8`, and other responses use the same 8-bit
normalization and `0xaf` threshold against a distinct table at `0x87428`.
Its sparse entries target secondary wrappers from `0x876e8` through `0x87888`;
this selector contract is modeled by
`recovered_startup_mode4_arm_873dc_secondary_selector.c`.
Several secondary comparison wrappers converge at `0x878a0`, which publishes
mode `5`, flag `1`, and `0x51c990 >> 8`, calls `0x888f0`, forwards
`0x5040d0` through `0x88af0`, and then joins `0x878f8`. This common mode-5
continuation is modeled by
`recovered_startup_mode4_arm_878a0_mode5_continuation.c`.
The response-1 wrapper and several secondary handlers converge at `0x87864`:
the block publishes the caller-supplied mode, flag `1`, and the high byte of
`0x51c990`, calls `0x88a10` with buffer `0x503ad0`, and joins `0x878f8`.
This shared mode continuation is modeled by
`recovered_startup_mode4_arm_87864_mode_continuation.c`.
The parallel callback gate at `0x87a10` uses trampoline `0x87a98`: bit 4 of
`0x5024a4` returns `1`, zero `0x503a7c` returns `0`, and nonzero control with
exception `0x61`/`0x63` stores command `0x63` when `0x503a70 <= 0x503a78`,
otherwise `0x61`, before returning `1`.
The fixed tail at `0x87b10` calls `0x294b0`, emits literal FIFO words `8` and
`16` to `0x884000`, and continues at `0x87b2c` by reloading `0x51c988`. This
tail is modeled by `recovered_stage_secondary_fifo_tail_87b10.c`; the dynamic
retry loop preceding it is modeled separately as a control-only contract.
That preceding controller is now bounded at `0x87ac0`: phase `20` or a probe
result other than `1` goes directly to `0x87b2c`; otherwise the callback gate
is consulted, and a zero result invokes `0x8d108` before `0x87b10`. A nonzero
gate result retries `0x18ab0` with `r4=0..4`, invoking `0x8d108` on the first
nonzero callback result or entering `0x87b10` after exhaustion. The helper
return values remain explicit model inputs in
`recovered_stage_secondary_probe_loop_87ac0.c`.
The `0x87b2c` continuation then advances the nonzero `0x51c988` state or the
zero-state timing word `0x51d5e4`, retaining timing through `0x77` and storing
zero above that limit. It runs the fixed helper sequence
`0x88620/0xc8f10/0x6fec0/0x9b308/0x6fec0/0xc8f60`, selects `0x503ad0` when
`0x51c9b4` is zero or `0x5040d0` otherwise for `0x9baa0`, then calls `0xde990`.
This state/timing prefix is modeled by
`recovered_stage_secondary_state_prefix_87b2c.c`; helper internals remain
outside the bounded contract.
The following bridge at `0x87bbc` calls `0xde990`, applies `0xbe1f0`,
`0xbd730`, the indirect `0x503ad4` callback, `0x23980`, and `0xdf070` to
`0x503ad0`, then applies `0x26cb8`, `0xbd810`, and the indirect `0x5040d4`
callback to `0x5040d0`. It converges at the `0x503a7c` gate at `0x87c2c` and
is modeled by `recovered_stage_secondary_service_bridge_87bbc.c`.
At `0x87c2c`, zero `0x503a7c` adds a `0xdf070` cleanup of `0x5040d0`. For a
negative `0x51c988`, the code rounds `0x51d5e4` upward by three when positive,
masks by `~3`, and performs the paired `0x400`-byte uploads only when the
original timing differs from that aligned value. It then runs
`0xbece0/0x9b320/0x41f20/0xc5530/0x6fec0/0x71080`; this gate is modeled by
`recovered_stage_secondary_indexed_upload_gate_87c2c.c`.
The `0x87ce8` timer-publication gate copies signed halfwords from
`0x51cbb0/0x51d1b0` into `0x503ca0/0x5042a0` only when `0x51c988` is
nonnegative, then calls `0x23d60` with `1`, formats through `0x1cac8` with
`(21,14)`, and calls `0x1fe60` with bit 2 of `0x5024e8`. Its bounded model is
`recovered_stage_secondary_timer_publication_87ce8.c`.
The shared command/setup bridge at `0x87d14` repeats the fixed
`0x23d60(1)` and `0x1cac8(21,14)` calls, then passes `0x5024e8 & 4` to
`0x1fe60` before entering the timing/upload branch at `0x87d38`. It is
modeled by `recovered_stage_secondary_command_setup_87d14.c`.
The timing arm at `0x87d38` rounds positive `0x51d5e4` by three and masks it
with `~3`; it admits uploads only for negative `0x51c988` and a timing value
different from the aligned result. The indexed pair uses `0x600` bytes from
`0x51d5f0`/`0x5289f0`, followed by fixed `0x580`-byte copies from
`0x560df0`/`0x561370` to `0x565320`/`0x5658a0`. This is modeled by
`recovered_stage_secondary_timing_upload_87d38.c`.
After that upload arm, `0x87de4` compares `0x51d5e4` with `0x51d5e8` and
then checks whether `0x51c988` is `-1`. Equality on both comparisons stores
`g14` to `0x51c988`; all other cases continue at `0x87e10`. This sentinel gate
is modeled by `recovered_stage_secondary_state_seed_gate_87de4.c`.
The next response gate at `0x87e10` reaches publication at `0x87e50` when
`0x51c988 > 31+r29`, flag bit 4 is set, or ready is nonzero with exception
word `0x61`/`0x63`. Otherwise it returns at `0x87f50`. At publication,
response `1` stores `g14` at `0x503ca2`, while response `0` stores it at
`0x5042a2`; the bounded model is
`recovered_stage_secondary_response_publication_gate_87e10.c`.
The response-buffer block at `0x87e70` admits the two `0x600`-byte transfers
only for negative `0x51c988`, sourcing `0x51c9e0`/`0x51cfe0` into
`0x503ad0`/`0x5040d0`. It stores `g14` at `0x503c4a` and `0x50424a`, sets
`0x503a00` to `12`, calls `0x1cac8(21,14)`, and renders `0x87aa0` through
`0x1da90`; this is modeled by
`recovered_stage_secondary_response_buffer_setup_87e70.c`.
The terminal publication at `0x87ee0` stores marker `1` at `0x503a60`, maps
`0x503aa4` values `0` and `1` to progress `1` (other values become `0xb4`),
stores that progress at `0x503a04`, selects command `0x61` when
`0x503a70 <= 0x503a78` or `0x63` otherwise at `0x5032f4`, records `g14` at
`0x51d5e0`, and returns at `0x87f50`. It is modeled by
`recovered_stage_secondary_terminal_publication_87ee0.c`.
The shared helper at `0x87f60` initializes `0x51c9b0` from `g14` and calls
`0x8d170` when `0x503a14` is zero; later calls increment `0x51c9b0`. It admits
the modulo-120 upload body at `0x87fac` only when the resulting counter has
low two bits clear. This counter gate is modeled by
`recovered_stage_secondary_counter_gate_87f60.c` and connects to the existing
`recovered_startup_mode4_arm_8d170_asset_table_initializer.c` contract.
The admitted `0x87fac` body computes `0x51c9b0 % 120`, shifts the remainder by
two and multiplies the row by three for the indexed table offset, uploads
`0x600`-byte pairs from `0x51d5f0`/`0x5289f0` to caller destinations `r5`/`r6`,
then emits fixed `0x580`-byte copies from `0x560df0`/`0x561370` to
`0x565320`/`0x5658a0` before continuing at `0x88030`. It is modeled by
`recovered_stage_secondary_counter_upload_body_87fac.c` and shares its
modulo-120 row arithmetic with `0x8d2a0`.
The `0x88030` continuation reads halfwords at `r5+0x108` and `r6+0x108`,
stores them into 12-byte slots of `0x5618f0` and `0x561e90` indexed by
`0x51c9b0 % 120`, and, for nonzero counter low bits, uploads `0x400`-byte
asset pairs using `(9 * remainder) % 90` and destinations `r5+0x200`/`r6+0x200`.
It then calls `0x880c0`; the row body is modeled by
`recovered_stage_secondary_row_publication_88030.c`.
The `0x880c0` continuation independently decodes caller masks `r5` and `g1`:
overlap with `0x5024a4` yields code `2`, fallback overlap with `0x50249c`
yields code `4`, and no overlap yields `0`. Its literal lane tables are loaded
from `0x3d90` and `0x3dc0`; the decoder continues at `0x88100` and is modeled
by `recovered_stage_secondary_flag_pair_880c0.c`.
The aggregation at `0x88100` extends those lane codes: `0x5024a4` overlap
with `r6`/`g2` sets bit 4, otherwise `0x50249c` overlap with `r5`/`g1` sets
bit 5. It stores the resulting codes at offsets `+4` and `+8` in the
modulo-120 `0x5618f0` row and returns at `0x881a4`; the bounded model is
`recovered_stage_secondary_flag_aggregate_88100.c`.
The sibling slot updater at `0x881b0` loads fixed return trampoline `0x881f4`,
indexes `0x561e90` by `0x51c9b0 % 120`, and stores caller words at offsets
`+4/+8` before returning through `bx(g2)`. This complements the
`0x5618f0` aggregation and is modeled by
`recovered_stage_slot_update_trampoline_881b0.c`, alongside the existing
`recovered_stage_slot_update_881b8.c` table abstraction.
The row-value accessor at `0x88200` preserves return trampoline `0x88240`,
returns `0xffff` when `0x51c988` is nonpositive, and otherwise reads the
`0x5618f0` row at `12 * 0x51d5e4`. Its bounded model is
`recovered_stage_row_value_accessor_88200.c`.
The sibling accessor at `0x88250` applies the same positive-state and
`0xffff` sentinel gate but reads the `0x561e90` row at `12 * 0x51d5e4`,
returning through fixed trampoline `0x88290`. It is modeled by
`recovered_stage_published_row_value_accessor_88250.c` and complements the
`0x561e90` slot updater.
The paired accessor at `0x882a0` saves return trampoline `0x88304`, writes
zero to both caller outputs when `0x51c988` is nonpositive, and otherwise
reads the `0x5618f0` row at offsets `+4` and `+8` using the same 12-byte
`0x51d5e4` index. Its bounded model is
`recovered_stage_paired_row_accessor_882a0.c`; those two fields are the
values published by the `0x88100` flag aggregation.
The parallel accessor at `0x88310` returns the corresponding `+4/+8` pair
from the `0x561e90` table, using the same positive `0x51c988` gate and
12-byte `0x51d5e4` indexing, then returns through fixed trampoline `0x88374`.
Its bounded model is `recovered_stage_paired_published_row_accessor_88310.c`
and it complements the `0x881b0` slot updater.
The `0x87b2c` fixed-call sequence enters `0x88620`, whose setup prefix calls
`0x295d0`, writes FIFO words `8` and `16`, initializes through
`0x2a990(0xd000,0)`, publishes the low byte of `g14` at `0x503c7a`, and
increments/clamps `0x51c984` to `0xb4` before the mode-15 dispatch split.
The model preserves the sparse `0x88690` handler table, including each
selected buffer (`0x503ad0` or `0x5040d0`) and helper call. This connection
is modeled by `recovered_stage_secondary_frame_setup_88620.c`.
Every `0x88690` dispatch arm rejoins at `0x8878c`. The common tail snapshots
the three full-word state values into `0x504b98/0x504b9c/0x504ba0`, publishes
the `0x51c940/0x51c944` short fields at `0x504baa/0x504ba8`, emits the
opcode `20/21/18` FIFO sequence, and derives `0x504d28` plus `0x5770f4`.
Its bounded model is `recovered_stage_secondary_frame_finalize_8878c.c`.
The cross-path helper at `0x88880` is entered by the slot-10 service at
`0x1add4`. It accepts only phase `10` with record word `+0x30` clear,
extracts nonzero `+0x48` values from the record and its linked `+0x74` record
into `0x51c98c/0x51c990`, and forwards the record `+0x1d6` field with the
first state to `0x861e8`; its bounded model is
`recovered_secondary_record_state_loader_88880.c`.
The `0x888f0` upload prefix continues at `0x88948` into a 29-pass status
scan. Each pass decrements timing by four and wraps nonpositive values to
`0x78`; the first nonzero result arms the scan, and the next zero publishes
that timing to `0x51c998`. If no such pair is found, `g14` is published to
`0x51c9a0`. This continuation is modeled by
`recovered_startup_mode4_arm_888f0_status_scan.c`.
The secondary setup at `0x87850` supplies the same source and buffer contract
for modes `11` and `5`, then jumps to `0x87864`; it is modeled by
`recovered_startup_mode4_arm_87850_shared_setup.c`.
The compact entries at `0x87794` and `0x87844` supply mode `11`, while
`0x8784c` supplies mode `5`; each jumps directly to `0x87850`. Their shared
entry contract is modeled by
`recovered_startup_mode4_arm_secondary_mode_entries.c`.
The response-10 park path and the secondary mode-5 side-effect path converge
at `0x878d8`, which forwards buffer `0x5040d0` through `0x88af0` and then
enters `0x878f8`. This buffer continuation is modeled by
`recovered_startup_mode4_arm_878d8_buffer_continuation.c`.
The failure paths at `0x878e8` call `0xf5058`, retain only bit 0 of its result,
store that value at `0x51c97c`, and join the same tail at `0x878f8`. This bridge
is modeled by `recovered_startup_mode4_arm_878e8_failure_bridge.c`.
The executable connection test
`test_recovered_startup_mode4_arm_failure_prng_connection.py` compiles this
bridge with `recovered_runtime_math.c` and verifies that the returned PRNG bit
is the value stored at `0x51c97c`.
The shared tail at `0x878f8` publishes mode `1` when either status word
`0x503b34`/`0x504134` is below `7`, uploads two `0x600`-byte blocks from
`0x51d5f0 + (((index >> 2) * 3) << 9)` and `0x5289f0 + (((index >> 2) * 3) << 9)`
to `0x503ad0`/`0x5040d0`, calls `0x88380`, sets marker `0x503a60`, advances or
seeds timing `0x51d5e4` (retaining timing+1 through `0x77`, otherwise using the
seed), stores `g14` to six workspace cells, increments
`0x503a00`, and returns at `0x87a00`. This common response-tail contract is
modeled by `recovered_startup_mode4_arm_878f8_shared_tail.c`.

The diagnostic target table at `0xf3ec0` contains the eleven service entries
now connected in the C models: `0xed220`, `0xed320`, `0xed5c0`, `0xeda30`,
`0xf04d0`, `0xf0980`, `0xf1c90`, `0xf2e20`, `0xf33a0`, `0xf3ab0`, and
`0xf3c50`.

The handler-7 body at `0xf3d30` has three phase paths. With `0x503a00 == 0`
it clears `0x5024c4/0x5024c6/0x5024c8`, samples `0x20a0`, and either advances
to phase 2 or emits five `0xeaeb0` text records at x=16 (y=15, 20, 22, 24,
32) using strings at `0xf3ca0`, `0xf3cc0`, `0xf3ce0`, `0xf3d00`, and
`0xf3d10`, then advances to phase 1. With phase 1 it gates on `0xeade8`
before incrementing the phase. The later path invokes the status/device
helpers and writes the startup flag at `0x5039f0` clear. The final literal-first
comparisons are now recorded explicitly: `cmpible 0,g4` tests signed
`g4 >= 0`, followed by `cmpibl 0,g4` testing signed `g4 > 0`; the second arm
is unreachable after the first, but is retained in the contract. It returns
before the diagnostic target table at `0xf3ec0`.
Handler 6 at `0xf3fe0` services the
counter, selects from that table, mirrors input state into the runtime buffer,
and returns at `0xf4138`.

Slot 1 (`0x2b9e0`) is a real status/service dispatcher. It checks the hardware
mode byte at `0x503a08` and controller/status bytes at `0x1d00034`, `0x5023f2`,
and `0x1d00038`; the status/phase split can load `29` into `0x503a00`, while the normal
path emits byte `16` to `0x5032f4`. It masks the phase to five bits and loads
the target from the 32-entry table at `0x2b960`. A null entry advances phase to
`1`; in hardware mode `2`, the populated special target `0xe3ab0` is also
suppressed and advances phase to `1`, while other populated targets use
`callx`. The normal tail calls `0x3ba0`, and when that returns zero calls
`0x29c08`, clears phase, and advances `0x5039f4`; a nonzero timing result
returns early. The mode-2 tail begins from byte `0x5770d0`, scans device/status
records relative to `0x1a14002`, and writes a selected byte to `0x5024f0`.
The candidate scan is bounded separately below. This bounds slot 1 as a
state/service dispatcher; it does not assign the meaning of the individual 32
sub-handlers.

The mode-2 candidate scan at `0x2ba90` decrements through candidates with a
seven-word/`0x700` stride. It accepts a raw value of `32` or a value whose
`raw - 34` result passes the `0xffff`-masked threshold, then publishes the
selected candidate at `0x1a14002`; the decrement/`bg` loop scans
`count-1` through `1`, visiting index `0` only when the initial count is `1`,
and an exhausted scan returns at `0x2bb28`.

Slot 4’s phase table at `0x18b00` is a 64-entry table. Entries `0..34` are
populated with the exact targets `0x18c00`, `0x18da0`, `0x19030`, the device
and text helpers through `0x0dc6d0`, while entry `35` and the remaining masked
slots are zero. The null entries therefore take the slot-4 phase-clear and
mode-increment fallback at `0x19330` rather than representing missing table
decodes.
The listing has a clean return at `0x2bb58`; `0x2bb60` begins the following
literal weapon/status names.

The second-level table at `0x2b960` is also bounded exactly. Its populated
entries are `0:0x2b500`, `1:0x2b7b0`, `2:0x2b7e0`, `3:0x2b810`,
`4:0x2b870`, `5:0x2dc50`, `6:0x2dd30`, `7:0x2ded0`, `8:0x2b550`,
`9:0x2b660`, `10:0xd24b0`, `11:0xd2560`, `12:0xd25b0`,
`13:0xe3ab0`, `14:0xe3d00`, `29:0x2b700`, `30:0x2b770`, and
`31:0x2b940`. Slots `15–28` contain zero pointers and follow the same
null-result fallback in the caller. The gaps are intentional/default service
slots, not undecoded instructions.

The late populated arms are also bounded: `0x2b700` performs a post-test
command/video transition and returns at `0x2b76c`; `0x2b770` decrements the
status subcounter and returns through `0x2b7a4`; and `0x2b940` is a small
continuation trampoline ending at `0x2b954`.

The adjacent geometry/status dispatch at `0x2bdd0` selects one of the three
arms in the table at `0x2bdc0` using the low two bits of `0x503a00`. Its
fallback advances `0x5039f4`; the dispatcher returns at `0x2be24`, immediately
before the frame-service initializer at `0x2be30`.

Several entries are already structurally identifiable from their boundaries:
`0x2b500` performs a video/status setup and advances the mode;
`0x2b550` initializes a geometry-record workspace; `0x2b660` continues that
workspace path; `0xe3ab0` updates the device-dependent status state; and
`0xe3d00` is its associated status/score route. The remaining populated arms
are now labeled as indirect targets, with semantics deferred until their
trace PCs and complete slices are correlated.

The four selected profile handlers share a strong geometry-setup skeleton.
Each preserves the incoming record registers, calls `0x27550` twice with
different profile-table bases/float operands, clears the paired record words
at `0x5040d2` and `0x503ad2`, selects status mode `13` through `0x577590`,
invokes the common geometry/text services, resets the transient workspace at
`0x5771d0` and `0x5771e0–0x5771ea`, runs the coordinate helpers at
`0x24f98`/`0x23ca8`, advances `0x503a00`, and restores the incoming registers.

The profile-specific constants are now explicit: handler 0 uses table entry
`0x19360` with float `0xc2c80000` followed by `0x42c80000`; handler 1 uses
`0x1936c`, `0xc2c80000`, `0x41200000`, and `0x42c80000`; handler 2 uses
`0x19360`, `0xc2480000`, `0x41200000`, `0x428c0000`, and `0x42c80000`;
handler 3 uses `0x19360`, `0xc2700000`, `0x428c0000`, and `0x43160000`.
The differing operands are evidence of four profile geometry variants, not
four unrelated routines.

The common calls after each profile setup are also now seeded as functions.
`0xde670` initializes the status/geometry workspace at `0x504b90–0x504bd4`,
emits selectors `30`, `27`, `29`, and `22` through `0x884000`, and derives
the packed values later consumed by the geometry service. `0x423a8` clears two
record tables with bounds `0x33c` and `0x508`, using `0xffff` sentinels, while
`0x9b498` clears sixteen `0x10`-byte geometry slots at `0x562b80` and resets
`0x562b70`. `0xc55a8` clears the mapped table at `0x576c50` through its
`0x3f4`-byte span and initializes the related `0x577070` entries. These
helpers are setup primitives shared by the profile arms, not per-profile
state machines.
The deterministic opening store slice through `0xde710` is modeled by
`recovered_startup_geometry_workspace_init_de670.c`; it captures the fixed
`0xde630` pointer, low-halfword callback/status publications, `0x600` seeds,
`0x41d00000` float seeds, and the caller/table-derived word at `0x504bd4`.
The later selector-30/27/29 FIFO payloads and device readbacks remain outside
that initialization contract.

The source table at `0x6eb60` contains sixteen records of `0x18` bytes. The
loaders use record offsets `0x0`/`0x4` as a 64-bit pair, offset `0xc` as the
record’s profile word, and offset `0x14` as a halfword/status value. The
selected pair is published into `0x51bb24` and `0x51bb28`, while the profile
word is published at `0x51bb20`; the halfword is also forwarded into the
geometry FIFO path. This gives the runtime profile state a precise ROM source
and layout without assigning units or object semantics to the values.

The shared transform service at `0x27550` is now bounded from `0x27550` to
the return at `0x27c4c`. It initializes the object record at `g0`: offsets
`0`, `0x2`, `0x4`, `0x64`, `0x68`, `0x6c`, and `0x74` receive the incoming
record/control values, while transform fields `0x170`, `0x172`, `0x174`,
`0x176`, `0x178`, `0x17a`, `0x17c`, and `0x17e` are reset. The routine chooses
one of several local profile assets based on the mode argument, stores a
selected pointer at offset `4`, and calls `0x6f600` after publishing the
position fields at offsets `8` and `0x10`.

It then clears the record’s command/derived fields, computes the timing field
at `0x1d0/0x1d8` from the selected table value, and routes the profile through
`0xe2120`. Finally it copies the record’s transform/status halfwords into the
shared snapshot fields at `0x5033ec–0x503400` and uses `0xf5d40` to copy the
associated `0x200`-byte asset. This is a concrete object-record constructor
and transform staging routine; the record fields’ game semantics remain
unassigned.

The downstream producer at `0x6f600` is now bounded to its return at
`0x6f6ec`. It adds the two incoming values, truncates them, shifts each by
one, and masks with `0xfffffe00`. If either result has the rejected low-bit
pattern it returns the fixed value `0x47c34f80`; otherwise it emits selector
`0x41`, packs the shifted coordinates, indexes the four-word profile table at
`0x51bb24`, and writes the resulting record words through `0x884000`. This
is the concrete producer called by `0x27550`, with no C-level math/library
assumption involved.

The asset helper at `0xe2120` is a short selector wrapper: it indexes the
pointer table at `0x142e94` using the incoming asset index and calls
`0xe2040`. The latter is the three-plane byte expander; `0xe2120` itself
does not perform decompression or geometry work. This cleanly separates the
profile record path from the text/video asset path in the call graph.

The common expander at `0xe2040` is now bounded through `0xe20d4`. It selects
one of three destination planes from `g0 << 9`, rooted at `0x1810000`,
`0x1814000`, and `0x1818000`. For each of 64 iterations it consumes three
bytes from source pointer `g1`, masks each byte to `0xff`, translates it
through the halfword glyph table at `0x5775b0`, and writes the three results
to the plane pair at offsets `0` and `0x100`. The source advances by three
bytes per iteration and each destination advances by two bytes. This is a
fixed 64-triplet expansion; there is no terminator or variable-length scan.

The geometry producer’s table state is populated by two tiny loaders. The
loader at `0x6f900` treats `0x6eb60` as records with an `0x18`-byte stride,
selects the indexed record, copies its 64-bit pair and two additional words
into `0x51bb20`, `0x51bb24`, and `0x51bb28`, and emits the associated attribute
bit to `0x884000`. The sibling at `0x6f970` has the same layout and uses the
alternate continuation stub. These routines explain why `0x51bb24` is RAM
state rather than a ROM table: the producer reads the current profile words
after these loaders have filled them.

The asset table at `0x142e94` is a 32-entry pointer table with 4-byte stride;
its entries run from `0x2fb3d90` through `0x2fb54d0` in `0xc0`-byte steps.
Thus each selected source record is exactly 192 bytes, or 64 three-byte
triplets—the complete input consumed by one expansion call. The parallel
table at `0x142f34` begins with the same sequence and then diverges for the
status-specific entries later in the table. The selector wrapper therefore
does not need to know the asset format itself.

The shared initializer at `0xe2130` is the first higher-level consumer of this
bank: it expands the bank-selected tile set through `0xe1f20`, then derives
five runtime pointers from the `0x2f8d890` source base and stores them at
`0x577594`, `0x577598`, `0x57759c`, `0x5775a0`, `0x5775a4`, and `0x5775a8`.
Its return at `0xe2320` cleanly precedes the next status routine at `0xe2330`.

The geometry arms at `0x2dc50` and `0x2dd30` form an initialization/build
pair. `0x2dc50` clears the video context, initializes service pointers through
`0x296d0`, seeds `0x51aaf8/0x51aafc` to `1`, clears geometry/status fields at
`0x503a64/0x503a68`, derives three low-bit values from the shared PRNG, and
advances `0x503a00`. `0x2dd30` preserves four incoming registers, calls the
profile initializer at `0xc8fa0`, and selects one of two geometry-record paths
based on `0x503a08`. Both paths transform records through `0x27550` and commit
the resulting workspace through `0x77e20`.

The build arm seeds command/frame state from `0x51aaf8`, `0x51aafc`,
`0x503a98`, and `0x503a9c`, uses float bits `0xc2a00000` and `0x42a00000`,
clears paired record words at `0x5040d2/0x503ad2`, and finishes by invoking
the geometry pipeline and text/status service helpers. This is a recovered
pipeline contract from the original listing, not a reconstructed C
replacement.

The three device/status arms in the `0xd24b0` family are now bounded. The
initializer at `0xd24b0` selects status text mode `13`, clears the video
context, writes command `1`, seeds delay constants `0x73` and `0x258`, resets
the eight-word status workspace at `0x577270–0x57727e`, clears `0x503a7c` and
`0x503a20`, and advances `0x503a00`. The profile dispatcher at `0xd2560`
calls `0xc8fa0`; if initialization succeeds, it selects one of four handlers
from the state byte at `0x577280` (`0xd0820`, `0xd0d10`, `0xd1280`, or
`0xd1ab0`) and then calls `0x20460`. The service wrapper at `0xd25b0` uses
the same four-way selection without the profile initialization and returns
directly from the selected handler.

This separates one-time status/video setup from recurring profile service and
also identifies `0x577280` as a four-state selector. The individual handlers
remain the next useful sieve boundary; their table-like structure is now
explicit rather than hidden behind the second-level indirect call.

The `0x2ded0` arm is the frame-service continuation for that workspace. It
advances the bounded counter at `0x51ab04` while comparing the frame/timing
fields at `0x503ca0` and `0x5042a0`; when the counter expires it calls
`0x2a870` and advances `0x503a00`. It then advances `0x51aaec`, invokes the
frame-service initializer at `0x2be30`, submits two command records through
`0x6fec0`, and runs the object/transform services at `0x9b308`, `0x9c050`,
`0xde990`, `0xdf070`, and `0x41f20`.

The tail conditionally commits the paired workspaces through `0x77de0` and
`0x77e20`, updates the second record at `0x5040d0`, and checks the device
status byte at `0x1d00026`. It masks `0x51aaec` by `0x870` and compares the
result with `0x437`; the accepted path scans six `0x5024f4`-relative words,
then selects patterned or cleared text through `0x1ef70`. The routine ends
by passing the service counter to `0xe5d30`. This bounds the arm as a
geometry/frame-service phase with a text-status tail, rather than a simple
counter increment.

Three of those arms are now bounded from the original listing. `0x2b500`
resets the video/text context, writes the high-bit text command, increments
the status counter, invokes two geometry-side helpers, and clears the pending
workspace fields at `0x51aac4` and `0x503aac`. `0x2b550` saves its register
context, clears the video state, initializes a record at `0x51c5b0 +
index*0x54` from ROM constants at `0x2aa80`, advances `0x503a00`, and queues
the associated status strings. `0x2b660` drains the pending workspace through
`0x6fb90`, emits selector `16` to `0x884000`, and calls the object/service
dispatcher at `0x2b430`.

The device-state arm at `0xe3ab0` is a three-state cycle. If device byte
`0x1d00026` is zero it advances `0x503a00` by `2`; otherwise it wraps the
state at `0x5783b4` into `0..2`, dispatches to `0xe3dc0`, `0xe3f30`, or
`0xe3b70`, then increments the stored state. The state-0 path clears the
status tile region, seeds the text asset at `0x578410`, and emits the fixed
status strings visible in the listing. These are concrete service effects;
the user-facing state names remain unresolved.

The next two compact arms are timing wrappers. `0x2b7b0` adds `2` to
`0x503a00`, then branches through its local return stub at `0x2b7d8`.
`0x2b7e0` does the same with an increment of `1`, returning through
`0x2b808`. These are genuine handlers, not table padding; their local
`lda`/`bx` shape is the compiler’s indirect continuation idiom.

The adjacent `0x2b810` arm increments the service counter, clears the video
context, emits command `0x7fff`, sets the text-plane attribute bits, copies a
fixed asset through `0x1f060`, clears `0x503a04`, and returns. `0x2b870`
converts the progress counter at `0x503a04` into a text-plane coordinate at
`0x504d28`, selects status messages through `0x2a5f0`, and advances the main
service counter when the progress reaches the terminal boundary. This gives
us the first direct bridge from the status subtable to the visible startup
text path.

### Geometry arithmetic and packet constants

The next compact slices expose additional values without requiring a guessed
subsystem model:

| Entry | Directly recoverable values |
| --- | --- |
| `0x23ce8` | reads signed halfwords at object offsets `0x1d0`, `0x1d2`, and `0x1d4`; computes a wrapped 16-bit delta, applies a sign correction when bit `15` is set, suppresses a negative result when `0x503a60` is nonzero, and stores the result back at offset `0x1d2` |
| `0x32810` | copies pointer fields from offsets `0x8` and `0x10` into `0xa4`/`0xa8`, then emits the fixed packet prefix `31, field[0x8], field[0x74]+8, 0, 0`, followed by the two fields from the source record, through `0x884000` |

The `0x23ce8` description preserves the observed 16-bit operations rather
than assigning units to the values. Likewise, `0x884000` is documented as a
packet sink because the listing proves the writes, while the receiving device
protocol remains unresolved.

The geometry slice at `0x23670` emits packet selectors `10` and `29` to
`0x884000`. Its bounds checks use `0x160000`, `0x180000`, and `0x1b800000`,
with masked subranges `0x2ffe` and `0x3fe`; the floating-point constants used
by the accepted path are `0x43200000` and `0x40200000`. These are listing-level
constants only—the meaning of the coordinate and address fields is not
assigned here.

The adjacent object-branch and transform helpers preserve additional fixed
operands. The branch helper masks its object flag with `0xff`, forms wrapped
windows using additions `0x17ff` and `0x1ff`, then tests those windows against
`0x2ffe` and `0x3fe`. Its signed response tests use lower bounds `-0xdff` and
`-0xbff`; the three resulting routes are represented as `0`, `1`, and `2`.
The transform helper reads parent fields at offsets `0x14`, `0x18`, `0x1c`,
`0x1c8`, `0x150`, and `0x1cc`, applies the supplied floating scale (including
its square), and sets the output flag to `1`. These are recovered arithmetic
and field-offset facts; route or field semantics remain unassigned.

The recovered state classifiers at `0x790a4`–`0x795c4` expose further exact
case values without resolving their meanings: the state-0 arms recognize role
values `1`–`6`, the state-6 helper recognizes `1`, `3`, `4`, `6`, and `7`, and
its related-tag tests use `31` with related state `3`. The state-2 and state-4
paths load float bits `0x4072c000`; the state-5 path also loads `0x40590000`.
The classifiers use mode bit `1` and globals `0x504e30`, `0x504d68`, and
`0x504d9c` as shown by the recovered sources. Their state semantics remain
unassigned.

The object initializer at `0x23670` emits commands `0x0a`, `0x1d`, and
`0x1e` to `0x884000`. It uses float-bit constants `0x43200000` and
`0x40200000`, adjusts object field `0x08` by a signed response, copies that
result to `0x94`, and updates fields `0x90`/`0x9c` from the third response;
fields `0xa0` and `0xa1` are cleared. The response selector at `0x23ef0`
reads from `0x884000`, indexes table `0x2be0008` with state-derived values
masked to `31`, and has fallback pointers `0x49c980` and `0x40005c` selected
by the low state bit.

The command packet helper at `0x6ff20` constructs `18` FIFO words, including
literal words `0x01540601`, `0x7f000000`, and `0x3f800000`; the other words are
the supplied registers and their sums/differences. The profile packet helper
at `0xc5d70` masks shifted input values with `0xffff`, emits selectors `28`,
`27`, and `43` for profile `3`, and otherwise emits a four-word selector-`43`
fallback. Its common output copies the FIFO result three times and appends the
caller-supplied tag. The packet tail at `0x70950` appends a zero after two
pending words.

The result-builder family at `0x9e250`, `0x9e450`, and `0x9eab0` uses the
parameter table `0x562436` with 12-byte selector stride, request sink
`0x884000`, scratch offset `0x40`, and paired offsets `0`, `4`, `8` mirrored
at `0x10`, `0x14`, `0x18`. Common request `31` has seven words and final
response offset `0x28`; follow-ups use three-word commands `29` and `30`, with
response offsets `0x18`/`0x20`, table base `0x562cb0`, and output offsets
`0x14`/`0x24`. The family also exposes flag offset `0xa0`, clear source
offset `0x184`, and immediate `0xffffe000`; command `29` response handling
toggles only bit `31` (`0x80000000`).

The profile selector at `0x28840` reads backup byte `0x1d00027` and publishes
three raw float-bit words to `0x512bd4`, `0x512bd8`, and `0x512bdc`. It has ten
indexed routes (index is backup byte minus one); index `9` selects first word
`0x3f266666` and then shares the default second/third words. Zero or an index
above `9` uses the default words `0x3f0ccccd`, `0x3f59999a`, and `0x3e19999a`.
The profile initializer at `0xc8fa0` skips setup only for
profile `13`, uses a 14-entry table family, initializes selector and pending
fields to zero, and publishes the setup handle twice. The dispatch wrappers
use a three-column table with middle/last-column indices `profile*3+1/+2`,
extract selector bits `13..15`, and increment the input after the last-column
callback.

The board-control prefix at `0x9d0d0` updates counters at `0x562c9c`,
`0x562ca0`, and `0x562ca4`: each object flag is masked to `0xff`; a nonzero
flag replaces its counter with the frame value, while a zero flag decrements
only positive counters. The update gate at `0x9d170` tests state bit `0`,
writes control value `0x909` to `0x800090`, uses frame addresses `0x804000`/
`0x804004`, and when enabled emits a five-word prefix to `0x884000`:
`5`, `55`, `0x3e23d70a`, `0xbdf92c60`, `0x3f800000`.

The setup prefix at `0x23d60` repeats the control writes (`0x909` at
`0x800090`, `0x44160000` at `0x804000`/`0x804004`) and emits `20` words to
`0x884000`. Its fixed words include selectors `5`, `16`, `18`, and `19`,
`58`, float bits `0xbd5a740e`, `0x3e8f5c29`, `0x3ada740e`, `0x41100000`, and
`0x3f800000`; the derived word occupies both command-19 records. It publishes
a pointer at `0x801008` using offset/bias `0x34`.

The lifecycle tail at `0x23954` increments the byte at offset `0x19` only
when the byte at offset `0x18` is zero and the prior value is at most `31`;
otherwise it preserves the prior value. The comparison and increment are
byte-sized, so no wider state interpretation is assigned.

The transition wrapper at `0x783c8` indexes table `0x72690` with selector
`0x504d68` and sets action `5`. The selector dispatcher at `0x784c8` has ten
targets (`0x78508` through `0x78618`) and returns immediately for selectors
at/above `10`. Its action-5 values by selector `0..9` are
`8,12,12,12,12,13,13,13,19,8`; action-10 values are
`9,16,12,12,12,13,13,13,17,9`. Flag writes depend on mode bit `1` for
selectors `0`/`6`, bit `2` for `1`/`3`, and either bit for the remaining valid
selectors.

The dynamic command-6 loop at `0x24690` starts at index `0`, increments by
`1`, and continues while the index is below its limit and active-mask bit `2`
is set. Both packet forms emit six words with header `5,19`, two computed
words, and trailer values `1,58`; the readback address is `0x802008` and the
published address is `0x801008`. The recovered arithmetic divides the two
computed quantities by `600` before single-precision rounding.

The response-vector selector at `0xdf0cc` treats the sign-extended related
object halfword as a three-way selector: `0` chooses the local triplet, `1`
the first-late triplet, and `2` the follow-up triplet. Any other value writes
three zero words.

The action dispatcher at `0x77e60` uses a 44-entry jump table rooted at
`0x77e7c`; entries cover targets `0x77f2c` through `0x7807c`, with the table's
entry `9` at `0x77f7c`, entry `11` at `0x77f74`, and entry `12` at `0x78084`.
Selectors at/above `44` also fall back to `0x78084`. The video dispatcher
prefix at `0xe2330` treats `0xff` as a no-op, values above `0x81` as the
default path, and otherwise indexes the table; its bank-A special case uses
geometry mode `0` or the exact combination mode `2`, palette mode `1`, gate
`0`, and equal board/palette values.

The first video jump-table arms provide concrete tile/source pairs: arm 0 at
`0xe25bc` emits tiles `11,21,23,25` from `0x2fb75d0,0x2fb5b90,0x2fb5c50,
0x2fb5d10` (count `4`); arm 1 at `0xe2600` emits six entries ending in tiles
`27,29` from `0x2fb6010,0x2fb60d0`; arms 2–4 each emit five entries with tile
`11,23,25,27,29`; arm 5 emits `11,27,29` (count `3`); arm 6 emits five
entries; arm 7 emits only tile `11`; and arm 8 emits tiles `11,29` from
`0x2fb75d0` and `0x2fb7450`. These are source addresses and counts only.

Arms `9–11` continue the same table: arm 9 at `0xe2830` emits four entries
for tiles `21,25,27,29` from `0x2fb6cd0,0x2fb7e10,0x2bfed8c,0x2fb6fd0`;
arm 10 at `0xe2874` emits nine entries for tiles
`11,1,3,5,7,21,25,27,29` using the recovered sources; and arm 11 at
`0xe2908` emits one tile `11` from `0x2fb75d0`.

The skipped arms are also explicit: arm 12 at `0xe291c` emits tiles `23,25,27`
from `0x2fb8350,0x2fb8410,0x2fb84d0` and exits via `0xe33e4`; arm 13 at
`0xe2950` emits tiles `21,23,25,27,29` from the `0x2fb7f90`–`0x2fb8290`
sequence and exits via `0xe33f4`; arms 25 and 26 emit tiles `1,3` and `5,7`
respectively with the same bank-dependent source pairs already used above;
and arm 31 at `0xe314c` emits tiles `21,23,25,27,29` from
`0x2fb3d90,0x142dd4,0x2fa5ad0,0x2fabb90,0x2fb1c50` through helper `0xe1fb0`.

Arms `14–17` provide further exact layouts: arm 14 at `0xe29a4` emits six
tiles `1,3,5,7,9,11`; arm 15 at `0xe29fc` emits four tiles `1,3,5,7`; arm
16 at `0xe2a40` emits tiles `5,7` with bank-dependent sources
`0x2fb4990/0x2fb4a50` or `0x2fb4b10/0x2fb4bd0`; and arm 17 at `0xe2a48`
emits tiles `9,11,1,3` with bank-dependent source sets beginning
`0x2fb5290` or `0x2fb5410`.

Arm 18 at `0xe2ad4` emits six tiles `1,3,5,7,9,11`; its bank-A sources are
`0x2fb3d90,0x2fb3e50,0x2fb4990,0x2fb4a50,0x2fb4c90,0x2fb5350`, and its
bank-B sources are `0x2fb3f10,0x2fb3fd0,0x2fb4b10,0x2fb4bd0,0x2fb4e10,
0x2fb4ed0`. It exits through `0xe30a8`/`0xe30cc` by bank. Arm 19 at `0xe2b88`
emits four tiles `5,7,9,11` and exits through `0xe2f24`/`0xe2f48`.

Arm 23 at `0xe2df8` emits tiles `9,11`, selecting sources
`0x2fb5290/0x2fb5350` or `0x2fb5410/0x2fb54d0` and exits via
`0xe3008`/`0xe304c`. Arm 24 at `0xe2e44` performs only that same bank-based
continuation choice. Arm 27 at `0xe2eec` emits tiles `9,11` from
`0x2fb4c90/0x2fb4d50` or `0x2fb4e10/0x2fb4ed0`, exiting via `0xe30a8`/`0xe30cc`.
Arm 28 at `0xe3004` emits tiles `1,3,5,7` and exits via `0xe33f4`; arm 29 at
`0xe3090` emits tiles `1,3` and also exits via `0xe33f4`.

Arms `20–22` continue the bank-dependent family: arm 20 at `0xe2c14` emits
tiles `9,11,1,3` and exits via `0xe2f70`/`0xe2f94`; arm 21 at `0xe2ca0`
emits tiles `1,3,5,7` and exits via `0xe2fbc`/`0xe2fe0`; arm 22 at `0xe2d2c`
emits tiles `5,7,9,11,13,15` and exits via `0xe33f4`. Their source tables
are explicitly bank-dependent in the recovered implementation.

Arm 30 at `0xe30dc` reads five words from `0x577598` through `0x5775a8`
for tiles `21,23,25,27,29`. Arm 32 at `0xe3130` emits one tile `3` from
`0x2fb7d50`; its following `mov 7` is unreachable after the immediate branch.
Arm 33 at `0xe3248` emits eight tiles `1,3,5,7,21,25,27,29`, uses helper
`0xe1fb0`, and exits via `0xe33f4`; the first four sources are bank-dependent.
Arm 34 at `0xe319c` uses table `0x142f34`, selector shift `<<2`, special
selector `5`, helper `0xe1fb0`, and emits two entries before `0xe33f4`.
Arm 35 at `0xe3314` additionally uses bank-A table `0x142e94`, fixed sources
`0x143704`, `0x1437c4`, and `0x2fb8590`, with helper `0xe2040` for the latter
three entries. The sentinel gate at `0xe33f4` compares against `0x200` and
continues at `0xe3444` or `0xe35a0`.

The post-sentinel arms retain these additional values: arm 36 compares against
sentinel `0x200`, uses helper `0xe2040` and sources `0x2fb5890/0x2fb5950`,
and continues to `0xe3444` or `0xe35a0`. Arm 37 handles the `0x21f` case with
sources `0x2fb5a10/0x2fb5ad0`. Arm 38 scales its sentinel by `4` and reads
from `0x2bfd544`/`0x2bfd5c4`, while preserving bank-selected tiles `5,7` or
`1,3`; both later arms continue at `0xe35a0`.

Arm 39 at `0xe353c` uses the same `sentinel * 4` indexing as arm 38 but reads
from `0x2bfd5c4`/`0x2bfd644`, with helper `0xe2040`, bank-selected tiles `5,7`
or `1,3`, and continuation `0xe35a0`. The terminal side effect returns
`0xff`. The post-route partition recognizes unsigned ranges beginning at
`0x200` (width `30`), exact sentinel `0x21f`, then ranges beginning at
`0x400` (width `31`) and `0x420` (width `32`); all other values take the done
route.

The lower-range post-sentinel arm at `0xe3444` scales its sentinel by `4`,
reads source pairs from `0x129e28` and `0x129ea8`, uses helper `0xe2040`,
selects bank-dependent tiles `5,7` or `1,3`, and continues at `0xe35a0`.

The status-code table contract at `0x1f680` is bounded to `9` records of
`16` bytes; index `8` is the documented blank record, and invalid indices
return zero. Its text-position fields are columns `8` and rows `14`. The
indexed glyph wrapper at `0x23620` calls helper `0x1cd18` and saves/restores
origin globals at `0x504d44` (column) and `0x504d40` (row).

The status-code dispatcher at `0x1f710` clamps selectors above `7` to case
`8`, selects messages from `0x1f680` with a 16-byte stride, and uses helper
`0x1df00` for the blanking block and `0x1dc90` for cases `0`–`7`. The case
source addresses are `0x2fe321c`, `0x2fe350e`, `0x2fe35e6`, `0x2fe343c`,
`0x2fe37fa`, `0x2fe33b4`, `0x2fe32d0`, and `0x2fe3746`; fixed widths include
`30` and `31`, while the common height is `3` and case `5` uses height `2`.

The paired status-panel route at `0x1f1b0` selects helper `0x1df70` and zero
source for mode `0`, otherwise helper `0x1dd10` and source `0x2fd832e`; it
uses column `2`, height `3`, and row/width values offset by `31`, with a
`0x50`-byte stack frame. The two-block builder at `0x1f4c0` uses source
`0x2fe01d4` at rectangle `(column 4,row 10,width 5,height 5)`, then selects
an entry from `0x2ea2010` using a low-nibble index after subtracting `0xd0`;
the second rectangle is `(28,20,8,5)`.

The parallel panel route at `0x1f290` has the same mode-dependent helpers,
zero fill, column `2`, row/width offsets of `31`, height `3`, and `0x50`-byte
frame as `0x1f1b0`, but its nonzero-mode source is `0x2fd848a`.

The insert-coin renderer at `0x1f470` selects message `0x1f440` for nonzero
input or `0x1f450` otherwise, calls text helper `0x1d9e0`, and adds `31` to
both caller position fields. The press-start renderer at `0x1f3b0` selects
message `0x1f370`/`0x1f390`, calls `0x1d210`, adds `31` to both positions, and
updates flag address `0x502484` with set mask `4` or clear mask `0xfffb`.

The three-stage panel sequence at `0x1f540` derives positions with offsets
`+2`, `-1`, `+12`, and `-7`. Stage one uses source `0x2fde9d0`, width `55`,
height `8`, and helper `0x1dc10` or `0x1dc90` by source mode. Stage two uses
source `0x2fe1606`, width `34`, height `2`, and helper `0x1dc10`. Stage three
uses width `30`, height `2`, source `0x2fe158e` or zero, and helper `0x1df00`
or `0x1dc90` by fill mode.

The fixed panel-10 transfer at `0x1fba0` calls helper `0x1dc10` with source
`0x2fe0404` at rectangle `(column 10,row 20,width 31,height 5)`.

The fixed attributed panel-7 transfer at `0x1fad0` calls helper `0x1dc10`
with source `0x2fe1350` at column/row `10,10`, width `caller_g12 + 31`, and
height `5`.

The adjacent panel routes at `0x1fb10`/`0x1fb50` use panel 8 source
`0x2fe1170`, helper `0x1dc90`, position `(7,10)`, width `caller_g17 + 31`,
and height `5`. Panel 9 selects source `0x2fe0d42` and helper `0x1dc10` when
source-present, otherwise uses fill helper `0x1df00` with zero source; its
position is `(5,10)`, width `caller_g22 + 31`, and height `5`.

The panel-11/12 routes at `0x1fdf0`/`0x1fe60` use panel 11 sources
`0x2fd892e` and `0x2fd894a` with helpers `0x1dc90` and `0x1dc10`, at
rectangle `(20,20,7,2)`. Panel 12 selects source `0x2fe0cb0` with helper
`0x1dc10` when present, otherwise fill helper `0x1df00`; it uses the current
position, width `20`, and height `2`.

The signed status-value route at `0x1fbe0` sends negative values through a
20-by-3 block from `0x2fe17ec`, then selects a 4-by-3 glyph from table
`0x2ea1fd0` using `((value - 0x30) & 0xf)` and advances the column by `21`.
Nonnegative values instead clear a 25-by-3 region with helper `0x1df00`.
The scoreboard route at `0x1fc30` normalizes values with sign bit `0x8000` to
zero, emits a `31×2` background through `0x1dc10`, uses digit table `0x2ea1e50`
with four-byte entries through `0x1dc90`, and has an early
return for state `0` plus mode `4`; its digit positions include columns
`25,27,30,32`, separator source `0x2fe158a`, and suffix source `0x2fe157a`.

The continuation renderer at `0x1fa00` selects message `0x1f9e0`, calls text
helper `0x1da90`, writes the caller-supplied column unchanged, and uses row
`20`. Panel 5 at `0x1fa30` selects source `0x2fe053a` with helper `0x1dc10`
when present, otherwise fill helper `0x1df00`; it uses column `2`, row `20`,
width `caller_g27 + 31`, and height `5`.

Panel 6 at `0x1fa80` selects source `0x2fe099a` with helper `0x1dc90` when
source-present, otherwise fill helper `0x1df00`; it uses column `8`, row `10`,
width `caller_g14 + 31`, and height `5`.

The fixed transfer descriptors at `0x1f640` and `0x1f660` both call helper
`0x1dc90` at the current position with dimensions `6` by `8`; their sources
are `0x2fded40` and `0x2fdeda0`, respectively.

The indirect-return thunks at `0x1f9c0` and `0x20160` both clear `g14` and
branch through register `g0`; their return stubs are `0x1f9d4` and `0x20174`.

The ten indexed profile routes at `0x28840` are, in order: (`0x3f000000`,
`0x3f4ccccd`, `0x3e4ccccd`), (`0x3ee66666`, `0x3f400000`, `0x3e800000`),
(`0x3ee66666`, `0x3f266666`, `0x3eb33333`), (`0x3eb33333`, `0x3f0ccccd`,
`0x3ee66666`), (`0x3eb33333`, `0x3ee66666`, `0x3f0ccccd`), (`0x3f800000`,
`0x3f59999a`, `0x00000000`), (`0x3f733333`, `0x3f59999a`, `0x00000000`),
(`0x3f59999a`, `0x3f59999a`, `0x3d4ccccd`), and (`0x3f400000`,
`0x3f59999a`, `0x3dcccccd`), followed by first word `0x3f266666` with
the default second/third words. These remain raw IEEE-754 bit patterns.

The association-release helper at `0x6fd50` uses `999` as the no-record
sentinel. It redirects link fields at record offsets `0x14` and `0x18`, or
updates side-table offsets `0x5c4` and `0x5c8`, then decrements the reference
count. The allocator tail at `0x6fd1c` advances its head by `0x30`, increments
the source count, and derives availability as `0 - next_head_word`. The cleanup
helper at `0x23ca0` clears object bytes `0xa0`–`0xa2`, publishes float bits
`0x41200000` to `0x504d54`/`0x504d58`, and returns through `0x23cd8`.

The state-dispatch slice at `0x25040` has explicit cases for state values
`12`, `20`, `1`, `5`, and `6`. It initializes record fields from global values
`0x50249c`, `0x5024a4`, and `0x503a00`, writes the halfword at offset `0x108`,
and uses sentinel `0xffff` in the state-6 path. Its common tail compares a
record halfword against `0x602`, clamps byte `0x4f` to `0xff`, and updates
seven entries at offsets `0x28` and `0x38` while clearing bit-15 results.

The status grid initializer at `0x227b0` selects on `phase % 192 == 0`, uses
source `0x2fe8fc4`, helper entries `0x1de80` and `0x1de00`, and builds `32`
cells over a `16` by `8` region with four columns per row. The patterned-fill
route at `0x22840` writes from `0x100d000 + 2*start_row`, repeats `192` times,
uses four fill and four solid repetitions per group, fills solid entries with
`0xffff`, and keeps generator/state values masked to `0x1ff`.

The formatter tail in `0x185c0` is also value-bounded: when `0x503a08` is
zero it emits the decimal remainder and quotient for divisor `10`, with the
second digit offset by `0x20`, followed by literal tile value `0xad`; when the
flag is nonzero it returns through the alternate path. This is enough to call
the operation a two-digit status formatter, but not enough to identify the
displayed status semantically.

### Runtime record-table constants

The record-management cluster around `0x3ecd0`–`0x423a8` also exposes a few
safe structural values:

| Entry | Directly observed values |
| --- | --- |
| `0x3ecd0`/`0x3ed60` | scan records rooted at `0x51ad10` with a `0x24`-byte stride, inspect halfword offset `2`, limit the scan at `23` entries, initialize fields at offsets `0x8`, `0xc`, `0x10`, `0x14`, `0x18`, `0x1c`, and `0x20`, and derive a table value from `0x3eca0[index & 0xffff]` |
| `0x3ef50` | uses record offsets `6`, `8`, `12`, and `16`, byte mask `0xff`, signed threshold `0xffffff80`, and floating constant `0x40340000` while emitting record data through `0x884000` |
| `0x3f4e8` | scans the same `0x24`-byte records through bound `0x33c`; a free slot is initialized with selector `10`, a table-derived halfword, caller field at offset `6`, zero at offset `4`, and caller value at offset `8` |
| `0x423a8` | clears the record table through bound `0x33c`, then clears a second table through bound `0x508`; both use sentinel halfword `0xffff` and zero-based record offsets |

These entries are structural descriptions derived from literal operands and
loop strides; no meaning is assigned to the record selector values.

### Fixed-point and geometry-state constants

Additional geometry helpers expose these exact values:

| Entry | Directly observed values |
| --- | --- |
| `0x6ede0`/`0x6f600` | convert two floating inputs using truncation, shift each result right by one, mask with `0xfffffe00`, reject the zero/low-bit case with return `0x47c34f80`, and otherwise emit selector `0x41` plus a packed value using a 9-bit shift |
| `0x6f908` | indexes records by `(input * 3) * 8`, reads offsets `0xc`, `0x14`, and a 64-bit value at the record base, writes attribute bit `6` to `0x884000`, and updates globals `0x51bb20`, `0x51bb24`, and `0x51bb28` |
| `0x6f9e8` | clears a 64-entry table at `0x51c860` using a `0x3f` bound, clears `0x51c5b0` entries with `0x54`-byte stride, and resets `0x51c880`; the cursor helper returns `-1` when the cursor is already at `0x3f` |
| `0x72c10` | gates on `0x5039f4 == 1` or `0x503a00 == 23`, then uses `0x5024e8 mod 30` with threshold `14`; a later route checks `0x5039f4 == 4`, `0x503a00 == 10`, and record field `0x64 == 9` |

The descriptions retain the observed arithmetic and memory operands. The
device meaning of selector `0x41` and the geometry-state fields remains open.

The next state/UI helpers expose these additional constants:

| Entry | Directly observed values |
| --- | --- |
| `0x74860` | checks halfword `0x504e42`, then gates on `0x504e28 == 1`, `0x504d98 == 1`, and a shifted field in the inclusive range `0x150000`–`0x190000`; the fallback path dispatches with saved values from `0x504d90` |
| `0x74e60` | clamps `0x504dc0` against `0x96`, stores the boolean at `0x504da4`, and dispatches through an eight-entry table selected by `0x504d7c`; one branch uses threshold `15*8` and writes state `3` |
| `0x75d90` | maps device byte `0x1d00021` values `1`, `2`, and `3` to selectors `8`, `30`, and `2`; all other values map to `4`, with a separate `0x5039f4 == 4` path |
| `0x761b0` | maps `0x504dc0` ranges ending at `0x4f`, `0x54`, `0x59`, `0x5e`, `0x63`, `0x6d`, and `0x77` to float constants `0x45000000`, `0x45800000`, `0x46000000`, and `0x46800000`, then emits selector `29` |

These are literal branch and table values; the associated UI/device states
remain intentionally unnamed.

Two more packet/state slices are bounded by their operands:

| Entry | Directly observed values |
| --- | --- |
| `0x72ea0` | when `0x503a08 == 2` and `0x5039f4 == 4`, reads byte `0x1a14002`, selects one of two `0x5024f0`-based records using bit `0`, and copies bytes at offsets `0x514`/`0x515` into `0x504dac`/`0x504db0`; a later path checks `0x503a00 == 20` and emits the resulting pair through `0x882a8` |
| `0x76590` | emits selector `31`, then fields at offsets `0x8` and `0x10` from two records; stores the returned word at `0x504d60`, then emits selector `10` followed by the signed differences of those `0x8`/`0x10` fields |

The selector values and offsets above are direct instruction evidence; the
destination device protocol remains unresolved.

### Command-record table constants

The command-record helpers around `0x9b288` add a small, well-bounded table
model, now represented by `recovered_command_record_write_9b288.c`,
`recovered_command_record_scan_9b320.c`, and
`recovered_command_record_pool_clear_9b498.c`:

| Entry | Directly observed values |
| --- | --- |
| `0x9b288` | selects a 16-byte record at `0x562b80 + ((0x562b70 & 0xf) * 16)`, writes byte `1` at offset `0`, byte `0` at offset `1`, and copies caller fields into offsets `2`, `4`, `8`, and `0xc`; the rolling index is incremented and stored back at `0x562b70` |
| `0x9b320` | scans records from `0x562b80`, tests the low byte against zero using mask `0xff`, and emits the modeled prefix `[5, 18, record+4, record+8, record+0xc, 21, widened(record+1)]` to `0x884000`; the later floating/device tail remains unresolved |
| `0x9b498` | clears the 16 record slots at `0x562b80` using offsets `0xf0` down to `0` in `0x10`-byte steps, then resets `0x562b70` to zero |

The table size and record layout above are structural facts from the address
arithmetic; the command meanings are not inferred.

### Object dispatch and lookup constants

The object-management slices around `0xbd5a8`–`0xbf2f0` expose these further
values:

| Entry | Directly observed values |
| --- | --- |
| `0xbd5a8` | copies `39`, `0x99b`, `0x333`, and `0x3fff` words from `0x13da68`, `0x13b3f8`, `0x13a728`, and `0x12a728` to `0x565e30`, `0x562cb0`, `0x565ed0`, and `0x566ba0`, then emits FIFO word `0x44` and stores `0xffffffff` at `0x577170` |
| `0xbd6b8` | clears 32 bytes at object offset `0x200` using a `0x20`-byte stride, and clears one of `0x576ba0` or `0x576ba4` based on equality with `0x503ad0`, always clearing `0x576ba8`; modeled by `recovered_object_table_reset_bd6b8.c` |
| `0xbd730`/`0xbd810` | inspect object bytes at offset `0x200` with mask `0xff`, reject values above `0xcc`, and dispatch through `0xbcf40[index * 8]`; the `0xbd730` and gated `0xbd810` preludes are modeled separately, with context bases `0x565320` and `0x5658a0` and the shared `0xffe0` halfword mask |
| `0xbd8e0` | paired-object admission loop requiring active byte nonzero, preceding halfword bit 15 set, and current halfword bit 15 clear; admitted entries begin FIFO with selector `72`, linked offsets `0xc/0x10/0x14`, and mode-table offsets `0x24/0x28`, modeled by `recovered_object_dual_admission_bd8e0.c` |
| `0xbece0` | scans two 32-entry object tables, publishes each object's `+0x68` word to `0x565e20`, admits values through `0xcc`, suppresses record halfwords with bit 8 set, and dispatches the remaining values through `0xbcf44[value*8]`; diagnostic and indirect callee paths remain separate |
| `0xbe1f0` | scans paired 32-entry records for active entries with halfword bit `0x8` and/or low bits `0x7`, issues selector-7 service requests, then requests status updates for nonzero `+0x48` bytes before entering the packet path; modeled prefix is `recovered_object_service_prelude_be1f0.c` |
| `0xbe304` | requires linked halfword `+0x2 == 0`, then emits selector `70`, linked words `+0x14/+0x18/+0x1c`, profile `+0x4` scaled by `1.0` or `0.5` for signed `+0x172 == 14`, and profile words `+0x8/+0/+0xc`; modeled by `recovered_object_profile_packet_prefix_be304.c` |
| `0xbf120` | walks a caller-supplied range backward in 0x20-byte row steps, masks each row's active byte to 8 bits, counts nonzero entries, and returns that count; modeled by `recovered_object_active_row_count_bf120.c` |
| `0xbf0c0` | walks the same row layout backward, returns the first nonzero active-row index, and returns `0xffffffff` when the supplied range is empty or has no active row; modeled by `recovered_object_last_active_row_bf0c0.c` |
| `0xbf180`/`0xbf1c0`/`0xbf200` | share the special-object comparison against `0x503ad0`, pass `object + 0x200`, select context base `0x565320` or `0x5658a0`, and route to callees `0xa1050`, `0xa98f0`, or `0xa55e0`; modeled by `recovered_object_dispatch_context_bf180.c` |
| `0xbedf0`/`0xbeee0`/`0xbefd0` | classify the signed halfword at offset `0x172` for exact/range values `24`, `14`, and `31`; value `31` refines through signed `0x188`, then select the family-specific table at `base + selector_offset + (field_64 * 24)` |
| `0xbf2f0` | gates on `0x503a08 == 2`, compares object byte `0` and halfword `0x4` against table `0xc4f40[index * 8]` and its predecessor, then emits selectors `5`, `16`, and `18` |

The table bases, scales, and branch constants are explicit; the object-state
interpretation is intentionally left open.

The selector at `0x9c050` applies the shared normalized grid index to both the
current and linked coordinate pairs, uses the 576-entry bound `0x23f`, and
publishes selected table words at `0x562c80` and `0x562c84`; its bounded
wrapper is represented by `recovered_geometry_descriptor_select_9c050.c`.

### Geometry lookup and raster constants

The helpers around `0x8d400` and `0x8d5d0` use the same bounded index
calculation: a signed halfword from object offset `0x4` is compared with the
incoming `g2` bound, retained as `g2` when above the bound, or changed to
`index - 1` otherwise; the halfword at offset `0x6` supplies the row scale,
and the object’s signed `+0x6` supplies the row scale; the resulting record offset is `12 * adjusted_index * signed(row_scale)`
from the caller base. The first path
emits selector `5` and places the selected record's words `+0`, `+0x4`, and
sign-extended halfword `+0x6` into the `0x804000` command window; the second emits selector `20` and
stores the signed negated lookup value. Its packet `+0x6` is a separate
selected-record halfword. The second path sign-extends its
count halfword into an absolute count. When that count is `N > 1`, the
`0x8d6ec` continuation processes exactly `N - 1` more 12-byte records: its
source cursor starts at source offset `12`, while its destination cursor starts
at offset `12*N`; counts through one branch directly to the return. The
prefix's three final values are sign-extended with `ldos` and then XORed
with bit 15, while the first three are masked to `0xffff`. The deterministic prefixes are modeled by
`recovered_geometry_batch_packet_8d400.c` and
`recovered_geometry_indexed_packet_8d5d0.c`.
The indexed record-header continuation at `0x8d6b8` advances the 12-byte
cursor, emits command `47`, XORs the three record halfwords with the per-record
mask, and branches to the empty/small-count return at `0x8d848` or the record
body at `0x8d6ec`. It is modeled by
`recovered_geometry_indexed_packet_8d6b8_record_header.c`.
The indexed record gate at `0x8d6ec` advances the source and table cursors,
computes the record address with a 12-byte stride, tests the active word, and
routes inactive records to `0x8d834` or active records to `0x8d704`; its
bounded model is `recovered_geometry_indexed_packet_8d6ec_record_gate.c`.
The active-record emitter at `0x8d704` builds the exact 13-word
`5/47/22/21/20/58` packet, writes the four-word `0x804000` window and
`0x800010=0x101` control, emits completion `6`, and loops back to `0x8d704`
or returns at `0x8d848`; its bounded model is
`recovered_geometry_indexed_packet_8d704_record_emit.c`.

The preceding indexed batch entry at `0x8d850` uses the same bound/row-scale
lookup but emits a distinct 13-word `5/47/22/21/20/58` packet. Its current
record is written to the four-word command window, and a positive absolute
count emits the packet and traverses `N` records at 12-byte intervals; zero
normalized count returns before emission. An inactive record instead
enters the `0x8da04` arm; indices through 5 publish the selected record dword
and `+0x8` word to `0x562430 + index*12`, while larger indices skip that
publication. The deterministic contract
is modeled by `recovered_geometry_indexed_batch_8d850.c`.

The sibling routine at `0x8da60` uses the same bounded lookup and absolute
count control, but emits a 10-word `20/21/22/58` prefix only for positive
normalized count. Its lookup row scale comes from the object’s `+0x6`, while
the first XORed packet payload comes from the selected record’s `+0x6`; it
publishes the selected
record dword and its `+0x8` word at `0x562480/0x562488`, and traverses the
remaining `N-1` records through `0x8dd30`. Its deterministic prefix/control
contract is modeled by `recovered_geometry_indexed_packet_variant_8da60.c`.

The first-record arm within the `0x8dfc0` routine at `0x8e000` uses a distinct
11-word `20/21/22/46/58` packet: it stores the absolute signed object `+0x6`
value at object offset `0x24c`; the first three values are negated after
sign extension, the final three are XORed with bit 15 without truncation, and
the paired record value is published at `0x562480/0x562488`. Its absolute
count gate and 12-byte next-record stride feed the later `0x8e120` loop. For
normalized count `N > 1`, that handoff processes `N-1` records with the selected
record cursor at `+8`, table cursor at `+12`, auxiliary cursor at `+2`, and
destination base at `+8`; this prefix/handoff is modeled by
`recovered_geometry_first_packet_8e000.c`.

The associated conditional writers at `0x8dd40`/`0x8dfc0` use object offsets
`0x4`, `0x6`, and `0x24c`, test byte/halfword masks `0xff` and `0xffff`, and
also emit selector `20`. Their `cmpobl 5,index` table guard is inclusive at
index 5 and skips only indices above 5. These are direct operand facts; the lookup table’s
semantic units are not established. The `0x8dd40` deterministic packet plan
takes survival of the upstream `0x8df64` table arm as an explicit input; its
table write then requires that admission and an index through 5. It is modeled
in `recovered_geometry_object_packet_8dd40.c`; `0x8dfc0` remains a
separate annotated boundary because its returned-vector destination differs.

The table builder at `0x866c0` fills a 20-byte record prefix with incoming
`g14` at offsets
`0x0` through `0x12` in 2-byte steps, rooted at `0x5050a0`, and advances its
source index by `20` bytes per record while storing the current record pointer
at `0x5074a0`. Its tail advances the two table cursors by `0x440` and
`0x480`, respectively, and repeats while the first cursor is at most
`0x1dc0`; this produces eight batches of eight records (64 records per
table). The updater at `0x881b8` reduces `0x51c9b0` modulo `15*8`,
scales the resulting slot index by `12` bytes, and stores two caller words at
output offsets `4` and `8` relative to `0x561e90`.

### Video/status asset constants

The later video/status helpers expose these additional exact values:

| Entry | Directly observed values |
| --- | --- |
| `0xde670` | initializes status fields at `0x504b90`, `0x504b94`, `0x504ba8`, `0x504bae`, `0x504baa`, `0x504bac`, and `0x504bb0`; the fixed float constant stored later is `0x41d00000` |
| `0xde990` | always clears `0x503c9c`/`0x503c98`, clears `0x50429c`/`0x504298` only for stage `4` with state `1`, and splits mode `0x504134 == 9` to `0xde9ec` versus `0xdead4` |
| `0xe37f0` | copies `0x50` bytes from `0x1d00144` to `0x578410`, then `0x78` bytes from `0x1d00194` to `0x578460` |
| `0xe3830` | formats values above `0x63` directly; otherwise emits quotient and remainder using divisor `10`, with glyph base offset `0x30` |
| `0xe39c0` | scales an index by `6`, then renders paired table entries rooted at `0xe36c0` and `0xe3700` |
| `0xe3a10`/`0xe3a70` | uses literal strings `WIN` and `LOSES`; the three-byte token helper reads bytes at offsets `0`, `1`, and `2` and renders each independently |

These values are directly visible in the instructions or adjacent literal
data; no game-state interpretation is added beyond the literal strings.

### Runtime utility constants

The traced utility cluster also gives exact, reusable boundaries:

| Entry | Directly observed values |
| --- | --- |
| `0xf50a8` | stores its input at `0x5785d0` and returns; the adjacent byte scanner advances one byte at a time until a zero byte and returns the count |
| `0xf5190` | uses a 32-entry dispatch table rooted at `0xf5210` (index range `0..31`) and hands ordinary bytes to the tile writer at `0x1cc40` |
| `0xf5c58` | compares byte streams until length zero or the first mismatch, returning zero for equality or the unsigned byte difference at the mismatch |
| `0xf5d40` | copies aligned data in `16`-byte blocks, then handles the residual count masked by `0xf`; alignment tests use masks `0xf`, `7`, and `0xff` |

These descriptions are limited to the observed loop and dispatch mechanics;
they do not infer calling-library names beyond the proven byte comparison and
copy behavior.

The object geometry helper at `0x9c050` derives a dispatch index from
`0x5770f0 * 5`, uses float constant `0x407e0000` for both coordinate paths,
and routes through the object record referenced by `0x74(g0)`. The visible
state stores in this slice are therefore index-scaled and coordinate-derived;
the later dispatch target is not assigned a semantic name.

The continuation makes the quantization explicit: both converted coordinates
are divided by `r4 = 31 - 22 = 9`, the combined table index is compared against
`0x23f`, and the selected table entry is loaded through the `0x9b8d0`/`0x9b8d4`
pointer pair. It stores intermediate results at `0x562c80` and `0x562c84`,
then uses the rolling index at `0x5770f0` to select a second pointer through
`0x9b8d8[index * 20]`. The packet path emits selectors `5` and `18`, uses
source `0x2bf0a4c`, and sets bit `30` in the record flags.

The following status-update values are also explicit: `0xe3ab0` increments
`0x503a00` by `2` when device byte `0x1d00026` is zero; otherwise it wraps
`0x5783b4` into the range `0..2`, dispatches states `0`, `1`, and `2` to three
separate helpers, and increments the stored state. The state-0 path at
`0xe3b70` clears `0x503a04`, initializes the video plane, emits a zero command,
and uses `g0 mod 3` with a 13-row transfer beginning at `0x578410`.

The status-score path at `0xe3c00` uses divisor `0xb40`, divisor `29` for a
secondary component, and the literal data at `0xe3b50`/`0xe3b5a`/`0xe3b5c`;
the bounds path at `0xe3d00` clamps `0x503a04` against `31`, computes
`0x200 - (value << 4)` into `0x504d24`, and uses threshold `0xbf` before
updating `0x504d2e`, `0x504d32`, and `0x504d30`.

The setup routine at `0x86240` stores a four-word value at `0x509b20` and a
two-word value at `0x509b30`. Its first branch uses thresholds `5`, `0x9c3`,
`0x5db`, `0x4af`, and `0x7cf`, with fallback values `0x9c5`, `0x5dd`,
`0x4b1`, and `0x7d1`; the alternate branch uses `2`, `0x2bb`, `0x1f3`, and
fallback values `0x2bd` and `0x1f5`. These are direct clamp operands, without
an assigned interpretation of the four fields.

The nearby state-transition callers expose additional exact case values:
`0x7a318` treats object field `0x64` values `1`, `2`, `5`, and `7` as one
route, while preserving a separate value `4` route; `0x7a3e0` has an explicit
field-`0x64` case for `8` and writes state `11` to `0x504d80`. The paired
callers at `0x7b430` and `0x7bf10` recognize object field values `2` and `7`
and select the `0x78740` or `0x786d0` paths. The `0x7a9f0` route uses threshold
`0x63`, stores initial state `10` at `0x504db8`, and indexes records from
`0x505060` using a 20-byte stride.

The following state-machine operands are also bounded:

| Entry | Directly observed values |
| --- | --- |
| `0x7d1f0` | scans one byte at `0x504da0+0x9a` and one at `+0x98`; each nonzero byte must lie in the inclusive `reference..reference+5` band to set its flag. It also walks `+0x94..+0x96` with a discarded lower-bound check, then applies the shared `0x504d9c`/`0x504d94`/`0x504db4`/base-offset/object-state gate before the selector table at `0x7d358` |
| `0x7d670` | scans seven six-byte records at `0x505060`, skips zero signed halfwords at record `+4`, selects the first minimum signed halfword at `+2`, and falls back to status `11` when `0x504d70 <= 4` or `10` otherwise; selected records feed the `0x884000` command packet path |
| `0x7dcc0` | returns unless signed `0x509b34 > 0x1f3`; its byte-window predicate requires a nonzero status byte, zero masked `0x0f00` halfword field, and an object byte in the inclusive `status..status+5` band; accepted slots enter command `10` emission |
| `0x7e390` | maps the object slot through `+0x200` with a `32`-byte stride, uses the resulting byte as a `48`-byte descriptor index from `0x562cb0`, reads descriptor offsets `+4/+0xc/+0x24`, and selects the exact state-3 arm; raw float constants are `0x40c00000`, `0x42f00000`, and special `0x3ff80000` |
| `0x7ea10` | requires signed `0x509b30 > 0x1f3`; the `0x172 == 31` arm requires both object states `6` and `0x504e48 == 3`, then stores `3`, `0x64`, `1`, `7`, and `30` to `0x504d9c`, `0x504da0`, `0x504d94`, `0x504d98`, and `0x504db8`; other values use the eight-entry threshold table at `0x7eab0` |
| `0x7f4d0` | requires signed `0x509b28 > 0x1f3`, scans status bytes `0x504e38..0x504e39` over 32 related-object slots at `+0x200` with a `0x20` stride, and retains the inclusive `status..status+5` match masks before candidate selection |
| `0x7fca0` | zero-extends related halfword `+0x172`; accepts the range arm for `0x10000 < value <= 0xd0000`, or the fallback state tuple `(+0x64 in {0,6}, +0x172 in {1,14}, +0x170 == 6)` before the `0x504dec` timing branch |
| `0x80710` | for `0x504d70 <= 1` subtracts `0x6800` from the current `+0x184` halfword, for values `2..9` adds it, classifies the related-current difference through `0x73508`, selects `0x72630[g6]`, initializes `0x504db8` to `10`, and calls `0x82800` when current timing is below converted `0x504df8` |
| `0x810d0`/`0x81120` | requires signed `0x509b2c > 0x1f3` and normalized related `+0x172` in `0x150000..0x190000`; for nonpositive current timing requires mode bit `3`, accepts object state `1` or `5`, rejects related states `1/5/6/7`, then publishes `7`, `30`, `2`, and `0x64` to the transition cells and calls `0x79d60` |
| `0x8168c` | forces status `18` for global states `2` or `7`; otherwise computes `0x5024e8 mod 240` and selects status `18` for remainder `<= 0x77` or `19` above it |
| `0x81e60` | calls `0x84d90` for the exact startup tuple `0x5039f4 == 4`, `0x503a00 == 10`, `0x504e42 == 0`, then dispatches mode-zero object states `0..9` through the ten-entry table at `0x81eb4` |
| `0x82040` | rejects object states above `9`, then dispatches states `0..9` through the exact ten-target action table at `0x82060` |
| `0x82800` | rejects selectors above `9`, then dispatches selectors `0..9` through the exact handler table at `0x82818` |
| `0x82ae0` | runs the `0x81f60` selector first, then gates on `0x503a14 <= g28+31`, `0x5039f4 == 4`, and `0x504dbc < 6`; states below `8` call `0x82db0`, while state `8+` calls `0x81e60` only when `0x504d7c == 5` |
| `0x82b38` | requires status `0x504d84 == 1`, rejects selectors above `g28+12`, and dispatches through the exact 44-entry table at `0x82b58` |
| `0x82c08` | handles scheduler selector `6`: writes state `7` when `0x504e1c == 0`, otherwise calls `0x81e60`, then rejoins the common scheduler tail |
| `0x82c6c` | handles scheduler selector `19`: writes status `2` outside object state `4`; state `4` writes status `8` through the signed `0x504dc0 <= 0x78000` split, or status `3` plus state `28`/`5` based on `0x504e28` |
| `0x82cc0` | constant scheduler entries write `0x504d98` values `3`, `1`, `13`, `14`, or `15` at targets `0x82cc0`, `0x82cc8`, `0x82cd0`, `0x82cd8`, or `0x82ce0` |
| `0x82ce8`/`0x82d04` | state-4 scheduler variants: `0x82ce8` writes status `3` plus state `28` for state `4`, otherwise status `2`; `0x82d04` writes status `2` for state `4`, otherwise status `3` |
| `0x82d18` | writes status `3` and selector `20` for object state `8`; all other states use the shared status-8 path |
| `0x82db0` | dispatches object states `0..8` through the exact nine-entry table at `0x82dd4`; states above `8` route to `0x82f90` |
| `0x82e40` | requires random remainder `4 mod 5`, then selects downstream value `2` for object state `3` or `5` otherwise; other remainders use the shared fallback |
| `0x82ea0` | requires object state `3`; random remainder `4 mod 6` selects downstream value `3`, remainder `5` selects `6`, and all other combinations use the shared fallback |
| `0x82ed4`/`0x82f10` | modulo-8 service variants: `0x82ed4` accepts state `3` with remainder `<3` -> value `3` or any state with remainder `6` -> `4`; `0x82f10` accepts state `3` with remainder `4/5` -> `3` or `7` -> `6` |
| `0x82f6c` | requires random remainder `4 mod 5` and object state `3`, then selects downstream value `2`; all other combinations use shared dispatch |
| `0x82f84` | computes signed `random % 7` and passes the remainder to the shared `0x82fac` selector table |
| `0x82f90` | adjusts negative random values by `3`, forms the `& ~3` remainder, and dispatches unsigned selectors `0..7` through the exact table at `0x82fbc` (nonnegative inputs normalize to `0..3`) |
| `0x82fac` | shared unsigned selector dispatcher: values `0..7` use the exact table at `0x82fbc`; larger values use the reject path at `0x830a0` |
| `0x82fdc` | shared handler prefix: selectors `0..3` call `0x79050` and select `30`, selectors `4..6` select `20` with statuses `1/2/3`, selector `7` calls `0x79d60` and selects `30`, and rejection selects `10` |
| `0x830c0` | rewrites status `9` to `12` for current object state `3`, then lets related state `0` override status/selector to `1/10` and restores caller `g14` to `0x504d94` |
| `0x83110` | for signed `0x504dc0 <= 149` and related state `19` or `20`, writes caller `g14` to `0x504d98` and returns; other inputs continue into the timing/status path |
| `0x83310` | sibling early gate with the same signed `0x504dc0 <= 149` and related-state `19/20` predicate, writing caller `g14` to `0x504d98`; other inputs continue into the ratio/status path |
| `0x83348` | sets `0x504e1c = 1`, compares the converted `0x5042a8/0x5042a2` ratio against `0.9`, clears mode bit `2` above the threshold, and dispatches state `5` through the five-entry table at `0x833c8` |
| `0x833dc` | ratio-table handlers: selector `0` calls `0x79d60`, selectors `1/2` publish status `28`, selector `3` publishes `26`, and selector `4` publishes `21` |
| `0x8342c` | remainder/mode handler: remainder `5` -> status `21`; remainder `4` with mode bit `1` -> `26`; positive remainder with mode bit `2` -> `28`; otherwise calls `0x79d60`, then writes `g14`/`15` to `0x504d8c/0x504d90` |
| `0x83ac0` | early related-state gate writes caller `g14` to `0x504d98`; otherwise sets `0x504e1c = 1`, calls `0x82800` below converted `0x504df8`, selects status `18` for negative timing, and splits state `5` remi-6 handling from the other-state remi-7/mode-bit path |
| `0x83cc0` | sibling early gate uses the same signed `0x504dc0 <= 149` and related-state `19/20` predicate, writing caller `g14` to `0x504d98`; the continuation loads state `0x504d7c` and branches into distinct state-5 mode/timing versus other-state remainder-18 logic |
| `0x83d58` | state-5 continuation calls `0x82800` below the converted negative timing limit, writes status `18` for negative timing, then applies signed remi-10: remainders below `5` select status `25`, while remainders `5+` select `33`; the following control/pair equality block is unreachable for ordinary remi-10 outputs |
| `0x83de4` | non-state continuation repeats the converted negative-timing gate, calls `0x82800` for positive remi-18 results or remi-3 result `2`, selects status `25`/`34` through the signed evenization test for the remaining nonpositive values, and hands larger values to the remi-6 continuation |
| `0x83e74` | non-state remi-6 continuation sends values at least `2` through signed parity (odd calls `0x82800`, even takes the common tail); lower values use mode bit `1` and the control/pair equality for status `27`, otherwise signed remi-3 selects status `40` for `0/1`, `19` for `2`, or the common tail for negative results |
| `0x83f50` | sibling early gate writes caller `g14` to `0x504d98` and returns for the inclusive related-state predicate; otherwise publishes `0x504e1c = 1` and dispatches state `5` to `0x83f9c` or other states to `0x84018` |
| `0x83f9c` | state-5 branch: mode bit `1` gives status `26` when `0x504e28 == 1`, otherwise `37`; with bit `1` clear, timing above converted `0x504dd8` plus mode bit `2` gives `39`, otherwise `37` |
| `0x84018` | loads the `0x504d80` quadword, replaces only its first word with the candidate status, preserves the other three words, and writes selector `30` for status `26` or `31 + 0x504e30`, otherwise selector `15` |
| `0x840b0` | sibling early gate writes caller `g14` to `0x504d98` and returns for the inclusive related-state predicate; otherwise publishes `0x504e1c = 1` and dispatches state `5` to `0x84104` or other states to `0x841a0` in the shared random/timing path |
| `0x840e8` / `0x841a0` | normalize the signed random value into the modulo-8 helper, call `0x82800` below converted timing, then hand state 5 to `0x84150` and other states to `0x841ec`; the latter reaches the caller-`g14`/status-15 tail |
| `0x84150` | consumes the signed helper from the state-5 random/timing path: helper `< 4` plus mode bit `2` gives `32`; negative helper plus mode bit `1` gives `37`; otherwise status `33` |
| `0x841ec` | non-state continuation: helper `< 4` plus mode bit `2` gives `32`; positive helper plus mode bit `1` gives `37`; otherwise status `33` before the `g14/15` tail |
| `0x84228` | shared non-state tail commits the selected status to `0x504d80`, caller `g14` to `0x504d8c`, and selector `15` to `0x504d90` |
| `0x84240` | installs return trampoline `0x84290`, clears callback `g14`, sets `0x504e1c = 1`, initializes status `43`, selector `15`, `0x504d8c = 0`, and `0x504d9c = 7`, then returns through `bx(g1)` |
| `0x842d0` | bit 0 of `0x504e50` skips the wrapper; otherwise it calls `0x84330`, `0x85c00`, `0x848d0`, `0x84b10`, and `0x858f0`, then calls `0x85b00` when `(0x5024e8 & 0xff) == 0` |
| `0x85b00` | loads the six callback accumulators, writes scaled values into the callback frame, ranks the three smallest signed entries, and stores either mode `6` or the lowest entry index at `0x504e48` when the third-minus-lowest spread exceeds `0x1f3` |
| `0x85c00` | derives the callback table mutator's working scale from object `+0x4a`, object `+0x190`, and related state 11/14 source fields `+0x63c/+0x640`; its following 32-entry mutation loop remains separate |
| `0x85d04` | in the selected callback-table path, addresses the state/selector row at `0x5050a0 + state*1152 + selector*144 + 0x8e`, adds 30 to one halfword, and caps the paired row at 1000 only when it is above that threshold |
| `0x85e20` | addresses the sibling state/selector row, subtracts 10 from one halfword, and writes 40 to the paired row when its value is at most 49; larger paired values reject the path |
| `0x85ef8` | walks 32 object records at `+0x20` strides and fills eligible zero odd-byte map slots with the low nibble of `0x504e42` plus bit 7 when global bit 11 is set |
| `0x85f8c` | checks the current outer-loop sibling-map byte for bit 6 and routes that record to `0x86000` when previous bits 9/8/11, current-halfword zero, or object-byte zero holds; otherwise it routes to `0x860a0` (or the shared return path when bit 6 is clear) |
| `0x86000` | replaces the selected `0x509ad0` secondary-map byte with `g14`, rescans that map for original low-nibble collisions, and updates the `0x5074a0` state/selector row with `+30` and a paired-row cap of 1000 only for a unique candidate |
| `0x860a0` | requires map bit 6 and either previous-halfword bit 10 or a nonzero `0x85c00` working scale before continuing to the fallback mutation at `0x860d4`; otherwise it exits through `0x86174` |
| `0x860d4` | subtracts 10 from the selected secondary row, writes paired value 40 for paired values at most 49, and stores callback `g14` into the selected `0x509ad0` map slot after scanning its 32 entries for the candidate's original low nibble |
| `0x86174` | replenishes zero odd-byte slots in the `0x509ad0` secondary map from eligible object records at `+0x20` strides when `0x504e42` bit 11 is set, storing the global low nibble with bit 6 |
| `0x861e0` | saves trampoline `0x86238`, sign-extends callback halfwords into `0x509b94/0x509b98`, clears the second when `0x503b18` is zero, and applies nonzero `0x503b1a` as the final override |
| `0x865e0` | publishes selected mode thresholds to the previous/current/active groups at `0x509b60/70`, `0x509b20/30`, and `0x509b40/50`, then writes `g14` to latches `0x509b80/84/88` |
| `0x86960` | adds 31 to two helper arguments, selects descriptor `0x2fd8872` for bit 8/9 or `0x2fd8876` otherwise, and dispatches with `g1=1,g2=2` to `0x1dc10` (bit 8/default) or `0x1d7d0` (bit 9) |
| `0x869d0` | preserves the input around the `0x85b00` frame-builder call, invokes `0x1cac8` with `g0=10` and saved input `g1`, then dispatches selectors 0–6 through `0x869fc`; selectors above 6 return |
| `0x86a90` | publishes `g14` to `0x503a60` and low-halfword `0x504b94`, calls `0xde630`, `0xc8f10`, `0x6fec0`, `0x9b308`, `0x6fec0`, and `0xc8f60` in order, then falls through to `0x86ac0` |
| `0x86ac0` | calls `0x9baa0` with `g0=0x503ad0`, then when `0x503a04 == 0x5a` copies `0x600` bytes from `0x51c9e0->0x503ad0` and `0x51cfe0->0x5040d0` through `0xf5d40` before rejoining at `0x86b0c` |
| `0x86b80` | calls `0xdf070` with `0x5040d0` only when `0x503a7c` is zero, otherwise skipping directly to `0x86b98` |
| `0x86b0c` | runs the fixed post-copy services through `0xde990`, `0xbe1f0`, `0xbd730`, dynamic `0x503ad4`, `0x23980`, `0xdf070`, `0x26cb8`, `0xbd810`, and dynamic `0x5040d4`, then reaches `0x86b80` |
| `0x86b98` | runs four fixed services, copies halfwords from `0x51cbb0/0x51d1b0` to `0x503ca0/0x5042a0`, calls `0x23d60` with `g0=1`, and calls `0x71080` with `g0=0x503ad0` before `0x86be4` |
| `0x86be4` | requires `0x503a04 == 0x5a`, then routes to `0x86c08` if either halfword at `0x503ca2` or `0x5042a2` is zero, to `0x86c64` if both are nonzero, or to `0x86cb8` when the marker mismatches |
| `0x86c08` | publishes `0x51c9a4/0x51c9ac` from `0x503aa4`; the `0x86c08` entry distinguishes values `0`, `1`, `2`, and other, while the `0x86c64` entry emits `(12,1)` for `0/1` and `(12,0xb4)` otherwise, then converges at `0x86cb8` |
| `0x86cb8` | decrements `0x503a04` and calls `0x1fe90` with `g0=0` when the result is zero, when a result through `0x57` has bit 4 set in `0x5024a4`, or when nonzero `0x503a7c` permits `0x5024f4` values `0x60`/`0x62`; other cases return at `0x86db4` |
| `0x86d38` | after the clear-service path, calls `0x1fe90` with inherited `g0`, then `0x1f080(g0=0)` and `0x423a8`, publishes `0x51c9a4/0x51c9ac` to `0x503a00/0x503a04`, sets `0x503a60`, selects command `0x60` or `0x62` at `0x5032f4`, and stores `g14` at `0x51c942`, `0x51d5e0`, and `0x51c9c0` |
| `0x86df0` | normalizes `0x51c9b0` into timing/state values at `0x51d5e8/0x51d5e4`: indices through `0x77` preserve the marker pair, larger indices use modulo-120 remainder and four-slot buckets, substitute the marker at bucket `120`, and subtract `120` from an oversized published state |
| `0x85c88` | scans 32 odd-byte map entries, applies primary/fallback eligibility gates, replaces a selected entry with callback `g14`, marks primary-path low-nibble matches with bit `5`, and rejects only fallback-path collisions before row adjustment |
| `0x84330` | adjusts the stack by `16`; when `(0x5024e8 & 3) == 0`, clears three halfword slots at `0x509a60` using incoming `g14`, then continues into the bitfield setup |
| `0x84368` | synthesizes selected `0x509a60` flags from preferred `0x5024a4` masks `0x100/0x200/0x400` into bits `4/0/2`, falling back to `0x50249c` bits into destination bits `5/1/3` |
| `0x84470` | flag finalizer: sets bit `7` when bits `5` and `1` are set; otherwise sets bit `6` for bit `4` with bit `0/1`, or bit `5` with bit `0` |
| `0x844f4` | uses `(0x5024e8 & 3)` as a slot selector; nonzero slots jump to `0x847b0`, while slot `0` increments `0x509a68` and subtracts `60` only when the caller-derived `g28 + 31` limit is exceeded before packet construction |
| `0x84524` | prepares the scheduler record header, stores the converted `0x504e28` value and packs `0x504e28/0x504e2c`, and on literal `0x504e20 == 0xffffffff` stores caller `g14` at header `+0x6` before continuing with `r7 = 16` |
| `0x8459c` | alternate scheduler packet path writes eight words to `0x884000`, masks the returned word to 16 bits, stores the record `g7` value at header `+0x6`, and continues at `0x8467c` |
| `0x8467c` | maps `0x509ac0`/`0x509b10` equality to row bits `15/14`, calls `0x847c0`, and publishes its result plus packed frame fields at row offsets `+0xa` and `+0x8` |
| `0x84724` | packs the four scheduler halfwords and object `+0x108` flags into row field `+0xc`; state `31` sets frame bit `3` and uses its alternate packed value |
| `0x847c0` | routes object states `2..13` to the zero-result exit, scans states above `13`, and lets states at or below `1` select zero under the object `+0x64 == 0` or `+0x64 == 6`/mode-bit-5/related-state/control predicates; the scan covers 32 classifier results, keeps the lowest through `5`, emits command `10` plus two difference words for each improvement, and returns the selected result with the last low-16-bit FIFO response |
| `0x848d0` | increments nonnegative `0x509a6c`, resetting above `120`; negative values return unless `0x503a14 > 239`, which continues into `0x8490c` |
| `0x84b10` | updates `0x509a70` with a `120` ceiling/reset, derives `0x5074a0 + related_field_64 * 1088` (`17*64`), and enters recovery scanning only when `0x509ac0 == 1`, mode bit `2` is clear, `0x503a14 > 239`, and the updated counter is zero |
| `0x84b7c` | sends failed recovery gates to `0x84d60`; admitted paths set `0x509a6c = 1` and enter the eight-record recovery search at `0x84bb4` with index `0` |
| `0x84bb4` | scans eight recovery records with 136-byte stride at signed-halfword field `+0x86`; target-greater records become selected and replace the working target, while target-less records advance; `-1` selects the current record |
| `0x84bec` | seeds the recovery source frame at `(0x509a68 - 1) mod 60`, scales it by `16`, sets scan limit `59`, and loads the frame `+0x8` low nibble |
| `0x84c98` | builds a recovery row at `base + index * 144`, copies signed scalar halfwords to `0/2/4/6/8/a`, stores `240 - 4*delay` at `+0x84`, selects scalar source data from `counter - delay` with one negative `+60` correction, copies 60 `+0xc` fields from source index zero, and marks the selected recovery record `+0x86` with `100` |
| `0x84d60` | stores the recovery flag at `0x509ac0`, copies control-byte bit `3` from `0x504e50` to `0x509b10`, and returns |
| `0x84d90` | saves/restores `g8` through `fp+0x40`; bit `0` of `0x504e50` returns immediately, otherwise execution continues at `0x84dc4` |
| `0x84dc4` | scans eight rows; field `+0x86 > 49`, global match set, and more than two local matches reaches `0x84dac`, otherwise exhaustion continues at `0x84f10` |
| `0x84dac` | sets bit `8` in live `g13`, stores it at `0x504e42`, stores caller `g14` at `0x504e44`, and branches to `0x84f10` |
| `0x84f10` | scans eight alternate rows; field `+0x7c > 49`, global match set, and more than two local matches reaches `0x85058`, otherwise the scan returns |
| `0x85058` | loads matched row `+0x8c`, sets bit `9` in `g13`, stores the result at `0x504e42`, stores the row value at `0x504e44`, restores `g8`, and returns |
| `0x85080` | saves `g8`/`g12` at `fp+0x50`/`fp+0x60`; control-byte bit `0` restores both and returns, otherwise execution continues at `0x850ac` |
| `0x850ac` | masks `0x5024e8` to a byte; values above `10` exit to `0x85128`, while `0`–`10` continue into the ratio setup |
| `0x850c0` | forms object/related first-over-second ratios from signed `+0x1d0/+0x1d8` halfwords; exits on nonnegative object-minus-related difference, otherwise continues at `0x85134` |
| `0x85134` | selects frame slot `0x5096a0 + slot*16`, table row `0x5074a0 + state*1088`, and upper-halfword targets minus `70`; row field `+0x86` is ANDed with the frame g8 upper-halfword before the `<=49` test, which exits to `0x853a0`, otherwise scanning continues at `0x851a8` |
| `0x851a8` | masks selected row field `+0` to 16 bits and compares it with `0x504d68`; equality sets the scan `r7` match flag |
| `0x851c0` | masks row field `+6`; sets `r5` for values through `frame_upper+70`, bypassing the lower bound when `frame_upper <=69`, otherwise requiring the inclusive +/-70 interval |
| `0x85204` | masks row field `+4` and frame `g9` low halfword; equal values increment `r5`, then execution reaches the shared `0x847c0` call |
| `0x8521c` | reloads object `+0x74` into `g0`, passes `fp+0x40`/`fp+0x44` in `g1/g2`, and calls shared handler `0x847c0` |
| `0x8522c` | masks row field `+6` to a byte and compares it with the value restored from `fp+0x40`; equality increments `r7` |
| `0x852ac` | exits to `0x853a0` when `r5 <= 2` or `r7 <= 1`; only `r5 >= 3` and `r7 >= 2` continue at `0x852b4` |
| `0x852b4` | sets status bit `10`, publishes row `+0x84` to `0x504e44`, dispatches selectors `0..6` as statuses `6,5,4,2,3,1,1`, and uses caller `g14` above `6` |
| `0x853a0` | increments the scan index, advances both row pointers by `0x88`, retries through index `7`, then restores `g8/g12` and returns |
| `0x853c0` | decodes published status/row values into object `+0xec+0x1c`; bit `8` selects `0x5050a0 + state*1152 + selector*144 + 20` or `0x5074a0 + state*1088 + selector*136 + 12`, maps table bits `8..11` to destination bits `12..15` while preserving the low nibble, increments `0x504e44`, and resets `0x504e42` above `239` |
| `0x8552c` | extracts the selected word high byte and derives callback `g1/g2`, `g3`, and `g13` through the observed bit-pair rules |
| `0x8558c` | aligns positive `0x504e44` upward and nonpositive values downward to four bytes; `cmpibge 1,delta` selects fallback `g3/g13 = 8` below delta `1` |
| `0x855b8` | requires `0x503a80 == 0` and `0x504dc0 <= 149`, then admits only target difference `>20` for the object-ratio path |
| `0x855f8` | admits signed object `+0x1d0 > (+0x1d8 >> 2)`; for timing differences above `45`, remainder `0x5024e8 % 300 > 45` forces dimensions `1/1` |
| `0x85634` | applies the early difference `>45`/remainder `>45` dimension `1/1` override, then exits for difference `<=20` or remainder `<=90`; only the remaining difference `>20` and remainder `>90` path forces dimensions `1/1` |
| `0x85678` | admits only decoded selector `1` into the selector-1 timing/position path; all other selectors branch to `0x85784` |
| `0x85784` | selector `2` with `0x504dc0 <= 149`, object ratio `+0x1d0/+0x1d8 > 1.65`, and dimensions `2/2` changes `g1` to `1`; other selectors skip to `0x857e4` |
| `0x857e4` | selector `3` with `0x504dbc <= 32`, object ratio `+0x1d0/+0x1d8 > 1.65`, and dimensions `2/1` changes `g1` to `1`; other selectors skip to `0x85844` |
| `0x85844` | converts callback `g1/g2` to dimensions `1/2/4`, sets persistent mode bits `3/4/5` from `g3/g13` and source bit `3`, and stores the two words at `0x504dac/0x504db0` |
| `0x858f0` | snapshots object `+0x48/+0x4a` at `0x509b8c/0x509b90`; unless `0x503a78 == -1`, caller `g14` becomes the second value, while the `-1` case scales it for related state `11/14` using `+0x63c/+0x640` divided by `100`; the earlier object `+0x190` compare is overwritten and does not gate scaling |
| `0x859b8` | masks `0x509b8c` low byte, calls the recovered stage-bucket entry `0x86638`, subtracts `1`, exits above normalized index `4`, and dispatches indices `0..4` through the five-entry callback table |
| `0x859ec`/`0x85a20`/`0x85a54`/`0x85a88`/`0x85abc` | divide `0x509b90` by `0x503a78+1`, add to `0x509b24/28/2c/30/34`, clamp at `10000`, store, and return |
| `0x8490c` | rejects object `+0x190 != 0`; related state `11/14` selects `+0x63c/+0x640`, divides by `100`, multiplies object `+0x4a`, and sends zero products to `0x84b08` |
| `0x84980` | sends zero ratio products to `0x84b08`; nonzero products set `0x509a6c = 1` and enter the eight-record search at `0x84994` with index `0` |
| `0x84994` | scans up to eight signed-halfword values at field `+0x8e` in 16-byte records; when the working target exceeds a record, that record becomes selected and replaces the working target, while `target <= record` advances without selection |
| `0x849d0` | converts the `0x8d2a0` result to `result - 1` or fallback `180` when result-minus-one is nonnegative, subtracts from `0x509a68`, adds `60` for a nonnegative slot, and scales the slot by `16` for `0x5096a0` |
| `0x84a04` | loads selected frame offsets `0/2/4/6/a`, computes the destination row with a `144`-byte stride, and feeds `240 - 4*normalized_delay` plus those sources to `0x84a34` |
| `0x84a34` | writes a packet row at `table_base + index * 144`, copying signed source halfwords to offsets `0xa/0xc/0xe/0x10/0x12` and storing `240 - 4*normalized_delay` at offset `0x8c` |
| `0x84a74` | advances the source cursor through `59`, wraps above that bound to zero, scales the next index by `16`, and enters the bulk copy at `0x84a80` |
| `0x84a80` | copies signed scalar frame fields, copies 60 record `+0xc` halfwords into row offsets starting at `+0x14`, writes `100` at `+0x8e`, and returns through `0x84b08` |
| `0x82d74` | clears the second word of the `0x504d80` quadword and publishes `0x504d90 = 15` for statuses `0..6` or `8` |
| `0x82650` | writes status `8` for `(r5,r6)=(0,0)`; for `(0,1)` writes `3` when `0x504d70 <= 4` or `4` above it; all other pairs continue into the descriptor path |

Its tail also exposes the snapshot protocol: the active four-word pair is
copied to `0x509b40`/`0x509b50`; when the guard at `0x509b80` is exceeded, the
previous snapshot is restored and `0x509b88` is refreshed from `0x503a70`.
The routine clears `0x509b88` when committing a new snapshot and uses
`0x503a74`, `0x503a6c`, and `0x503a70` as the three guard inputs.

The remaining transition helpers expose these additional literals:

| Entry | Directly observed values |
| --- | --- |
| `0x80710` | compares `0x504d70` against `1`, reads object halfword `0x184`, applies offset `0xffff9800` on the low-state path, and subtracts `8` from the state on the alternate path; the accepted result is classified through `0x73508`, then `0x72630[g6*4]` is stored at `0x504d94` and the base state is initialized to `10` at `0x504db8` |
| `0x807d0` | returns unless `0x509b24 > 0x1f3`; accepted processing uses floats `0xbf800000` and `0x42c80000`, byte mask `0xff`, and halfword masks `0xffff`/`0xffff8000` |
| `0x807d0` tail | uses object offsets `0x200` and `0x218`, reads the status byte at `0x504e34`, accepts masked-byte differences up to `5`, and emits selectors `29`, `30`, and `10`; the packet coordinate constant is `0x41a00000` |
| `0x810d0`/`0x81120` | gate on `0x509b2c > 0x1f3` and range `0x150000..0x190000`; use float `0x406f4000`, test `0x504e50` bit `3`, and recognize field values `5`, `1`, `6`, and `7` |
| `0x81610` | chooses `0xffffc000` or `0x4000`, classifies through `0x73508`, indexes `0x72780[g0*4]`, and emits selector `30` |
| `0x81e60` | requires `0x5039f4 == 4`, `0x503a00 == 10`, and `0x504e42 == 0`; its later dispatch table is selected by object field `0x64` |
| `0x81f60` | classifies the state/timing prefix, writes the paired `0x504d78/0x504d7c` selector cells, chooses `2` or `3` for state `6` with negative `0x504d60` timing, and clears `0x504d88` on the fallback arm |
| `0x82040` | dispatches object field `0x64` through a ten-entry table for values `0..9` |

The first dispatcher bodies make several constants explicit: cases `0`–`3`
compare the converted `0x504df8` value against `0x504d60`; case `0` also uses
`g0 mod 10` and a three-way remainder split. Case `2` compares against the
converted `0x504dd6` value using float `0x40340000` and writes states `1` or
`7` to `0x504d80`. Case `3` uses float `0x406f4000`, gates on
`0x504e28 == 1`, and stores state `11` when the remainder from divisor `10`
is below `3`. These are arithmetic/control-flow facts only; the case names
remain unresolved.

The adjacent object-transition slices add these literal values:

| Entry | Directly observed values |
| --- | --- |
| `0x7f4d0` | gates on `0x509b28 > 0x1f3`, uses floats `0xbf800000` and `0xbff00000`, object offsets `0x200`/`0x218`, byte mask `0xff`, and halfword mask `0xffff` |
| `0x7f4d0` tail | stores selector `6` at `0x504d9c`, stores `0x64` at `0x504da0`, derives `0x504db4 = 0x9c4 - 1`, and has explicit result states `1` and `22`; the alternate object halfword gate is `0x90000` |
| `0x7f4d0` extended tail | on the paired route, recognizes object halfword values `27` or `30`, uses threshold `0x5dc`, and applies coordinate offsets `0xffff9a80` or `0x6580`; the selected result comes from `0x72780[index*4]` or `0x72720[index*4]`, with state `30` stored at `0x504db8` |
| `0x7fca0` | compares the shifted object halfword `0x172` against `0x10000` and `0xd0000`, then recognizes object field values `0`, `6`, and halfword values `1`, `14` |
| `0x7ff40` | indexes object bytes at `0x200` using a 32-byte stride, derives a record from `0x562cb0` using a 48-byte stride, and uses float `0x41200000` after a modulo-6 reduction |

The remaining small case bodies write additional explicit states to
`0x504d80`: direct values `19`, `26`, and `27` occur, while another path adds
`2`, `4`, or `11` to its computed base. The fallback formatter uses `g0 mod 3`
and maps the remainder cases to states `19` and `20`. These writes complete the
recoverable literal outputs of this ten-way dispatcher without assigning
meaning to the state numbers.

### Object-command packet constants

The repeated builders at `0x9de50`, `0x9e250`, `0x9e650`, `0x9e880`, and
`0x9eab0` all expose the same packet layout. They scale an input index as
`index * 3 * 4`, read halfwords at ROM addresses `0x562436`, `0x562438`, and
`0x56243a`, emit selector `25` (the instruction form is `31 - 6`), and then
copy the resulting four words from `0x884000` into caller/output fields at
offsets `0`, `4`, and `8` plus the paired `0x10`, `0x14`, and `0x18` fields.
The repeated structure makes the address scaling and offsets confident, while
the command’s device-level meaning remains unresolved.

### Later state and dispatch constants

The state helpers around `0x77b00`–`0x786d0` provide another bounded set of
values:

| Entry | Directly observed values |
| --- | --- |
| `0x778b0` | uses float constant `0x461c4000`, table base `0x505060`, state base `0x504d70`, masks `0x3fff` and `0xffff`, and compares paired converted fields from record offsets `8` and `16` |
| `0x77c40` | scans per-record byte/halfword data at base offset `0x200`, tests byte mask `0xff`, bit `13`, and marks the output byte at `0x504e50` with bit `3`; its record selector limit is `0x48` |
| `0x77de0`/`0x77e20` | copy exactly `0xf4` bytes between `0x504f60`, `0x504d60`, and `0x504e60` using the aligned copy helper |
| `0x78090` | maps state values `4` and `7` to divisor `0xbb8`, otherwise uses `0x64`; clamps the quotient to `0x5a`, forces state `1` when the source reaches `15*8`, and stores the result at `0x504d88` |
| `0x784c8` | dispatches values `0` through `9` through a ten-entry table; the first cases test bits `1` and `2` of `0x504e30` and set `0x504d84` to `1` |
| `0x786d0` | compares `0x504d60` against converted `0x504dd6`, uses float constant `0x40340000`, and routes to the selectors initialized at `0x78408`/`0x783c8` |

These values are recovered from literal operands and table sizes; the state
machine’s higher-level labels remain unresolved.

The adjacent constructors add two more explicit table facts: `0x3f550`
scans `0x51ad10` in `0x24`-byte steps with a `23`-entry bound, uses selector
`18` when the caller flag is nonzero and `17` otherwise, and derives the
halfword field through `0x3eca0[index & 0xffff]`; its allocation counter stops
at `0xcf`. The dispatcher at `0x41f20` uses the same `23`-entry/`0x24`-byte
walk, masks a record selector with `0xffff`, and indexes its indirect-call
table at `0x41c50[selector * 4]`.

The next trace comparison promotes ten routines whose dataflow is bounded:

| Entry | Confirmed behavior |
| --- | --- |
| `0x34c0` | clears the input/timing fields at `0x5024c0–0x5024d2`, then calls `0x22f0` and `0x2330` |
| `0x3540` | clears `0x5023f2`, updates `0x5023e4` from bit 3, and on state 6 with timing <= `0x3ff` and `0x1d00034 == 0` advances the `0x1d00038`/`0x1d0003c` fields, copies the table, and optionally calls `0x2a580(0x111b)`; its `0x3658`/`0x3754` counter gates update or clear `0x5024c2`/`0x5024c0` and conditionally advance the remaining timing fields |
| `0x3a38` | parses one byte, handles zero/refill and signed-underflow cases (including the pending-second decrement), and clears a selected bit in `0x502484` |
| `0x3ae0` | applies the byte parser to the two state bytes at `0x5024cc` and `0x5024d0` |
| `0x3b10` | gates the incremented `0x1d0002e` timing value against `0x1d00038`, requires `0x5024a4` bit 4 after the status exception, and reaches the copy helper only when the signed counter wraps before `0x2a580(0x111c)` |
| `0x3ba0` | compares controller timing/status registers at `0x1d0002c`, `0x1d00034`, and `0x1d00038`; equality at the limit advances, while the `0x2330` copy/rewind is limited to zero-mode signed-counter wrap |
| `0x183b8` | classifies a device address into result values `0–3` using masked range tests |
| `0x18438` | validates a pair of mode values and returns boolean success in `g0` |
| `0x18488` | initializes the host byte queue state |
| `0x1c2c0` | saves arguments and floating-point context, then prepares the video transfer workspace |
| `0x1cbb8` | handles TAB/LF control characters and updates text column/row state |

The trace confirms these routines execute, while the direct dataflow supports
the names above without requiring a final interpretation of individual input
bits or controller registers.

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

The I/O self-test branch is also bounded. `0x00002768` returns directly when
the low-byte check succeeds. On failure it calls `0x00002700`, which clears
byte fields at `0x00502480`, `0x005023f0`, `0x00502481`, and `0x00502482`,
clears the halfword at `0x00502484`, invokes the input initializer at
`0x00002bb0`, and then initializes the 16-byte host queue at `0x00018488`.
The success arm (`bal 0x000026e8`) is a single-use link-laundering thunk —
same shape as the shared `0x27d8` trampoline but with this dispatch as its
only caller — rejoining the `[0x5023e0]` reload with no observable effect.
The routing plan is modeled in `recovered_io.c` as the pure
`recovered_io_self_test_dispatch_plan` (the integrated image already
performs the exact service-call sequence), checked by
`von/tools/test_recovered_io_self_test_dispatch.py`. The 60-second
attract PC log visits `0x2768`, `0x2774`, and `0x277c`, attesting the
failure arm on that path. Both arms share the exit tail at `0x277c`
(`ld [0x5023e0],g0`, `ret` at `0x2784`), now inside the dispatch ledger
range. Immediately past it, the continuation-thunk cluster at
`0x2790`/`0x27b0`/`0x27d0` repeats the link-laundering shape with
continuations `0x27a4`/`0x27c4`/`0x27e4`; the word `0x00012790` appears
at table entry `0x132ec`, but sibling entries address data records so even
that role is unproven — while the mid-body entries at `0x2798`/`0x27b8` are
called by flag-dispatch arms with the link preserved. The cluster is modeled
as ABI scaffolding, not translated.
`recovered_io_failure_reset()` is the pure five-field translation of the
deterministic stores. The input initializer's 60 index values and 1,170-byte
port-write plan are checked by `von/tools/test_recovered_io.py`; its mapped
port execution remains separate from the pure plan.

The normal-mode command builder at `0x00002ab0` is now bounded as well. It
emits a 34-byte sequence: the nine-byte inline prefix at `0x00002aa0`, five
`0x51/0x71` plus `0xd1/0xf1` pairs selected from input-index bits 5 through 9,
five corresponding pairs selected from table-value bits 15 through 11, and
the fixed tail `01 01 51 d1 51`. Its final wait on the controller status port
is not folded into the pure command model. The plan is checked across all 60
input indices and representative edge/full-mask table values.

The following input sampler loop at `0x00002da0` normalizes the eight-byte
state block at `0x00502490` through `0x00502497`: each byte becomes the floor
average of its previous value and the low byte read from `0x01c0001e`. The
control writes and subsequent packed-status synthesis use additional device
reads and remain separate. The averaging transform is covered for every
possible sampled byte.

The remainder of `0x00002da0` is now represented as a pure packed-state
transform. Reads at controller offsets `+2`, `+4`, `+6`, and `+c` form the
24-bit mask written through `status_49c` and the three low-byte status fields;
the ROM then applies `andnot`/`notand` operations to the work words at
`0x005024a0–0x005024bc`. The transform is vector-tested with edge masks and
nontrivial prior state, while controller write timing and input-bit labels
remain unassigned.

The normal-mode wrapper at `0x00002c10` now has a complete host-side schedule:
for each of 30 table entries it emits the 21-byte setup sequence followed by
the indexed 34-byte command, then repeats the same table with indices offset
by 30. It then emits the fixed 21-byte sequence at `0x000028b0`, yielding
3,321 bytes in the exact ROM order. Only the per-byte controller wait remains
outside the pure schedule.

The failure-mode sampler at `0x00002cf8` is also bounded. After writing `0x4f`
to `0x01c00010`, it masks the sampled input byte with the low byte of the
`0x01c00002` word, stores the resulting byte and complementary status bytes
at `0x005023f0`, `0x00502480`, `0x00502481`, and `0x00502482`, and latches
the saved halfword to `0x01c0000a`. The pure transform is covered by the same
I/O vector test; the meanings of individual input bits remain unassigned.

This gives us an initial host-code order for the next annotations: I/O board
startup, SHARC bootstrap, geometry bootstrap, then the main-data copy and
decompression callers.

The first non-bootstrap `main_data` consumer worth annotating is the routine at
`0x3c40`. It publishes device command `8`; when phase and status gates permit,
it walks a table at bus address `0x02ea2918`, consumes two 16-bit fields at a
time, and passes each record through `0x1cac8`. That helper stores the three
current fields in the host state block at `0x00504cdc`-`0x00504ce4` and returns
through a saved pointer; nonzero text bytes are emitted through `0x1cc40`.
The handler decrements progress at `0x503a04`; on the `-1` comparison
completion path it sets `0x5024d4`, clears phase, and advances `0x5039f4`. It
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

The formatter boundary is now more specific. `0xf5100` saves the incoming
register arguments in a 0x40-byte local context, stores the format-string
pointer and an initial argument cursor, then enters `0xf5190`. That routine
handles ordinary bytes immediately through `0x1cc40`; other bytes are decoded
through the 0x100-entry table at `0xf5210`, with unsupported entries landing at
`0xf5bf4`. The parser maintains a flag bitfield in `r9`, a separate argument
cursor in `r5`, and pending numeric/width state in the local context. The
table has distinct live handlers for flag updates, width/alignment, character
and string arguments, signed integer conversion, and floating-point
conversion. This explains why the existing plain-string walker and two-digit
formatter are safe isolated slices, while the general formatter still needs
conversion-specific vectors before it can be replaced.

The dispatch table can now be stated exactly from the listing. The parser's
`g4 <= 120` guard means only the first 121 table slots are reachable. Slot
zero returns through the ordinary end-of-string path; slots 1-31 and the
remaining slots are unsupported and land at `0xf5bf4`. There are 39
non-default slots in the reachable range. The live slots are:

```text
  ' ' -> f53f4       '#' -> f5408       '%' -> f5608
  '*' -> f5410       '+' -> f5474       '-' -> f546c
  '.' -> f547c       '0' -> f5544       '1'..'9' -> f554c
  'D' -> f561c       'E','G','e','f','g' -> f5688
  'L' -> f5588       'O' -> f5800       'U' -> f5954
  'X' -> f59b4       'c' -> f55a0       'd','i' -> f5620
  'h' -> f5590       'l' -> f5598       'n' -> f5790
  'o' -> f5804       'p' -> f5860       's' -> f58bc
  'u' -> f5958       'x' -> f59bc
```

This separates syntax from conversion semantics: space, hash, plus, minus,
zero, length/precision punctuation, and decimal digits update parser state;
`c`, `d`/`i`, `e`/`f`/`g`, `o`, `s`, `u`, and `x` reach conversion handlers.
The uppercase `D`, `E`, `G`, `L`, `O`, `U`, and `X` entries are not aliases
that can be assumed from their lowercase neighbors: they select distinct
ROM handlers or flag updates. The map is static evidence only; conversion
width, argument consumption, and output rounding still require vectors.

The integer handlers share a single emission tail at `0xf5a24`-`0xf5c04`.
The signed `d`/`i` handler at `0xf5620` reads one 32-bit argument, converts a
negative value to its magnitude, records `'-'` as the prefix, and selects
radix 10. The `u` handler at `0xf5958` selects radix 10 without signed
normalization; `o` at `0xf5804` selects radix 8; and `x` at `0xf59bc`
selects radix 16. Digits are generated by repeated remainder/division while
walking backward from the local buffer at `0x19c(fp)`. The lowercase path
uses the `0123456789abcdef` table at `0xf5150`; `X` first switches to the
uppercase table at `0xf5170` and then uses the same radix-16 tail. `D`, `O`,
and `U` enter their lowercase counterparts after setting the formatter's
bit-zero mode, so they are distinct ROM entry points rather than aliases in
the dispatch table.

The common tail then computes the required field width, emits leading
padding or the recorded prefix, emits the reversed digit buffer, and applies
trailing padding for left alignment. A zero value has a separate path at
`0xf5a38`; alternate-form handling can replace the digit alphabet pointer
with the lowercase table at `0xf5a68`. This closes the integer formatter's
control flow, but the exact caller-visible contract for precision zero,
alternate prefixes, and the uppercase mode still needs runtime vectors.

There are now two concrete integer call sites besides the standalone format
string: `0x00c57b84` formats `"Result : Node ID = %-2d\n"`, and
`0x00c5a88` formats `"Total Nodes = %-2d"`. The same diagnostic block calls
the formatter with `"%s"` at `0x00c57ffc`, giving a direct string-conversion
vector in addition to the integer vectors. These callers pass the text origin
through `0x1cac8` immediately before the formatter call, so their output can
be checked in a future trace by correlating the resulting tile writes at
`0x01000000` with the formatter's shared sink.

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

The reconstructed C path preserves the transport detail that matters here:
`0x00884000` is a fixed FIFO port, so every halfword is written to the same
address. An incrementing `u16 *` implementation reached the end of the mapped
window after `0x2000` writes, produced an 8,192-word boot, and triggered an
ADSP PC-stack underflow. The fixed-port implementation transfers all 11,038
words; the paired geometry program stream is also enabled from its validated
`main_data + 0x00fc6290` source window.

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

The next trace sieve identifies four shared helpers: `0x2a4e0` validates a
command or mode value before updating runtime state; `0x6ece0` converts paired
floating-point coordinates into fixed-point values; `0xbf0c0` searches a
packed bitfield for the next set bit; and `0xe1f20` expands byte values through
the glyph table into the three geometry/text tile planes.

The trace also confirms `0xf5058` as the runtime PRNG step: it advances the
persistent state at `0x5785d0` with a fixed multiply-and-store sequence.

`0xf5d40` is the shared alignment-aware memory-copy helper used by reset-time
table and ROM transfers; its tail handles 8-, 4-, 2-, and 1-byte units.

`0xf5c58` is the matching byte-buffer comparison helper, returning zero for
an equal span or the first differing byte delta.

`0xf5100` walks formatted/text strings and routes ordinary characters through
the tile writer at `0x1cc40`, with separate handling for control values.

`0xf5190` is the formatter core used by that dispatcher: it walks the input,
sends ordinary characters to `0x1cc40`, and routes control/format bytes through
its local handler table.

The same trace cluster exposes a 64-entry command queue at `0x51aa70`:
`0x2a458` checks space, `0x2a4a8` pushes a value and advances the write index,
and `0x2a430` supplies a short countdown delay used around queue operations.

The adjacent `0x2a5f0` entry is the alternate command/mode validator, with
the same queue-space and enqueue sequence but a separate continuation path.

`0x79050` is now marked as a randomized record-state dispatcher. It selects
one of ten handlers from the state byte at record offset `0x64`, using the
record value at offset `0x74` and the shared PRNG as inputs.

`0x1c618` initializes the video-plane state: it clears the four mapped tile
planes and resets the associated control fields in `0x504d24–0x504d38`.

`0x1ccf8` is the corresponding one-byte video command/data write primitive;
it stores its argument at the mapped window `0x1800000` and returns through
the saved indirect return address.

`0x1d310` is the shared glyph-render core called by several string walkers;
it selects one of four glyph-layout entries and writes the character into the
active tile/attribute state.

`0x9e050` is a geometry record upload helper. It selects profile words from
the table at `0x562436+`, emits them through the geometry FIFO `0x884000`, and
copies the resulting three-word record into the caller's buffers.

`0x1bb90` expands packed 16-bit glyph/tile words by rearranging their bit
groups into the output plane layout, including overlapping upper-bit fields;
source bits 4..7 and 15 are dropped. It is used by the text-table builders.

`0xe2040` is the related three-plane byte expander. It looks up each byte in
the glyph table at `0x5775b0` and writes the result into paired base and
`+0x100` tile planes.

`0xe2120` selects a text asset through the table at `0x142e94` and delegates
its expansion to `0xe2040`, uploading the resulting bytes into the three tile
planes.

`0xe1e08` dispatches geometry/text output mode from the hardware byte at
`0x1d00027`, selecting one of ten mode-specific setup blocks.

`0xdf070` updates geometry object transform state: it validates position and
mode fields from the object record, selects the applicable transform branch,
and prepares values for the geometry submission path.
Its bounded prelude is now modeled by
`recovered_geometry_transform_payload_select_df070.c`: the halfword at the
related record's `+0x02` selects the local `+0x14/+0x18/+0x1c` triplet for
class 0, the late `+0x158/+0x15c/+0x160` triplet for class 1, or the follow-up
`+0x164/+0x168/+0x16c` triplet for class 2; unsupported classes use the zero
default before the shared `0xdf120` path. Position/mode validation and the
indirect transform handlers remain separate.

`0xe2330` dispatches startup input/device mode. It checks board mode bytes at
`0x1a14002`, `0x5770d0/1`, and `0x577590`, then selects a mode-specific handler
from its local dispatch table.

`0xe3a70` renders a compact three-byte text token, routing each byte through
the glyph-block writer at `0x1d570`; callers use it for short status labels.

`0xe39c0` selects paired status strings from the tables at `0xe36c0` and
`0xe3700`, rendering them through the alternate and control-aware text walkers.

`0xe39f0` is the status-row string wrapper around `text_string_walk_control`,
used while rendering repeated rows of UI/status text.

`0xe3a00` wraps the glyph-table matcher at `0x1d880` for status/result label
rendering.

The data immediately following the video dispatch terminal at `0xe35a0` is
structured rather than executable: `0xe35b0` holds ten 8-byte MSB/source
descriptors, `0xe3600` holds ten 12-byte alternate descriptors, and
`0xe3680`, `0xe36c0`, and `0xe3700` hold the ordinal/suffix string tables.
The copy helpers at `0xe3740`, `0xe37b0`, and `0xe37f0` transfer those tables
into runtime buffers before the status render helpers use them. `0xe3a30`
renders the WINS/LOSSES row, while `0xe3a70` consumes exactly a three-byte
status token and routes each byte through the glyph-block writer.

The following service arm at `0xe3ab0` selects one of three status screens
through the counter at `0x5783b4`; its handlers are `0xe3b70`, `0xe3dc0`, and
`0xe3f30`. The first two are now bounded through their visible returns. Their
associated literals include `TODAY'S BEST PILOTS`, `TODAY'S TOP WINS`, and
`FAVORITE MACHINES`, with compact formatting tables immediately preceding the
render code.

The third handler at `0xe3f30` is the most data-heavy of the three: its first
loop accumulates eight device scores from the `0x1d00000` table, and its second
loop resolves those scores into an eight-entry work array before rendering
machine names and counts. It returns at `0xe4188`, after advancing the shared
status counter.

The next startup preparation pair begins at `0xe4250` and `0xe4720`.
Both paths build compact runtime records from the machine/status data at
`0x578410`/`0x578460`, initialize the shared workspace and queue state, and
return the saved register context. Their short early exits at `0xe4700` and
`0xe4abc` only set service state `26`. The four adjacent alphabet tables at
`0xe4190`, `0xe41c0`, `0xe41f0`, and `0xe4220` are literal machine-name
character maps used by this status subsystem.

The startup dispatch target at `0xe4ae0` is a long shared runtime service,
ending at `0xe5430`. It updates mode/timing fields, services both player
object records through indirect callbacks and transform helpers, then advances
the status/geometry state. The visible `ret` at `0xe5430` provides the
boundary; the following `0xe5440` region is literal data.

The `0xe5440` literal block is a fixed-width three-byte token table. The
consumer at `0xe54a0` scans it against the active bytes at `0x5784e8–0x5784ea`,
applies the PRNG-based normalization case when needed, and publishes the
result into the selected `0x578410`/`0x578460` record. The following dispatcher
at `0xe5650` routes status state values to the next renderer and returns at
`0xe5698`.

The main list renderer at `0xe56e0` returns at `0xe5a88`; its branch at
`0xe587c` handles the populated-record case and otherwise uses the
space-filled fallback at `0xe56a0`. The alternate renderer at `0xe5a90`
returns at `0xe5bb0` and shares the ordinal/count/token helpers, but sources
its records from the alternate runtime buffer.

The following variant at `0xe5bb4` repeats the same nine-record presentation
using the alternate record buffer and returns at `0xe5d2c`. The compact
dispatcher at `0xe5d30` gates on the board byte at `0x1d00026`, selects among
the state-specific paths: state 1 reaches `0xe61c0`, state 2 reaches
`0xe6660`, and states 0 or at least 3 reach the common gateway at `0xe5da0`.

The dispatcher prefix is modeled by
`recovered_status_service_state_dispatch_e5d30.c`: a zero board byte at
`0x1d00026` returns immediately; admitted state 1 targets `0xe61c0`, state 2
targets `0xe6660`, and states 0 or at least 3 target `0xe5da0`.

The entry prefix of `0xe5da0` is modeled by
`recovered_status_transition_gateway_prefix_e5da0.c`. It reduces the signed
timer modulo `0x870`, returns for remainders through `0x437`, routes exactly
`0x438` into the special packet arm, and sends larger remainders to
`0xe5de8`.

The exact-`0x438` arm is modeled by
`recovered_status_transition_gateway_special_438_e5dbc.c`: it calls
`0x1c618`, publishes `0xc000`/`0x8000` to `0x504d2c/0x504d2e`, sets bit 9 at
`0x100a000`, and joins the shared continuation at `0xe60d0`.

The following gateway gate is modeled by
`recovered_status_transition_gateway_439_gate_e5de8.c`: only remainder
`0x439` reaches the status-render setup at `0xe5df0`; other general-window
values continue at `0xe5f48`.

The first status-record gate at `0xe5e40` is modeled by
`recovered_status_render_record_gate_e5e40.c`: record `+4` at `0x578410`
equal to `0xffffffff` selects asset `0xe3b50` through `0xe3a00`; other values
enter numeric formatting at `0xe3a10`.

The numeric arithmetic at `0xe5e60` is modeled by
`recovered_status_render_numeric_values_e5e60.c`: it derives
`record/0xb40`, `(record/48)%60`, and `((record%48)*33)/48` using signed
division/remainder, with all three values sent to `0xe3a10` between assets
`0xe3b5a` and `0xe3b5c`.

The row epilogue at `0xe5ebc` is modeled by
`recovered_status_render_row_advance_e5ebc.c`: it advances the record offset
by `8`, text column by `3`, and loops through row `4` before continuing at
`0xe60d0`.

The general-window `0xe5f48` arm is modeled by
`recovered_status_transition_gateway_special_654_e5f48.c`: only remainder
`0x654` enters it, publishing `0xc000`/`0x8000`, storing `0x200` at
`0x504d24`, setting device bit 9, and starting status setup through `0x1cac8`.

The transition gateway at `0xe5da0` reduces the service timer modulo `0x870`
and handles the early transition values before joining its common continuation
at `0xe60d0`; its visible return is at `0xe61bc`. The parallel gateway at
`0xe61c0` performs the corresponding alternate rendering path and joins at
`0xe6410`, returning at `0xe64fc`.

The state-1 gateway prefix at `0xe61c0` is modeled by
`recovered_status_transition_variant_prefix_e61c0.c`: it uses the same
signed modulo-`0x870` and `0x437/0x438` split, returning at `0xe61d0`, sending
exact `0x438` through `0xe61dc` to `0xe6410`, and routing larger values to
`0xe6208`.

The state-1 exact-`0x438` arm at `0xe61dc` is modeled by
`recovered_status_transition_variant_special_438_e61dc.c`: it calls the fixed
helper at `0x1c618`, stores `0xc000` and `0x8000` at `0x504d2c` and
`0x504d2e`, sets bit 9 at device address `0x100a000`, and continues at
`0xe6410`.

The larger state-1 branch at `0xe6208` is modeled through
`recovered_status_transition_variant_439_prefix_e6208.c`: exact remainder
`0x439` enters the alternate renderer setup, using helper `0x1cac8`, renderer
`0x1d880`, and five 12-byte records rooted at `0x578460`; its text column
starts at 19 and advances by 3 per record before joining `0xe6410`. Other
remainders fall through to the `0x654` comparison at `0xe62f8`.

The state-1 exact-`0x654` arm at `0xe62f8` is modeled by
`recovered_status_transition_variant_654_prefix_e62f8.c`: it publishes
`0xc000`/`0x8000` and `0x200`, sets device bit 9, invokes the status helper
with renderer arguments 13 and 12, and scans five 12-byte records from
`0x578460 + 0x3c` using index offset 31 and text columns 19,22,25,28,31
before joining `0xe6410`.

The shared state-1 continuation at `0xe6410` is modeled by
`recovered_status_transition_variant_common_tail_e6410.c`. It accepts the
signed remainder windows `0x438..0x478` and `0x654..0x694` (with values below
the first lower bound rejected), programs the
status fields (`0x504d2c = 0x4000`, `0x504d24 = 0x8000`, and clears
`0x504d26`), and initializes 0x200 halfwords rooted at `0x577bb0`; values
outside those windows clear the transient status fields and return at
`0xe64fc`. The table-entry helper now captures the exact nonzero band:
indices `0x98..0x10f` receive `abs(0x200 - 8 * window_delta)` and all other
indices are zero.
The final return gate at `0xe64f0` calls `0x1c618` only for exact remainder
`0x86f`, then returns at `0xe64fc`.

The profile renderer entry at `0xe6500` bounds its selector to eight cases and
dispatches through the local table at `0xe651c`. The effective profile mapping
is `[0,4,3,7,1,2,6,5]`; out-of-range selectors use profile 0. The selected
arms join the profile rendering loop at `0xe6578`, which emits the
geometry/status fields and returns at `0xe6640`; `0xe6648`–`0xe665c` are
literal fallback dot strings. This dispatch prefix is modeled by
`recovered_status_profile_selector_dispatch_e6500.c`.
The larger frame builder at `0xe6660` constructs the 8-by-13 status grid,
renders the active columns through `0xe6500`, updates the video-state words,
and returns at `0xe6d3c`.

The state-2 entry prefix is modeled by
`recovered_status_service_state2_prefix_e6660.c`: it reduces the signed timer
modulo `0x870`, returns through `0xe6678` for remainders through `0x437`,
handles exact `0x438` with helper `0x1c618`, status values `0xc000`, `0x200`,
and `0x8000`, sets device bit 9, and continues at `0xe6c50`; larger values
enter the `0xe66b4` path.

The first state-2 grid phase at `0xe66b4` is modeled by
`recovered_status_state2_grid_seed_e66b4.c`. It seeds ten 12-byte frame
records, writing `0xffffffff` at offset `0x40` and zero at offset `0x44`,
reads ten source words from `0x1d0000a4` at 16-byte spacing, sums them, clamps
nonpositive totals to 1, and continues at `0xe6708`.

The matching pass at `0xe6708` is modeled by
`recovered_status_state2_grid_match_e6708.c`: it scans eight source rows and
eight 12-byte frame columns, writes matched source values at frame offset
`0x44`, and computes offset `0x48` as `(source * 100) / normalized_sum`.
The row loop re-enters at `0xe6714` and leaves for the renderer setup at
`0xe67f4`; the insertion/compaction copy loop remains a separate unresolved
side effect.

The alternate state-2 branch at `0xe6968` is modeled by
`recovered_status_service_state2_second_half_e6968.c`: only remainder
`0x674` enters it, publishing `0xc000`, `0x200`, and `0x8000` plus device bit
9, rendering rows 4–7 from frame offset `0x30`, and passing frame offsets
`0x70`, `0x7c`, `0x88`, and `0x94` to `0xe6500` with the same four argument
pairs before continuing at `0xe6c50`.

The per-row renderer at `0xe6818` is modeled by
`recovered_status_state2_grid_row_render_e6818.c`: it visits four frame rows
at 12-byte spacing, alternates formatter IDs 8 and 16 with helper arguments
13 and 21 by parity, reads frame offsets `0x40` and `0x48`, and advances text
columns `19,22,25,28`. The shared formatter/lookup/suffix targets are
`0x1cac8`, `0xe3a00`, `0xe3a60`, `0xe665c`, and `0x1d9e0`; the handoff is
`0xe6930`.

The state-2 render handoff at `0xe67f4` is modeled by
`recovered_status_state2_grid_render_handoff_e67f4.c`: four 12-byte frame
rows are rendered through `0x1d880` from text column 19 with stride 3, then
the four frame fields at offsets `0x40`, `0x4c`, `0x58`, and `0x64` are passed
to the profile dispatcher `0xe6500` with argument pairs `(2,13)`, `(31,16)`,
`(2,25)`, and `(31,28)`, before the path reaches `0xe6c50`.

The state-2 shared tail at `0xe6c50` is modeled by
`recovered_status_service_state2_common_tail_e6c50.c`. It uses the same
accepted signed windows, but initializes the 0x200-halfword table at
`0x577fb0`; indices `0x63..0x123` receive
`abs(0x200 - 8 * window_delta)`. Out-of-window values clear the transient
status fields, and the final `0xe6d30` gate calls `0x1c618` only for exact
remainder `0x86f` before returning at `0xe6d3c`.

The short helper at `0xe6d40` copies 0x200 16-bit words from the caller's
source to destination, loads the fixed local continuation `0xe6d78` into
`g2`, and branches through it at `0xe6d74`.

This helper is modeled by `recovered_status_record_word_copy_e6d40.c`: it
copies exactly 0x200 halfwords with 2-byte source and destination strides,
then branches through the fixed local return stub at `0xe6d78`.

The four adjacent emitters at `0xe6d80`, `0xe6ef0`, `0xe7060`, and `0xe71d0`
share a fixed-point conversion pattern: they quantize the phase in
`0x5783d8`, form the paired coordinates, and emit the geometry command words
through `0x884000`. Their returns are at `0xe6ee8`, `0xe7054`, `0xe71c4`,
and `0xe7330` respectively. The small dispatcher at `0xe7340` selects among
these four variants from `0x5783dc` and returns after the selected call.

The phase prefix of variant A at `0xe6d80` is modeled by
`recovered_geometry_status_emit_phase_prefix_e6d80.c`: it clamps
`0x5783d8` to `0..40`, quantizes `(phase << 10) & 0xfc00`, emits the fixed
opcode sequence `29,29,30,18` through `0x884000`, and stores `phase - 1` back
before returning at `0xe6ee8`. The floating-point coordinate conversions are
left to a separate emitter-focused recovery.

The dispatcher at `0xe7340` is modeled by
`recovered_geometry_status_emit_dispatch_e7340.c`: it reads mode word
`0x5783dc`, sends modes 1, 2, and 3 to emitters `0xe6ef0`, `0xe7060`, and
`0xe71d0`, respectively, and defaults all other modes to variant A at
`0xe6d80`.

The object-packet dispatcher at `0xe7390` consumes the active object fields
at `0x5784e0`, selects the status/geometry mode, and emits the coordinate and
scale words through `0x884000`. Its alternate branches at `0xe7560` and
`0xe76d0` remain part of the same frame and choose either direct packet
submission or the queued `0x804000` path. All paths restore the saved context
and return at `0xe79e0`.

The admission prelude at `0xe7390` is modeled by
`recovered_geometry_object_packet_prelude_e7390.c`: it compares the object
byte at `-3` with the caller tag byte, sends mismatches to `0xe7560`, and
routes matching objects with queue flag zero through `0xe7340`; nonzero queue
flags enter the direct packet path at `0xe7420`.

The direct packet prefix at `0xe7420` is modeled by
`recovered_geometry_object_direct_packet_e7420.c`: it emits
`[18, saved_base + computed_offset, coordinate0, coordinate1]` through
`0x884000` and joins the common object-packet tail at `0xe7454`.

The common-tail prefix at `0xe7454` is modeled by
`recovered_geometry_object_packet_tail_e7454.c`: the saved incoming control
flag at `fp+0xc0` being zero emits
`[19, 0x3f800000, 0x3f800000, 0x41200000, computed_offset + 27]` through
`0x884000`, while a nonzero value skips the suffix; both paths converge at
`0xe7490`, where the same control flag selects the response route.

The response split at `0xe7490` is modeled by
`recovered_geometry_object_packet_response_e7490.c`: it emits
`computed_offset + 27` and the `0x802008` control word, writes
`control + 0x34` to `0x801008`, and uses the saved incoming control flag at
`fp+0xc0` to route to fallback assets `0x49317c`, `0x4931ac`, and `0x900514`
at `0xe74cc`; the subsequent `0x884000` readback is separate transport data.
Nonzero control flags
use status `0x101`, control `0x400020`, and the queued `0x804000` block at
`0xe7518`.

The alternate admission at `0xe7560` is modeled by
`recovered_geometry_object_alternate_admission_e7560.c`: after calling
`0xf50c8`, it accepts when object byte `-2` matches the caller tag or the
caller tag is literal `60`, continuing at `0xe758c`; failures route to
`0xe76d0`.

The accepted alternate packet path at `0xe758c` is modeled by
`recovered_geometry_object_alternate_packet_e758c.c`: it emits the same
opcode-18 prefix and queue-flag suffix as the primary path, but selects
fallback assets `0x4934b0`, `0x493534`, and `0x900905` according to the saved
control flag at `fp+0xc0`; the `0x884000` readback is modeled separately. Its
nonzero-control queued descriptor is `0x8fe625`, with returns at `0xe7684`
and `0xe76cc`.

The fallback admission at `0xe76d0` is modeled by
`recovered_geometry_object_fallback_admission_e76d0.c`: after `0xf50c8`, it
accepts object byte `-1` on caller-tag equality or literal caller tag `62`,
then reaches `0xe76fc`; rejected values go to `0xe7850`, which selects the
emitter dispatcher `0xe7340` for queue flag zero or direct packet path
`0xe7874` otherwise.

The fallback direct packet path at `0xe7874` is modeled by
`recovered_geometry_object_fallback_packet_e7874.c`: it emits the opcode-18
prefix and optional suffix, selects fallback assets `0x49353c`, `0x493744`,
and `0x9009b6`, or queued descriptor `0x8fe654`, according to the saved
control flag at `fp+0xc0`; the `0x884000` readback is separate transport data.
It returns through `0xe77f4` or `0xe784c`.

The caller-facing scene service at `0xe79f0` renders the active status scene
from the record bytes at `0x5783c0`/`0x5784e4`, repeatedly invoking the object
packet dispatcher above for the scene's geometry groups. It uses the mode word
at `0x5783c4` and the six-entry arm table at `0xe8920` for the final scene
variant; the complete service returns at `0xe9138`. The next entry at
`0xe9140` begins a separate command/setup path.

Its final indirect branch is modeled by
`recovered_geometry_status_scene_arm_dispatch_e8920.c`: mode word
`0x5783c4` is accepted only for unsigned values `0..5`, selecting
`0xe8938`, `0xe89d4`, `0xe8ae0`, `0xe8c5c`, `0xe8e44`, or `0xe8fe4` from
the table at `0xe8920`. Values above 5 bypass the table and return at
`0xe9138`.

Arm 0 at `0xe8938` is modeled by
`recovered_geometry_status_scene_arm0_e8938.c`. It gates on bit 3 of
`0x5024e8`; the admitted path emits `5,19,0x41400000,0x41400000,1.0`,
loads the object byte at `0x5784e4 + 0x5783c0`, and calls `0xe7390` with
fixed words `0x49c980`, `0xc0c00000`, and `0xc0900000`, followed by
completion opcode `6`. A clear feature bit returns at `0xe89d0`.

Arm 1 at `0xe89d4` is modeled by
`recovered_geometry_status_scene_arm1_e89d4.c`. It always calls `0xe7390`
for the fixed byte at `0x5784e8`, then uses bit 3 of `0x5024e8` to gate a
second call for the scene-count-indexed byte at `0x5784e4 + 0x5783c0`.
Both calls use the `5,19,0x41400000,0x41400000,1.0` packet and finish with
opcode `6`; the second call changes the middle transform word to zero.

Arm 2 at `0xe8ae0` is modeled by
`recovered_geometry_status_scene_arm2_e8ae0.c`. It always renders the bytes
at `0x5784e8` and `0x5784e9`, then gates a third indexed call on bit 3 of
`0x5024e8`. The first two calls use middle transform `0xc0c00000`; the
third uses `0x40c00000`, while all retain `0x49c980` and `0xc0900000` as
the other fixed transform words.

Arm 3 at `0xe8c5c` is modeled by
`recovered_geometry_status_scene_arm3_e8c5c.c`. It always dispatches the
three fixed bytes `0x5784e8`, `0x5784e9`, and `0x5784ea`, then gates a fourth
indexed byte on feature bit 3. Its middle transform words are respectively
`0xc0c00000`, `0`, `0x40c00000`, and `0x41400000`. After completion opcode
`6`, it decrements `0x503a04`; a zero result calls `0xe54a0` and `0xe37b0`
and increments `0x503a00`, before returning at `0xe8e40`.

Arm 4 at `0xe8e44` is modeled by
`recovered_geometry_status_scene_arm4_e8e44.c`. Bit 3 of `0x5024e8` gates
three fixed-object calls for `0x5784e8`, `0x5784e9`, and `0x5784ea`, using
middle transforms `0xc0c00000`, `0`, and `0x40c00000`. Both the clear-bit
branch and the admitted path converge at the arm-3 cleanup tail `0xe8fac`,
which returns at `0xe8fe0`.

Arm 5 at `0xe8fe4` is modeled by
`recovered_geometry_status_scene_arm5_e8fe4.c`. It unconditionally dispatches
the three fixed bytes `0x5784e8`, `0x5784e9`, and `0x5784ea`, using middle
transforms `0xc0c00000`, `0`, and `0x40c00000`, then branches to shared
completion at `0xe8e34`, which emits opcode `6` before the scene service
returns at `0xe9138`.

The fixed entry/prologue is modeled by
`recovered_geometry_status_scene_prologue_e79f0.c`. It publishes the setup
words at `0x800070`, `0x800030`, `0x800090`, `0x8000a0`, and `0x800160`,
prepares the `8,16,18,0,0,0x43000000` FIFO prefix, then enters the object
record loop at `0xe7b14` with initial record index `-5`. Each group reaches
the object packet dispatcher at `0xe7390`; the scene count and record bytes
come from `0x5783c0` and `0x5784e4`.

That separate path is the runtime event dispatcher at `0xe9140`. It updates
the rolling event fields at `0x5783e4–0x578400`, derives pairwise geometry
deltas from the active records, and selects the next event arm using
`0x5783fc % 12` and the table at `0xe91f0`. The arm targets are distributed
through the later `0xea...` region, but converge through the shared finalizer
at `0xea9a0` and return at `0xeaa50`; `0xeaa60` begins the next separate
command/setup entry. This bounds the complete dispatcher at `0xe9140–0xeaa54`.

The modulo-12 selector is modeled by
`recovered_geometry_runtime_event_arm_dispatch_e91d0.c`. It reads the rolling
counter at `0x5783fc`, applies `remi 12`, and selects the exact target from
`0xe91f0`; the assembly's exceptional guard target is `0xea744`.

Event arm 0 at `0xe9470` is modeled by
`recovered_geometry_runtime_event_arm0_e9470.c`. It derives the masked
geometry word from prior phase `0x5783e6` and record word `0x184 + 0x3000`,
emits the six-word `29/30` prefix using `0x43020000`, and captures shared
field updates through `0x5783e4`, `0x5783e6`, `0x5783ec`, `0x5783f4`,
`0x5783f8`, and `0x5783e8`. Its next continuation is `0xea720`.

Event arm 1 at `0xe95a4` is modeled by
`recovered_geometry_runtime_event_arm1_e95a4.c`. It mirrors arm 0 using the
alternate record base: the record word is reduced by `0x3000`, the prior
phase by `0x100`, and `0x41c80000` is published at `0x5783f0`. It emits the
same `29/30` prefix, updates the shared event fields, and continues at
`0xea6fc`.

The second paired-delta family at `0xea1a0` is modeled by
`recovered_geometry_runtime_event_arm4_prefix_ea1a0.c`. It emits opcode
`10` with the word-10 delta and reversed word-8 delta, publishes the FIFO
response at `0x5783e4`, and compares `0x578400` against `44`, selecting
`0xea1f8` or the extended path at `0xea2b8`.

The opening of event arm 2 at `0xe96b8` is modeled by
`recovered_geometry_runtime_event_arm2_prefix_e96b8.c`. It loads word-8 and
word-10 pairs from the `0x5040d0` and `0x503ad0` record bases, emits opcode
`10` with the pair deltas followed by opcode `31` with the paired word-8
values, increments phase `0x5783e6`, and continues at `0xe974c`. Its later
feedback/division loop remains separate.

The opening of event arm 3 at `0xe9da8` is modeled by
`recovered_geometry_runtime_event_arm3_prefix_e9da8.c`. It emits opcode
`10` with paired word-10/word-8 deltas, stores the FIFO response at
`0x5783e4`, and compares `0x578400` with threshold `44`, selecting
`0xe9e00` or the extended path at `0xe9ec0`.

The shared event finalizer at `0xea0b0` is modeled by
`recovered_geometry_runtime_event_common_finalize_ea0b0.c`. It emits opcode
`10` with record-word deltas, then opcode `31` with the current `0x5783f4`
and record word-8/word-10 values plus two zero words, publishes the first
FIFO response to `0x5783e4`, and continues at `0xea6fc`.

The short path at `0xe9e00` is modeled by
`recovered_geometry_runtime_event_arm3_short_e9e00.c`. It scales the event
count by `2^14/45`, applies the indexed displacement `0xffff8000`, masks the
lookup word to 16 bits, emits `29/30` with `0x43020000`, and consumes a
second FIFO response before continuing at `0xe9e50`.

The shared preparation tail at `0xea6fc` is modeled by
`recovered_geometry_runtime_event_prepare_ea6fc.c`. It stores the derived
value at `0x5783e8`, emits `20,0x5783e8,21,-0x5783e4` through the geometry
FIFO, and branches to the common finalizer at `0xea9a0`. Arm 0 reaches the
equivalent setup sequence at `0xea720`.

The terminal event finalizer at `0xea9a0` is modeled by
`recovered_geometry_runtime_event_finalize_ea9a0.c`. It snapshots the state
words into `0x504b98`, `0x504b9c`, `0x504ba0`, and the low-halfword fields
`0x504ba8/0x504baa`, emits opcode `18` with the bit-31-toggled state words,
derives `0x504d28` and `0x5770f4`, and returns at `0xeaa50`.

The helper at `0xeaa60` is called by both status-preparation paths. It emits
the event setup packet, derives the shared fields at `0x5783e4–0x5783f8`,
resets the event counters when required, and returns at `0xead1c`.
`0xead20` begins its literal geometry-event lookup data.

The setup-helper prefix at `0xeaa60` is modeled by
`recovered_geometry_event_setup_prefix_eaa60.c`. It calls `0x295d0`, emits
setup words `8/16`, calls `0x2a990` with `0xd000`, then emits opcode `10`
with deltas from the `0x503ad8` and `0x5040d8` workspace pairs before the
FIFO response at `0xeaaf0`.

The response-dependent opcode-31 stage at `0xeaaf0` is modeled by
`recovered_geometry_event_setup_packet_eaaf0.c`. It emits
`31,0x503ad8,0x5040d8,0,0,0x503ae0,0x5040e0` and continues at `0xeab48`;
the subsequent fixed-point state derivation remains separate.

The paired runtime arms at `0xea598` and `0xea610` now have a shared prefix
model in `recovered_geometry_runtime_event_arms6_7_prefix_ea598.c`. Arm 6
adds `0x6000` to record word `0x184`; arm 7 adds `0xffffa000`. Both mask the
result to 16 bits, emit `[29, masked, 0x430c0000, 30, masked, 0x430c0000]`,
consume the two FIFO responses, load record words `8/0x10/0xc`, and converge
at `0xea684`, where the shared state derivation begins.

The first setup-helper state stage at `0xeab48` is modeled by
`recovered_geometry_event_setup_state_prefix_eab48.c`. It adds `0x4000` to
the phase word, masks that value for the two visible opcode-29/30 packets,
and publishes the state fields at `0x5783e4–0x5783f4`; preserved `g14` feeds
the `0x5783e6` and `0x5783e8` lanes. The i960 extended-real
conversion/division results are retained as explicit inputs; the exact
instruction semantics remain unresolved. The modeled boundary is `0xeac1c`,
where the next opcode-10 stage begins.

The following handoff at `0xeac1c` is modeled by
`recovered_geometry_event_setup_handoff_eac1c.c`. It replays opcode `30`,
publishes preserved `g14` to both `0x578400` and `0x5783fc`, consumes the
FIFO response, and emits opcode `10` with the extended-real word and
`0x430c0000` before continuing at `0xeac84`.

The terminal setup-helper packet tail at `0xeac84` is modeled by
`recovered_geometry_event_setup_finalize_eac84.c`. It emits opcode `20` with
the low halfword of the opcode-10 response, opcode `21` with
`-0x5783e4`, and opcode `18` with bit-31-toggled state words. It publishes
the computed division result (`g6`) at `0x5783f8` and reuses that same value
for the final toggled word before reaching the helper return at `0xead1c`.

The following compact helpers are now separated by their visible return
stubs. The gates at `0xeada0`, `0xeade0`, and `0xeae20` are modeled by
`recovered_runtime_flag_gates_eada0.c`: they test `(0x5023f0 bit 3, then
0x5024b4 bit 1)`, `(0x5023f0 bit 2, then 0x5024b4 bit 0)`, and
`(0x502480 bit 2, then 0x5024b8 bit 0)` respectively, returning boolean
results through caller continuations. The model
`recovered_runtime_byte_expand_eae60.c` captures `0xeae60`: it copies
`g2 >> 1` source bytes and writes a zero byte after each copied byte before
returning through the caller continuation. The host wrapper reports a
capacity failure without writing when the supplied destination is too small.
The wrappers at `0xeaeb0`, `0xeaed0`, and `0xeaf20` are modeled by
`recovered_runtime_format_wrappers_eaeb0.c`: they all forward `g2` through
numeric helper `0x1cac8`; the first calls renderer `0xf5100`, the adjusted
wrapper selects argument `32` for board byte `1` or `2` and `42` otherwise
through helper `0x1cc40` before calling `0xf5100`, and the final wrapper calls
alternate renderer `0x1da90`.

The literal block at `0xeaf40–0xeb054` contains the diagnostic menu labels
(`TEST MENU`, memory/input/output/sound tests, assignment and backup prompts).
The renderer at `0xeb060` is modeled by
`recovered_diagnostic_menu_render_eb060.c`: it lays fourteen strings into the
fixed tile coordinates, using the alternate wrapper for the first entry and
the ordinary numeric wrapper for the others. It then updates the selected-menu
marker from `0x5784fc`, returning through `0xeb19c` for a nonzero selection or
`0xeb1b4` for zero.

The runtime-table helpers following it are now bounded individually. The
scanner at `0xeb1c0` is modeled by
`recovered_runtime_packed_record_scan_eb1c0.c`: it fills `g0 >> 1` halfwords
at `0x5785a4`, scans `g0 >> 2` two-halfword records after that region, and
publishes the low/high-byte matches at `0x578548`, `0x57854c`, and `0x578550`.
The initializer at `0xeb2c0` is modeled by
`recovered_runtime_record_table_init_eb2c0.c`: it sets workspace base
`0x200000`, packed byte count `0x220000`, runs the scanner for `0xffff`, the
all 16 powers of two from `1` through `0x8000`, and the caller-supplied target,
then normalizes zero match slots at `0x578548/0x57854c/0x578550/0x578554` to
`1` and increments the status counter. `0xeb2c0` initializes and rebuilds that workspace;
The selector at `0xeb3b0` is modeled by
`recovered_runtime_record_base_select_eb3b0.c`: all-primary markers equal to
`1` select `0x200000`, otherwise all four alternate markers equal to `1`
select `0x1080000`, and all other cases select fallback `0x5e0000`. The
chosen base is published at `0x501cc4` before the caller continuation; and
the alternate scanner at `0xeb450` is modeled by
`recovered_runtime_alternate_record_scan_eb450.c`: it fills `g0 >> 1`
halfwords at `0x501cc0`, scans `g0 >> 2` two-halfword records, compares full
16-bit values, and records post-increment pointers for mismatches at
`0x578558` and `0x57855c`. The reset/copy helper at
`0xeb510` is modeled by `recovered_runtime_record_table_reset_copy_eb510.c`:
it resets the packed byte count to `0x20000`, reruns the alternate scanner at
`0xeb458` for `0xffff`, powers of two `1..0x8000`, and the caller target, then
copies `0x10000` halfwords from the selected source published at `0x501cc4`
into `0x501cc0`, returning at `0xeb5a8`.

The ROM-bank loader family at `0xeb5b0–0xeb824` is modeled by
`recovered_runtime_rom_bank_loaders_eb5b0.c`. The eight entries select banks
`0x5e0000`, `0x5c0000`, `0x5a0000`, `0x580000`, `0x560000`, `0x540000`,
`0x520000`, and `0x502000` respectively. The first seven copy `0x10000`
halfwords; the final loader copies `0xf000` halfwords. Each publishes the
source at `0x501cc0`, uses destination `0x501cc4`, and invokes the reset/copy
helper at `0xeb510`. The orchestrator at
`0xeb830` is modeled by `recovered_runtime_rom_bank_load_all_eb830.c`: it
enters the selector continuation at `0xeb3b8`, runs all eight loaders in
order, normalizes zero mismatch slots `0x578558/0x57855c` to `1`, increments
`0x578510`, and returns at `0xeb898`. The
scanner at `0xeb8a0` is modeled by
`recovered_runtime_packed_record_match_scan_eb8a0.c`: it seeds `g0 >> 2`
dwords at `0x5785b0`, scans the following `g0 >> 2` dwords with four byte
masks, and records matching pointers at `0x578560–0x57856c`.
The repeated scanner at `0xeb9a4` is modeled separately by
`recovered_runtime_packed_record_match_scan_b_eb9a4.c`: it uses the same four
byte masks and output slots but seeds/scans from workspace base `0x910004`,
returning at `0xebaa4`.

The following initializer at `0xebab0` is modeled by
`recovered_runtime_alt_record_table_init_ebab0.c`. It selects workspace base
`0x900004`, packed count `0xfffc`, and invokes `0xeb8a0` for
`0xffffffff`, all 16 shifted `0x01010101` targets through `0x80808080`, and
the caller target. It normalizes zero match slots at `0x578560–0x57856c`,
increments `0x578510`, and returns at `0xebb98`.

The parallel packed-record family begins at `0xebba0` and repeats the
scan/init pattern for additional ROM layouts.
The scanner at `0xebba0` is modeled by
`recovered_runtime_alt_packed_record_scan_ebba0.c`: it fills
`packed_byte_count >> 1` halfwords at `0x5785a4`, scans the following
single-halfword records, compares the low and high bytes independently with
`0xff` and `0xff00`, and publishes the last matching record addresses at
`0x578570` and `0x578574` before returning at `0xebc5c`.
Its initializer at `0xebc60` is modeled by
`recovered_runtime_alt_record_table_init_ebc60.c`: it selects workspace base
`0x1000000`, packed count `0x10000`, and invokes the scanner for `0xffff`,
all 16 power-of-two targets from `1` through `0x8000`, and the caller target.
It normalizes zero slots at `0x578570`/`0x578574`, increments `0x578510`,
and returns at `0xebd14`.
The paired scanner at `0xebd20` is modeled by
`recovered_runtime_alt_packed_record_scan_b_ebd20.c`: it scans
`packed_byte_count >> 2` two-halfword records after the same initialized
region, independently compares low/high bytes, and publishes matches for the
first halfword at `0x578578`/`0x57857c` and the second at
`0x578580`/`0x578584`.
Its initializer at `0xebe20` is modeled by
`recovered_runtime_alt_record_table_init_ebe20.c`: it selects workspace base
`0x1080000`, packed count `0x80000`, and repeats the 18-target rebuild,
normalizes all four marker slots, increments `0x578510`, and returns at
`0xebf04`.
The next scanner/initializer pair at `0xebf10`/`0xebfd0` is modeled by
`recovered_runtime_alt_packed_record_scan_c_ebf10.c` and
`recovered_runtime_alt_record_table_init_ebfd0.c`. This format scans
`packed_byte_count >> 1` halfwords, publishes low/high-byte matches at
`0x578588`/`0x57858c`, and uses workspace base `0x1800000` with packed count
`0x4000`; its initializer performs the same 18-target rebuild and returns at
`0xec084`.
The strided scanner/initializer pair at `0xec090`/`0xec140` is modeled by
`recovered_runtime_alt_packed_record_scan_d_ec090.c` and
`recovered_runtime_alt_record_table_init_ec140.c`. The scanner initializes
`packed_byte_count >> 1` halfwords, then examines 32 groups of 128 halfwords
with `0x200`-byte group strides, matching the low seven bits of the target
byte and publishing at `0x578590`; the initializer selects base `0x1810000`,
packed count `0x4000`, performs the 18-target rebuild, and returns at
`0xec1dc`.
The following pair at `0xec1e0`/`0xec290` repeats this strided format with
match slot `0x578594`. It is modeled by
`recovered_runtime_alt_packed_record_scan_e_ec1e0.c` and
`recovered_runtime_alt_record_table_init_ec290.c`; the initializer selects
workspace base `0x1814000`, retains packed count `0x4000`, performs the
18-target rebuild, and returns at `0xec32c`.
The bounded entries through `0xec1e0` use the alternate workspace slots at
`0x578570`, `0x578574`, `0x578578`, `0x57857c`, `0x578580`, `0x578584`,
`0x578588`, and `0x578590`; each initializer selects a different packed-ROM
base before invoking its scanner. This establishes a second data-family
pipeline without conflating its record widths with the first family.
The selector at `0xec480` is modeled by
`recovered_runtime_alt_record_base_select_ec480.c`. It maps the marker groups
to bases `0x200000`, `0x1000000`, `0x1080000`, `0x1800000`, `0x1810000`,
`0x1814000`, and `0x1818000`; when no group is complete it increments
`0x578510`, then joins the common continuation at `0xec5b8` and indirect
return at `0xec61c`.
The `0xec330`/`0xec3e0` pair extends the strided format to match slot
`0x578598`; its scanner and initializer are modeled by
`recovered_runtime_alt_packed_record_scan_f_ec330.c` and
`recovered_runtime_alt_record_table_init_ec3e0.c`, using workspace base
`0x1818000`, packed count `0x4000`, and the same 18-target rebuild.

The continuation through `0xec8e4` extends that alternate pipeline: the
initializers/scanners at `0xec290`, `0xec330`, `0xec3e0`, `0xec6a0`, and
`0xec760` cover additional packed layouts; `0xec480` selects the matching
ROM base; and `0xec630` copies the selected table. The copy routine is
modeled by `recovered_runtime_alt_record_table_copy_ec630.c`: it transfers
`0x2000` halfwords from the pointer at `0x5785ac` to `0x1d00000`, increments
`0x578510`, and returns through the indirect continuation at `0xec698`. The
final scanner/initializer pair at `0xec6a0`/`0xec760` is modeled by
`recovered_runtime_alt_packed_record_scan_g_ec6a0.c` and
`recovered_runtime_alt_record_table_init_ec760.c`; it scans paired halfwords,
publishes matches at `0x57859c`/`0x5785a0`, and rebuilds the table from
workspace base `0x1d00000` with packed count `0x4000`. The
builder at `0xec820`
expands the three 16-bit literals at `0xead20` into a 3x32x8 halfword table
at `0x1800010`, after seeding eight `0x88888888` words at `0x1080000`;
`0xec8f0` orchestrates the pipeline before returning at `0xec91c`. This
layout is modeled by
`recovered_geometry_event_lookup_table_build_ec820.c`; the table's
application-level command meanings remain unresolved.
The dispatcher at `0xec8f0` is modeled by
`recovered_runtime_alt_record_pipeline_dispatch_ec8f0.c`; it records the
four preparation calls (`0x29a80`, `0x1c220`, `0x1bda0`, `0x28840`), clears the
zero argument before the final preparation stage, invokes `0xec820`, and
advances `0x578510` before returning.

The following event helpers are bounded individually. `0xec920` advances the
service counter, `0xec940` sets the event-mode flag, and `0xec970`/`0xec9d0`
accumulate packed-record bytes using their distinct stride patterns. The six
publishers from `0xeca30` through `0xecb20` store the derived event results in
the separate `0x578530–0x578544` workspace fields. The literal handler table
at `0xecb50` follows these wrappers.
The handler table is modeled by `recovered_runtime_event_handler_table_ecb50.c`:
it contains 25 entries at `0xecb50`, covering the six publishers, recovered
record-family initializers/scanners, pipeline dispatch, selector/copy helpers,
and the repeated `0xec940` flag setter entries, followed by a zero word at
`0xecbb4`.
The first two helpers are modeled by
`recovered_runtime_event_counter_step_ec920.c` and
`recovered_runtime_event_mode_flag_set_ec940.c`: `0xec920` calls `0x28418`
and increments `0x578510`, while `0xec940` writes `1` to `0x578514` and
returns through `0xec960`.
The six checksum publishers from `0xeca30` through `0xecb48` are modeled by
`recovered_runtime_event_result_publish_wrappers_eca30.c`. They bind the
checksum variants and source spans to workspace outputs `0x578530` through
`0x578544`, and each advances `0x578510` after the checksum continuation.
The checksum helpers are modeled by
`recovered_runtime_record_checksums_ec970.c`: `0xec970` sums byte offsets
`0`/`1` in each four-byte chunk, while `0xec9d0` sums offsets `2`/`3`; both
return the low 16 bits through their recorded continuations.

The table is followed by diagnostic formatting support: `0xecbb8–0xecd78`
holds the result format, GOOD/BAD text, and IC-number labels; `0xecbe0` and
`0xecc40` are the basic and expected-value comparison formatters. The result
menu renderer at `0xecd80` lays out the IC results and accumulated status
values, returning at `0xed0c4`.
The two formatter contracts are modeled by
`recovered_diagnostic_result_format_ecbe0.c`: both use helper `0x1cac8`,
renderer `0xf5100`, and format string `0xecbb8`; the basic formatter maps
status `1`/`0`/other to GOOD/blank/BAD, while the comparison formatter maps
`-1` to blank, equality with the expected value to GOOD, and mismatch to BAD.

The workspace reset at `0xed0d0` clears the primary and alternate
match/result slots before returning through its continuation at `0xed1cc`.
It is modeled by `recovered_runtime_record_workspace_reset_ed0d0.c`: the six
result slots `0x578530–0x578544` receive `0xffffffff`, while the 23 marker
slots from `0x578548` through `0x5785a0` receive zero before the indirect
return through `0xed1d0`.
The following `0xed1e0–0xed218` block is literal test-button and wait-prompt
text. The service at `0xed220` initializes the diagnostic result state,
renders through `0xecd80`, then dispatches the next handler via `0xecb50` and
returns at `0xed2e0`; its fallback path begins at `0xed2e4` and returns at
`0xed300`.
The service contract is modeled by `recovered_diagnostic_service_ed220.c`:
it resets the workspace, clears the service counter and event-mode flag,
renders the prompt (`0xed1e0` or `0xed200`) and menu (`0xecd80`), then indexes
the 25-entry handler table at `0xecb50`; active event mode instead calls
`0xeade8` and uses the fallback return at `0xed300`.

The input-test service at `0xed320` handles the input-state transition and
returns at `0xed438`. Its literal status rows at `0xed440–0xed5b4` cover
direction, shot, dash, start, coin-chute, service, and test-button states.
The state-machine portion is modeled by
`recovered_diagnostic_input_test_service_ed320.c`: it handles state-1/2/3+
transitions (with state 0 taking the direct wrapper path), combines the two
hardware words for state 2, selects GOOD/BAD format strings, and records the final wrapper/fallback calls through
`0xeaeb0` and `0xeade8`.
The renderer at `0xed5c0` lays those rows into the tile plane, checks the
input/status flags, and returns at `0xed968`.
Its fixed layout is modeled by `recovered_diagnostic_input_test_render_ed5c0.c`:
the renderer emits 12 base rows, then conditionally emits 12 rows from the
listed `0x50249c` flag bits, using the shared wrapper at `0xeaeb0` and the
diagnostic renderer at `0xf5100`.

The next diagnostic block, `0xed970–0xeda28`, contains the Versus City
billboard and winner-lamp/7-segment/start-lamp labels. The renderer at
`0xeda30` advances its test state, emits the corresponding lamp and segment
patterns through the shared test-pattern helper, and returns at `0xedcf8`.
The fixed billboard contracts are modeled by
`recovered_diagnostic_billboard_test_render_eda30.c`: it records the six
pattern values sent to `0x184e8`, state/hardware/modulo workspace addresses,
the winner and lamp label coordinates, and the final `0xeaeb0`/`0xeade8`
handoff; the lamp bit semantics remain unresolved.
The following data is diagnostic naming metadata: indexed `SDE_*` event-name
records begin at `0xedd20`, while the `SDB_*` record family begins at
`0xeff60`. Their indexed prefix and terminated ASCII names should be treated
as lookup data rather than i960 instructions.

The CRT/test-pattern service at `0xf04d0` initializes the diagnostic state,
renders the CRT labels, and cycles indexed pattern data through its six-entry
arm table at `0xf0674`; its arm returns finish at `0xf0884`. The separate
buffer filler at `0xf08c0` writes the indexed bit-plane layout and returns at
`0xf0938`.
The filler geometry is modeled by
`recovered_diagnostic_crt_pattern_buffer_fill_f08c0.c`: it writes four planes
of six rows and 32 halfwords per row, with the recovered destination and
pattern-value formulas derived from the nested i960 loops.
The fixed CRT service contract is modeled by
`recovered_diagnostic_crt_test_service_f04d0.c`: it records the initial state
writes, header placement, shared label/pattern helpers, and all six handler
addresses at `0xf0674`.

The match/time diagnostic at `0xf0980` renders play-time, match/death-match,
pending/start-state, and network-link fields, builds the associated test
structures, and returns at `0xf0b38`. Its common header uses `(23,1)` and
`0xf0940`; the zero-mode path prompts with `0xf0960` and sends builders the
sources `0x2bde7ac` and `0x2be27ec`, while the nonzero path prompts with
`0xed1e0` and sends the recovered five-source sequence
`0x2bde82c, 0x2be286c, 0x2be28ac, 0x2be28ec, 0x2be292c`. All builder calls use
the recovered `0x80` flag. The builder's exact memory effects and
register-derived loop bounds remain unresolved.

The coin/credit diagnostic entry at `0xf1c90` initializes `0x578500` to
`0xffffffff` when needed, advances `0x578518` modulo 20 after `0xeada8`
succeeds, writes pattern value 30 with an `0x80` stride at `0x100451c`, and
dispatches through the 20-entry function/selector table at `0xf1be0` before
returning at `0xf1d40`. Its formatter helper at `0xf1db0` computes
and prints credit arithmetic through `0xf1ebc`. The formatter has a bounded
five-column model that records each product, optional `r8` adjustment,
quotient/remainder, prior-quotient comparison, and special/general/blank string
choice; the shared `0x1cac8` formatter and `0xf5100` renderer remain external.
The coin-chute status renderer
at `0xf1f20` reads the live status word at `0x1d0002a` and returns at
`0xf20a4`. Its bounded model captures the zero early return, type-27 free-play
layout, normal two-call handoff to `0xf1db0`, and packed lookup indices derived
from the status word through table base `0xead30` (offsets `0,2,3` on the first
call and `0,1,3` on the second).

The bookkeeping service at `0xf2e20` maintains three diagnostic state fields,
selects primary versus alternate flow from `0x578524`, advances the selected
counter modulo 5 after `0xeada8` succeeds, masks the index with `7`, and calls
the active accounting sub-handler from `0xf2de0` or `0xf2e00` before returning
at `0xf2ee4`. The nearby
The modeled input arms `0xf2c20` and `0xf2c90` advance decoded input bytes
modulo 10 with their recovered zero/one replacement rules and call `0xf2770`.
The `0xf2d00`/`0xf2d70` arms apply the same modulo-10/zero-to-one update to
`0x1d00030`/`0x1d00032` with their adjacent pattern buffers.
format strings identify this family as bookkeeping, coin-chute, credit, and
game-time reporting.
The game-time statistics entry at `0xf33a0` initializes `0x578500` to `1`
when needed, branches on `0x57850c` to the alternate path at `0xf3668`, and
in its primary path renders header `0xf2ef0` at `(18,6)` plus fixed rows
sourced from `0x1d00040`, `0x1d00044`, `0x1d00048`, `0x1d0003c`, `0x1d0004c`,
and `0x1d00054`, returning at `0xf3a3c`.

The paired tables dispatch nine bounded arms: record validation at `0xf2940`,
which scans 25 records from `0xead30 + 4` in field order `0/3/2/1`,
publishes a 1-based selector on match, and clears `0x578500` on exhaustion,
including the modeled `0xf2a60` and `0xf2ae0` arms, which advance the coin and
credit-start fields modulo 5 and clamp the opposing field when necessary;
`0xf2b60` advances manual setting modulo 28 and reconnects to `0xf19e8`,
credit/coin updates at `0xf2a60–0xf2bc0` (including the modeled reset arm’s
type-27-to-1 selector reset and `0xf19e8` handoff), input-byte updates at `0xf2c20` and
`0xf2c90`, and coin-chute counter updates at `0xf2d00` and `0xf2d70`. Each arm
returns before the next table/data boundary, making these indirect paths
available for per-state tracing.

Two shared renderers feed those arms: `0xf2170` formats coin-chute type and
credit/manual settings through its return at `0xf22e0`, while `0xf2770`
formats the live coin/input matrix and multipliers through its return at
`0xf2930`. The matrix renderer’s bounded model captures the title `(18,6)`,
zero/nonzero strings for `0x1d00035` and `0x1d00036`, and its two linked
`0xf23e0` builder calls rooted at x positions `17` and `27` using decoded
fields `0x1d00030` and `0x1d00032`. The settings model captures the title
`(18,6)`, the zero/nonzero
string branches for `0x1d0002c` and `0x1d0002e`, and the manual-setting branch
on `0x1d0002a` that connects normal status rendering to `0xf1f20`.

The shared coin-configuration decoder at `0xf19e8` derives a packed index from
`0x1d0002a`, reads offsets `0/2/1/3` from `0xead30`, writes the resulting
fields to `0x1d00035/30/32/36`, normalizes `0x1d00034` to whether the final
byte equals `1`, sets `0x5785b4`, and returns through `0xf1aa8`. The arithmetic helper at `0xf23e0` then builds a
nine-entry coin/credit matrix using those bytes, returning at `0xf264c`.

The adjacent site/status probe at `0xf1ac0` gates on `0xeade8` and validates
the two hardware status windows at `0x502408` and `0x502448` through `0xf5c58`;
windows, stores the resulting site byte at `0x1d00028`, and returns at
`0xf1bb8`; failed validation publishes status `2`, and its fallback arm at
`0xf1bc0` calls `0xeade8` again, sets `0x5784f8` to `2` and clears
`0x578500` when that probe succeeds, then returns at `0xf1bdc`. The paired
target/index records at `0xf1be0` feed the coin diagnostic’s indexed display
dispatch.

That table’s remaining 18 arms are now bounded individually: five
configuration toggles cover `0x1d00016–0x1a`, and the subsequent arms update
the diagnostic fields at `0x1d0001b–0x1f`, `0x1d00020–0x24`, `0x1d00026–0x28`,
and `0x1d00027`. Their short returns make each selector/index pair directly
traceable in Ghidra.

The statistics renderer at `0xf33a0` reads the `0x1d00040–0x1d000a0`
accounting fields and formats game-time/bookkeeping results, returning at
`0xf3a64`. The EEPROM confirmation service at `0xf3ab0` is gated by mode `1`
and clear result state, displays the clear/cancel choices, swaps pending
pattern buffers, handles completion through `0x2350`, and toggles `0x578508`
after the final `0xeada8` probe, returning at `0xf3c0c`. The compact
test-mode exit/reset handler at `0xf3c50` clears the test video/input state and
returns at `0xf3c9c`. The adjacent exit/reset handler at `0xf3c50` also
initializes `0x578500` when needed, writes marker `0x52` to `0x5032f4`, clears
`0x5770b0` and `0x503a00`, and increments `0x5039f4`.

`0x6fec0` initializes a geometry-device command path: it validates the
selector, programs `0x800030`, and emits the associated fixed packet through
the `0x804000` command window.

`0x27d8` is a small indirect-return trampoline used by the nearby byte-copy
loops; it restores the local continuation at `0x27e4` and branches through it.

`0x73508` classifies the low halfword of a signed difference into ten bounded
ranges (`0–9`), which callers use to select match-profile and status-table
entries.

`0x17c8` selects a startup device mode: it updates the mode mask at
`0x501cd0`, mirrors it to `0xe80004`, and writes the mode-specific setup value
to the `0xf00000` register window.

`0x3120` is the buffer checksum helper used by the ROM-signature paths. It
folds input bytes through the lookup table at `0x2f20` and returns the final
16-bit checksum value.

`0x1348` enables the startup device-mode bit: it sets bit 10 in `0x501cd0`
and mirrors the updated mask to `0xe80004`.

`0x1380` performs the larger startup device-mode transition: it preserves the
floating-point/register context, updates the mode mask, and routes selector
values through the corresponding hardware setup branches.

`0x1bb8` performs the startup hardware reset/configuration sequence: it clears
`0xe80000`, initializes the four `0xf00000` register slots, installs mode mask
`0x23d`, and clears the startup state at `0x51aac0`.

`0xe3a10` is a thin status-render wrapper around `0xe3830`, formatting a
numeric value as a two-digit decimal glyph sequence for the score/result UI.

`0x79d60` is the parallel randomized record-state dispatcher. It uses the
same `0x64`/`0x74` record fields and PRNG, but selects handlers for the adjacent
runtime record family.

`0x6f6f0` is a related geometry float-transform helper. It converts paired
coordinates, emits the corresponding geometry command words through
`0x884000`, and supplies the transformed value stored in object field `0x154`.

The callable record services in the same cluster are now bounded separately.
`0x6fb90–0x6fd4c` allocates and initializes a 0x54-byte geometry record from a
template at `0x51c854`, clears its transient fields, installs association
indices or sentinel `999`, and advances the allocation head. `0x6fd50–0x6fe6c`
releases the two association links, redirecting to side tables when the
record is already shared, then decrements the corresponding reference count.
`0x6fec0–0x6ff1c` is the short device-command initializer called throughout
the recovered object/update code: it rejects selectors outside its accepted
range, while valid selectors program `0x800030` and the `0x804000` command
window.

The following callback builder at `0x6ff20–0x6fff4` is also now bounded as a
function (exclusive end `0x70000`). It emits the fixed command preamble and
the caller-supplied vector words through `0x804000`, then branches through
the continuation saved in `g7`; the `0x6fff8` `ret` is its normal stub.
The next aligned entry, `0x70000–0x700d4`, is a sibling callback builder with
the same command-window protocol but a different coordinate arrangement. The
short fixed-constant writer at `0x700e0–0x70194` is separately bounded as a
third variant; its following aligned code at `0x701a0` is therefore not
accidentally absorbed into the packet writer.
The heavily reused routine at `0x701a0–0x70968` is now bounded as
`geometry_clip_packet_builder`: it compares the signed coordinate pairs to
choose among four ordering arms, emits the matching packet, and converges on
the internal tail at `0x70950` before returning. This target is called from
both startup geometry setup and the active object/update paths.
The separate late-path target at `0x70970–0x70c70` is now bounded as
`geometry_extended_packet_builder`; it emits the longer multi-command packet
sequence used by the object setup callers and returns at `0x70c70`.
The following table-style entries are bounded independently as well:
`0x70c80–0x70fb8` emits the longer frame-initializing packet variant, and
`0x70fc0–0x7107c` emits the compact fixed-constant variant. Their separate
return sites leave the prologue at `0x71080` available as the next routine
boundary.
The prologue-backed routine at `0x71080–0x72044` is now bounded as
`geometry_object_match_update`. Its direct callers pass object records; the
routine validates match state, derives transformed frame values, emits the
associated geometry packets, stores generated response fields back into the
record, and updates shared timing counters before its epilogue.

The motion/update family continues through `0x2f360–0x30220`.  The aligned
entries at `0x2f360`, `0x2f460`, `0x2f580`, `0x2f930`, `0x2fb20`, `0x2fe30`,
`0x2ff80`, and `0x300c0` are phase-specific object state/callback handlers.
`0x2fa20–0x2fb10` and `0x2fd50–0x2fe28` are continuation trampolines: they
save the shared geometry result, clear the transient callback state, and
return through a caller-supplied address rather than ending with `ret`.
The same structure continues at `0x30230`, `0x30c20`, and `0x30d40`; the
phase-reset helpers at `0x303e0`/`0x30420` and motion handlers through
`0x30e40` form the next profile-selection cluster.
The following entries through `0x31910` continue the same generated family:
`0x30ff0`, `0x31210`, and `0x313e0` select indexed profiles, while
`0x315a0`, `0x316d0`, `0x317f0`, and `0x31910` emit geometry packets and
advance the object/frame phase state through their callback tables.
The dispatch data immediately following this code confirms the next six
entries: `0x31ab0`, `0x31d20`, `0x32120`, `0x32330`, `0x324e0`, and `0x32540`.
They cover the remaining profile/timing transitions and two small phase
callback helpers, ending at the object-motion table beginning at `0x32560`.

`0x32810` is the next large object-state machine.  Its prologue saves the
caller frame, the internal table at `0x32968` selects fourteen state arms from
field `0x1b2`, and the machine restores the frame across several return arms
through `0x3645c`.  The state arms combine fixed-point motion, geometry FIFO
packets, profile projection, and scene/object callback updates.

The table at `0x37130` confirms the following fourteen sibling entries:
`0x36460`, `0x36690`, `0x367f0`, `0x36980`, `0x36af0`, `0x36bb0`, `0x36c40`,
`0x36cc0`, `0x36d50`, `0x36de0`, `0x36e70`, `0x36ef0`, `0x36f90`, and
`0x37060`.  They cover profile-state initialization, object coordinate
transforms, and profile transition predicates, with continuation returns at
the end of each table slot.

The next executable boundary is `0x371e0`.  This routine reads the active
object pointer from `0x6c`, performs the per-frame decrement of the `0x1db` and
`0x1dc` timers, advances the fixed-point fields at offsets `0x32` and `0x34`,
and selects phase/state transitions through the table at `0x37130`.  Its last
return is at `0x37f30`; the words at `0x37f40` are data, so `0x37f50` is a
separate entry rather than a continuation of the same bounded function.

`0x37f50` is a motion-output continuation.  It clears transient fields at
`0x186`/`0x188`, clamps the signed fixed-point delta applied to object field
`0x2e`, advances or reverses phase field `0x194`, and publishes a geometry
resource pointer/value through `0x51acfc`/`0x51ad00`.  Its branches return via
the caller-supplied address in `g2` at `0x380c8`, `0x381b4`, `0x38218`,
`0x3826c`, and `0x382dc`, followed by the routine boundary at `0x382e0`.

The table at `0x382f0` is a resource-profile table indexed by object field
`0x188`; its first four executable consumers are bounded at `0x38340`,
`0x38490`, `0x385f0`, and `0x386c0`.  These siblings load profile-dependent
timing values, advance phase fields `0x17a`/`0x17e`, and publish the selected
resource and fixed-point result through `0x51acfc`/`0x51ad00`.  Their exact
returns are `0x38484`, `0x385e0`, `0x386b4`, and `0x388e4`, after which the
next distinct entry begins at `0x388f0`.

`0x388f0` is the fifth sibling: it advances the primary resource phase and
uses the same profile timing envelope before clearing the transient result at
return `0x389e0`.  `0x389f0` begins a sixth sibling, which updates the
secondary fixed-point coordinate at field `0x36`, clamps the per-frame delta
against the observed `0x40`/`0x3f` bounds, and advances phase field `0x178`.
Its terminal returns are at `0x38b00`, `0x38b24`, and `0x38b2c`; the next
distinct geometry packet path begins at `0x38b30`.

`0x38b30` is a separate paired-packet updater.  When the service mode at
`0x51acac` permits it, the routine emits two related records through `0x884000`,
derives a fixed-point difference from the object and its paired record, clamps
the motion delta, and updates object fields `0x36` and `0x38`.  Its terminal
returns converge at `0x38d30` or `0x38da0`; the next entry begins at `0x38db0`.

`0x38db0` walks the service counters at `0x51acc0`/`0x51acd0`, handling the
three counter states, dispatching payloads through the geometry producers at
`0xbbcf0`/`0xbb640`, and advancing the associated table cursor.  The loop
returns at `0x38ee0`.  A larger packet-builder routine begins at `0x38ef0` and
is left as the next boundary to sieve.

`0x38ef0` is the larger profile packet builder.  It indexes records rooted at
`0x51ab60`, emits multiple coordinate tuples through `0x884000`, derives the
relative position from object fields `0x84`/`0x184`, and clamps both resulting
axes before updating the selected record.  Its loop returns at `0x392ac`.

`0x392b0` begins a separate displacement classifier.  It compares the object
offset against fixed-point thresholds, writes the resulting class to field
`0x17c`, selects a profile record through the same `0x51ab60` table, and
advances phase field `0x178`; its terminal paths return at `0x393fc` or
`0x39404`.  The next continuation-style service begins at `0x39410`.

`0x39410` is a short service-state continuation.  It checks the four-word
state at `0x51acd0`, updates the active entries in `0x51acd0`/`0x51acd8` and
the paired counter table, then returns through the supplied continuation in
`g2` at `0x3947c` (`ret` at `0x39480`).  The longer state/update path begins at
`0x39490` and remains separate pending its full branch-connected boundary.

The branch-connected `0x39490` routine is a three-state service-motion
updater.  Its state-0, state-1, and state-2 arms emit paired records through
`0x884000`, use the object fields at `0x184`/`0x36` plus service constants at
`0x51ab30`/`0x51ab40`/`0x51ab3c`/`0x51ab54`, clamp the fixed-point deltas, and
advance the associated service state.  The state-3 arm falls through at
`0x39740`, and its terminal return is at `0x39848`; the internal returns at
`0x39558`, `0x39674`, and `0x39730` are all within this one function.  The next
distinct entry begins at `0x39850`.

`0x39850` is a phase-gated resource-motion variant.  It selects alternating
resource records, dispatches the corresponding geometry payload through
`0xbabc0`, advances phase field `0x178`, and returns at `0x39908`.
`0x39910` is a short remainder-based continuation: it reduces the current
phase against the resource constant at `0x2adc158`, publishes the selected
resource/result pair, and returns through `g1` at `0x3996c` (`ret` at
`0x39970`).
`0x39980` is the next phase-specific resource dispatcher.  It handles the
special phase values observed at `10`, `13`, `19`, `0x3f`, and `0x42`, updates
the associated service/result slots, and returns through `g1` at `0x39a68` or
`0x39a88` (`ret` at `0x39a8c`).  The next framed packet-emission routine begins
at `0x39a90`.

`0x39a90` is a framed geometry-batch initializer.  It emits the `5,18`
batch prefix and fixed-point constants through `0x884000`, programs the
`0x800010` command selector and `0x804000` tuple window, then submits related
records sourced through the tables at `0x51ace8` and `0x51acf0`.  Its stack
frame is restored and the routine returns at `0x39d94`; `0x39da0` begins a
separate floating-point/packet path.

`0x39da0` is the next framed selector packet builder.  It converts the input
selector with i960 floating-point operations, emits the `5,18` packet prefix
and selector-dependent coordinate/constants through `0x884000`, and reuses
the `0x800010`/`0x804000` tuple-window setup.  Its internal branch target at
`0x3a054` remains part of the same routine; the frame is restored at
`0x3a138` and the terminal `ret` is at `0x3a13c`.  The next distinct entry is
`0x3a140`.

`0x3a140` is a separate selector geometry emitter.  It derives a
selector-dependent floating-point value, emits the `5,18` prefix and the
corresponding constants through `0x884000`, and has internal packet-layout
arms at `0x3a1b0` and `0x3a360`.  The routine returns at `0x3a504`; the next
framed status/geometry routine begins at `0x3a510`.

`0x3a510` is that larger framed scene/object update routine.  It manages the
scene resource cursor at `0x51acb4`, emits repeated profile and object packets
through `0x884000`/`0x804000`, applies the fixed-point and floating-point
geometry transforms, updates object fields including `0x18c`, `0x198`, and
`0x1af`, and dispatches the associated effect callbacks.  Its frame restore is
at `0x3d508`/`0x3d50c`, with `ret` at `0x3d510`.

The following table at `0x3d520` contains eight phase routes back into the
recovered resource handlers: `0x37f50`, `0x38340`, `0x38490`, `0x385f0`,
`0x386c0`, `0x388f0`, `0x39980`, and `0x39910`.  This confirms that those
handlers are consumers of the central scene update dispatch rather than an
unrelated linear code island.

Immediately after the table, `0x3d540` is a shared fixed-point clamp helper.
Its branch at `0x3d558` enters the second half of the same routine; all
bounded exits are the returns at `0x3d570`, `0x3d5a8`, and `0x3d5c8`.
The following `0x3d5d0` routine initializes the shared geometry service state:
it clears the `0x51ab3c`/`0x51ab40` counters, the `0x51acxx` cursors and
flags, resets the object service fields, and selects the active profile-table
roots at `0x51ace8`–`0x51acf4`.  It returns at `0x3d728`; `0x3d730` begins
the next object-record initialization path.

The `0x3d730` object-record path is a complete update routine ending at
`0x3e5d8`.  Its caller supplies an active object record; the routine emits the
initial `0x884000` setup, derives the profile/service selector, advances the
shared service counter, and runs several profile-dependent fixed-point motion
and clamp paths.  It publishes derived coordinates at record offsets `0x2e`,
`0x154`, `0x1c8`, and `0x1cc`, updates phase/state fields around `0x170`–`0x18c`,
and returns through four branch-linked exits at `0x3e484`, `0x3e53c`,
`0x3e5ac`, and `0x3e5d8`.  The repeated calls to `0x3d540` are the shared
fixed-point clamp service, not separate object routines.

The adjacent `0x3e5e0` entry is a distinct profile/state initializer ending
at `0x3ec90`.  It consumes the shared service cursor at `0x51ab20`, selects
profile-specific floating-point constants for the cursor range, writes the
profile record at offsets `0xc`, `0x10`, and `0x34`, and then advances or
rewinds the cursor while driving the object phase/timer state.  The direct
callers at `0x274ac` and `0x27540` therefore select separate geometry update
families: `0x3e5e0` performs profile-state initialization, while `0x3d730`
performs the full object-record motion/update path.

The following record-pool island is now split at its padding boundaries.  The
packed table at `0x3eca0` holds selector-derived halfwords.  `0x3ecd0` and
`0x3ed60` scan 23 records rooted at `0x51ad10` with a `0x24`-byte stride and
initialize the first free slot; `0x3edd0` updates a free slot from caller
geometry values, and `0x3eeb0` seeds a reset record.  The emitters at
`0x3ef50` and `0x3f120` convert packed input components to fixed-point values
and emit the shared selectors 8/13/29/30.  `0x3f2b0` and `0x3f380` are the
corresponding packet constructors with alternate profile constants.

The continuation-style table services at `0x3f470` and `0x3f4e0` clear the
bounded 0x33c-byte pool, with the latter seeding selector 10; `0x3f550` is a
separate bounded scan that fills available slots with the requested selector
pair and returns at `0x3f5e4`.  These are record-pool management services
called by the geometry paths, not additional object-motion variants.

The next three continuation-style services (`0x3f5f0`, `0x3f6e0`, and
`0x3f7d0`) seed free runtime records from command-17 readbacks.  The first two
scan the 23-entry `0x51b070` pool and copy twelve payload words into the
record; the second additionally writes selector `1` at offset zero.  The
`0x3f7d0` variant scans the larger `0x508`-byte pool, marks the selected slot
with state `2`, and copies the command payload into its 0x30-byte record
area.  Each has a continuation pointer in `g14` and returns via `bx (g2)`;
their terminal `ret` instructions are separate continuation targets.

The following block is a repeated command-5 profile-emitter family.  Entries
begin at `0x3f8d0`, `0x3fa90`, `0x3fc50`, `0x3fdc0`, `0x3ff80`, `0x400f0`, and
`0x40310`; each updates the three object coordinate fields, compares the
selector-derived value from `0x3eca0`, optionally reports diagnostic codes
`0x1101`/`0x1102` (with variant-specific alternatives), and submits a
profile-specific payload through `0x804000`.  The variants share the same
record contract but use different ROM payload tables, so they are retained as
separate functions rather than merged into one generalized C routine.

After the `0x40270` dispatch/data table, `0x406d0` is another command-5
emitter.  It performs the same profile comparison and coordinate submission,
then emits two successive payloads from `0x2be3eb4` and `0x2be4034` before
returning at `0x408a4`.  This is a separate two-stage variant, not a fall-through
continuation of the framed `0x40310` routine.

The next packet-producer family begins at `0x408b0`.  Its six verified entries
at `0x408b0`, `0x40a80`, `0x40bc0`, `0x40d00`, `0x40e10`, and `0x40f50`
decrement the active record state, emit command-5 object coordinates, and
submit variant-specific command-18/19/21/30 payloads through `0x804000`.
Their payload tables are distinct (`0x2be0ef4`, `0x2be129c`, `0x2be0f9c`,
`0x2be105c`, `0x2be135c`, and `0x2be17dc`), which confirms six ROM-backed
variants sharing a protocol skeleton rather than one function with an
accidental linear split.

The subsequent motion-aware variants begin at `0x41090`, `0x41340`, and
`0x414b0`.  They accumulate object motion fields before submitting the same
command-5 geometry protocol, with the first also emitting command 18/19/21
records.  Their payload tables (`0x2be14dc`, `0x2be159c`, and `0x2be171c`)
remain distinct, and the exact returns at `0x41330`, `0x414ac`, and `0x4161c`
confirm three separate routines.

The dispatch table at `0x41c50` adds three more entries in this family:
`0x41620`, `0x41800`, and `0x419c0`.  The `0x41620` handler is state-sensitive
and performs fixed-point motion interpolation before emitting the shared
command-5/18/19/21 tail; `0x41800` is an alternate profile comparison and
payload route; and `0x419c0` is the framed interpolation variant.  Their
returns at `0x417f0` and `0x419b0`, followed by the `0x419c0` entry, confirm
that the table is an indirect selector over distinct handlers rather than a
single linear routine.

The table’s shared execution path begins at `0x41cb0`.  This batch emitter
walks seven object inputs, performs fixed-point interpolation, emits the
`0x202`/`0x804000` geometry records, and copies the transformed tail back into
the caller object before returning at `0x41f1c`.  The framed dispatcher at
`0x41f20` then walks the 23-entry `0x51ad10` pool through `0x41c50`, scans the
larger `0x51b070` pool, and emits active command-5/7/9 records; it returns at
`0x42310`.  `0x42320` is a separate two-buffer output-record store ending at
`0x42394`, selecting between `0x51b5b0` and `0x51b850` and writing seven
caller-provided words into the indexed 16-byte record.

The next profile-transition family is table-backed.  `0x42460` and `0x42760`
are separate seven-word descriptor tables; their handlers begin at `0x42480`,
`0x42670`, `0x42780`, and `0x428e0`.  Each advances the shared profile cursor
fields at `0x51ab08`/`0x51ab0c`/`0x51ab10`/`0x51ab12`, applies phase-dependent
thresholds, and publishes bounded object state at offsets `0xc2` and `0xc8`.
The first pair returns through `0x42660`/`0x4274c`, while the alternate pair
returns through `0x428d0`/`0x429bc`; the padding and continuation pointers
confirm four distinct handlers.

The following profile-transition pair is rooted at the six-word descriptor table
`0x429d0`.  The framed handler at `0x429f0` advances phase/timing state, emits
paired command-5/18/19/21 records, and publishes the bounded state fields at
`0xc2`/`0xc8` before returning at `0x430cc`.  The continuation-style alternate
at `0x430d0` uses the adjacent descriptor values and returns through
`0x43194`/`0x43198`.  This is the next layer above the smaller cursor-state
variants, not a fall-through extension of `0x428e0`.

The next sibling block continues the same state protocol.  Descriptor tables at
`0x431a0`, `0x43510`, and their adjacent continuation pairs feed distinct
handlers at `0x431c0`, `0x43420`, `0x43530`, and `0x43680`.  These routines
advance the shared profile cursor/timing globals, apply phase-dependent limits,
and publish bounded object fields, including the `0xd2`/`0xd4` and `0xc2`/`0xc8`
windows.  Their exact returns at `0x43410`, `0x43500`, `0x43678`, and `0x43770`
separate four handlers from the descriptor/data regions.

The following table-backed siblings are `0x437ac`, `0x438e0`, and `0x439e0`,
fed by descriptor tables at `0x43780` and `0x439c0`.  They retain the same
cursor/timing update convention but target different object phase windows;
the first publishes `0xbc`/`0xc0`/`0xc4`, while the later pair uses the shared
bounded state and phase latch.  The returns at `0x438d0`, `0x439bc`, and the
two internal exits of `0x439e0` establish the boundaries; `0x43ac4` is a
branch target inside the last handler, not a separate function.

The next cursor-transition group contains `0x43b00`, `0x43bb0`, and `0x43cb0`,
which share descriptor data around `0x43b90` and publish the same profile cursor
globals.  The latter two include initial-state and phase-threshold handling;
`0x43cb0` is the compact advance-only form.  The following descriptor table at
`0x43d20` feeds floating-point variants `0x43d50` and `0x43e00`, which update
the object scalar at `0xac` while retaining the shared cursor/timing protocol.
Returns at `0x43b88`, `0x43ca0`, `0x43d0c`, `0x43dfc`, and `0x43ed8` delimit
these handlers from their tables and padding.

At `0x43ee0`, the runtime profile pools are cleared across both configured
contexts, including their indexed phase arrays and phase latch bytes; the
routine returns through `0x43f90`/`0x43f94`.  The next entry, `0x43fa0`, is a
real indexed phase dispatcher: it selects one of eight state arms through the
table at `0x43fc8` using object offset `0x64`, computes bounded `0xc2`/`0xc8`
values, and returns at `0x44388`.  The table and its branch arms are therefore
one dispatch routine, rather than eight independent top-level functions.

The caller-facing timing/state routine at `0x44390` updates the active
object's `0x172`/`0x17a` timing fields according to the global mode at
`0x51c9d0`.  Its mode-specific paths can invoke the `0x43fa8` phase dispatcher
for both the object and its associated state record; the early and late returns
at `0x44498`, `0x44518`, and `0x44590` are internal exits of this one routine,
whose next aligned code begins at `0x445a0`.

The routine at `0x445a0` selects the active runtime profile mode from hardware
and startup state, stores the selected mode at `0x51bb18`, and dispatches the
corresponding geometry/state update through the eight arms at `0x44948`–
`0x449b8`.  It then publishes the selected cursor/timing values and writes the
derived hardware timing words before returning at `0x44ac0`; this is the
profile-mode coordinator rather than another packet-emission variant.

The mode-7/default hardware path calls `0x44ad0`, a separate timing emitter.
It derives scaled values from the selected profile and object record, writes
the command words through `0x884000`, updates `0x51bb00`/`0x51bb04`/`0x51bb08`,
and returns at `0x45078`.  This isolates the hardware conversion tail from the
larger mode-selection routine.

The same dispatcher selects additional hardware timing emitters at `0x45080`,
`0x45380`, `0x45680`, `0x45c30`, and `0x45f50`.  These are separate routines,
not shared fall-through code: each has its own scaling constants and returns at
`0x45378`, `0x4567c`, `0x45c28`, `0x45f48`, and `0x46474`, while retaining the
common `0x884000` command stream and `0x51bb00`-series profile outputs.

The remaining two mode targets are `0x46480` and `0x466b0`.  The former is a
sixth `0x884000` timing emitter that incorporates object-local timing inputs;
the latter switches to the paired `0x804000` geometry-buffer path while still
deriving its values from the shared profile state.  Their returns at `0x46474`,
`0x466a0`, and `0x4692c` confirm the final two standalone variants and the
boundary before the next subsystem.

The next callable cluster begins at `0x4a420`.  It derives profile-relative
thresholds from the active record, sets the per-object flags at `0x1dd`/`0x1de`/
`0x1df`, and stores normalized values at `0x1e2`/`0x1e4`/`0x1e6`, returning at
`0x4a770`.  The phase advance at `0x4a780` then consumes descriptor records from
the large data region beginning at `0x46930`, updates `0x178`/`0x17c` and the
shared cursor globals, and returns at `0x4a98c`.  Its alternate at `0x4a990`
uses adjacent descriptor records and returns at `0x4abb8`; these are distinct
phase handlers, not code embedded in the descriptor table.

The following phase-transition siblings begin at `0x4abc0`, `0x4ad50`,
`0x4ae70`, `0x4af20`, and `0x4aff0`.  Each consumes a different descriptor pair
from the large profile data region, advances `0x178`/`0x17c`, publishes the
shared cursor globals, and has a mode-specific reset path.  Their returns at
`0x4ad48`, `0x4ae60`, `0x4af1c`, `0x4afec`, and `0x4b088` establish five more
standalone handlers in this family.

The next descriptor-backed transition at `0x4b090` consumes the `0x46a20`
records and returns at `0x4b148`.  The larger routine at `0x4b150` combines
profile cursor updates with event/status handling: it selects additional
descriptor records, advances the object phase, sets event flags, and emits
mode-dependent status identifiers through the existing text/status service.
Its normal and alternate exits at `0x4b560` and `0x4b5f0` delimit it from the
following runtime state routine.

The runtime event-progress routine at `0x4b600` mirrors the preceding event
handler for the alternate profile range: it advances phase progress, selects
descriptor records, updates the shared cursor fields, resets object state at
range completion, and emits the corresponding status events.  It returns at
`0x4b934`.  Two cursor-transition siblings follow at `0x4b940` and `0x4bb10`,
using descriptor records at `0x46a90` and `0x46af0`; their returns at
`0x4bb00` and `0x4bcd8` delimit the paired handlers.

The dispatch-table target at `0x4bce0` is the profile-state finalizer.  It
resets the object phase fields, emits the associated state words through
`0x884000`, updates the shared profile/event state, and applies the status
identifier selected by the object mode.  Its return at `0x4c044` marks the
boundary before the next runtime state routine.

The next runtime-update siblings begin at `0x4c050`, `0x4c610`, and `0x4c8f0`.
They use successive descriptor ranges, advance the object timing/phase state,
apply the same event/status mapping, and refresh the associated profile record.
Their returns at `0x4c604`, `0x4c8e8`, and `0x4ca3c` establish three separate
handlers before the following state cluster.

The next update siblings are `0x4ca40`, `0x4cb70`, `0x4cc20`, and `0x4cd00`.
They continue the descriptor-driven profile/event protocol, with distinct
phase ranges and reset behavior; the last uses the `0x46bb0` descriptor range.
The exact returns at `0x4cb68`, `0x4cc18`, `0x4ccfc`, and `0x4d040` separate
four more handlers from the following state cluster.

Three additional cursor-transition targets follow in the dispatch table at
`0x4d540`, `0x4d720`, and `0x4d880`.  The first selects among the
`0x207641c`, `0x2077504`, and `0x20785ec` descriptor/scalar ranges; the second
uses the compact descriptor records at `0x46c40`, `0x46c48`, and `0x46c50`.
Both publish `0x51ab08`/`0x51ab0c` and the paired cursor values at
`0x51ab10`/`0x51ab12`, advance object phase `0x178`, and apply the shared
`0x150` timing correction before returning at `0x4d710` and `0x4d870`.

The third target at `0x4d880` is a related but richer transition handler.  It
uses the `0x46c60`-series records, raises mode-specific status flags, selects
message identifiers through the text/status service at `0x2a4e0`, and handles
the later phase ranges through `0x46c68` and `0x46c70`.  Its final timing
correction and state publication return at `0x4da78`, cleanly delimiting the
handler from the following table-backed routine.

The next three dispatch targets continue the same family at `0x4da80`,
`0x4dce0`, and `0x4def0`.  The first two are near-identical indexed-record
variants over `0x46c80` and `0x46ce0`; each advances object phase `0x17a`,
publishes the paired shared cursor values, and enters a status-reset path when
its range completes.  Their multiple case exits at `0x4dc7c`, `0x4dca0`, and
`0x4dcdc`, followed by `0x4ded0`/`0x4dee4`, are internal arms of those two
handlers rather than new table entries.

The `0x4def0` target uses the smaller `0x46d40` record range and a different
phase scale.  It still publishes `0x51ab08`/`0x51ab0c` and the paired cursor
fields, but its completion arm also raises the mode-specific status flag and
selects a text/status message.  The handler returns at `0x4df68` on the short
path and `0x4e070` after the reset path; the following `0x4e080` entry is a
separate routine.

The `0x4e080` target is a second threshold-normalization handler.  It clamps
the three object timing fields at `0x1ec`/`0x1ea`/`0x1ee`, derives the
corresponding threshold flags at `0x1de`/`0x1dd`/`0x1df`, and recomputes the
normalized values at `0x1e4`/`0x1e2`/`0x1e6` from the active hardware profile.
Its caller-link return at `0x4e3cc`/`0x4e3d0` separates it from the next
phase-dispatch variant.

That phase dispatcher begins at `0x4e3e0`.  It consumes the object phase and
shared timing state, selects the appropriate profile transition path, and
returns through the supplied link at `0x4e5e8`/`0x4e5ec`.  The distinct
`0x4e3e0` entry confirms this is a sibling dispatcher rather than a fall-through
continuation of threshold normalization.

The phase-dispatch family continues at `0x4e5f0`, `0x4e820`, and `0x4e920`.
These are separately delimited siblings: `0x4e5f0` uses the `0x46dc0` record
set, `0x4e820` selects a descriptor base in the `0x2572744` data region, and
`0x4e920` reads paired records at `0x46e20`/`0x46e24`.  All three publish the
shared cursor fields and use caller-link returns at `0x4e814`, `0x4e918`, and
`0x4ea30`, with profile reset/status transitions on their completion paths.

The compact phase-transition table at `0x7f98` adds four more siblings:
`0x4ea40`, `0x4eaf0`, `0x4ebc0`, and `0x4ec60`.  They consume descriptor
ranges at `0x46e40`, `0x46e50`/`0x46e54`, `0x46e70`, and
`0x46e80`/`0x46e84`, respectively.  Each publishes `0x51ab08`/`0x51ab0c`,
advances the object phase, and either returns through its caller link or resets
the phase fields at range completion.  Their clean boundaries are the
following aligned entries at `0x4eaec`, `0x4ebbc`, `0x4ec58`, and `0x4ed18`.

The table target at `0x4ed20` is the parent phase-state dispatcher for the
next group.  It first updates object field `0x2e` from the current offset and
`0x184`, then switches on phase state `0x17c`.  The arms at `0x4ed80`,
`0x4ee1c`, `0x4ef00`, and `0x4efa4` select different profile record bases and
status transitions; they are internal paths of the same routine, not separate
dispatch entries.  The short arms return at `0x4ed70`/`0x4ed7c`, the normal
progress arm at `0x4edf8`/`0x4ee18`, and the later arms at `0x4eefc`,
`0x4efa0`, and `0x4f018`, with the aligned `0x4f01c` boundary ending the
parent handler.

The next data-table entries are `0x53050` and `0x53280`.  The former uses the
paired `0x472f0`/`0x472f4` records and finishes its profile/status transition at
`0x53278`.  The latter is a caller-link phase dispatcher over
`0x47350`/`0x47354`; it publishes the shared cursor fields, applies the phase
completion flag checks, and returns at `0x534bc`/`0x534c0`.  The aligned
`0x5327c` and `0x534c4` boundaries keep these handlers separate from the next
state-transition routines.

Two further phase-transition helpers begin at `0x4f020` and `0x4f1f0`.
The first uses paired records at `0x46ea0`/`0x46ea4`, while the second uses
`0x46f00`/`0x46f04`; both advance `0x17a`, publish the shared cursor fields,
and take a bounded reset path when their descriptor range completes.  Their
caller-link returns at `0x4f1e0`/`0x4f1e4` and `0x4f3cc`/`0x4f3d0` delimit the
helpers from the following subsystem entries.

The later dispatch table resumes with two extended runtime-state handlers at
`0x51440` and `0x517f0`.  The first selects indexed records at
`0x470b0`/`0x470b4` across several timing ranges, while the second uses the
corresponding `0x47110`/`0x47114` records.  Both publish the shared cursor
fields, advance phase `0x17a`, and enter the common status/reset path when a
range completes.  Their return boundaries are `0x517ec` and `0x51a74`, just
before the following `0x51a80` table target.

The `0x51a80` target is the object-pair form of threshold normalization.  It
clamps `0x1ec`/`0x1ea`/`0x1ee`, applies the profile-dependent flag updates, and
then calls the service at `0xbf120` before recomputing normalized
`0x1e2`/`0x1e4`/`0x1e6` values.  Its final return at `0x520d8` confirms the
handler extends across the internal completion paths and ends at the aligned
`0x520dc` boundary before the next state family.

The `0x72c10` orchestrator's `0x76b00` edge is labeled
`match_geometry_state_transition`. Its entry loads the linked object at
`+0x74`, tests the current object's `+0x64` field, and returns immediately
for value 9; the remaining state-dependent updates are not folded into the
bounded orchestrator model.
The route-prefix predicate model is implemented in
`recovered_match_geometry_state_gate_76b00.c`; it records the early state-9
return, class/state route selection, and bit-6 publication arm without
claiming the subsequent float comparisons or profile-table dispatch.
The entry also tests the linked record's signed `+0x172` class against the
19/20 pair before taking the state-6 arm. That arm updates `0x504d98` from
`0x504d60` under its observed threshold tests, while the alternate bit-6
path publishes `g14` to `0x504d94` and resets `0x504d98` to 23. The common
tail gates on `0x504dc0 <= 15` and `0x504db4 > 0` before selecting the
profile table or continuing through the transform checks. These direct
predicates are now called out as the unresolved `0x76b00` boundary; the
floating comparison branches and downstream state updates still require a
dedicated model.

The `0x75200` range-update path calls `0x77470`, whose entry consumes object
fields `+0x1c4` and signed `+0x18e`, combines them with `0x504d94` and
`0x504db4`, and dispatches through the 21-entry table rooted at `0x77508`
using `0x504d94 - 1`. This call boundary is annotated as
`match_geometry_profile_dispatch`; its floating normalization and individual
table arms remain separate.

The following phase-state dispatch siblings begin at `0x520e0` and `0x52360`.
The first switches among descriptor bases `0x47200`, `0x47208`, `0x47210`, and
`0x47218`, while the second uses the `0x47220`-series records.  Both branch on
phase state `0x17c`, publish the shared cursor fields, and contain mode-specific
reset/status arms before returning at `0x5235c` and `0x52640`.

The data table at `0xa960` then exposes `0x52650` as a separate threshold-event
handler.  It tests the normalized threshold flag at `0x1dd`, emits the
`0x1208`/`0x1230` status message through `0x2a4e0`, updates object flag `0x1a6`,
and advances through descriptor bases `0x47260`, `0x47268`, and `0x47270`.
Its short and completion exits at `0x52858` and `0x52874` delimit it from the
separate table target at `0x52880`.

The paired `0x52880` target repeats this threshold-event protocol for the next
profile range.  It tests the same normalized flag, emits the `0x1208`/`0x1230`
message, updates `0x1a6`, and consumes records at `0x47280`/`0x47284` while
advancing object phase `0x178`.  Its progress and completion returns at
`0x52adc` and `0x52af4` delimit the sibling before the next `0x52b00` handler.

The next compact transition trio is exposed by the `0xa968`-range table:
`0x52b00`, `0x52ba0`, and `0x52ca0`.  They consume descriptor bases
`0x472b0`, `0x472c0`, and `0x472d0`, respectively, publish the shared cursor
fields, and reset or advance phase `0x178` at their range boundaries.  The
`0x52ca0` variant additionally sets phase flag bit 19 before entering its reset
state.  Their returns at `0x52b9c`, `0x52c9c`, and `0x52d2c` delimit the trio
from the following `0x52d30` handler.

The `0xa978` table target at `0x52e30` is a parent phase-state dispatcher.  It
updates object field `0x2e` from the current offset and `0x184`, then selects
internal transition arms at `0x52e84`, `0x52f30`, and `0x52fac`.  Those arms
consume the large data ranges rooted at `0x22749d8`, `0x22770e8`, and
`0x22749e0`, publish the shared cursor fields, and emit mode-specific status
messages on completion.  The internal returns at `0x52f2c`, `0x52fa8`,
`0x53020`, and `0x53040` are contained within the parent, which ends at the
aligned `0x53044` boundary.

The `0xa9dc` entry at `0x534d0` is a further profile phase-state dispatcher.
It refreshes derived object field `0x2e`, selects among the large profile data
ranges rooted at `0x22749d8`, `0x22770e8`, and `0x22749e0`, and publishes the
shared cursor/status state.  Its short and completion exits at `0x53558`,
`0x535ec`, `0x53654`, and `0x5367c` delimit it from the next target.

The following `0xa9e0` target at `0x53680` marks a subsystem boundary.  It
performs floating-point/fixed-point runtime geometry math, derives a correction
for object field `0x150`, updates `0x192` and `0x1c4`, and emits the associated
status/geometry state.  Its return at `0x53a10` and aligned end at `0x53a14`
separate this math service from the later transition entries.

The next table entries are a pair of larger profile status transitions at
`0x53a20` and `0x53d00`.  They share the phase tests, cursor publication, and
status-reset protocol, but select different descriptor ranges:
`0x473c0`/`0x473c8`/`0x473d0` for the first and
`0x473e0`/`0x473e8`/`0x473f0` for the second.  Their returns at `0x53cf8`
and `0x53fdc` delimit the siblings.

The following `0x53fe0` and `0x540a0` entries are compact transition handlers.
They use descriptor bases `0x473f8` and `0x47400`, respectively, publish the
same shared cursor fields, reset phase/status state at their low range, and
return through saved completion links.  Their direct returns at `0x5409c` and
`0x5415c` keep these arms separate from the larger `0x54160` dispatcher.

The `0x54160` table target is the next parent phase-state dispatcher.  It
consumes the `0x47410`/`0x47418`/`0x47428` records, advances object phase
`0x178`, publishes the shared cursor fields, and applies the derived geometry
correction to object field `0x150` before completing at `0x54334`.

Two compact saved-return siblings follow at `0x54340` and `0x543f0`; they use
the `0x475d0` and `0x475d8` descriptors and reset the same phase/status fields.
The `0x544a0` and `0x545f0` entries are paired threshold-event handlers using
`0x475c0` and `0x475c8`.  Each has a primary and range-reset terminal arm
within the same function, so the alternate returns at `0x545ec` are not new
top-level entries.

The next pair, `0x54760` and `0x54a60`, performs indexed geometry selection
from the `0x47440` and `0x47470` record families.  They publish paired cursor
values, advance phase `0x17a`, and feed the common status transition protocol;
their aligned ends are `0x54a54` and `0x54db0`.

The following `0x54e00` handler repeats the runtime geometry/status update
pattern with records derived from `0x22740d0`.  It advances phase `0x178`,
publishes the shared cursor fields, and applies the same object-`0x150`
correction before returning at `0x54f48`.  Its compact companion at `0x54f50`
publishes the next cursor range and returns through the saved link at
`0x550ac`, with the aligned function end at `0x550b4`.

The `0x550c0` entry begins the next indexed geometry updater.  It selects
paired records from the `0x474a0` family according to the two object phase
indices, publishes both cursor coordinates, and contains the status reset and
message path before its return at `0x552f4`.

The `0x55300` and `0x55550` entries continue the indexed updater family with
the `0x47500` and `0x47560` paired record tables.  Both publish the two cursor
coordinates and advance phase `0x17a`; the first has internal exits at
`0x55380`, `0x55454`, and `0x554dc` before its final status arm and aligned end
at `0x5554c`.  The sibling’s threshold/event arms run through `0x5578c`,
`0x55794`, and `0x55804`, ending at `0x55808`.

The next top-level boundary at `0x55930` is a per-frame object kinematics
service rather than another profile-table selector.  It clamps the three
position fields at `0x1ec`/`0x1ea`/`0x1ee` against the active record, derives
collision flags at `0x1dd`/`0x1de`/`0x1df`, and computes normalized extents at
`0x1e2`/`0x1e4`/`0x1e6` using fixed-point division.  It returns through the
saved link at `0x55c88`.

The `0x55c90` controller consumes phase/state `0x17c` and selects the
`0x475e0`/`0x475e8`/`0x475f0` records for progression, reset, and cursor
publication.  Its internal arms end at `0x55e9c`.  The following `0x55ea0`
variant uses `0x47600` indexed records and carries the same transition protocol
through its aligned return at `0x560c8`.

The following compact transition cluster runs from `0x560d0` through
`0x56638`.  `0x560d0` uses the `0x2572744`-derived records, while the indexed
siblings at `0x561f0`, `0x56320`, and `0x563f0` consume the
`0x47660`/`0x47664`, `0x47680`, and `0x47690`/`0x47694` families.  The final
two compact handlers use `0x476b0` and `0x476c0`; all six publish the shared
cursor fields and either advance phase or enter the common reset state.  Their
aligned ends are `0x561e8`, `0x5631c`, `0x563ec`, `0x564dc`, `0x5657c`, and
`0x5663c`, respectively.

At `0x56640`, the code changes back to a parent phase-state dispatcher.  It
recomputes derived object field `0x2e`, then selects among record families
rooted at `0x2563700`, `0x2564a28`, and `0x2566a30`, publishing cursor state and
status messages for each arm.  The internal completion returns through
`0x56724`, `0x56890`, `0x56908`, and `0x56928`; the parent ends at `0x5692c`.

The following indexed siblings at `0x56930` and `0x56b30` use the paired
`0x476e0`/`0x476e4` and `0x47740`/`0x47744` records.  They advance phase
`0x17a`, publish paired cursor coordinates, and enter the shared reset path at
their range limits; their aligned ends are `0x56b28` and `0x56d08`.

The `0x56d10` handler begins another parent phase-state dispatch.  It clears
object fields `0x186`/`0x188`, recomputes derived field `0x2e`, and selects the
`0x477a0`/`0x477a8`/`0x477b0` records while publishing phase and status state;
its internal arms end at `0x56f3c`.  The larger `0x56f40` sibling uses the
`0x477c0`/`0x477c8`/`0x477d0` records and adds collision-flag checks and status
message paths before its aligned end at `0x57264`.

The `0x57270` handler continues the phase/status dispatcher family with
records at `0x477e0`/`0x477e8`/`0x477f0`; it gates on collision state, publishes
the shared cursor fields, and completes at `0x5752c`.  The paired indexed
updaters at `0x57530` and `0x576d0` use the `0x47800` and `0x47810` record
families, respectively, with phase progression and reset paths ending at
`0x576cc` and `0x5786c`.

The `0x57870` entry is the first explicit video/geometry command producer in
this run.  It emits the object packet through `0x884000`, polls the command
result, advances subphase `0x17e`, and publishes `0x1c4` plus the associated
status fields before ending at `0x57ac8`.  Its larger sibling at `0x57ad0`
uses the `0x47830` record pair and follows the same command-port handoff,
ending at `0x57d64`.

The compact `0x57d70` transition uses the `0x47840` descriptor and returns
through its saved link at `0x57e28`.  The following `0x57e30` command producer
uses `0x47848`, repeats the command-port polling and phase/status publication,
and ends at `0x57fb8`.

The next compact transition run contains `0x57fc0` and `0x58070`, which use
the `0x47a30` and `0x47a38` descriptors and return through saved links.  The
qword-record siblings at `0x58120` and `0x58230` use `0x47a10` and `0x47a20`,
publish the paired cursor values, and emit the same status message on phase
completion.  Their aligned ends are `0x58068`, `0x58118`, `0x58228`, and
`0x58338`.

The larger indexed pair at `0x58340` and `0x58690` uses the
`0x47850`/`0x47854` and `0x47880`/`0x47884` record families.  Both publish
paired cursor values, advance phase `0x17a`, and contain multiple status and
reset arms within one top-level function; their aligned ends are `0x58688`
and `0x5892c`.

The next compact indexed transition at `0x58930` consumes the
`0x478b0`/`0x478b8`/`0x478c0` records and ends at `0x58ae4`.  The `0x58af0`
handler then returns to the runtime geometry/status pattern, using records
derived from `0x2560bc8`, correcting object position, and ending at `0x58c3c`.
The larger `0x58c40` sibling uses `0x478d0`/`0x478d8`, adds collision/status
gating, and ends at `0x58ea4` after its multi-arm completion paths.

The following indexed handlers continue the same profile-transition family:
`0x58eb0` uses `0x478f0` and ends at `0x590b8`, while `0x590c0` uses the
paired `0x47950`/`0x47954` tables and ends at `0x5936c`.  The larger driver at
`0x59370` spans several threshold arms and ends at `0x59630`.  Its arms publish
the same shared cursor records while moving profile state and resetting object
status fields.

At `0x59640`, the code evaluates three geometry bounds, sets per-axis collision
flags, clamps the profile coordinates, and computes derived ratios through
`0x59990`.  The next controller at `0x599a0` dispatches profile phases 0--3
through the `0x47e20`/`0x47e28`/`0x47e30`/`0x47e38` records and ends at `0x59c34`.

The sibling controller at `0x59c40` covers the same four profile states with
the `0x47e40`/`0x47e44`/`0x47e48`/`0x47e4c` records and ends at `0x59f3c`.
`0x59f40` then handles the next phase-transition stage, using the `0x47e80`
and `0x47e88` records to advance frame counters and reset phase status; its
aligned end is `0x5a194`.

The next controller at `0x5a1a0` selects the `0x47ea0`/`0x47ea4`/`0x47ea8`
records and ends at `0x5a438`.  Two compact siblings follow: `0x5a440` uses
the `0x47ed0` record and ends at `0x5a4dc`, while `0x5a4e0` uses `0x47ee0` and
ends at `0x5a5dc`; both advance or reset the shared phase counter at their
terminal thresholds.

The compact transition siblings continue at `0x5a5e0` with the `0x47ef0`
record, ending at `0x5a67c`, and at `0x5a680` with the `0x47f00` record,
ending at `0x5a77c`.  Both preserve the shared cursor publication pattern while
advancing or resetting the profile phase counter.

The next multi-state transition at `0x5a780` incorporates geometry-derived
timing and ends at `0x5aabc`.  Two indexed siblings follow: `0x5aac0` consumes
the paired `0x47f10`/`0x47f14` records and ends at `0x5acb8`, while `0x5acc0`
consumes `0x47f70`/`0x47f74` and ends at `0x5af00`.  All three continue the
shared cursor publication and phase/status completion pattern.

The next large phase transitions are `0x5af10` through `0x5b1dc`, using the
`0x47fd0`/`0x47fd8`/`0x47fe0` records and status-gated frame progression, and
`0x5b1e0` through `0x5b4ac`, using the parallel `0x47ff0`/`0x47ff8`/`0x48000`
records.  Both handlers converge their threshold arms into terminal reset
logic rather than representing separate functions at each internal return.

The following pair continues the same long-transition structure: `0x5b4b0`
uses the `0x48008` record and ends at `0x5b600`, while `0x5b610` uses the
parallel `0x48010` record and ends at `0x5b764`.  Both publish cursor progress,
reset terminal state, and perform the fixed-point object-geometry setup before
returning through their controller links.

Four compact handlers follow: `0x5b770` uses `0x48020` and ends at `0x5b82c`,
while `0x5b830` uses `0x48018` and ends at `0x5b8ec`.  The short-counter pair
at `0x5b8f0` and `0x5b9a0` uses `0x48230` and `0x48238`, ending at `0x5b994`
and `0x5ba44` respectively.  These handlers advance phase/frame counters and
reset or publish the next object state through their linked return paths.

The next frame-transition pair begins at `0x5ba50` and `0x5bb60`, using the
`0x48210` and `0x48220` records and ending at `0x5bb54` and `0x5bc64`.
`0x5bc70` then expands this into a larger indexed transition using the paired
`0x48030`/`0x48034` records; its linked completion boundary is `0x5bfe0`.

The parallel indexed transition at `0x5bff0` uses the `0x48060`/`0x48064`
records, repeats the status-gated threshold and object-state setup pattern, and
ends at its linked return boundary `0x5c360`.

The next multi-arm indexed transition begins at `0x5c370`, uses the object
`0xfc`/`0xf8` arrays and the paired `0x48090`/`0x48094` records, and ends at
`0x5c648`.  Its separate reset helper at `0x5c650` selects the mode-specific
record, clears phase fields, and initializes the next state before returning at
`0x5c6b8`.

The next indexed sibling at `0x5c6c0` uses the paired `0x480f0`/`0x480f4`
records and the object arrays, ending at `0x5c97c` after its terminal
phase/status arms.  Its reset helper at `0x5c980` selects the mode-specific
record and reinitializes object state through `0x5c9e8`.

The following indexed transition at `0x5c9f0` uses the paired
`0x48150`/`0x48154` records and the object arrays; its forward arms converge at
`0x5cd04` and end at `0x5cd18`.

The reset helper at `0x5cd1c` ends at `0x5cd88`.  The following larger
transition at `0x5cd90` uses `0x481b0`/`0x481b8`, performs cursor and object-state
updates plus geometry correction, and ends at `0x5cfe8`.  Its parallel sibling
starts at `0x5cff0`, uses `0x481d0`/`0x481d8`, and ends at `0x5d1b8`.

The next phase-transition handler at `0x5d1c0` uses the
`0x481f0`/`0x481f8`/`0x48200` records and converges at `0x5d3cc`.  Its
geometry evaluator sibling begins at `0x5d3d0`, performs the same bounds,
axis-flag, and derived-ratio work as the earlier evaluator, and is linked
through `0x5d72c`.

The next phase controller at `0x5d730` dispatches through the
`0x48240`/`0x48248`/`0x48250` records and ends at `0x5d964`.  The indexed
controller at `0x5d970` then uses the `0x48260` records for object-state and
cursor progression, with its linked completion boundary at `0x5dc80`.

The compact table-driven transition at `0x5dc90` selects among the
`0x482c0`/`0x482c8`/`0x482d0`/`0x482d8` records according to phase thresholds
and returns at `0x5de4c` after publishing the next counter state.

The following transition at `0x5de50` uses the `0x482e0` records, advances the
cursor through its threshold arms, and ends at `0x5e034` after terminal
status/object-state handling.  The compact sibling at `0x5e040` uses the
`0x48360` record and ends at `0x5e104` after advancing or resetting the object
phase counter.

The next compact table-driven trio consists of `0x5e110` through `0x5e1f4`
using `0x48370`/`0x48374`, `0x5e200` through `0x5e298` using `0x48390`, and
`0x5e2a0` through `0x5e358` using `0x483a0`/`0x483a4`.  They publish cursor
progress and apply the corresponding object-phase reset paths at their
thresholds.

The next controller at `0x5e360` derives the object coordinate from fields
`0x34`, `0x184`, and `0x2e`, then drives several phase arms.  It publishes
`0x79034`-based assets through `0x51ab08`/`0x51ab0c`, advances the shared phase
counter, and performs terminal object-state resets before returning at
`0x5e520`.

The indexed transition at `0x5e530` uses the paired `0x483c0`/`0x483c4`
records, publishing the selected pair and entering the terminal progression
path when the phase reaches its threshold; it ends at `0x5e724`.  Its sibling
at `0x5e730` uses the `0x48420` records and returns through a saved callback,
ending at `0x5e900`.  The parallel controller at `0x5e910` repeats the
multi-arm `0x79034` asset/phase pattern and ends at `0x5eae4`.

The following controller at `0x5eaf0` uses the `0x26d1f5c` asset records,
phase/status gates, and object geometry setup before returning through its
callback at `0x5ecbc`.  The compact transitions at `0x5ecc0` and `0x5efa0`
use the `0x48480`/`0x48488`/`0x48490` and `0x484a0`/`0x484a8`/`0x484b0`
records respectively, with shared cursor publication and terminal resets;
they end at `0x5ef94` and `0x5f24c`.  Two parallel record-backed transitions
follow at `0x5f250` (`0x484f0`, ending `0x5f584`) and `0x5f590` (`0x484c0`,
ending `0x5f750`).

The callback-based family continues with `0x5f930` and `0x5f9f0`, using the
`0x48500` and `0x48508` record pairs and returning at `0x5f9ec` and `0x5fac0`.
The short phase controllers at `0x5fad0` and `0x5fb80` use `0x486e0` and
`0x486e8`, ending at `0x5fb78` and `0x5fc24`.  Their neighboring transitions
at `0x5fc30` and `0x5fcf0` use `0x486d0` and `0x486d8`, ending at `0x5fcec`
and `0x5fdac`.

The larger indexed controller at `0x5fdb0` uses the paired `0x48510`/`0x48514`
records, applies phase/status gates and geometry correction, then returns
through its callback at `0x6004c`.

The indexed controller at `0x60050` uses the paired `0x48540`/`0x48544`
records and ends at `0x6036c`.  The callback-returning controller at
`0x60370` uses generated asset addresses and ends at `0x6057c`; its sibling
at `0x60580` continues the generated-asset phase progression through
`0x607fc`.

The indexed transitions at `0x60a30` and `0x60c60` use the
`0x48570`/`0x48574` and `0x485d0`/`0x485d4` records respectively, publishing
cursor pairs and applying state changes at their thresholds.  Their linked
boundaries are `0x60ac0` and `0x60e78`.

At `0x611d0` the code changes role: it decrements and clamps the three
object extents, updates the `0x1dd`/`0x1de`/`0x1df` axis flags from geometry
and collision tests, computes derived ratios at `0x1e4`, and returns through
the saved callback at `0x615e8`.

The next multi-state controller at `0x615f0` selects from the
`0x47a40`/`0x47a48`/`0x47a50` records, advances phase and object-state fields,
and returns at `0x6182c`.  The indexed sibling at `0x61830` uses the
`0x47a60` records and the object selector at `0x188`, ending at `0x61aa4`.

The following transitions use the nearby record tables: `0x61ab0` uses
`0x47ab0`/`0x47ab8`/`0x47ac0` and ends at `0x61c38`; `0x61c40` uses the
`0x47a90`/`0x47a94` pair and ends at `0x61d50`; `0x61d60` uses `0x47ac8` and
ends at `0x61e0c`; `0x61e10` uses `0x47ad0`/`0x47ad4` and ends at `0x61edc`;
`0x61ee0` uses `0x47af0` and ends at `0x61f78`; and `0x61f80` uses
`0x47b00`/`0x47b04` and ends at `0x62038`.

The object-state controllers at `0x62040` and `0x62260` use the
`0x2338078` asset base plus `0xb3e98`, publishing active object data and
applying visibility/state gates.  They end at `0x62258` and `0x62570`.
The indexed transition at `0x62580` uses the paired `0x47b20`/`0x47b24`
records and ends at `0x62918`.

At `0x62920` the code switches to geometry setup: it clears object selectors,
recomputes the centered coordinate, emits object words through the `0x884000`
FIFO, and calculates the fixed-point transform value stored at `0x1c4`; the
handler ends at `0x62d28`.  The following phase transition at `0x62d30` uses
the `0x47c00`/`0x47c08` records and ends at `0x62fc8`.

The next compact transitions use the `0x47c18` pair (`0x62fd0–0x6311c`)
and the `0x47c20` pair (`0x63120–0x631dc`), followed by the short
`0x47e10` controller at `0x631e0–0x63284` and the `0x47e00` transition at
`0x63290–0x6336c`.  The larger indexed controller at `0x63370` uses the
`0x47c30`/`0x47c34` records with status gating and ends at `0x636b0`.

The large indexed controller at `0x636c0` uses the `0x47c90`/`0x47c94`
records and ends at `0x63a88`.  The following transitions use the
`0x47cc0`/`0x47cc8`/`0x47cd0` records (`0x63a90–0x63bf0`) and the
`0x47ce0`/`0x47ce8`/`0x47cf0` records (`0x63c00–0x63d50`), including cursor
progression, timing thresholds, and movement-state correction.

The generated-asset controller at `0x63d60` uses the
`0x47d00`/`0x47d08`/`0x47d10` records, scales the cursor in fixed point,
updates state flags, and returns through its callback at `0x63f24`.

The indexed transition at `0x63f30` uses the paired `0x47d20`/`0x47d24`
records and publishes the selected cursor pair before applying its phase
limit and terminal object-state reset; it ends at `0x64190`.  The late
indexed sibling at `0x641a0` uses `0x47d80`/`0x47d84`; its alternate arm
continues through `0x6422c`, so the complete function boundary is `0x64300`.

The phase controller at `0x64310` advances the paired counters at `0x1f8`
and `0x1fa`, selects `0x47dc0`/`0x47dc4` records, publishes the active
cursor pair, and performs terminal progression through `0x6459c`.

At `0x645a0` the geometry bounds evaluator clamps the three extents, applies
the object-record offsets, updates the `0x1dd`/`0x1de`/`0x1df` axis flags,
and computes the derived ratios at `0x1e4`/`0x1e2`/`0x1e6`; it returns through
its saved callback at `0x648c4`.

The object-state controllers at `0x648d0` and `0x64b00` are parallel
callback-driven handlers.  The first uses `0x486f0`/`0x486f8` records and
movement flags, ending at `0x64af0`; the second indexes the `0x48710` table
using the object selector at `0x188`, ending at `0x64d3c`.

The following object-state family is table-backed as well: `0x64d40` uses
the `0x48770`/`0x48778` records and ends at `0x64f50`; `0x64f60` uses the
indexed `0x48790` records and ends at `0x65190`; `0x651a0` uses `0x487f0` and
ends at `0x65268`; and `0x65270` selects paired `0x48800`/`0x48804` records
using the object selector at `0x188`, ending at `0x65358`.

The compact handlers at `0x65360` and `0x65400` continue the same cursor and
phase protocol with `0x48820` and selector-indexed `0x48830`/`0x48834` records;
they end at `0x653f8` and `0x654b8`, respectively.

The recentering handlers at `0x654c0` and `0x65630` share the `0x48850`/
`0x48854` record pair.  Both first recenter the object coordinate from the
`0x34`/`0x184`/`0x2e` fields, then publish the active cursor pair and apply
the terminal phase reset; their boundaries are `0x6562c` and `0x6577c`.
The `0x65660` block is an internal continuation of the latter handler, not a
separate table entry.

The indexed transition at `0x65780` uses the paired `0x48880`/`0x48884`
records, publishes both cursor pairs, and handles the phase-limit transition,
ending at `0x65974`.  The indexed phase controller at `0x65980` uses the
`0x488e0`/`0x488e4` records, returns through its saved callback, and ends at
`0x65bc0`.

The larger object-state controller at `0x65bd0` uses the `0x48940`/
`0x48948`/`0x48950` records.  It aligns the phase cursor, gates on status
bytes at `0x1db`/`0x1dc`, publishes the active record pair, and initializes
the next object state before returning at `0x65ef4`.

The next controller family covers six table entries.  `0x65f00` uses the
`0x48960`/`0x48968` records and ends at `0x66210`; `0x66220` uses the packed
`0x489b0` pair and ends at `0x66414`; and `0x66420` uses the packed `0x48990`
pair and ends at `0x665f8`.  Each gates on the status bytes at `0x1db`/`0x1dc`
while advancing and aligning the phase cursor.

The parallel handlers at `0x66600` and `0x66840` use the packed `0x48980`
and `0x489a0` pairs, respectively, and end at `0x66830` and `0x66a70`.
The compact callback-returning handler at `0x66a80` uses `0x489c0` and ends
at `0x66b48`; all three perform the same terminal object initialization
protocol with variant-specific phase thresholds.

The compact controllers at `0x66b50`, `0x66c10`, and `0x66cc0` continue the
same protocol with the `0x489c8`, `0x48bd0`, and `0x48bd8` records; they end at
`0x66c0c`, `0x66cb8`, and `0x66d68`.  The larger phase controller at `0x66d70`
uses the packed `0x48bb0` pair and ends at `0x66f84`.

The indexed phase controllers at `0x66f90` and `0x672c0` use the `0x489d0`
and `0x48a00` record tables respectively.  Both publish paired cursor data,
apply status/phase gates, and perform terminal object-state transitions; their
boundaries are `0x672b8` and `0x675f8`.

The indexed family continues at `0x67600`, `0x67800`, and `0x67a30`, using
the `0x48a30`/`0x48a34`, `0x48a90`/`0x48a94`, and `0x48af4` record tables; their
boundaries are `0x677f4`, `0x67950`, and `0x67ba4`.  These handlers publish
paired cursor values and apply the same phase-limit and terminal-state
protocol as the preceding indexed controllers.

The packed-record controllers at `0x67c90`, `0x67e40`, and `0x68040` use the
`0x48b50`, `0x48b70`, and `0x48b90` pairs respectively.  They advance the
phase cursor, publish the active record pair, and handle terminal transitions;
their boundaries are `0x67e38`, `0x68034`, and `0x68228`.

The parallel geometry bounds evaluator at `0x68230` repeats the extent clamp,
object-offset, axis-flag, and derived-ratio sequence from `0x645a0`; it
returns through its saved callback at `0x68548`.  The `0x68500` arithmetic is
the final ratio tail within this function.

The later geometry layer links those state machines to video command output.
The phase/selection controller at `0x6d130` updates active object phase and
cursor fields through `0x6d38c`; `0x6d390` then serializes geometry state and
transform data to the `0x884000` FIFO, ending at `0x6dce0`.  The phase-state
controller at `0x6ddb0` advances selectors and mode-dependent counters before
returning at `0x6e0a4`.  Its companion writer at `0x6e0b0` emits structured
object coordinates, dimensions, and mode words to the same FIFO, ending at
`0x6e62c`.

The motion threshold service at `0x6e630` gates phase states 10 and 11,
selects the floating-point thresholds `0.4`, `0.55`, `0.9375`, or `1.0`,
updates motion state, and publishes the resulting value through
`0x804008`/`0x80400c`; it returns at `0x6e6e0`.

The motion math dispatch cluster follows at `0x6e6f0`, `0x6e7f0`,
`0x6e8f0`, `0x6e940`, and `0x6ea40`.  These floating-point dispatchers select
phase-dependent constants and return through supplied callbacks at
`0x6e7e4`, `0x6e8e4`, `0x6e93c`, `0x6ea34`, and `0x6eb34`.  The minimal bridge
at `0x6eb40–0x6eb54` completes the callback path.  Their repeated constant
selection and callback structure identifies them as motion math helpers,
while the exact higher-level operation remains unresolved.

The late callback table also points at instruction site `0x6ef70`, inside the
larger renderer beginning at `0x6efd0`.  This site emits the assembled
vertex/attribute packet to the `0x884000` FIFO; it is intentionally recorded
as an internal target, not as a separate function entry.

The complete renderer boundary is `0x6efd0–0x6efcc`.  It combines two object
vectors, converts them to fixed-point packet fields, emits the command
sequence to `0x884000`, and contains the `0x6ef70` callback-table target.

The parallel bounds evaluator at `0x68550` repeats the extent clamp,
object-offset, axis-flag, and derived-ratio sequence, returning through its
saved callback at `0x6876c`.  The separate phase/selection controller at
`0x68770` dispatches on state byte `0x1ae`, advances the object phase fields,
and returns at `0x68a3c`; its `0x687b0` and `0x687e8` blocks are internal arms
of that controller.

The next command/state family alternates FIFO writers and state dispatchers.
The packet writers at `0x68a40`, `0x69560`, and `0x6aa60` serialize geometry
data to `0x884000`, ending at `0x69040`, `0x69c54`, and `0x6ae78`.
The state-byte controllers at `0x69050`, `0x69c60`, `0x6a6a0`, and `0x6ae80`
dispatch on `0x1ae` and advance the object phase fields, ending at `0x69460`,
`0x69f20`, `0x6aa5c`, and `0x6b3c8`.

The larger controller at `0x69f30` handles match phase 27, updates object
status and transform fields, and performs terminal match-state transitions
before returning at `0x6a694`.

The following geometry bridge contains three independently referenced
services.  The transform/motion controller at `0x6b3d0` computes fixed-point
coordinates and phase-dependent offsets before emitting geometry commands to
`0x884000`, ending at `0x6c768`.  Its state-byte dispatch counterpart at
`0x6c770` routes through the `0x1ae` jump table and ends at `0x6cc1c`.
The packet writer at `0x6cc20` serializes object transform data and mode words
to the same FIFO, ending at `0x6d07c`.

`0x1bc20` converts asset words in bulk, swapping the two byte lanes of each
16-bit source word while preserving the masked layout for ROM-backed graphics
and data regions.

`0x1d1b0` walks a null-terminated string and routes each byte to the
control-aware character handler at `0x1ce00`; sibling walkers select alternate
character handlers for other text modes.

`0x1ce00` is the control-aware character tile writer. It clamps the character
code, indexes glyph data at `0x2ea10d0`, and writes the selected glyph words
into the active text plane using the current region state.

`0x1cea0` is the alternate character tile writer. It uses the same glyph
table and region state as `0x1ce00`, with the alternate plane/attribute layout
selected by the corresponding string walker.

`0x1d9e0` scans a NUL-terminated string for printable-range validity, then
renders it through the glyph core with the selected text mode.

`0x1da90` is the alternate printable-string renderer. It uses the same
printable-range validation as `0x1d9e0` but emits through the alternate text
mode used by the startup/device-status strings.

`0x1de80` copies a rectangular tile region into the active text plane at
`0x1004000`, setting the high attribute bit on each source word as it writes.

`0x1f010` updates the active UI text-region coordinates at
`0x504cdc–0x504ce4`, then copies a prepared tile rectangle or clears the
region through the text-plane helpers.

`0x20210` initializes fixed UI text assets: it resets the active region
coordinates, loads ROM-backed strings, and invokes the text-plane writers
before handing the region to `ui_text_region_update`.

`0x1f060` loads a fixed UI asset into the `0x1004000` text plane by selecting
the ROM source at `0x1fce520` and invoking `asset_tiled_row_copy`.

`0x1bc90` copies tiled graphics rows in bulk, invoking `memcpy_aligned` for
each row and advancing the destination by `0x80` between rows.

`0x2a990` submits a fixed geometry command packet through `0x884000`,
including caller-provided coordinate values, and copies returned words into
the caller's frame for subsequent service initialization.

`0xe2130` initializes startup status text: it checks board/device mode bytes,
selects the output mode, and expands fixed ROM strings into the tile planes.

`0xe37f0` copies two fixed startup/device tables from `0x578410/0x578460` to
`0x1d00144/0x1d00194` through `memcpy_aligned`.
