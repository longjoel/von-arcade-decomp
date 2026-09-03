# i960 Boot-Path Notes

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
the geometry startup call at `0x189d4`.

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
`0x29b20` converts indexed records from ROM into the device window at
`0x1802010`; `0x29c08` clamps a command value into `0x51a260` and clears its
adjacent state fields; and `0x29ca0` copies 64-word rows between the two
device windows at `0x1810000` and `0x1810100`. These names are based on direct
loops and mapped-address use, while the device protocol remains unresolved.

### Geometry/service sieve pass

The next trace-confirmed entries extend the startup chain into geometry
service setup. `0x292d8` uploads caller-provided words through `0x804000`
after programming `0x800060`; `0x295d0` is a profile upload variant that
calls it and finishes through `0x28d30`; `0x296d0` initializes service pointer
slots at `0x515090–0x5150c0`; and `0x29738`/`0x29778` fill 64-entry pointer
tables using offsets `0x40` and `0x100`.

`0x29d50` transforms 32-bit buffer samples across mapped windows rooted at
`0x1810000`, `0x1810100`, `0x1814000`, and `0x1818000`. The trace also reaches
`0x2b430`, which indexes object records and dispatches either to `0x6fd50` or
an indirect table entry, and `0x2be30`, which initializes frame-service
counters and dispatches through the 12-entry table at `0x2bee4`.
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

The transform route at `0x2d9a0` is now bounded through its return at
`0x2dc40`. It emits the `0x884000` packet and stores derived frame values in
`0x51aad0–0x51aae4`; the following initializer begins at `0x2dc50`.

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
| `0x18a10` | classifies `0x01d00028`: exact `0xff` selects state `2`, masked value `1` selects state `1`, and all other values select state `3`; state byte is written to `0x005770b1` and the flag to `0x503a08`; then calls `0xc5870` and accepts only a zero result or `0x5039f4 == 5` on the guarded path |
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

Each iteration at `0x187e4` services timing and input, masks the controller
word at `0x502484` with `0xfffb`, and calls the warning/text service. The
current mode in `0x5039f4` is reduced to its low nibble and used to load an
indirect target from `0x18680`; a zero target repairs the mode to `1`. The
target is called with `callx`, so the table entries—not the dispatcher—are
the next control-flow boundary to recover.

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
| 0 | `0x003c40` | renders/advances the startup text or status phase and updates `0x503a04` |
| 1 | `0x02b9e0` | status/service dispatcher with mode-2 device tail and 32-entry subtable |
| 2 | `0x018650` | writes a text/video command, clears the service counter, and increments the mode |
| 3 | `0x0190d0` | initializes a startup phase, clears phase state, and increments the mode |
| 4 | `0x019180` | submits setup words through `0x884000` and advances startup state |
| 5 | `0x0f3f00` | sets the startup flag, clears the video/device state, initializes counters, and advances the mode |
| 6 | `0x0f3fe0` | services the startup counter and selects a sub-handler from its own table |
| 7 | `0x0f3d30` | initializes the text/video phase and selects one of the startup messages |
| 8 | `0x018620` | clears `0x5039f4`/`0x503a00` and returns through the video byte writer |
| 9–14 | `0` | null entry; the dispatcher repairs the mode to `1` before `callx` |
| 15 | `0x018620` | same handler as slot 8 |

The attract trace’s slot-9 observation is therefore useful: it does not
identify a missing handler; it proves the null-entry recovery branch at
`0x1881c–0x1883c`, after which the next iteration runs slot 1. Slots 0, 5,
and 8 are now explicitly seeded as indirect-call targets in the annotation
script. Their higher-level UI meanings remain intentionally unresolved.

The handler-7 body at `0xf3d30` initializes the text/video phase, selects
startup messages, and advances or resets `0x503a00`; it returns before the
diagnostic target table at `0xf3ec0`. Handler 6 at `0xf3fe0` services the
counter, selects from that table, mirrors input state into the runtime buffer,
and returns at `0xf4138`.

