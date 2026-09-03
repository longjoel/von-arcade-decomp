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

The subsequent trace comparison adds six boundary labels. `0x2d9a0` routes
geometry transforms back through the profile uploader; `0x2e1c8` and
`0x2e1e8` are paired status-render routes; `0x27550` is a repeated geometry
record-transform service; `0x281f0` selects texture-profile entries through a
dispatch table; and `0x284b8` is the geometry command-window clear route.

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
| 1 | `0x02b9e0` | handler not yet bounded in this pass |
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

The second-level table at `0x2b960` is also bounded exactly. Its populated
entries are `0:0x2b500`, `1:0x2b7b0`, `2:0x2b7e0`, `3:0x2b810`,
`4:0x2b870`, `5:0x2dc50`, `6:0x2dd30`, `7:0x2ded0`, `8:0x2b550`,
`9:0x2b660`, `10:0xd24b0`, `11:0xd2560`, `12:0xd25b0`,
`13:0xe3ab0`, `14:0xe3d00`, `29:0x2b700`, `30:0x2b770`, and
`31:0x2b940`. Slots `15–28` contain zero pointers and follow the same
null-result fallback in the caller. The gaps are intentional/default service
slots, not undecoded instructions.

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