Slot 1 (`0x2b9e0`) is a real status/service dispatcher. It first checks the
hardware mode byte at `0x503a08` and controller/status bytes at
`0x1d00034`, `0x5023f2`, and `0x1d00038`. One guarded path loads `29` into
`0x503a00`; the normal path emits byte `16` to `0x5032f4`. It then masks the
counter to five bits and dispatches through the 32-entry table at `0x2b960`.
A null table result normally advances the counter to `1`, except for the
special mode-2 handler at `0xe3ab0`.

The mode-2 tail scans device/status data relative to `0x1a14002`, writes a
selected byte into `0x5024f0`, and decrements through candidate entries until
the `0xffff`-masked test succeeds. The non-mode-2 tail calls the timing/status
helper at `0x3ba0`; when it returns zero, it resets the service counter,
advances `0x5039f4`, and returns. This bounds slot 1 as a state/service
dispatcher; it does not assign the meaning of the individual 32 sub-handlers.
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
three raw float-bit words to `0x512bd4`, `0x512bd8`, and `0x512bdc`. It has nine
indexed profiles (index is backup byte minus one) and a default path for zero
or an index at/above `9`; the default words are `0x3f0ccccd`, `0x3f59999a`,
and `0x3e19999a`. The profile initializer at `0xc8fa0` skips setup only for
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
zero, uses digit table `0x2ea1e50` with four-byte entries, and has an early
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

The nine indexed profile triples at `0x28840` are, in order: (`0x3f000000`,
`0x3f4ccccd`, `0x3e4ccccd`), (`0x3ee66666`, `0x3f400000`, `0x3e800000`),
(`0x3ee66666`, `0x3f266666`, `0x3eb33333`), (`0x3eb33333`, `0x3f0ccccd`,
`0x3ee66666`), (`0x3eb33333`, `0x3ee66666`, `0x3f0ccccd`), (`0x3f800000`,
`0x3f59999a`, `0x00000000`), (`0x3f733333`, `0x3f59999a`, `0x00000000`),
(`0x3f59999a`, `0x3f59999a`, `0x3d4ccccd`), and (`0x3f400000`,
`0x3f59999a`, `0x3dcccccd`). These remain raw IEEE-754 bit patterns.

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
model:

| Entry | Directly observed values |
| --- | --- |
| `0x9b288` | selects a 16-byte record at `0x562b80 + ((0x562b70 & 0xf) * 16)`, writes byte `1` at offset `0`, byte `0` at offset `1`, and copies caller fields into offsets `2`, `4`, `8`, and `0xc`; the rolling index is incremented and stored back at `0x562b70` |
| `0x9b320` | scans records from `0x562b80`, tests the low byte against zero using mask `0xff`, and emits selectors `5`, `18`, and `21` to `0x884000`; the halfword at offset `1` is widened from 16 bits before emission |
| `0x9b498` | clears the 16 record slots at `0x562b80` using offsets `0xf0` down to `0` in `0x10`-byte steps, then resets `0x562b70` to zero |

The table size and record layout above are structural facts from the address
arithmetic; the command meanings are not inferred.

### Object dispatch and lookup constants

The object-management slices around `0xbd5a8`–`0xbf2f0` expose these further
values:

| Entry | Directly observed values |
| --- | --- |
| `0xbd5a8` | copies `9` words from `0x13da68` to `0x565e30`, then copies `0x99b` words from `0x13b3f8` to `0x562cb0` |
| `0xbd6b8` | clears 32 entries at object offset `0x200` using a `0x20`-byte stride, and clears one of `0x576ba0` or `0x576ba4` based on the caller value, always clearing `0x576ba8` |
| `0xbd730`/`0xbd810` | inspect object bytes at offset `0x200` with mask `0xff`, reject values above `0xcc`, and dispatch through `0xbcf40[index * 8]`; the associated table lookup masks with `0xffe0` |
| `0xbedf0`/`0xbeee0`/`0xbefd0` | classify the halfword at offset `0x172` for exact/range values `24`, `14`, and `31`, then select one of paired tables at `0xbcc74/0xbcc7c`, `0xbcd64/0xbcd6c`, or `0xbce54/0xbce5c` using field `0x64` scaled by `8` |
| `0xbf2f0` | gates on `0x503a08 == 2`, compares object byte `0` and halfword `0x4` against table `0xc4f40[index * 8]` and its predecessor, then emits selectors `5`, `16`, and `18` |

The table bases, scales, and branch constants are explicit; the object-state
interpretation is intentionally left open.

### Geometry lookup and raster constants

The helpers around `0x8d400` and `0x8d5d0` use the same bounded index
calculation: a signed halfword from object offset `0x4` is clamped against a
caller-supplied bound, the halfword at offset `0x6` supplies the row scale,
and the resulting record is selected from the caller base. The first path
emits selector `5`; the second emits selector `20` and stores the signed
negated lookup value. Both use mask `0xffff` after widening the halfwords.

The associated conditional writers at `0x8dd40`/`0x8dfc0` use object offsets
`0x4`, `0x6`, and `0x24c`, test byte/halfword masks `0xff` and `0xffff`, and
also emit selector `20`. These are direct operand facts; the lookup table’s
semantic units are not established.

The table builder at `0x866c0` clears a 20-byte record prefix at offsets
`0x0` through `0x12` in 2-byte steps, rooted at `0x5050a0`, and advances its
source index by `20` bytes per record while storing the current record pointer
at `0x5074a0`. The updater at `0x881b8` reduces `0x51c9b0` modulo `15*8`,
scales the resulting table value by `6`, and stores two caller words at output
offsets `4` and `8` relative to `0x561e90`.

### Video/status asset constants

The later video/status helpers expose these additional exact values:

| Entry | Directly observed values |
| --- | --- |
| `0xde670` | initializes status fields at `0x504b90`, `0x504b94`, `0x504ba8`, `0x504bae`, `0x504baa`, `0x504bac`, and `0x504bb0`; the fixed float constant stored later is `0x41d00000` |
| `0xde990` | clears `0x503c9c`/`0x503c98` and, on the `0x503b00 == 4` / `0x504100 == 1` route, also clears `0x50429c`/`0x504298`; another branch checks `0x504134 == 9` |
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
| `0x7d1f0` | scans byte pairs at `0x504da0 + 0x9a/0x9b` and then `+0x98/0x99`, masks each byte with `0xff`, and compares the masked value against a neighboring field with an allowed increment of `5` |
| `0x7d670` | gates on `0x504d9c != 4`, accepts the shifted `0x172` field only in `0x150000..0x190000`, then checks `0x504d68` against `4` |
| `0x7dcc0` | returns unless `0x509b34 > 0x1f3`; accepted processing uses float `0xbf800000`, object offsets `0x200`/`0x218`, byte mask `0xff`, and halfword mask `0xffff` |
| `0x7e390` | indexes object bytes from offset `0x200` with a `32`-byte stride, looks up records from `0x562cb0` using a `48`-byte stride, and uses float constants `0x40c00000`, `0x42f00000`, and branch-specific `0x3ff80000`; the visible branch distinguishes caller field values below/at `3`, emits selector `29`, masks with `0xffff`, and its later route emits selector `30` after loading record offsets `0x10` and `0x18` and using offset/base constant `0xffffa000` |
| `0x7ea10` | requires `0x509b30 > 0x1f3`, object halfword `0x172 == 31`, both object fields `0x64 == 6`, and `0x504e48 == 3` before storing `3`, `0x64`, `1` into `0x504d9c`, `0x504da0`, and `0x504d94` |

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
| `0x81f60` | uses state case `6`, float `0x404e0000`, and chooses output states `2` or `3` |
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
| `0x3540` | updates the packed state at `0x5023e4` according to bit 3 of `0x502482` |
| `0x3a38` | parses one byte, handles zero/underflow cases, and clears a selected bit in `0x502484` |
| `0x3ae0` | applies the byte parser to the two state bytes at `0x5024cc` and `0x5024d0` |
| `0x3ba0` | compares controller timing/status registers at `0x1d0002c`, `0x1d00034`, and `0x1d00038` |
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
groups into the output plane layout; it is used by the text-table builders.

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
the state-0/1/2/3/4 handlers, and returns from each selected call path.

The transition gateway at `0xe5da0` reduces the service timer modulo `0x870`
and handles the early transition values before joining its common continuation
at `0xe60d0`; its visible return is at `0xe61bc`. The parallel gateway at
`0xe61c0` performs the corresponding alternate rendering path and joins at
`0xe6410`, returning at `0xe64fc`.

The profile renderer entry at `0xe6500` bounds its selector to eight cases and
dispatches through the local table at `0xe651c`. The selected arms join the
profile rendering loop at `0xe6578`, which emits the geometry/status fields and
returns at `0xe6640`; `0xe6648`–`0xe665c` are literal fallback dot strings.
The larger frame builder at `0xe6660` constructs the 8-by-13 status grid,
renders the active columns through `0xe6500`, updates the video-state words,
and returns at `0xe6d3c`.

The short helper at `0xe6d40` copies 0x200 16-bit words from the caller's
source to destination, preserving the caller's continuation in `g2`; its
indirect branch is at `0xe6d74` and its local return stub is at `0xe6d78`.

The four adjacent emitters at `0xe6d80`, `0xe6ef0`, `0xe7060`, and `0xe71d0`
share a fixed-point conversion pattern: they quantize the phase in
`0x5783d8`, form the paired coordinates, and emit the geometry command words
through `0x884000`. Their returns are at `0xe6ee8`, `0xe7054`, `0xe71c4`,
and `0xe7330` respectively. The small dispatcher at `0xe7340` selects among
these four variants from `0x5783dc` and returns after the selected call.

The object-packet dispatcher at `0xe7390` consumes the active object fields
at `0x5784e0`, selects the status/geometry mode, and emits the coordinate and
scale words through `0x884000`. Its alternate branches at `0xe7560` and
`0xe76d0` remain part of the same frame and choose either direct packet
submission or the queued `0x804000` path. All paths restore the saved context
and return at `0xe79e0`.

The caller-facing scene service at `0xe79f0` renders the active status scene
from the record bytes at `0x5783c0`/`0x5784e4`, repeatedly invoking the object
packet dispatcher above for the scene's geometry groups. It uses the mode word
at `0x5783c4` and the six-entry arm table at `0xe8920` for the final scene
variant; the complete service returns at `0xe9138`. The next entry at
`0xe9140` begins a separate command/setup path.

That separate path is the runtime event dispatcher at `0xe9140`. It updates
the rolling event fields at `0x5783e4–0x578400`, derives pairwise geometry
deltas from the active records, and selects the next event arm using
`0x5783fc % 12` and the table at `0xe91f0`. The arm targets are distributed
through the later `0xea...` region, but converge through the shared finalizer
at `0xea9a0` and return at `0xeaa50`; `0xeaa60` begins the next separate
command/setup entry. This bounds the complete dispatcher at `0xe9140–0xeaa54`.

The helper at `0xeaa60` is called by both status-preparation paths. It emits
the event setup packet, derives the shared fields at `0x5783e4–0x5783f8`,
resets the event counters when required, and returns at `0xead1c`.
`0xead20` begins its literal geometry-event lookup data.

The following compact helpers are now separated by their visible return
stubs: `0xeada0`, `0xeade0`, and `0xeae20` are feature-flag gates that return
boolean results through caller continuations; `0xeae60` copies a byte span;
and `0xeaeb0`, `0xeaed0`, and `0xeaf20` wrap the shared numeric/text rendering
helpers, including the board-specific adjustment path.

The literal block at `0xeaf40–0xeb054` contains the diagnostic menu labels
(`TEST MENU`, memory/input/output/sound tests, assignment and backup prompts).
The renderer at `0xeb060` lays those strings into the status tile plane and
updates the selected-menu marker, returning through either `0xeb19c` or
`0xeb1b4`.

The runtime-table helpers following it are now bounded individually:
`0xeb1c0` scans packed records and stores matching pointers at
`0x578548–0x578550`; `0xeb2c0` initializes and rebuilds that workspace;
`0xeb3b0` selects the active base address from the match markers; and
`0xeb450` performs the alternate-table scan. The reset/copy helper at
`0xeb510` restores the table defaults and copies the selected words into the
active workspace, returning at `0xeb5a8`.

The ROM-bank loaders at `0xeb5b0`, `0xeb600`, `0xeb650`, `0xeb6a0`,
`0xeb6f0`, `0xeb740`, `0xeb790`, and `0xeb7e0` select banks at
`0x5e0000`, `0x5c0000`, `0x5a0000`, `0x580000`, `0x560000`, `0x540000`,
`0x520000`, and `0x502000` respectively. Each copies the packed words into
the active table and invokes the reset/copy helper. The orchestrator at
`0xeb830` runs the bank sequence and normalizes the match markers. The
scanner at `0xeb8a0` then copies the packed records and records four masked
match locations at `0x578560–0x57856c`.

The parallel packed-record family begins at `0xebba0` and repeats the
scan/init pattern for additional ROM layouts.
The bounded entries through `0xec1e0` use the alternate workspace slots at
`0x578570`, `0x578574`, `0x578578`, `0x57857c`, `0x578580`, `0x578584`,
`0x578588`, and `0x578590`; each initializer selects a different packed-ROM
base before invoking its scanner. This establishes a second data-family
pipeline without conflating its record widths with the first family.

The continuation through `0xec8e4` extends that alternate pipeline: the
initializers/scanners at `0xec290`, `0xec330`, `0xec3e0`, `0xec6a0`, and
`0xec760` cover additional packed layouts; `0xec480` selects the matching
ROM base; and `0xec630` copies the selected table. The builder at `0xec820`
expands the literal records from `0xead20` into the command lookup table, and
`0xec8f0` orchestrates the pipeline before returning at `0xec91c`.

The following event helpers are bounded individually. `0xec920` advances the
service counter, `0xec940` sets the event-mode flag, and `0xec970`/`0xec9d0`
accumulate packed-record bytes using their distinct stride patterns. The six
publishers from `0xeca30` through `0xecb20` store the derived event results in
the separate `0x578530–0x578544` workspace fields. The literal handler table
at `0xecb50` follows these wrappers.

The table is followed by diagnostic formatting support: `0xecbb8–0xecd78`
holds the result format, GOOD/BAD text, and IC-number labels; `0xecbe0` and
`0xecc40` are the basic and expected-value comparison formatters. The result
menu renderer at `0xecd80` lays out the IC results and accumulated status
values, returning at `0xed0c4`.

The workspace reset at `0xed0d0` clears the primary and alternate
match/result slots before returning through its continuation at `0xed1cc`.
The following `0xed1e0–0xed218` block is literal test-button and wait-prompt
text. The service at `0xed220` initializes the diagnostic result state,
renders through `0xecd80`, then dispatches the next handler via `0xecb50` and
returns at `0xed2e0`; its fallback path begins at `0xed2e4` and returns at
`0xed300`.

The input-test service at `0xed320` handles the input-state transition and
returns at `0xed438`. Its literal status rows at `0xed440–0xed5b4` cover
direction, shot, dash, start, coin-chute, service, and test-button states.
The renderer at `0xed5c0` lays those rows into the tile plane, checks the
input/status flags, and returns at `0xed968`.

The next diagnostic block, `0xed970–0xeda28`, contains the Versus City
billboard and winner-lamp/7-segment/start-lamp labels. The renderer at
`0xeda30` advances its test state, emits the corresponding lamp and segment
patterns through the shared test-pattern helper, and returns at `0xedcf8`.
The following data is diagnostic naming metadata: indexed `SDE_*` event-name
records begin at `0xedd20`, while the `SDB_*` record family begins at
`0xeff60`. Their indexed prefix and terminated ASCII names should be treated
as lookup data rather than i960 instructions.

The CRT/test-pattern service at `0xf04d0` initializes the diagnostic state,
renders the CRT labels, and cycles indexed pattern data through its six-entry
arm table at `0xf0674`; its arm returns finish at `0xf0884`. The separate
buffer filler at `0xf08c0` writes the indexed bit-plane layout and returns at
`0xf0938`.

The match/time diagnostic at `0xf0980` renders play-time, match/death-match,
pending/start-state, and network-link fields, builds the associated test
structures, and returns at `0xf0b38`.

The coin/credit diagnostic entry at `0xf1c90` advances its indexed display
pattern and returns at `0xf1d40`. Its formatter helper at `0xf1db0` computes
and prints credit arithmetic through `0xf1ebc`; the coin-chute status renderer
at `0xf1f20` reads the live coin/status bytes and returns at `0xf20a4`.

The bookkeeping service at `0xf2e20` maintains three diagnostic state fields,
selects from the paired handler tables at `0xf2de0` and `0xf2e00`, and calls
the active accounting sub-handler before returning at `0xf2ee4`. The nearby
format strings identify this family as bookkeeping, coin-chute, credit, and
game-time reporting.

The paired tables dispatch nine bounded arms: record validation at `0xf2940`,
credit/coin updates at `0xf2a60–0xf2bc0`, input-byte updates at `0xf2c20` and
`0xf2c90`, and coin-chute counter updates at `0xf2d00` and `0xf2d70`. Each arm
returns before the next table/data boundary, making these indirect paths
available for per-state tracing.

Two shared renderers feed those arms: `0xf2170` formats coin-chute type and
credit/manual settings through its return at `0xf22e0`, while `0xf2770`
formats the live coin/input matrix and multipliers through its return at
`0xf2930`.

The shared coin-configuration decoder at `0xf19e8` derives the live input and
coin fields from the selected configuration and returns through its caller
continuation at `0xf1aa4`. The arithmetic helper at `0xf23e0` then builds a
nine-entry coin/credit matrix using those bytes, returning at `0xf264c`.

The adjacent site/status probe at `0xf1ac0` reads the two hardware status
windows, stores the resulting site byte at `0x1d00028`, and returns at
`0xf1bb8`; its fallback arm at `0xf1bc0` returns at `0xf1bdc`. The paired
target/index records at `0xf1be0` feed the coin diagnostic’s indexed display
dispatch.

That table’s remaining 18 arms are now bounded individually: five
configuration toggles cover `0x1d00016–0x1a`, and the subsequent arms update
the diagnostic fields at `0x1d0001b–0x1f`, `0x1d00020–0x24`, `0x1d00026–0x28`,
and `0x1d00027`. Their short returns make each selector/index pair directly
traceable in Ghidra.

The statistics renderer at `0xf33a0` reads the `0x1d00040–0x1d000a0`
accounting fields and formats game-time/bookkeeping results, returning at
`0xf3a64`. The EEPROM confirmation service at `0xf3ab0` displays the clear /
cancel choices and completion state, with a return at `0xf3c0c`. The compact
test-mode exit/reset handler at `0xf3c50` clears the test video/input state and
returns at `0xf3c9c`.

`0x6fec0` initializes a geometry-device command path: it validates the
selector, programs `0x800030`, and emits the associated fixed packet through
the `0x804000` command window.

`0x27d8` is a small indirect-return trampoline used by the nearby byte-copy
loops; it restores the local continuation at `0x27e4` and branches through it.

`0x73508` classifies a signed 16-bit geometry difference into six bounded
ranges (`0–5`), which callers use to select profile/table entries.

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
