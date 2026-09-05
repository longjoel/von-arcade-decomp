# i960 Disassembly Annotations

> **Working notebook:** labels and bounded interpretations here guide analysis
> but are not validation by themselves. Current promotion rules and evidence
> requirements live in the
> [reconstruction handbook](../docs/reconstruction.md) and
> [evidence plan](../docs/evidence-and-assets-plan.md).

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

The adjacent helper at `0x0001ccf8` is a narrow tile/control bus wrapper. It
writes its 32-bit argument unchanged to `0x01800000` and returns through the
i960 link register. `recovered_text_write_tile_control()` preserves that write
without assigning a higher-level register name; its pure bus description is
checked across all 65,536 low-word input values by
`von/tools/test_recovered_text_control.py`.

The related initializer at `0x0001c618` resets six halfword fields at
`0x00504d24..0x00504d2e`, stores the tile-clear count `0x4000` at
`0x00504d32`, clears the words at `0x00504d34` and `0x00504d38`, and then
zeros four video-memory ranges:

```text
0x01000000: 0x4000 halfwords
0x0100c000: 0x1000 halfwords
0x01008000: 0x0800 halfwords
0x0100a000: 8 halfwords
```

`recovered_text_video_initialize()` preserves this bounded clear plan. Its
state and region descriptors are checked by
`von/tools/test_recovered_text_video.py`; the hardware-clearing wrapper remains
available for the future caller integration pass.

The shared video helper at `0x0001bc90-0x0001bcd0` performs one forward copy
for each requested row. Each call advances its source pointer by `0x80` bytes
and its destination pointer by `halfwords * 2` bytes while copying that byte
count. `recovered_text_video_copy_rows()` preserves this schedule.

The preceding `0x0001bb90-0x0001bc20` converter consumes `blocks * 16`
halfwords. It expands source bits `0..3`, `4..7`, `8..11`, and bits `12..14`
into a packed output halfword while dropping bit 15. The exact transform is
implemented by `recovered_word_expand_blocks()` and exhaustively checked over
all 65,536 source values.

The adjacent `0x0001bc20-0x0001bc90` loop copies a caller-selected number of
halfwords with each source halfword's bytes reversed. The concrete
`recovered_halfword_byte_swap_copy()` implementation and all 65,536 possible
halfword swaps are host-tested.

Its larger caller at `0x0001bda0-0x0001c21c` is now partially named as the
startup asset loader. It selects profile zero only for a zero argument;
nonzero arguments select the alternate profile. The recovered transfer plan
exposes all mapped-memory operations without issuing them: profile zero has
six block-expansion records and three bulk byte-swap records, while the
alternate profile has four and two. Both then share six further byte-swapped
regions, a 16-halfword `0x9999` fill, and four one-block expansions. This
identifies a concrete ROM-to-video-RAM layout and the profile-dependent asset
windows, but does not yet assign resource names or execute the hardware writes.
`recovered_text_startup_asset_transfer_plan()` is checked against all 37
records (20 zero-profile and 17 alternate-profile operations).

The adjacent `0x0001c220-0x0001c2b4` video-control bootstrap now has an
instruction-level plan as well. It writes the `0x1c2c0` helper entry to
`0x00504d20`, programs `0xffac` and `0xfffe` into the two control windows,
prepares the fixed `0x1c730` request (`0x02ea0bb8` to `0x01080000`, flag
`0x80`, count one), then invokes the existing clear routine at `0x1c618`.
The ten direct writes retain the original caller-supplied `g14` value rather
than assuming it is zero; the last write stores the explicit `0xffffffff`
sentinel. Both the request and all write records are host-tested.

The helper reached by that bootstrap at `0x0001c730-0x0001c7d0` expands each
input byte into two four-pixel, four-bit lane groups. Its mode argument is
masked to four bits; each set input bit selects that mode value in one output
nibble. The high source nibble occupies output bits `0..15`, the low source
nibble output bits `16..31`. The helper processes eight bytes/words per block.
`recovered_text_expand_video_byte()` and
`recovered_text_expand_video_blocks()` preserve that conversion and are tested
over every source byte and mode value; mapped-RAM execution remains separate.

The `0x00020180` caller supplies a fixed upload request: source `0x01004000`,
destination pointer slot `0x02fd61d0`, `0x40` halfwords per row, and `0x40`
rows. `recovered_text_video_upload()` now executes that exact handoff through
the shared row-copy loop.

The adjacent `0x20160` block is a clear-`g14` indirect-return thunk targeting
the single `ret` at `0x20174`; its contract is captured in
`recovered_clear_g14_return_20160.c`.

The `0x201a0` upload selects one of three destination planes while keeping
source `0x01004000`, `0x40` halfwords per row, and `g17+31` rows. Profiles
`0`, `1`, and all other values select destinations `0x1fcfd20`, `0x1fd49d0`,
and `0x1fd1520`, respectively; the wrapper also preserves incoming `g14`
when it initializes the text-origin globals. The plan is in
`recovered_video_profile_upload.c`.

The compact `0x20300` writer stores two halfwords directly into mapped video
RAM. It computes a byte offset of `14*g1`, ORs both source words with
`0xc000`, and selects source pairs `0x2fe3214/16` or `0x2fe3218/1a` with
destination pairs `0x1001288/8a` or `0x1001290/92` based on `g0`. It returns
through stub `0x2038c` after clearing `g14`; the write plan is in
`recovered_attribute_pair_writer.c`.

The `0x20390` wrapper uploads source `0x01004000` to destination `0x1fccd20`
with `0x40` halfwords per row and `g17+31` rows through `0x1bc90`. Its
neighbor `0x203b0` transfers source `0x2fe0864` through `0x1dc90` at the
current origin as `31×5`. Both plans are in
`recovered_video_upload_20390_panel17.c`.

The wrappers at `0x203d0`, `0x20400`, and `0x20430` each upload the fixed
source plane through `0x1bc90` to the profile-0, profile-1, or profile-2
destination, restore their incoming selector into `g0`, and call `0x1fff0`.
That panel then uses origin `(11,21)`, width `g9+31`, and height `8`; the
combined wrapper contract is in `recovered_profile_upload_panel_wrappers.c`.

The `0x20460` wrapper uploads source `0x01004000` to `0x1fd89d0` with
`0x40` halfwords per row and `g17+31` rows through `0x1bc90`. Its following
`0x20480` route advances the current column by `4`, then transfers
`0x2fcf468` as `8×4` through `0x1dc10` when `g0` is nonzero, or clears the
same region through `0x1df00` otherwise. Both are captured in
`recovered_upload_20460_panel18.c`.

The repeated routes at `0x204d0`, `0x20520`, `0x20570`, `0x205c0`, and
`0x20610` all advance the current column before selecting a source-or-clear
operation. `0x204d0` uses source `0x2fcf2c8`, advance `4`, and width `8`;
the remaining four use sources `0x2fcf528`, `0x2fcf828`, `0x2fcf628`, and
`0x2fcf928`, advance `2`, and width `12`. Every route uses height `4` and
dispatches to `0x1dc10` or `0x1df00`. The shared plan is in
`recovered_repeated_status_routes.c`.

The next status blocks at `0x20660`, `0x20690`, and `0x206c0` preserve the
current origin, use height `4`, and select source blocks `0x2fcf9e4`,
`0x2fcf308`, and `0x2fcf388` for nonzero `g0`. Their widths are `16`, `16`,
and `28`; zero `g0` takes the matching `0x1df00` clear with the same width.
The grouped contract is in `recovered_status_block_routes_20660.c`.

The following six helpers at `0x206f0`–`0x207d8` keep the current origin and
clear or transfer four rows. Their source blocks are
`0x2fcf4a8`, `0x2fcf7a8`, `0x2fcf688`, `0x2fcf588`, `0x2fcf888`, and
`0x2fcf708`; the first three are width `16`, and the last three width `20`.
Nonzero `g0` uses `0x1dc10`, while zero `g0` uses `0x1df00`. The grouped
plan is in `recovered_status_block_routes_206f0.c`.

The transition at `0x207e0` uses source `0x2fcf708` through plain helper
`0x1dc10` as `20×4`; `0x20810` switches to attributed helper `0x1dc90`
with source `0x2fcf988` as `23×2`. Both retain current-origin source-or-clear
behavior. Their shared plan is in `recovered_status_transition_routes.c`.

The attributed routes at `0x20840`–`0x209b8` retain the current origin and
select source blocks `0x2fcfa64`, `0x2fcfbe4`, `0x2fcfdd4`, `0x2fd0014`,
`0x2fd0124`, `0x2fd02e4`, `0x2fd0464`, and `0x2fd0634`. Their widths are
`24`, `31`, `g5+31`, `g3+31`, `28`, `24`, `29`, and `29`; the fourth route is
`4` rows and the others are `8` rows. Nonzero source uses `0x1dc90`, while
zero source uses `0x1df00`. The grouped plan is in
`recovered_attributed_status_routes_20840.c`.

The next two attributed routes at `0x209c0`–`0x20a18` use sources
`0x2fd09a4` and `0x2fd07f4`, widths `28` and `27`, and height `8`. They also
retain the current origin, using `0x1dc90` for a present source and `0x1df00`
for the clear path. Their descriptor is in
`recovered_attributed_status_routes_209c0.c`.

The helper at `0x20a20` builds a centered strip in plane `0x0100c000` at
row `g6` (`base + (row << 6)`). It computes `amount = min(g0*g2, g1)`,
then emits three-cell patterns for `(g1-amount)>>1`, `amount`, and the same
trailing remainder. The outer segments repeat `g14`; the middle segment
repeats the supplied `g3/g4/g5` values. The arithmetic and segment contract
are captured in `recovered_text_strip_builder.c`.

The sibling at `0x20ae0` clears/fills the fixed hardware strip beginning at
`0x0100d000` for `0x5ff` halfwords. A nonzero mode writes `0xffff`; zero mode
writes `0`. It returns through the local `0x20b48` stub and leaves the fill
register at zero. The route is represented by
`recovered_hardware_strip_clear.c`.

The table at `0x20b50` contains ten `0x68`-byte weapon/status records. The
record selector at `0x211f0` computes `base + selector*0x68`, reads the asset
pointer at offset `0`, and dispatches selectors `0`–`7` to handlers
`0x21240`, `0x21314`, `0x214bc`, `0x21784`, `0x213e8`, `0x216a0`,
`0x21674`, and `0x21580`. Selectors `8`, `9`, and out-of-range values use the
fallback at `0x218a0`. The ten asset pointers and selector behavior are
captured in `recovered_weapon_record_dispatch.c`.

Handlers `0x21240`, `0x21314`, and `0x213e8` share a three-point geometry
path. They render the selected asset at text origin `(3,8)` with width `31`
and height `selector+31`, using `0x1dd80`/plane `0x01002000` for zero mode or
`0x1dc10`/plane `0x01000000` otherwise. Record words at `0x34/0x38`,
`0x3c/0x40`, and `0x44/0x48` form `(x,y)` pairs; each writes marker `0x2674`
through table offsets `0x114`, `0x118`, and `0x110`, respectively. The shared
address plan is in `recovered_weapon_three_point_handlers.c`.

Handler `0x214bc` is the one-point variant: it renders at `(1,8)` with the
same width and selector-relative height, then reads the record pair at
`+0x44/+0x48` and writes five consecutive marker halfwords (`0x2674`) through
table offset `0x114`. Its route plan is in
`recovered_weapon_five_marker_handler.c`.

Handler `0x21784` is the three-quad variant. It renders at `(2,8)` and then
starts three four-marker runs at the record-derived pairs
`(+0x34,+0x38)`, `(+0x3c,+0x40)`, and `(+0x44,+0x48)`. Each run stores four
consecutive `0x2674` halfwords through table offset `0x110`. The address plan
is in `recovered_weapon_three_quad_marker_handler.c`.

Handler `0x21580` is the irregular three-run case: it uses text origin
`(3,8)`, then starts marker runs of `2`, `4`, and `4` cells at the three
record coordinate pairs through table offset `0x114`. Handler `0x21674`
shares the same text prologue but immediately selects the mode-dependent text
writer and emits no markers. Both contracts are in
`recovered_weapon_irregular_handlers.c`.

The entry path at `0x218f0` saves the shared text/FP frame and forces the
fill value to zero. When the status latch at `0x504d10` is nonnegative, it
also writes marker value `0x8000` to `0x504d2c`, `0x504d30`, `0x504d2e`, and
`0x504d32`, then clears `0x01800000`. The isolated entry/reset contract is in
`recovered_status_loop_entry_reset.c`; the later status branches remain
state-dependent.

The low-latch branch at `0x2196c` handles latch values through `8`: it loads
source `0x02fe8fc4`, sets the text origin to column `0` and row `latch-8`,
and calls attributed block helper `0x1de80` with width `0x40` and height `8`.
The route preserves the i960 unsigned wraparound for rows below `8`; its
descriptor is in `recovered_status_low_latch_upload.c`.

The mid-latch branch at `0x219a8` handles latches `9`–`20`. It masks the
first generator result to `0x1ff`, adds it modulo `0x200` to state
`0x504d28`, stores the second masked result at `0x504d30`, and renders source
`0x02feab34` through `0x1de00` as `64×4` at `(column=0,row=4*latch-36)`.
Latch `9` then takes the existing special handoff at `0x21f1c`; the route
plan is in `recovered_status_mid_latch_route.c`.

The upper branch at `0x21a1c` handles latches `21`–`95` with the same masked
`0x1ff` state updates, but renders source `0x02fda1d0` through plain helper
`0x1dc10` as `64×4` at row `4*latch-84`, column `0`. Values above `95` skip
rendering and clear, in order, `0x504d24`, `0x504d2c`, `0x504d28`,
`0x504d30`, `0x504d26`, `0x504d2e`, `0x504d2a`, and `0x504d32`. The route
plan is in `recovered_status_upper_latch_routes.c`.

The initializer at `0x227b0` selects its grid path when phase
`0x005024e8 % 192 == 0`. It then visits 32 origins in row-major order:
columns `0,16,32,48` and rows `0,8,16,24,32,40,48,56`. Each origin receives
the same `16×8` asset `0x02fe8fc4`, first through `0x1de80` and then through
`0x1de00`. The pure grid plan is in
`recovered_status_grid_initializer.c`.

The alternate branch at `0x22840` fills the hardware strip when the phase is
not divisible by `192` and the current row is at most `1`. It starts at
`0x0100d000 + row*2` and repeats `[fill,fill,fill,fill,0xffff,0xffff,0xffff,0xffff]`
for `192` groups. The shared tail at `0x228b0` then updates `0x504d28` with
the generator result plus its old value modulo `0x200`, and updates `0x504d2a`
with generator-minus-old-value modulo `0x200`. The plan is in
`recovered_status_patterned_fill.c`.

The tile-pattern writer at `0x228f0` emits a `16×7` block at the current
column and row in plane `0x01000000`. It writes 112 sequential values
`0xc000 | (0x1488 + index)`, advances the row modulo `64` after each 16-tile
row, and keeps the column fixed. Its pure address/value plan is in
`recovered_status_tile_pattern_228f0.c`.

The following writers at `0x22970` and `0x229e0` emit sequential two-row
patterns at the current origin. The first is `23×2`, starts from source index
`0x3db0`, and uses base `0x01000000`; the second is `29×2`, starts from
`0x3d10`, and uses base `0x01000034`. Both store `0xc000 | (source_index+i)`
with row-major 64-tile addressing. Their shared plan is in
`recovered_status_wide_tile_patterns.c`.

The duplicate family at `0x22b90` repeats the `23×2`, base-`0x01000000`,
`0x3db0` pattern. Its companion at `0x22bfc` emits a `19×2` pattern from
`0x3f40` using base `0x01000034`; both retain the `0xc000` attribute and
current-origin row stride. The shared model covers these variants as well.

The indirect-return thunks at `0x22c70` and `0x22cb0` clear the two tile
planes at `0x01000000` and `0x01004000`, respectively. Each pre-decrements a
`0x1000` bound and therefore stores zero to `0xfff` halfwords, then returns
through its local stub (`0x22ca4` or `0x22ce4`). Their common plan is in
`recovered_plane_full_clear_thunks.c`.

The reset helper at `0x22d30` fills `0x0100c940` in groups of four `0xffff`
halfwords, with `caller_r1+31` groups. It clears `0x504d26`, `0x504cfc`,
`0x504d08`, and `0x504d04`, then masks the generator result to `0xfff`,
reduces modulo `5`, and stores that value at `0x504d00` unless the reduced
value is `4`; that case stores `0x503a98+4` instead. The ABI-level plan is in
`recovered_hud_reset_22d30.c`.

The adjacent writer at `0x22f0` checksums one backup-SRAM record per call.
The index scales as `((i*33)*4-i)*4` (`shlo 5`, `addo`, `shlo 2`, `subo`,
`shlo 2`), giving a 524-byte stride into the `0x01d00000` window. It loads
the data address `0x1d00016+r4`, calls the `0x3120` CRC16 helper with
stride `1` and count `31+3`, then stores the result with `stos` at
`0x1d00014+r4`. The short store keeps only the low 16 bits: the `0x2594`
and `0x2604` verifiers reload the slot with `ldos`, mask both sides with
`0xffff`, and take the `0xf5d40` path on mismatch. Static callers at
`0x3478`, `0x3504`, and `0x3a18` all pass index `0`. The pure schedule is
in `recovered_record_checksum_22f0.c`.

The tiny probe at `0x2080` is the same CRC idiom without indexing: it adds
`12` to the incoming pointer, calls `0x3120` with stride `1` and count
`31+7`, and returns the checksum for the caller's masked 16-bit comparison.
Ten static call sites (from `0x20b0` through `0xf1af0`) follow the
`ldos` reload, `0xffff` mask on both sides, and mismatch branch. The pure
schedule is in `recovered_crc_probe_2080.c`.

The subroutine at `0x292d8` is the geometry program-port word pump used by
the `0x294b0`/`0x295d0` setup family (reached via `bal` from `0x29564` and
`0x29634`). It saves the return link into `g3`, clears `g14`, writes `0x606`
to `0x00800060`, emits the two header words (`g0`, `g1`) to the `0x00804000`
port, then loops `g1` times storing two words per iteration from `(g2)` to
the fixed port address. The `0x294b0` call passes headers `(0, 32)` for 64
table words from `0x293b0`. The pure schedule is in
`recovered_fifo_upload_292d8.c`.

The four entries at `0x1d1d0`, `0x1d210`, `0x1d230`, and `0x1d250` are
fixed-callee instances of the `0x1d1b0` NUL-terminated walk shape: test
the byte first, emit each nonzero byte with the byte in `g0` through the
fixed callee, and stop at the first NUL. The callees are `0x1cea0`,
`0x1d090`, `0x1cf40`, and `0x1cfe0` respectively, each modeled as an
emitter below. The route table is in
`recovered_text_walk_dispatch_1d210.c`.

The fourth sibling at `0x1cea0` pairs plane `0x01000000` with the forced
`0xc000` combination and its own table at `0x2ea10d0`, under the same
shifted gate and column-wrap contract. The pure plan is in
`recovered_glyph_emit_p0a_1cea0.c`, completing the emitter family.

The retry controller at `0x3ba0` steps the sign-extended `0x1d0002c`
counter and compares the `0x1d00038` limit ordinally: a limit inside the
step returns early unless the mode byte is set with bit `4` of `0x5024a4`
also set, while a limit past the step advances (a zero mode byte first
rewinds the limit through `0x2330`). The tail calls `0x2a580` with
`0x111c` and reports `1`. The pure decision is in
`recovered_retry_3ba0.c`.

The block cluster around `0x1ef70` homes the cursor words (`16` to
`0x504cdc`/`0x504ce0`, `18` to `0x504ce4`), then fills a `32x6` block
through `0x1df00` for a zero selector or emits one through `0x1dc90`
from `0x2fd6d20` otherwise. The emitter writes `rows x width` halfwords
with `0xc000` attributes from the cursor slot; the fill writes the
caller link instead. The pure schedules are in
`recovered_home_dispatch_1ef70.c`, `recovered_block_emit_1dc90.c`, and
`recovered_block_fill_1df00.c`.

The store triple at `0x29c08` is a three-way signed clamp: the `bl`
arm takes the pre-`setbit` `g5` floor of `-256` when `g0 < -256`, the
`cmpible` arm keeps values through `0x100`, and anything above stores
the `0x100` ceiling — while `0x51a264`/`0x51a268` receive the cleared
link (zero). The pure schedule is in `recovered_clamp_store_29c08.c`.
(Corrected from a minimum-only reading that mishandled below-`-256`
inputs; the boundary test now pins both arms.)

The neighboring routine at `0x29c50` re-arms the cluster: it loads
`0x29c9c` into the link slot, clamps `g0` into `0x51a260` with a
`0`-floor variant (`cmpi g0,0` sends negatives to 0, then the same
`0x100` ceiling), stores the forced link to the counter at `0x51a264`
— a huge `>= 3` value, so the next `0x29d50` call is active — and the
entry `g1` to the mode slot, returning one-way through `bx(g2)` to the
`ret` at `0x29c9c`. Its second entry at `0x29c58` skips the forced link
so the counter takes the caller's link instead; the three callers there
(`0x1a7c0`, `0xdc338`, `0xdc77c`) are link-valued. No direct caller of
the `0x29c50` entry is visible in maincpu — the re-arm trigger stays
open in U-0001. The pure schedule is in
`recovered_rearm_store_29c50.c`.

The uploader at `0x29d50` opens with a guard plus bank-select prologue:
counters below 3 restore and return, otherwise the old counter shifted
left 12 selects six 4KB source/dest pointers (`0x181x100`/`0x181x000`
triples), the counter is bumped at `0x51a264`, and a zero mode word at
`0x51a268` takes the direct path at `0x29f60` while any nonzero mode
takes the bit-selected blend path at `0x29dc0`. The pure schedule is in
`recovered_upload_select_29d50.c`; the long masked-blend loops stay
unresolved.

The setup tail at `0x29d2c` seeds that cluster: the caller link goes to
both `0x51a260` and `0x51a268` while `0x51a264` is preset to 4, so the
first `0x29d50` call is already past the sub-3 guard. Note the lifecycle
link: a later `0x29c08` clamp overwrites `0x51a260` with `min(g0, 0x100)`
and zeroes `0x51a264`/`0x51a268`, which parks the uploader (counter 0)
until the state is re-seeded. The pure schedule is in
`recovered_upload_state_init_29d2c.c`; who re-arms it stays unresolved.

Every pixel loop in `0x29dc0-0x2a0bc` shares one per-texel kernel over
`in & 0x00ff00ff`: the bit-clear/direct-scale arm stores
`(factor * masked) >> 8` while the bit-set/direct-fade arm stores
`masked + (factor * (masked - mask)) >> 8`, with low-32-bit products and
logical shifts. The canonical instance is the `0x29dec` loop (factor
`g4`, add-back form); the other five blend loops and both direct-path
loops repeat it with `0x100 - fade` or `fade + 0x100` factors. The pure
kernel is in `recovered_blend_kernel_29dec.c`; loop trip counts, pointer
chasing, and fault semantics stay unresolved.

The inner-loop counter block is a fixed trip schedule, shown canonically
at `0x29e68`: the body runs first, then `addo r6,1 / cmpi 31,r6 / bge`
exits once `31 >= r6` fails, giving exactly 32 passes with src/dst each
advancing `32 x 4 = 0x80` bytes for 32 stores. The pure schedule is in
`recovered_blend_loop_schedule_29e68.c`; the `0x180` stride fixups and
the outer `r15` cadence stay unresolved.

Those fixups form the outer-cadence schedule: each pass adds `0x180` to
both pointers of pairs 0 and 1 (one fixup each, at `0x29e54`/`0x29e5c`
and `0x29ed0`/`0x29ed8`) but twice to pair 2 (transition plus the outer
bottom at `0x29f4c`/`0x29f50`), giving per-pass totals of `0x200`,
`0x200`, and `0x380` over the inner `0x80`. The reloaded mode word picks
each plane's loop form per pass (set bit = fade loop, clear = scale
loop), and the body-first `r15` block runs 8 passes. Pairs 0/1 therefore
span exactly `8 x 0x200 = 0x1000` bytes — one full bank from the
`0x29d50` prologue. The pure schedule is in
`recovered_blend_stride_schedule_29e4c.c`; pixel data and fault
semantics stay unresolved.

The mode-0 direct path at `0x29f60` reuses both kernel forms and the
same 32x8 cadence, with its own dispatch and uniform strides: fade
values at most zero take the `0x2a00c` fade form (factor = fade),
anything above takes the scale form with `fade + 0x100`, and both outer
bottoms advance all six pointers by `0x180`, so every pair totals
`0x200` per pass — exactly one bank each, without the blend path's
pair-2 asymmetry. The pure schedule is in
`recovered_direct_stride_schedule_29f60.c`.

The full lifecycle is chained in
`von/tools/test_recovered_upload_cluster_e2e.py`: seed presets counter
4, clamp parks the uploader, reseed plus prologue selects bank 4,
direct and blend stride schedules span their banks over 8 passes, one
inner loop contributes 32 kernel texels, and the run budgets exactly
`8 x 3 x 32 = 768` stores.

One parking caller is identified at `0x1b960`: the leaf fixes `g0` to 0
so the clamp stores 0 (parking the uploader), publishes 25 to
`0x503a00`, and saves the link at `0x5024c6`. The pure schedule is in
`recovered_park_store_1b960.c`; the re-arm source stays open (U-0001).

A second parking leaf at `0x1b980` does the same clamp-0 park, then
publishes service-table constants around two caller-owned sub-calls:
`0x14a` to `0x503a04`, 16 to `0x503a00`, and `-1` (from `subo 1,0`) to
`0x577170`. Link/return mechanics stay caller-owned. The pure schedule
is in `recovered_service_publish_1b980.c`.

Just above, the `0x1b940` leaf forwards the service halfword at
`0x503a80` to `0x5032f4` (bit-preserving), hands its sign extension to
the `0x1fe90` sub-call, and passes 3 to `0x2a4e0`. The pure schedule
is in `recovered_slot_forward_1b940.c`.

The `0x1ba08` block calls `0x2a4e0` with 2, publishes 1 to `0x5039f4`,
and stores the call's own resume address `0x1ba10` (not the entry link)
to `0x503a00`. The pure schedule is in
`recovered_link_publish_1ba08.c`.

Its dispatch head at `0x1b9d0` masks the `0x503a04` counter to bit 5
for the `0x1fa30` call, then either jumps to the link block on flag
`0x5024a4` bit 4 with no store, or decrements the counter in place and
takes the link block only when the entry counter was exactly 1. The
pure schedule is in `recovered_counter_dispatch_1b9d0.c`.

Further down, the `0x1ba70` tail gates a `0x2a4e0` call with `0x1317`
on counter equality with 480, then runs the same dispatch shape with a
constant terminal: flag-set stores 22 to `0x503a00` with no counter
store, otherwise the counter decrements and the 22-store happens only
from counter 1. The pure schedule is in
`recovered_threshold_dispatch_1ba70.c`.

Its head at `0x1ba30` chains four sub-calls (`0x1c618` on entry
registers, `0x1ccf8` with 0, `0x2a4e0` and `0x1fa00` with `0x1013`),
then presets `0x12c` to `0x503a04` and bumps `0x503a00` by one. The
pure schedule is in `recovered_service_head_1ba30.c`.

The `0x1bac0` block runs only when the `0x503a04` counter equals
`0x118`: it stores 7 to `0x503a00` and clears bit 0 of the halfword
register at `0x10000000`. The pure schedule is in
`recovered_flag_block_1bac0.c`.

The `0x1bafc` block masks the same counter to six bits: a zero mask
issues `0x1ffb0` with 1 plus `0x2a4e0` with `0x1342`, a 32 mask issues
`0x1ffb0` with 0 alone, and any other mask skips the calls — then the
counter always bumps in place. The pure schedule is in
`recovered_masked_call_1bafc.c`.

Four input dispatchers (`0x2c70`, `0x2c90`, `0x2cb0`, `0x2d60`) test the
same `0x5023e0` flag and forward with no argument shuffling: the zero arm
takes `0x27b8`/`0x2798`/`0x2cd8`/`0x2d88` (all `bal`), while the nonzero
arm takes `0x2bb0`/`0x2c10`/`0x2da0` (`call`) except `0x2cb0`, whose
nonzero arm is also `bal` to `0x2cf8`. The pure table is in
`recovered_flag_dispatch_2c70.c`.

The predicate at `0x18438` matches the ordered pairs `(0,1)`, `(1,0)`,
`(2,3)`, and `(3,2)`, returning the boolean in `g0` through the saved
link in `g2` (`g14` cleared on entry). The pure function is in
`recovered_pair_match_18438.c`.

The classifier at `0x183b8` gates three masked port words ordinally:
`[g0-0x2001] <= 0x3ffe` reports `3`, `[g0+0xa000] <= 0x4000` reports `0`,
`[g0+0x5fff] <= 0x3ffe` reports `2`, otherwise `1`. The link moves to `g1`
with `g14` cleared. The pure function is in
`recovered_port_classify_183b8.c`.

The pump at `0x18538` drains a 16-entry byte ring at `0x504c60` (head
`0x504c70`, tail `0x504c74`): a nonempty queue emits the head byte to
`0x1c00008` and `0x503312` and advances the head modulo `16`, while an
empty queue refreshes `0x504c78` from `0x502512` when they differ and
emits its low byte to port `0`. The pure schedule is in
`recovered_queue_pump_18538.c`.

The straight-line prologue at `0x34c0` stores the caller link across a
fixed run of state slots (`stob`/`stos`/`st` widths preserved), calls
`0x22f0` with index `0` and then `0x2330`, and finishes with four more
halfword stores plus one word store. The ordered fifteen-op schedule is
in `recovered_init_schedule_34c0.c`.

The plane-0 emitter at `0x1d090` masks the byte to `0x7f`, subtracts `32`,
and sign-extends the low byte (`shlo 24`/`shri 24`, confirmed arithmetic in
the MAME i960 core). Biased values `0x4b`/`0x54` emit the fixed control
pairs `0x837c`/`0x837d` and `0x837e`/`0x837f`; anything above `0x5f` would
be zeroed first (unreachable for masked input). Other bytes index the glyph
table at `0x2ea0fd0`, so control bytes keep negative indices. Each glyph is
a vertical tile pair in plane `0x01000000` with `0xc000` attributes, and the
column in `0x504ce0` advances while at most `61`. The pure plan is in
`recovered_glyph_emit_1d090.c`; the `0x1cf40`/`0x1cfe0` plane variants
remain separate.

The sibling at `0x1cf40` is the same glyph shape without control-code
branches: the entry gate compares the shifted (not sign-extended) value
against `0x5f000000`, so every masked byte stays on the table path. It
targets plane `0x01002000` with only bit `15` set (no `0x4000` bank
attribute) and shares the column-wrap contract. The pure plan is in
`recovered_glyph_emit_plane1_1cf40.c`.

The third sibling at `0x1cfe0` shares the `0x1cf40` gate, table, plane,
and wrap contract, but combines glyph data with `or 0xc000` instead of
`setbit 15`: a set bit `14` survives `0x1cf40` and is forced here. The
pure plan is in `recovered_glyph_emit_attr_1cfe0.c`.

The command-6 helper at `0x6ede0` validates a float pair and emits an
eight-word FIFO packet. Both floats truncate toward zero (`cvtzri`); each
truncated value is halved arithmetically and masked with `0xfffffe00`, so
the pair is valid exactly for `[0, 1023]` inputs, with the `0x47c34f80`
reject returning no FIFO traffic. The index is asymmetric
(`trunc_y * 512 + trunc_x >> 1`), unlike `0x6ece0`, and addresses
20-byte records from `0x51bb28`. The packet order is `53`, record `+0x04`,
`x` bits, record `+0x0c`, `y` bits, record `+0x08` with only bit `31`
flipped, record `+0x10`, record `+0x08`; the record's first two halfwords
also go out through the caller pointers. The `0x40800000` load is dead
(the `addrl` adds a zero register). The pure plan is in
`recovered_command6_pair_6ede0.c`.

The tiny emitter at `0xe39c0` renders ranking ordinals from parallel
tables: `0xe36c0` holds `" 1"`, `" 2"`, ... while `0xe3700` holds `"ST"`,
`"ND"`, `"RD"`, `"TH"`, ... The index scales by `((i*2+i)*2)` (`shlo 1`,
`addo`, `shlo 1`) for a six-byte stride. The number half goes through the
`0x1d1d0` walker and the suffix through the `0x1d1b0` walker. Ten static
callers sit in the `0xe3xxx`–`0xe6xxx` results screens. The pure schedule
is in `recovered_rank_string_e39c0.c`.

The fixed fan-out at `0xe3a70` emits the first three string bytes through
the `0x1d570` status helper, sign-extending each low byte (`shlo 24`/
`shri 24`). The pure schedule is in `recovered_tribyte_emit_e3a70.c`.

The state-shift helper at `0x77e20` chains two `0xf5d40` forward copies of
`0xf4` bytes: first `0x504d60` to `0x504e60`, then `0x504f60` to `0x504d60`.
Like the `0x2330` wrapper it is a call-site contract reusing
`recovered_memory_copy_forward()` with fully immediate addresses and
length, so no second copy implementation is introduced.

The divider at `0x78090` selects `0xbb8` for modes `4`/`7` and `0x64`
otherwise (the `cmpibge` arm compares literal-first, so mode `7` still
reaches its own check), divides the `0x504dc0` dividend, saturates the
quotient down to `90`, and reports `1` when the dividend exceeds `120`.
The pure plan is in `recovered_divisor_clamp_78090.c`.

The gate at `0x81e60` calls `0x84d90` only when mode `0x5039f4` is `4`,
`0x503a00` is `10`, and `0x504e42` is nonzero; the ten-way table at
`0x81eb4` then dispatches on the object's `+0x64` field for states `0-9`
(the `cmpobl` arm compares literal-first, so anything above `9` exits).
The entry object still sits in `r4` for the target. The pure plan is in
`recovered_dispatch_gate_81e60.c`; the ten `0x83xxx` targets stay outside.

The decimal emitter at `0xe3830` compares its input ordinally against
`99`: larger values emit the shared `"99"` string at `0xe3824` through
the `0x1d9e0` walker, while values `0-99` emit `value/10` and `value%10`
as `0x30`-biased characters through the `0x1d310` walker with modes
`(3, 0)`. The pure plan is in `recovered_decimal_emit_e3830.c`, which
also covers the `0xe3a10` alias thunk.

Two results-screen thunks are pure aliases needing no translation:
`0xe39f0` calls the `0x1d1b0` walker and `0xe3a00` calls the `0x1d880`
classifier, each returning directly. Both are tracked as ABI scaffolding
like the `0x27d8` trampoline.

The head of `0x7a3e0` routes on the object's `+0x64` state and its peer's
(`+0x74`): own `8` reports mode `11` through `0x78790`; peer `0`/`3`
reports mode `9` through `0x7a9f0`; own `1`/`3`/`4`/`5` falls into the
ratio computation; anything else takes the `0x7a4a8` arm. All arms test
equality, so no operand-order proof is needed. The pure decision is in
`recovered_route_head_7a3e0.c`; the downstream bodies stay outside.

Both ratio arms (`0x7a438` reporting mode `10` through `0x7ad90`,
`0x7a4a8` reporting mode `9` through `0x7a9f0`) share one predicate that
needs the `0x504e2c` flag at `1`: the four `+0x1d0`/`+0x1d8` halfwords are
sign-extended, converted with `cvtir`, and divided `src2/src1`, so each
side is first/second. The win needs the object ratio strictly below the
peer ratio (`cmpr`/`bge` skips otherwise). The pure predicate is in
`recovered_ratio_duel_7a438.c`.

The reset helper at `0x23510` first calls `0x1dfd0` with source `0`, width
`64`, height `4`, and row count `caller_g14+31`. It then clears the two state
halfwords at `0x504d26` and `0x504d24`, followed by `0xfff` zero halfwords at
`0x0100c000`. The recovered descriptor is in
`recovered_status_strip_reset_23510.c`.

The stateful renderer at `0x23410` runs only when `0x503a7c` is zero and
`0x5770f0` is one of modes `0`–`4`, `7`, or `9`. For accepted modes it always
advances `0x504d26` by `-2` modulo `0x200`. When the low nibble of that state
is zero, it selects source-table family `0x02ea289c` using
`0x504d00 & 0xf`, calls `0x1dd80` for a `2×4` block at column
`(62 - ((0x504d26 & 0xffff) >> 3)) & 0x3f` and row `31+0x504cfc`, then
advances `0x504cfc` as `(old+1) % table_modulus`. The source-table slot and
state transition are captured in `recovered_status_mode_renderer_23410.c`.

The status string helper at `0x23560` saves the active text origin from
`0x504d40/0x504d44` into the glyph writer's `0x504ce0/0x504ce4` state, scans
the string after its first byte for lowercase ASCII, and calls `0x1d310` with
attributes `0x4000`. A lowercase suffix selects byte `0` with font mode `0`;
otherwise it selects byte `1` with font mode `1`. It then copies the glyph
writer's resulting origin back to `0x504d40/0x504d44`. This selector contract
is in `recovered_status_string_glyph_23560.c`.

The sibling wrapper at `0x23620` performs the same origin save/restore around
the alternate glyph helper `0x1cd18`, but selects `text[index]` directly and
passes the caller's index unchanged. Its pure wrapper contract is in
`recovered_status_indexed_glyph_23620.c`.

The geometry initializer at `0x23670` begins by sending command `0x0a` with
the object's `+0x0c` value and the object-minus-parent `+0x0c` delta. It
then sends command `0x1d` with the object's signed `+0x184` halfword and
`0x43200000`, folds the returned signed halfword into `+0x08` and `+0x94`,
derives `+0x0c + 2.5f` into `+0x8c` and `+0x98`, and sends command `0x1e`
with the `+0x184` value and the signed `+0x84 - +0x184` delta. The second
response is added to `+0x10` into `+0x90` and `+0x9c`; bytes `+0xa0/+0xa1`
are cleared. The common prefix is modeled in
`recovered_geometry_object_init_23670.c`; branch-specific packet tails remain
separate.

The valid-transform branch at `0x2381c` (duplicated at `0x23b3c`) copies the
parent fields `+0x14/+0x18/+0x1c` into the object base coordinates, then
updates object `+0x0c`, `+0x10`, and `+0x14` as
`parent_1c8*scale+base_x`, `parent_150*scale^2+base_y`, and
`parent_1cc*scale+base_z`. It sets object byte `+0x18` to `1` before entering
the shared lifecycle tail. The common arithmetic is in
`recovered_geometry_object_transform_update_2381c.c`; the scale-producing
bound checks remain part of the dispatcher.

Those dispatcher bounds at `0x237ac` are now explicit. With object byte `+0x18`
zero, the first route requires `((g6+0x17ff)&0xffff) <= 0x2ffe` and the
sign-extended low halfword of `g7` to be at least `-0xdff`; it reaches
`0x2381c`. Failed first checks enter the second window, which requires
`((g6+0x1ff)&0xffff) <= 0x3fe` and signed `g7 >= -0xbff`, also reaching the
transform body. A nonzero `+0x18`, or failed second checks, reaches `0x238a0`.
The normalized operands and three-way route are modeled in
`recovered_geometry_object_branch_dispatch_237ac.c`.

The alternate branch at `0x238a0` emits command `0x1d` with the signed
`+0x184` halfword and `0x43200000`, subtracts the response from object `+0x08`
into both `+0x08` and `+0x0c`, and derives the adjusted `+0x0c` value into
`+0x04` and `+0x10`. It then emits command `0x1e` with the same halfword and
the shared signed delta, adds the response to `+0x10` into `+0x08` and
`+0x14`, and clears bytes `+0x18/+0x19`. The field-update model is in
`recovered_geometry_object_alternate_update_238a0.c`.

The shared lifecycle tail at `0x23954` returns immediately when object byte
`+0x18` is nonzero. Otherwise it increments byte `+0x19` only while its
current value is at most `31`; values `32` and above are left unchanged. The
isolated state transition is in
`recovered_geometry_object_lifecycle_tail_23954.c`.

The indirect cleanup helper at `0x23ca0` clears object bytes `+0xa0`, `+0xa1`,
and `+0xa2`, publishes raw constant `0x41200000` to globals `0x504d54` and
`0x504d58`, and returns through local stub `0x23cd8`. Its pure contract is in
`recovered_geometry_cleanup_helper_23ca0.c`.

The position-update helper at `0x23ce8` loads signed halfwords from object
offsets `+0x1d0`, `+0x1d2`, and `+0x1d4`. It forms the raw delta
`object_+0x1d0 - object_+0x1d2`, then follows the i960 compare-source ordering
to select the original `+0x1d4` when delta is at most the limit, retain the
raw delta when it is at least the negated limit, or use the negated limit
otherwise. If the selected delta is negative and global `0x503a60` is zero,
it is cleared before being added to `+0x1d2`; the result is stored back as a
signed halfword. The helper returns through `0x23d5c` and is reached from the object
update paths at `0x23d88`, `0x273f4`, and `0x274a4`. Its instruction-level
contract is in `recovered_geometry_position_delta_23ce8.c`.

The setup entry at `0x23d60` begins with a deterministic geometry-board
prefix. After its optional `0x23ce8` update, it writes `0x909` to
`0x800090`, writes `0x44160000` to both `0x804000` and `0x804004`, and emits
three FIFO phases at `0x884000`. The phases contain fixed command/constants
plus one runtime-derived word repeated in the two command-19 packets; the
third phase ends with `31 + 27 = 58`. It then reads `0x802008`, emits that
readback through the FIFO, and publishes the readback address plus `0x34` to
`0x801008`. This deterministic prefix is isolated in
`recovered_geometry_board_setup_23d60.c`; the subsequent polling and
geometry-math sequence remains separate.

The response/state selector at `0x23ef0` first compares signed state
halfwords `0x503ca2` and `0x503ca0`. If the former is greater, it selects
`0x40005c` or `0x49c980` based on bit 0 of `0x5024e8`. Otherwise it compares
`0x503ca0` against signed `0x503ca8` thresholds divided by `4`, `3`, and `2`,
selecting a 32-entry table index from `0x2be0008` as `state*2`, `state`, or
`state/2`; the final threshold selects `0x49c980`. The FIFO read source is
`0x884000`. The literal branch/table contract is in
`recovered_geometry_response_selector_23ef0.c`; the subsequent command-6
packet construction is not included.

The command-6 setup at `0x240dc` initializes frame slots `0xc0` through
`0xcc`, writes control value `0x101` to `0x800010`, publishes the selected
geometry pointer at `0x804004`, and writes the fixed frame pair beginning at
`0x804008`. It then calls the existing clip dispatcher `0x701a0` four times
with explicit raw argument tuples. The first two calls share the runtime
derived clip word; the final call uses the previous call's `g0` result in both
argument positions. Those call descriptors are isolated in
`recovered_geometry_clip_calls_240dc.c`; device-side clip packet effects and
the later command-6 phases remain separate.

The object response selector at `0x24460` repeats the same threshold shape
using signed object halfwords `+0x1d0`, `+0x1d2`, and `+0x1d8`. If `+0x1d2`
is greater than `+0x1d0`, it selects `0x40002c` or `0x49c980` from bit 0 of
`0x5024e8`. Otherwise it selects table indices `state*2`, `state`, or
`state/2` from `0x2be0088` at the quarter, third, and half thresholds; the
final route selects fixed pointer `0x49c984`. The recovered contract is in
`recovered_geometry_object_response_selector_24460.c`.

The following command-6 block at `0x24540` publishes the selected pointer at
`0x804004`, emits the fixed `0x804008` frame pair, and calls the existing
`0x701a0` clip dispatcher four times. The first call uses the fixed rectangle
`(0xc2040000, 0x431c0000)` against `(0xc2040000, 0x43130000)`; its returned
value is converted and carried as the shared `r4` value for the remaining
three calls. Those calls use the exact register-derived tuples captured in
`recovered_geometry_object_clip_calls_24540.c`. The conversion arithmetic is
left as an explicit input until the `cvtir`/`addrl` helper semantics are
recovered independently.

The continuation at `0x24690` now has a bounded host-side route. A signed
negative `0x503a78` value branches directly to the common mode-zero sequence at
`0x24cc8`; nonnegative values initialize an index at zero and enter the
generated geometry loop. Each iteration compares the index against
`0x503a6c` and separately requires bit 2 of the `0x5024e8` mask. The enabled and
fallback forms both begin with FIFO commands `5, 19`, emit the six-word packet
`[5,19,computed0,computed1,1,58]`, read `0x802008`, and
publish the readback-derived `+0x34` address through `0x801008`; the index
advances by one. The two computed words are now bounded: after `r4:r5` is
prepared as long-real `600.0`, the active and fallback bodies compute
`computed0 = (float)(4.0 / 600.0)` and `computed1 = (float)(r6 / 600.0)` via
`divrl`. The constant `1` comes from `g3`, and the final `58` comes from the
shared frame word in `r9`. This routing and framing is implemented in
`recovered_geometry_command6_loop_24690.c` and tested by
`von/tools/test_recovered_geometry_command6_loop_24690.py`.

The `r6` term should remain an explicit incoming register value for now. The
`0x240dc` and `0x24540` routines use it before and after the four `0x701a0`
calls (`cvtir r6` at `0x240dc`/`0x245d8`, then `shrdi 1,r6` at `0x2428c`),
but none of those clip calls writes it. In the later command-6 loop,
`movr r6,fp0` consumes the same register as a raw IEEE single before the
division. The visible callers also do not establish it immediately before the
call, so its upstream semantic source and intended dual-use representation are
not yet proven; it is not safe to label it a clip result. The host model keeps
the value as `r6_bits` and performs the raw-bit reinterpretation explicitly.

The common branch target at `0x24cc8` begins a second fixed geometry-board
sequence: fifteen FIFO words containing command `5/16/18`, two command-19
parameter groups, and the `58` tail. It publishes frame slots `0xb0` through
`0xbc`, writes control `0x101`, and then invokes `0x701a0` four times with
the fixed rectangles `(0xc2c40000, 0x432f0000)` and
`(0xc36f0000, 0x43170000)`. The prefix and raw call descriptors are captured
in `recovered_geometry_mode_zero_clip_calls_24cc8.c`; the following object
state packet begins at `0x24eb4`.

The object-state packet at `0x24eb4` calls `0x1cac8` with `(10,24)`, emits
command `31`, and alternates the three words loaded from helper-object
offsets `+0x08/+0x0c/+0x10` with the corresponding words from the current
object. The board readback at `0x884000` is consumed by `0x1e370`. Its tail
implements a persistent status latch: a byte at `+0x1da` above `0xc8` with
global `0x503a60` active stores `0x5024e8 & 2`; otherwise a zero
`0x504d50` latch stores the persistent `g14` control word (`0x101`), with both updates calling
`0x1f080`. The packet and latch contract is isolated in
`recovered_geometry_object_state_packet_24eb4.c`.

The shared callee at `0x9d0d0` opens with three persistent countdown updates.
Object flag bytes `+0x1de`, `+0x1dd`, and `+0x1df` reset the corresponding
globals `0x562c9c`, `0x562ca0`, and `0x562ca4` to the incoming `g14` frame
value. When a flag is zero, the matching counter is decremented only while
positive; zero and negative values are preserved. This deterministic prefix
is captured in `recovered_geometry_global_countdowns_9d0d0.c`.

The board-update entry at `0x9d170` writes `0x909` to `0x800090` and
`0x44160000` to both `0x804000` and `0x804004`. A `bno` after `chkbit 0,
0x5024e8` skips the update body when bit 0 is clear. When enabled, the FIFO
begins with five words: command `5`, the `31+24` tail value `55`, constants
`0x3e23d70a`, `0xbdf92c60`, and `1`. This gate and prefix are isolated in
`recovered_geometry_board_update_gate_9d170.c`; the following command-19
branches remain state-dependent.

The first command-19 branch at `0x9d1ec` requires object `+0x1de` and the
low byte of `+0x138` both to be zero, then emits payload `0x3bc49ba6`, resets
`0x562c9c` to `30`, and—when its prior value was nonzero—calls `0x1cac8`
with `(39,28)` followed by `0x1e760(1)` before storing the frame value.
Other paths use `0x3bc49ba6` while `0x562c9c` is live, or use
`0x3b03126f` when that counter is zero. If both counters `0x562c90` and
`0x562c9c` are zero on the rearm path, it additionally calls `(39,28)` and
`(43,29)` through `0x1cac8`, invokes `0x1d210`, and sets `0x562c90` to `1`.
The branch and side effects are captured in
`recovered_geometry_command19_branch_9d1ec.c`.

When the next object flag has bit 1 set, `0x9d334` emits command `29` with
the low nibble of signed `0x5024e8` shifted left 12 and fixed parameter
`0x40400000`. After the board response, it emits command `19` with the
response-derived word, `0x42200000`, that same derived word, and `1.0`, then
command `18`, `1.0`, two zero words, and the `58` tail. It publishes a
`(0,0x40009c)` frame pair and the usual `0x802008+0x34` readback pointer.
The bit-1 gate and packet shape are captured in
`recovered_geometry_flagged_state_packet_9d334.c`; the alternate clear-flag
floating-point path remains separate.

The second flagged state path at `0x9d730` repeats the command-29/response
sequence with the `+0x1dd` bit-1 gate. It emits command `29`, the masked
state parameter, and `0x40400000`, then command `19` with the derived word,
`0x42200000`, the derived word again, and `1.0`; command `18` follows with
`1.0`, two zero words, and `58`. Its frame publication is `(g14,0x40009c)`
with tail constants `0x84553f` and `1`. The exact branch contract is in
`recovered_geometry_second_flagged_state_packet_9d730.c`; the clear-flag
`+0x1e2` path remains separate.

The second clear path at `0x9d858` uses signed object halfword `+0x1e2` for
another FP-derived command-19 payload, followed by the same fixed
`0x40a00000`/command-18 packet and `58` tail. After readback, low byte
`+0x1dd` selects local frame slots `0x50/0x54` with pointer `0x40005c`, or
`0x60/0x64` with pointer `0x40002c`; both publish `g14` as the first frame
word and carry tail constants `0x84553f` and `1`. The exact packet/frame
contract is captured in `recovered_geometry_second_clear_flag_packet_9d858.c`;
the FP derivation remains an explicit input.

The third mirrored command-19 sequence at `0x9d9a0` begins with
`19, 0xbd888889, 0xbdf92c60, 1.0`, then applies the same special/countdown/
rearm decision shape using object `+0x1df`, low byte `+0x13a`, and counters
`0x562ca4`/`0x562c98`. Its special and live-counter payload is `0x3bc49ba6`;
the rearm payload is `0x3b03126f`. The special helper uses `(23,28)` and
`0x1e760(1)`, while a fully rearmed path uses `(23,28)`, `(26,29)`, and
`0x1d210`, then sets `0x562c98` to `1`. This branch is captured in
`recovered_geometry_command19_branch_9d9a0.c`.

The following bit-1 state split at `0x9db3c` repeats the flagged command-29/
19/18 packet using `+0x1df`, the masked low nibble of `0x5024e8`, and the
same derived word twice. It publishes `(g14,0x40009c)` with the standard
tail. The clear branch at `0x9dc64` uses signed halfword `+0x1e6`, emits the
fixed command-19/18 packet, and publishes either frame slots `0x80/0x84`
with `0x40005c` or `0x90/0x94` with `0x40002c`, with tails at `0x88`/`0x98`.
The packet contracts are captured in
`recovered_geometry_third_flagged_state_packet_9db3c.c` and
`recovered_geometry_third_clear_flag_packet_9dc64.c`; both FP-derived words
remain explicit inputs.

After the third state publication, `0x9ddac` emits a one-word command `6`
and applies a persistent dispatch gate at `0x562ca8`. A nonzero gate is
replaced by the current `g14`; a zero gate is also replaced by `g14` unless
all three countdowns `0x562c9c`, `0x562ca0`, and `0x562ca4` equal `30`.
When all three are `30` and the gate is zero, it calls `0x2a4e0(0x114c)` and
sets the gate to `1`. This post-state contract is captured in
`recovered_geometry_post_state_gate_9ddac.c`.

The clear-flag path at `0x9d454` sign-extends object halfword `+0x1e4` and
uses extended FP arithmetic to derive a command-19 payload: divide by the
long-real `3.390625` (`0x40590000`), multiply by `3.0625` (`0x40440000`),
then store the rounded single-precision result. Its fixed packet
is `19, derived, 0x40a00000, 1.0, 18, 1.0, 0, 0, 58`, followed by the
usual `0x802008+0x34` readback publication. The low byte of `+0x1de` then
selects either frame `(0,0x40005c)` or `(g14,0x40002c)` for the `0x804000`
publication; both variants carry frame tail constants `0x84553f` and `1`.
The exact packet and frame contract is captured in
`recovered_geometry_clear_flag_packet_9d454.c`; its host reference helper is
tested on signed boundary values, while exact extended-FP edge rounding
remains an explicit qualification.

In the shared result builder at `0x9de50`, the flag-set branch now has an
explicit data-flow model: response scratch words are subtracted from related
object fields `+0x14`, `+0x18`, and `+0x1c`, and each wrapped 32-bit difference
is written to both the output record and its mirror slots. This is captured by
`recovered_geometry_result_builder_related_differences` and covered by the
result-builder test; the field names remain intentionally structural.
The selector preamble is also executable at the raw-data level: selector `s`
addresses signed-halfword record `s*3` in table `0x562436`, and emits its
three values in order before the command-38 request. The extraction helper and
signed-value test live in the same result-builder model.
On the clear-flag branch, the fallback table halfword and object `+0x184` are
sign-extended into output offsets `+0x0c/+0x0e` and mirror offsets `+0x06/+0x08`;
the persistent control word is copied to output/mirror `+0x10/+0x04/+0x0a/+0x1c`,
and the raw `0x562cb0` word fills output `+0x14`. This signed/raw distinction is
now covered by the result-builder test.

The mirrored command-19 sequence at `0x9d59c` begins with
`19, 0xbe962fc9, 0xbdf92c60, 1.0`, then applies the same special/countdown/
rearm decision shape using object `+0x1dd`, low byte `+0x139`, and counters
`0x562c94`/`0x562ca0`. Its special and live-counter payload is
`0x3bc49ba6`; the rearm payload is `0x3b03126f`. The special helper uses
`(7,28)` and `0x1e760(1)`, while a fully rearmed path uses `(7,28)`,
`(9,29)`, and `0x1d210`, then sets `0x562c94` to `1`. This mirrored branch
is captured in `recovered_geometry_command19_branch_9d59c.c`.

The second object variant at `0x23980` starts with command `0x0a`, using
object `+0x7c` and the object-minus-parent `+0x0c` delta. Its preamble derives
`object_+0x84 - 0x504baa`, subtracts `0x504ba8` from the first FIFO response,
and gates the transform branch on fixed-point `+0x172` being above
`0x150000` and at most `0x190000`, with the response delta above
`0x1b800000`. Failed bounds enter the alternate branch at `0x23acc`. The
normalized preamble is in `recovered_geometry_object_variant_23980.c`.

The smaller wrapper at `0x0001f060` selects the same source plane but a
different fixed destination: it passes source `0x01004000`, destination
`0x02fd2520`, `0x40` halfwords per row, and `g17+31` rows to `0x1bc90`.
`recovered_text_video_upload_wrapper.c` captures this descriptor, including
the i960 32-bit wraparound of the row count.

The mixed upload routine at `0x20210` first performs a plain `64×30` transfer
from `0x2fefee8` through `0x1dc10` at origin `(g14,g14)`. It then performs
four converted `0x1de80` transfers, all width `64`: source `0x2ff16e8` with
height `g8+31` at `(g14,g14)`, followed by source `0x2ff1568` with height `4`
at rows `g8+31`, `g14`, and `g16+31`. The ordered plan is captured in
`recovered_video_mixed_upload.c`.

The two-block panel builder at `0x1f4c0` first copies a fixed 5×5 block from
`0x02fe01d4` at `(4,10)`. It then selects an 8×5 source-table entry at
`0x02ea2010 + (((g0-0xd0) & 0xf) * 4)` and copies it at `(28,20)`. The
selector is derived from the adjusted pointer value itself; the pure plan is
implemented in `recovered_status_panel_builder.c`.

The follow-on routine at `0x1f540` performs three transfers. It advances the
current position to `(column+2,row-1)`, draws `0x2fde9d0` as a `55×8` block
using `0x1dc10` when `g1` is nonzero or attributed `0x1dc90` otherwise, then
advances to `(column+14,row-8)` and draws `0x2fe1606` as `34×2`. At that same
final position, `g0` selects either source `0x2fe158e` via `0x1dc90` or a
zero fill via `0x1df00`, both `30×2`. The sequence is implemented in
`recovered_status_panel_sequence.c`.

The fixed helper at `0x1f640` delegates to attributed writer `0x1dc90` with
source `0x2fded40`, width `6`, and height `8`, consuming the current text
position globals. This transfer descriptor is implemented in
`recovered_fixed_panel_transfer.c`.

The sibling at `0x1f660` makes the same `0x1dc90` attributed `6×8` transfer
from fixed source `0x2fdeda0`, also using the current text-position globals.
Its descriptor is kept separate in `recovered_fixed_panel_transfer2.c`.

The bytes at `0x1f680` are a nine-entry status-code table, not executable
code. Each record occupies 16 bytes; indices `0–7` contain displayed status
strings and index `8` is blank. The consumer initializes text position
`(8,14)` before passing the selected record to `0x1d210`. The table shape and
bounded record-address calculation are implemented in
`recovered_status_code_table.c`.

The consumer at `0x1f710` first clears a `((g7+31)×3)` region with
`0x1df00`, then maps selectors `0..7` to eight case bodies; all other values
use the blank case at `0x1f978`. Every valid case resets text position to
`(8,14)` and emits the corresponding 16-byte table record. The case blocks
use `0x1dc90` with sources `0x2fe321c`, `0x2fe350e`, `0x2fe35e6`,
`0x2fe343c`, `0x2fe37fa`, `0x2fe33b4`, `0x2fe32d0`, and `0x2fe3746`, with
widths derived from the caller registers or fixed constants; case 5 uses
height `2` and the others height `3`. The pure dispatcher plan is implemented
in `recovered_status_code_dispatch.c`.

The tiny `0x1f9c0` thunk loads `0x1f9d4` into `g14`, copies it to `g0`, clears
`g14`, and performs `bx (g0)` into the single `ret` instruction at `0x1f9d4`.
Its contract is represented by `recovered_clear_g14_return.c`.

The fixed continuation renderer at `0x1fa00` loads the message
`"TO BE CONTINUED..."` from `0x1f9e0`, writes both text-origin globals from
incoming `g14`, sets row `20`, and calls `0x1da90`. Its register-dependent
plan is implemented in `recovered_continued_renderer.c`; the caller context
must supply the column value through `g14`.

The adjacent `0x1fa30` route writes column `2`, row `20`, and height `5`,
with width `g27+31`. For nonzero `g0` it transfers source `0x2fe053a`
through `0x1dc10`; for zero `g0` it clears the same region through
`0x1df00`. This source/fill contract is implemented in
`recovered_panel5_source_fill_route.c`.

The sibling `0x1fa80` route writes column `8`, row `10`, and height `5`,
with width `g14+31`; its source branch transfers `0x2fe099a` through
`0x1dc90`, while its zero branch clears through `0x1df00`. The fixed
`0x1fad0` transfer writes column/row `(10,10)`, width `g12+31`, height `5`,
and transfers source `0x2fe1350` through `0x1dc10`.

The next pair continues the same layout: `0x1fb10` transfers source
`0x2fe1170` through `0x1dc90` at `(7,10)`, with width `g17+31` and height
`5`; `0x1fb50` uses `(5,10)`, width `g22+31`, height `5`, and selects source
`0x2fe0d42` through `0x1dc10` or a `0x1df00` clear based on `g0`.
`recovered_panel8_panel9_routes.c` records both contracts.

The fixed `0x1fba0` transfer sets origin `(10,20)`, copies source
`0x2fe0404` through `0x1dc10`, and uses dimensions `31×5`. Its contract is
implemented in `recovered_panel10_transfer.c`.

The signed-value renderer at `0x1fbe0` branches on `g0 < 0`. The negative
route copies source `0x2fe17ec` as a `20×3` plain block at the current text
position, advances the column by `21`, and emits a `4×3` glyph through
`0x1dc10`. The glyph helper `0x1e7c0` selects the table entry at
`0x2ea1fd0 + (((g0-48) & 15) * 4)`. Nonnegative values clear a `25×3` region
through `0x1df00`. This split and the derived table index are implemented in
`recovered_status_value_renderer.c`.

The renderer at `0x1fc30` normalizes each input to zero when bit 15 is set.
Unless `(0x503a7c,0x5770f0)` is `(0,4)`, it emits the fixed background
`0x2fe14fe` at `(15,18)` as `31×2`, then renders decimal tens/units from the
table at `0x2ea1e50`. The first pair lands at `(25,21)` and `(27,21)`;
separator source `0x2fe158a` lands at `(29,22)`; the second pair lands at
`(30,21)` and `(32,21)`; suffix source `0x2fe157a` lands at `(34,21)` as
`4×2`. The recovered state plan is in `recovered_scoreboard_renderer.c`.

The paired `0x1fdf0` panel sets origin `(20,20)` and performs two `7×2`
transfers: source `0x2fd892e` through `0x1dc90`, followed by source
`0x2fd894a` through `0x1dc10`. The following `0x1fe60` route preserves the
current origin and either transfers source `0x2fe0cb0` as `20×2` through
`0x1dc10` or clears that region through `0x1df00`. Both contracts are in
`recovered_panel11_panel12_routes.c`.

The fixed clear routine at `0x1fe90` uses `0x1df00` three times, clearing
regions `(4,10,33×8)`, `(22,10,38×8)`, and `(20,10,24×8)` in that order.
The sequence is captured by `recovered_multi_region_clear.c`.

The `0x1ff20` wrapper preserves the current text origin and uses height `5`
with width `g3+31`. Nonzero `g0` transfers source `0x2fe0b5c` through
`0x1dc10`; zero `g0` clears the same region through `0x1df00`. The contract
is implemented in `recovered_panel13_source_fill_route.c`.

The `0x1ff50` helper masks `(g0-48)` to four bits, selects a 2-byte table
entry from `0x2ea2090`, and transfers it through `0x1dc10` as `1×2` at the
current origin. It advances the current column by one unless that column is
already beyond `g30+31`; the lookup contract is in
`recovered_panel14_lookup_renderer.c`.

The `0x1ff90` block is another indirect-return thunk: it loads the return
stub at `0x1ffa4`, copies it to `g0`, clears `g14`, and branches through `g0`.
The `0x1ffb0` route writes explicit position `(4,17)`, height `5`, and width
`g23+31`; nonzero `g0` transfers source `0x2fe0f54` through `0x1dd10`, while
zero `g0` clears through `0x1df70`. Its route contract is implemented in
`recovered_panel15_source_fill_route.c`.

The `0x1fff0` route sets origin `(11,21)`, height `8`, and width `g9+31`.
It transfers source `0x2fdff54` through `0x1dc90` when `g0` is nonzero, or
clears the same region through `0x1df00` otherwise. Its contract is captured
in `recovered_panel16_source_fill_route.c`.

The `0x20060` status route first clears a `22×2` slot at
`(g11+31,g11+31)`. For values at or below `99` it emits the embedded
`"OVER 100 STRAIGHTS WINS"` string at that origin through `0x1d1f0`; the
other path is gated by the `1` comparison and runs the two-digit renderer
through `0x1ff50`, followed by fixed sources `0x2fdfc00` (`13×2`) and
`0x2fdfbfc` (`1×2`) at columns `g14+31` and `g27+31`. The instruction-level
route is captured in `recovered_streak_status_renderer.c`.

The lower-level call target at `0x000f5d40-0x000f5e80` is a general forward
non-overlap copy primitive, not a video-specific blitter. It selects aligned
16-, 8-, 4-, 2-, and 1-byte loops but has the standard byte-for-byte forward
copy contract captured by `recovered_memory_copy_forward()`. Its overlap-aware
sibling begins at `0x000f5e80` and remains separate.

The glyph writer at `0x0001d310-0x0001d410` masks characters to seven bits,
maps printable bytes `0x20-0x7f` to indices `0-95` and other inputs to index
zero, then selects one of four glyph tables using `font_mode & 3`. Each glyph
descriptor is eight bytes (a tile-word pointer and width). The writer copies
`width` words into two adjacent 64-tile rows at
`0x01000000 + 2 * ((row << 6) + column)`, ORs each with `0x8000` and the
caller attribute bits, and then advances the column by the width. The `0x5c`
glyph has one extra column of spacing. `recovered_text_emit_glyph()` preserves
the mapped-memory implementation; all 384 descriptors are verified against
the `main_data` ROM image by `von/tools/test_recovered_text_control.py`.

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

The input-free coverage trace also enters the helper at `0x00000a30`. Its
entire `0x28`-byte body is i960 ABI setup (`flushreg`, PFP marking, and first
spill-frame bounds), not game behavior. `start_reconstructed.s` supplies the
equivalent register-stack foundation before its first nested C call, so this
unit is classified separately from the reset copy/MMIO routine.

The same trace reaches `0x00018488` from the board-I/O failure dispatch. This
routine initializes a 16-byte host queue at `0x00504c60` to `0xff`, clears its
read/write indices at `0x00504c70/74`, and stores `0x00ff` sentinels at
`0x00504c78` and `0x00503312`. `recovered_host_queue.c` preserves those
effects and is conditionally called when the reconstructed I/O test fails.

### High-Frequency Attract Leaves

The 60-second input-free trace identifies `0x000f5058` as a heavily reused
31-bit pseudorandom step. It multiplies the state at `0x005785d0` by
`0x5d588b65`, then uses `chkbit 31` plus `addc high,high` to fold the 64-bit
product across bit 31. Clearing bit 31 leaves the new state in the range
`0..0x7fffffff`. `recovered_random_step()` expresses the arithmetic separately
from the MMIO-addressed state wrapper so deterministic vectors can be tested.

The leaf at `0x00073508` sign-extends its low 16-bit argument and returns one
of ten bands. Nonnegative boundaries are `0x038d`, `0x1554`, `0x3fff`, and
`0x5fff`; negative boundaries are `-0x6000`, `-0x4000`, `-0x1555`, and
`-0x038e`. Observed callers immediately use the result in halfword or word
lookup tables, supporting the classifier interpretation without assigning a
more specific gameplay name yet.

The cluster at `0x0002a458-0x0002a574` is the producer side of a 64-byte
host-to-SCSP command ring. Read and write indices live at `0x0051aa70/74`,
with bytes at `0x0051aa80`. The interrupt path at `0x000016dc` checks sound
status `0x009c0004`, removes one queued byte, and writes it to `0x009c0000`.
Normal 16-bit commands are framed as `0xae`, high byte, low byte; `0xff` is a
one-byte special case. After enqueue, `0x00001348` raises bit 10 in the host
control mirror and MMIO register to request service. The recovered source
keeps the capacity, enqueue, framing, suppression gate, and kick operations
separate enough for focused validation.

The `0x00001348-0x00001370` thunk is now represented as
`recovered_host_service_request()`, rather than being folded into the producer.
The command framing and all 64-by-64 ring-capacity combinations are covered by
`von/tools/test_recovered_audio_queue.py`; this validates the pure producer
semantics without dereferencing the target's MMIO addresses.

The corresponding consumer branch at `0x000016dc` is represented by
`recovered_audio_queue_consume()`. It requires a nonempty FIFO and SCSP status
bit 0, then reads one byte, advances the read index modulo 64, and writes the
value to `0x009c0000`. The reconstructed heartbeat polls bit 10 of the generated
control mirror and invokes the MMIO wrapper, while the state-only behavior is
covered across every read/write-index pair and representative status value by
`von/tools/test_recovered_audio_queue_consumer.py`.

The host interrupt-mask helper at `0x000017c8-0x000018a8` is now represented
by `recovered_host_interrupt_mask_update()`. It clears the requested bit in
`0x00501cd0` and `0xe80004`, reloads the timer selected by masks `4`, `8`,
`16`, or `32`, re-arms the bit, and writes the inverse mask to `0xe80000`.
The timer selection and reload table is checked for every 16-bit mask by
`von/tools/test_recovered_host_control.py`.

The warning-string helper at `0x0001da90-0x0001db34` scans bytes after the
first string byte. It selects glyph mode `1` when no lowercase ASCII byte is
present and mode `0` otherwise; `recovered_text_string_font_mode()` checks
that decision for all 65,536 two-byte prefixes. The reconstructed
`recovered_text_write_glyph_string()` then sends every non-NUL byte through
the mapped-ROM glyph writer at `0x0001d310` with zero attribute bits.

The common dispatcher begins at `0x00001380`. Its recovered gate clears the
requested source mask from `0x00501cd0` and `0xe80004`, then selects a
downstream route: mask `1` enters the system path, masks `2` and `0x800` enter
the fatal/unhandled path, `0x200` enters text/video service, and `0x400` enters
the audio FIFO consumer. Other values are acknowledged without a downstream
service. `recovered_host_interrupt_route()` records this route contract and
is exhaustively checked for all 65,536 16-bit masks; the side-effecting
downstream handlers remain separate work units.

The nonfatal dispatcher tail at `0x00001750-0x00001780` writes `~mask` to
`0xe80000`, then restores `mask` in both the `0x00501cd0` mirror and
`0xe80004` control register. `recovered_host_interrupt_acknowledge()`
preserves this acknowledgement/rearm sequence and is checked for every
16-bit source mask.

The bit-9 branch at `0x00001670` now maps to
`recovered_text_voltage_warning_interrupt_path()`: it performs the fixed
upload, resets text/video state, writes four voltage-warning records at
`(4,16)`, `(4,19)`, `(4,25)`, and `(20,28)`, then enters the fatal halt at
`0x000012d0`. That halt executes `flushreg` and loops forever; it remains
uninvoked by the reconstructed heartbeat.

The adjacent bootstrap at `0x0001bb8-0x0001c10` is represented by
`recovered_host_interrupt_initialize()`. It acknowledges with zero, loads
`0x61a80` into timer registers `0xf00004`, `0xf00000`, `0xf0000c`, and
`0xf00008` in the observed order, installs interrupt control `0x23d` at both
`0x00501cd0` and `0xe80004`, and clears `0x0051aac0`. The source is compiled
into the reconstruction, but active invocation waits for the unrecovered
interrupt dispatcher at `0x1380`: enabling this mask reaches the original
vector path before the current heartbeat can run. Its two constants are
checked alongside the exhaustive interrupt-mask table by
`von/tools/test_recovered_host_control.py`.

### Additional Audio Producer Helpers

Ghidra labels for the host-side audio boundary are maintained in
`von/ghidra/AnnotateVonI960.py`. The audio labels intentionally stop at the
host-to-SCSP interface: `audio_scsp_fifo_send_u16` and its idle-gated sibling
produce command bytes, `audio_scsp_initialize` performs the six-value SCSP
startup sequence, and `audio_scsp_fifo_consumer` drains one byte into
`0x009c0000` when status bit 0 permits it. The sample ROM is not itself an i960
address space; its sound assets belong to the separate 68000 program and must
be annotated from decoded SCSP descriptors rather than inferred from raw WAV
segments.

Five adjacent host-side audio units are now represented in
`von/i960/recovered_audio_queue.c`:

- `0x0002a430` is a four-iteration volatile countdown used to let SCSP
  register writes settle. The initializer calls it between its control writes.
- `0x0002a5f0` duplicates the u16 producer framing but suppresses normal
  commands when mode is 1 and the low board-status byte is 0. The `0xff`
  special case remains unconditional, matching the sibling at `0x2a4e0`.
- `0x0002a690` clamps a signed level to `1..127` and sends `0xa0, 1, level`.
- `0x0002a870` sends `0xa0, 0, low_byte(value)` without the clamp.
- `0x0002a8a0` initializes both FIFO indices, fills all 64 queue bytes with
  `0x99`, writes the SCSP control sequence `0, 0, 0, 0x40, 0x4e, 0x37`
  with five intervening short delays, and queues the `0xff` startup command.

The pure framing, clamp, delay-count, and initialization-constant helpers are
covered by `von/tools/test_recovered_audio_queue.py` and
`von/tools/test_recovered_audio_helpers.py`. The reconstructed main path now
invokes the SCSP initializer after geometry startup, so the bounded audio
startup sequence is part of the generated runtime rather than a disconnected
translation.

### Reused Geometry Service Boundary: `0x0002a990`

The attract worklist's next high-frequency host target is a fixed SHARC
service wrapper. It writes this request to the coprocessor FIFO at
`0x00884000`:

```text
5, 16, 20, (first & 0xffff), 21, (second & 0xffff), 26,
0xbf34fdf4, 0xbf34fdf4, 0x3f34fdf4
```

The wrapper then reads three response words, marks geometry command-window
offset `0xa0` with `0x0a0a`, forwards the first two responses followed by its
third argument to the geometry program port at `0x00804000`, and writes FIFO
completion word `6`. `recovered_geometry_service_packet()` isolates the
deterministic request framing for exhaustive testing; the MMIO wrapper retains
the response and forwarding order without assigning a meaning to the SHARC
service itself.

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
  Static audit against `0x28e88-0x28efc` confirms those operations and their
  order; it is represented in production C, though not byte-validated.
- `recovered_geometry_frame_submission()` reproduces the confirmed phase
  selection at `0x28de8`: initialize `0x00803008` from the prior phase, poll
  bit 2 of `0x0098000c` until it changes, toggle `0x00511ba0`, and write the new phase to
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
caller-side buffer producer. The `0x28b80` transformation is now closed at
the scalar and runtime-vector level: it uses the i960 floating-point
conversion helper at `0x28b40` to generate a byte-packed exponent ramp.
Compiler/ABI calibration still prevents claiming byte-for-byte C machine-code
identity, but the behavior itself is no longer an unresolved guess.

### Geometry Buffer Preparation: `0x00028b80`

The Ghidra report establishes the shape of the producer without assigning
field names:

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

`recovered_geometry_pipeline_startup()` now captures the full `0x28d80`
orchestration sequence. It first applies the profile constants, conditionally
uploads the SHARC bootstrap and geometry program when mode is zero, performs
the register/texture/command-window/handshake setup, then conditionally loads
textures and submits the auxiliary stream. Both paths prepare and submit the
host buffer before storing `0xffff` to `0x0181c000`. The individual helpers
remain separately named and verified; this caller preserves their ROM order.
Direct invocation from the reconstructed MAME harness now completes. The
earlier i960 `Unhandled 00` at PC zero was a register-stack spill failure: the
fifth nested C call exceeded the cached local-register frames before the
replacement startup had initialized `fp`, `pfp`, and `sp`. Initializing those
registers around `0x00500400`, matching the original startup convention,
allows the full zero-mode pipeline to reach INIT with a live heartbeat.

Two small startup helpers are now recovered in
`recovered_geometry_commands.c`: `recovered_geometry_initial_handshake()`
preserves the `0x28418` control/phase reset sequence, and
`recovered_geometry_register_clear()` preserves the `0x28d08` write of
`0x4004` to `0x10000000`. The larger texture initializer at `0x28548` remains
separate. `recovered_texture_initializer()` now covers that routine: two
127-entry `floor(index / 2)` ramps at `0x11400000`, followed by an `0x2080`-byte
copy from ROM address `0x02fb1d10` into `0x11401000`.

The `0x28418-0x28464` handshake is also built as an isolated C candidate in
`reconstructed_geometry_handshake.c`. The remote i960 build produces a
76-byte comparison image: 18 bytes match the original. The writes and values
are preserved, but ordinary C does not reproduce the original register
allocation or its `g0/g14` branch-link prologue and `bx (g0)` return. It remains
provisional until a C build can be byte-validated.

The texture initializer is likewise built as an isolated candidate in
`reconstructed_texture_initializer.c`. Its 172-byte comparison image matches
17 bytes of the original. The two 127-entry ramps and the `0x2080`-byte ROM
copy are behaviorally represented, but compiler loop and register choices keep
the slice provisional.

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
triple. `von/tools/test_recovered_geometry_profile.py` now checks all 256 byte
inputs and the 32-bit output ABI.

The continuation is now bounded more precisely, even though its floating-point
meaning is still open. After storing the selected triple, `0x28840` seeds a
lookup-table pass at `0x01818000`, uses `0x01800000` as the source-side base,
and iterates the low 16-bit index until the derived row reaches `0x40`. Each
pass emits to the `0x01818000` and `0x0181c000` regions, advances the source
halfword cursor, and packs four converted values into one word. A second pass
starts from the post-first-pass cursor and uses a `3 << 6` phase offset. The
routine finishes after the derived low-16-bit row wraps to zero. The operations
between `0x289d0` and `0x28aac` are i960 extended floating-point (`divrl`,
`logrl`, `roundrl`, `exprl`, `scalerl`); they are recorded as a table-generation
boundary rather than translated with host `float` semantics.

The texture/profile setup at `0x28120` displays the loading messages, calls
the loader `0x27e50` for two ROM-board/texture-bank ranges, and stores the
resulting profile state in `0x005039f4` and `0x00503a00`. Its first source
pointer is `0x02c00008`; the later bank uses `0x02c77438`. The loader returns
the decoder's nonzero shared status latch on failure.

`recovered_texture_loader_profile_setup()` now preserves the complete local
loader sequence: it places the static loading/Bank0/Done/Bank1 messages using
the recovered plain-text helpers, calls the decoder with `0x11000000/0x11200000`,
saves the second source at `0x00512bd0`, then calls the decoder with those
destinations swapped. A nonzero decoder result writes `0` and `5` to
`0x00503a00` and `0x005039f4` respectively. The broad printf-style formatter
remains separate, but this loader uses no format arguments and is now
semantically C-covered.

The loader target `0x27e50` is now labeled `texture_decompressor`. Static
analysis shows it initializes `0xfed` bytes at `0x00511bb0`, clears status at
`0x00515080`, reads a four-byte big-endian header from its source pointer, and
returns zero on the normal completion path or the status word at
`0x00515080` on the alternate path. The status latch is not assigned by the
decoder itself, so a nonzero result requires another device/interrupt path to
raise it during expansion. It writes decoded halfwords through the two
destination pointers supplied by `0x28120`. `von/i960/recovered_texture_decompress.c`
now contains a static candidate for the decoder: 12-bit ring-buffer
references, flag-byte token selection, literal/back-reference lengths, and the
palette-based secondary-bank test.

The recovered decoder is behaviorally validated against MAME's focused debug
write trace: all first 64 `vonj_texture_write` records match the C model's
destination address and halfword value. This is the valid evidence boundary;
the later full-RAM snapshots are not used because subsequent loader calls
reuse and overwrite both texture-RAM windows.

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

The latest linked run is preserved under
`von/captures/twin-vonj-20260901T165911Z/` with matching exported assets in
`von/build/disasm/player-select-twin/twin-vonj-20260901T165911Z/`. Both sides
reach the same scripted checksum checkpoints through frame 6900, while the
primary log records 3,766 `0x208f2` geometry-entry traces and 33 complete
`0x208ff`–`0x20908` interpolation sequences. This strengthens the
matrix-driven player-select integration evidence, but the address distribution
contains no execution of opcode `0x17` or helper `0x20de1`.

The event-sequenced trace makes an animated export possible without guessing:
each complete select-screen timestamp contains 40 object submissions, and
the latest matrix at each submission is its effective transform. The exporter
`von/tools/export_geometry_animation_gltf.py` emits 40 mesh nodes with
translation, rotation, and scale channels for 250 captured frames. Its output
is `von/build/disasm/player-select-animation.gltf`; the current animation is
the select-screen sequence, not a gameplay skeleton or a frame-swapped mesh.

The generated i960 path now consumes the corresponding 40-object slot list from
the exact `16.288808`-second frame in
`recovered_geometry_match_object_seed()`. This promotes the ripped
polygon-ROM player assemblies from an offline export into the visible
reconstructed display list, including the complete 37-matrix event sequence
for that captured frame.

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

The deterministic first-match capture now has a material trace as well. A
scene-focused patch begins recording texture commands at the observed
27.5-second transition, after the player-select submissions, and bounds the
stream at 16,384 records per cabinet. The linked passive capture reached
29.309 seconds before that bound while exposing 531 distinct texture-window
keys; 530 indexed PGM tiles were extracted from the primary decompressed
texture bank for each cabinet. The wrapper and profile are
`scripts/trace-geometry-material-twin.sh` and
`VON_MAME_PATCH_SET=geometry-material`; the wrapper now combines those records
with the palette/color-translation/luma trace and writes palette-rendered PNG
tiles into the UV-associated glTF material groups. The grayscale fallback keeps
the indexed texel values available when a palette trace is not present.

### UV-to-Tile Contract

Texture dumps use the Model 2 sheet's physical addressing rather than a
linear 2048x1024 image: logical X coordinates `1024..2047` are stored in the
other 1024x1024 bank, at `(x - 1024, y ^ 1024)`.  Tile extraction applies this
mapping before decoding packed 4bpp texels.

The texture-point stream is directly ordered as `pv, pu` 16-bit words per
vertex. MAME converts both values from 1/8-texel units before sampling, so the
exporter reads the pair as `(u=pu, v=pv)` and writes tile-local glTF coordinates
`(pu / 8 / width, pv / 8 / height)`. The texture-header origin identifies the
tile's source rectangle in the selected 2048-by-1024 texture sheet; it is not
added to the glTF coordinates because the exported PNG already contains that
cropped rectangle. Header bits 6/7 select U/V repeat, while bits 8/9 select
mirrored repeat and override the corresponding repeat bit. With neither flag,
the exporter uses clamp-to-edge, matching the renderer's non-smooth boundary
path. The first-match P1 capture has 8,893 textured polygon faces, all using
repeat on both axes; this validates the existing output for that capture while
preserving correct behavior for future clamp or mirror materials.

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

The available Model 2 documentation does not fill that gap. MAME's TGP
research notes identify the Model 2B substitution explicitly—two SHARCs replace
the earlier TGP devices—and state that the Model 2B coprocessor program is
uploaded rather than an exposed fixed-function instruction set. The notes also
direct readers to the Fujitsu TGP datasheet as the useful public documentation;
that datasheet describes the other Model 2 family, not the Virtual-On SHARC
program. Consequently, the ROM listing plus runtime traces remain the primary
source for opcode `0x17` and helper `0x20de1`, with the ADSP-2106x manual used
for instruction semantics.

The apparent C-side math in `model2.cpp` belongs to the older TGP path:
table-backed sine/cosine, atan, reciprocal, and inverse-square-root handlers
are implemented under `model2_tgp_state`. That path is not active for Model 2B.
Its renderer-side `clip_polygon` helper does contain a conventional edge-plane
interpolation, `scale = (distance - curdot) / (nextdot - curdot)`, but that is
not a match for the SHARC helper's scratch-derived products and reciprocal
refinement. It is therefore useful as a renderer convention reference only,
not as an implementation of `0x20de1`.
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

The primary architecture references are Analog Devices' [ADSP-21060/62 SHARC
data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ADSP-21060_21060L_21062_21062L_21060C_21060LC.pdf)
and [ADSP-2106x SHARC User's Manual, revision
2.1](https://www.analog.com/media/en/dsp-documentation/processor-manuals/50836807228561adsp2106xsharcprocessorusersmanual_revision2_1.pdf).
The manual is the relevant source for multifunction compute/memory
instructions, register-transfer restrictions, rounding modes, and the
fetch/decode/execute pipeline; the data sheet supplies the processor-family
and numeric-format summary.

The manual also gives a constraint that is easy to miss when translating the
ROM to ordinary C.  The bootstrap's `MODE1 = 0x00018000` sets both `TRUNC`
(round floating results toward zero) and `RND32` (use the 32-bit floating
point boundary).  With `RND32` set, the SHARC clears the low eight bits of
each 40-bit floating-point input before an ALU or multiplier operation and
clears the low eight bits of the result.  The recovered services therefore
should not be validated only with host `float` arithmetic: ordinary vectors
can agree while values near a rounding boundary differ by one or more low
bits.  The current C models intentionally retain their tested normal-path
contracts; boundary-focused probes are the next validation step for the
reciprocal and `RSQRTS` chains.

### SHARC Service Dispatcher

The corrected 6-byte-to-8-byte program packing exposes the startup dispatcher.
Initialization at program slots `0x092-0x11d` builds a table at SHARC data
memory `0x00030000`. The main loop then:

1. Waits for FIFO input flag 0 to become non-empty.
2. Reads an opcode and masks it to the low byte.
3. Loads `DM(0x00030000 + opcode)` as an indirect program address.
4. Calls that address in the `0x20000` program-memory bank.

The extracted table writes begin at listing slot `0x99`, corresponding to DM
`0x30099`; the preceding entries are setup data. Consequently the verified
opcode-to-target relation for the later services is `table slot = opcode +
0x99`: `0x17 -> 0x2034a`, `0x18 -> 0x2038e`, `0x1a -> 0x2039b`, and
`0x1e -> 0x203dc`. The complete checked mapping is recorded by
`von/tools/test_sharc_dispatch_table.py`.

The bootstrap instruction at slot `0x080` sets `MODE1 = 0x00018000`. Under
the ADSP-2106x definition this enables truncation (`TRUNC`, bit 15) and the
32-bit floating-point rounding boundary (`RND32`, bit 16), so the published
reciprocal refinement should be interpreted in 32-bit/truncating mode unless
a later service changes `MODE1`.

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
The `0x00`, `0x01`, and `0x02` bodies are now statically bounded as the same
two-input service shape: two FIFO reads into `R0`/`R1`, one persistent-register
operation on `F0`/`F1`, and one output-FIFO write. A focused interpreter trace
resolved the apparent register-name ambiguity: in MAME's SHARC core the
floating aliases expose the same raw register lanes, so the first FIFO read
changes the F0 lane at `0x20135`, the second changes F1 at `0x20137`, and the
operation result is visible in F0/R0 two instructions later. The captured
vectors are `1 + 2 = 3`, `2 - 1 = 1`, and `0.5 * 2 = 1`, with each result
following the expected output-FIFO write. The trace hook is reproducible with
`von/tools/probe_sharc_scalar_services.lua` and guarded by
`von/tools/test_sharc_scalar_trace_patch.py`.
The adjacent `0x03` and `0x04` handlers share the same two-input/output FIFO
shape and the three-stage reciprocal refinement. A focused interpreter trace
now resolves their service-boundary staging: `0x03` reads the first operand
into F0/R0 and the second into F12/R12, returning `2.0`, `0.5`, and `-2.0`
for `(2.0,1.0)`, `(1.0,2.0)`, and `(-2.0,1.0)`. Its recovered contract is
the numerator/denominator quotient using the ROM's RECIPS seed and three
32-bit correction boundaries. `0x04` stages the second word into F2/R2 and
copies the first through R7 into F1/R1 before its final subtraction; it
computes `first - (first/second)*second`, normally zero but preserving the
small reciprocal residual (the live pair `(1.7, 1/3)` returns `0xb4000000`).
The expanded trace is reproducible with
`von/tools/probe_sharc_reciprocal_services.lua` and the isolated `0x04` probe;
the recovered finite models are in
`von/i960/recovered_sharc_reciprocal_services.c` and guarded by
`von/tools/test_recovered_sharc_reciprocal_services.py`.
These bodies are guarded by `von/tools/test_sharc_reciprocal_services.py`;
the Analog Devices manual defines `RECIPS` as an 8-bit reciprocal seed: its
exponent is `-e - 1` for input exponent `e`, with the mantissa selected from a
ROM table. The manual's published division sequence is the same three-stage
Newton refinement recovered here and requires `F11 = 2.0`; the final result is
accurate to one LSB in the selected 32- or 40-bit mode. This resolves the
reciprocal algorithm itself. Persistent-register staging, exception behavior
at the service boundary, and FIFO timing remain to be validated.
The listing also makes the operand staging concrete: the first FIFO word is
loaded into `R0` and copied to `R7` in parallel with `RECIPS F12`, while the
second word is loaded into `R12`/`F12`; `F1` and (for `0x04`) `F2` are not
loaded by these handlers.

An exception-boundary post-boot capture is available in
`von/tools/probe_sharc_reciprocal_edges.lua`. In the current MAME SHARC core,
`0x03` returns `0xffffffff` for `1/0`, `1/+inf`, `NaN/1`, and `1/NaN`, returns
`0x00000000` for `0/1`, preserves `+inf` for `+inf/1`, and preserves the
smallest positive denormal for `denormal/1`. The tested `0x04` residual cases
`1/0`, `1/+inf`, and `NaN/1` also return canonical `0xffffffff`. These are
valuable compatibility observations, but remain emulator-boundary evidence;
the recovered C contracts intentionally remain finite-only until a hardware
or authoritative SHARC exception trace confirms the policy.
The same ten-vector probe was run with both MAME's default DRC and `-nodrc`
interpreter; all FIFO words matched exactly. The captured logs can be checked
with `von/tools/verify_sharc_reciprocal_edges.py`, including a two-log parity
comparison.

The preceding state services are now bounded as well. Opcode `0x05`
increments the state index at DM `0x30100` up to seven, copies twelve words
through the current pointer at DM `0x30101` using an 11-word offset, and saves
the advanced pointer. Opcode `0x06` decrements the same index when nonzero and
subtracts twelve from the pointer without touching the FIFO. Opcode `0x07`
consumes twelve FIFO words (`R0..R11`) and stores them sequentially through the
state pointer. These exact shapes are guarded by
`von/tools/test_sharc_state_services.py`; the meaning of each state window is
still pending correlation with the vector consumers.
Opcode `0x09` is the larger state-preparation boundary immediately after
these controls. It consumes twelve FIFO words in four three-word groups,
combines each group with the nine coefficient words reached through DM
`0x30101`, and writes four transformed triplets back to offsets `0x00..0x0b`
of that state buffer. For each input `(x,y,z)`, the output is
`(x*s0+y*s3+z*s6, x*s1+y*s4+z*s7, x*s2+y*s5+z*s8)`; this is the same
column-dot ordering used by opcode `0x1a`, with no translation-tail term.
The reusable model is `von/i960/recovered_sharc_opcode_09.c`, covered by
`von/tools/test_recovered_sharc_opcode_09.py`. A caller-level packet is now
identified in the main-CPU listing at `0x41fbc..0x41ff4`: the branch emits
SHARC opcode `0x05` to advance/select a state window, emits opcode `0x09`, and
then feeds three quadwords from the current host record at offsets `+0x08`,
`+0x18`, and `+0x28`. These are three four-element lanes, not three complete
records: the FIFO order is `[x0,x1,x2,x3,y0,y1,y2,y3,z0,z1,z2,z3]`, and the
SHARC's three-at-a-time reads therefore form `(x0,y0,z0)` through
`(x3,y3,z3)`. This establishes the four transformed triplets as a
twelve-word derived state block associated with one host record, rather than
an isolated test service. The semantic names of the three lanes remain
unresolved. A bounded runtime diagnostic for this exact caller is preserved
in `third_party/patches/0022-von-opcode-09-caller-tracing.patch`; passive and
scripted 35/75-second captures did not reach `0x41fbc` because diagnostic
logging slowed emulated time and the scripted path remained in its pre-match
transition, so they are not treated as runtime coverage. The apparent
`0x09` values at
i960 `0x8e3e0` in the gameplay trace remain payloads of preceding host command
`0x2e` packets and are not evidence of this direct call.
The object constructors at `0x3f600` and `0x3f6e0` first request twelve
state-readback words with FIFO command value `17` (SHARC opcode `0x11`) and
store them contiguously at `+0x08..+0x34`. Since opcode `0x11` reads the
selected twelve-word state window, these fields are snapshots of that window:
state words `0..3`, `4..7`, and `8..11` occupy the three object lanes. The
neighboring object-update paths at `0x420e4` and `0x421cc` reuse the same
`+0x08`, `+0x18`, and `+0x28` four-word loads for opcode `0x07`. This makes the
object layout itself stronger than the currently unavailable runtime call:
the state-readback payload is consumed as three lane-major four-element arrays,
`(s0..s3,s4..s7,s8..s11)`, yielding triples `(s0,s4,s8)` through
`(s3,s7,s11)` in opcode `0x09` and uploaded unchanged by opcode `0x07`. With
the established row-major matrix plus translation-tail state layout, those
triples are `(M00,M11,M22)`, `(M01,M12,T0)`, `(M02,M20,T1)`, and
`(M10,M21,T2)`. Their higher-level role (vertices, bounds, or another
geometry primitive) remains intentionally unnamed. The cross-path lane invariant is
guarded by `von/tools/test_recovered_sharc_opcode_09_caller.py`, and the
state-to-vector mapping is explicit in
`recovered_sharc_opcode_09_state_vector()` and its model test.
The surrounding main-CPU packet narrows the state lifetime without naming the
four vectors: after the three opcode-`0x09` quadwords, it emits command value
`31+27 = 58` (SHARC opcode `0x3a`), whose handler copies the seeded table from
DM `0x30141` to a host-derived destination, and later emits opcode `0x06` to
move the selected state window back. There is no immediate opcode `0x10`,
`0x11`, or `0x12` in this packet. Those services remain static consumers or
state utilities elsewhere: `0x11` reads the complete selected window, while
`0x12` accumulates a vector into its translation tail. This establishes the
producer/packet boundary but does not justify calling the four transformed
triplets vertices, planes, or another named primitive yet.
The stores at offsets `0x0a` and `0x0b` occur in the delayed-return slots.
The exact packet shape and all twelve output destinations are guarded by
`von/tools/test_sharc_matrix_state_service.py`; the coefficient layout's
mathematical meaning remains unresolved.
Opcode `0x0a` (`0x20211`) is a separate two-input scalar boundary. It reads
the first word into `R1`, then reads the second word into `R0` in the CALL's
delayed slot, so helper `0x20d68` starts with the register pair `(R0,R1)`.
After loading the fixed scale word `0x4622f83d`, it multiplies, applies `FIX`,
and emits one result. The recovered C model exposes both the register-order
entry point and a host-packet-order wrapper; this prevents the delayed-slot
staging from being mistaken for a C argument order. The delayed call/return
arrangement is guarded by `von/tools/test_sharc_opcode_0a.py`.
Opcode `0x0b` (`0x2021b`) is bounded as a nine-input vector service. Its
FIFO reads populate `R8,R9,R10,R12,R13,R14,R8,R8,R8`; the body forms the vector
intermediates, normalizes them with `RSQRTS F0` and three correction rounds,
then emits three results from `R0`, `R1`, and `R2`. The third output is in the
delayed-return slot after `RTS (DB)`. This exact packet and output shape is
guarded by `von/tools/test_sharc_opcode_0b.py`; the source-vector field
meaning is now bounded for the finite path: the first six words form two 3D
endpoints, the next two form the XY components of the second vector with
implicit Z=0, and the ninth word is consumed after those operands have been
formed without affecting the recovered arithmetic. A dispatcher-aligned
interpreter-backed probe confirms the normalized cross product `(A-B) x
(ex,ey,0)` and exact baseline output `0xbf34b4b4, 0x3f34b4b4, 0xbd70f0f0`.
The same probe confirms canonical NaN output (`0xffffffff` in all lanes) for
zero, degenerate, NaN, infinity, and denormal endpoint packets. The semantic
model and exact vector test are in
`von/i960/recovered_sharc_opcode_0b.c` and
`von/tools/test_recovered_sharc_opcode_0b.py`. A status-aware, dispatcher-
aligned MAME probe confirms the same zero-vector result through a non-empty
response FIFO. Other exceptional numerical behavior remains provisional.
Opcode `0x0c` (`0x2024e`) is the adjacent three-input normalization service.
It reads `R6`, `R9`, and `R5`, forms their sum of squares in `F0`, computes
`RSQRTS(F0)` with three correction rounds, and emits the normalized components
through `R0`, `R1`, and `R2`. The third output is in the delayed-return slot.
Its exact packet, accumulator, and output shape are guarded by
`von/tools/test_sharc_opcode_0c.py`. An interpreter-backed forced runtime
probe confirms `(3,4,12)` emits `0x3e6c4ec4, 0x3e9d89d8, 0x3f6c4ec4` and a zero
vector emits canonical SHARC NaN `0xffffffff` in all three lanes. The C model
in `von/i960/recovered_sharc_opcode_0c.c` implements the shared seed and
three-round refinement. The dedicated edge probe
`von/tools/probe_sharc_opcode_0c_edges.lua` additionally establishes
all-lane canonical NaNs for zero, signed zero, standalone denormal, and NaN;
infinity preservation for infinite axes; the `0x1f800000` `RSQRTS(+inf)`
artifact for finite lanes beside infinity; and denormal preservation in the
final finite normalization multiply. These cases are checked by
`von/tools/test_recovered_sharc_opcode_0c.py`; other mixed nonfinite
combinations remain provisional.
The dedicated probe `von/tools/probe_sharc_opcode_0c_rounding.lua` also
exercises adjacent-ULP, cancellation, and large-magnitude inputs. Live output
is reproduced by `von/tools/test_recovered_sharc_opcode_0c.py`: the asymmetric
pair returns `0x3f3504f3,0x3f3504f4,0`, cancellation returns
`0x3f3504f4,0xbf3504f3,0`, and the large mixed vector returns
`0x3f13cd3a,0x3f13cd3a,0x3f13cd3b`. A dedicated bounded `0x0c` logger keeps
startup output from consuming the result evidence budget.
Opcode `0x0d` (`0x2026d`) is a one-word pointer-publication service. It consumes
`R0`, calls helper `0x20d5d`, and returns through the delayed `RTS` at `0x270`.
The apparent reads at `0x272..0x278` are the start of opcode `0x0e`, not part
of this handler. The helper treats the word as a base/index for external table
reads at `base + 0x01c00010` and `base + 0x01c00020`, adds `0x01c00000` to
each fetched word, and publishes derived pointers at DM `0x30103` and
`0x30104`. A forced interpreter probe that incorrectly
queued four payload words left the three extra words for the dispatcher and
reproduced the `R0=0xbf000000` corruption; this is now understood as a packet
framing error. The one-word boundary is guarded by
`von/tools/test_sharc_opcode_0d.py`,
`von/i960/recovered_sharc_opcode_0d.c`, and
`von/tools/test_recovered_sharc_opcode_0d.py`.
Opcode `0x0e` (`0x20271`) is the actual four-word state-upload service. It
consumes `R0,R1,R2,R3`, stores them at DM `0x30105..0x30108`, and places the
last two stores in the delayed-return slots. Its corrected shape is guarded by
`von/tools/test_sharc_opcode_0e.py`.
Opcode `0x0f` (`0x2027e`) is a four-input difference service. It reads
`R1,R0,R3,R2`, forms `F1 = F1 - F3` and `F0 = F0 - F2`, calls helper
`0x20d68`, multiplies by `0x4622f83d`, applies `FIX`, and emits one result.
Runtime probes establish that the helper is a signed angle reduction: the
first difference is the X component and the second is Y, with the result
scaled to signed 16-bit angle units. `(x,y)=(0,1)` emits `0`, `(1,0)` emits
`0x3fff`, `(1,1)` emits `0x1fff`, and `(0,-1)` emits `0xffffc000`.
The negative-axis result confirms signed two's-complement angle units, while
the negative-X axis emits `0x7fff` for the positive π endpoint. The provisional
C model is in
`von/i960/recovered_sharc_opcode_0f.c`, with isolated probes in
`von/tools/probe_sharc_opcode_0f_single.lua`.
Opcode `0x10` (`0x2028e`) initializes the state pointer at DM `0x30101` with
the 12-word identity block `(1,0,0,0, 1,0,0,0, 1,0,0,0)` using raw IEEE words
`0x3f800000` and `0x00000000`; the final two stores follow `RTS (DB)`.
Opcode `0x11` (`0x2029e`) is the matching 12-word state readback: it loads
the pointer from DM `0x30101`, reads sequentially with `M1`, waits for each
output slot, and emits twelve words, with the last write delayed after `RTS`.
Opcode `0x12` (`0x202c5`) consumes three inputs, reads state-tail offsets
`0x09..0x0b`, walks coefficients `0x00..0x08`, and writes the tail back. Its
arithmetic is `tail[column] += sum(vector[row] * matrix[row,column])` for each
of the three columns. This matrix-vector tail accumulation is modeled in
`von/i960/recovered_sharc_opcode_12.c` and guarded by
`von/tools/test_recovered_sharc_opcode_12.py`.
Opcode `0x13` (`0x202dc`) consumes three inputs, scales coefficient row 0 by
`R0`, row 1 by `R1`, and row 2 by `R2`, then writes all nine matrix words. The
row-scaled writeback is modeled in `von/i960/recovered_sharc_opcode_13.c` and
guarded by `von/tools/test_recovered_sharc_opcode_13.py`; identity state plus
`(2,3,4)` produces diagonal `(2,3,4)` state. Higher-level transform meaning
remains provisional.
Opcode `0x14` (`0x202f6`) is the scalar projection variant writing offsets
`0x03,0x06,0x04,0x07,0x05,0x08`. Opcode `0x15` (`0x20312`) writes
`0x00,0x06,0x01,0x07,0x02,0x08`, and opcode `0x16` (`0x2032e`) writes
`0x00,0x03,0x01,0x04,0x02,0x05`; all reuse the signed-16/helper/scale path
and delayed-return stores. These matrix-field descriptions are guarded by
the corresponding structural tests and remain provisional at caller level.
Runtime tracing with `von/tools/probe_sharc_rotation_zero.lua` now confirms
the 0x14 dispatch reaches `0x202f6`, executes the `0x20dbe`/`0x20dc4` helper
pair, and falls through the six-store sequence; the neighboring 0x15 and
0x16 handlers are also observed in the live command stream. The probe does
not yet establish the angle sign convention or caller-level axis meaning.
The zero-input trace also shows the stores target the current state window
through `I7` (for example, `0x30200` and `0x3021b` in different frames), so
the earlier non-identity readback was live-state traffic rather than proof
that the initializer or rotation command failed.
An atomic FIFO snapshot (`0x10`, `0x14` with payload zero, then `0x11`)
returns the stable matrix words
`3f800000,0,0,0,3f7fffff,0,0,0,3f7fffff` (followed by three zero tail
words). Thus the zero-angle path preserves identity structure while the
ROM's fixed-point helper produces cosine `0x3f7fffff`, one representable step
below exact `1.0`; this is now a runtime oracle for future nonzero-angle
probes.
With payload `0x4000` (approximately π/2), the same snapshot returns
`[1,0,0 / -0,0,-1 / 0,1,0]`, with cosine `0xb8492eef`. This confirms the
0x14 X-axis row-pair operation `row1' = cosine*row1 - sine*row2` and
`row2' = sine*row1 + cosine*row2`. The semantic model is implemented in
`von/i960/recovered_sharc_opcode_14.c` and checked by
`von/tools/test_recovered_sharc_opcode_14.py`.
The sibling atomic snapshots confirm the same convention for opcode 0x15:
`[cosine,0,sine / 0,1,0 / -sine,0,cosine]`, a Y-axis rotation, and opcode
0x16: `[cosine,-sine,0 / sine,cosine,0 / 0,0,1]`, a Z-axis rotation. Their
semantic models are implemented in `recovered_sharc_opcode_15.c` and
`recovered_sharc_opcode_16.c`, with matching recovered-model tests.
Opcode `0x17` (`0x2034a`) begins a streamed table/geometry service. It
consumes three FIFO words (`R0`, `R8`, `R9`), selects a record through the
table pointer at DM `0x30103`, and uses the selected value as a `M7` offset
into the 16-word state source rooted at DM `0x30104`. Each selected record is
copied into the scratch window at DM `0x3010b..0x3011a`; a four-iteration
arithmetic loop forms a signed 2×2 determinant from scratch-window
differences, skips the helper on an equal/zero determinant, and otherwise
calls helper `0x20de1` before emitting two words into the result stream. The
zero-determinant branch therefore emits no pair and does not advance the
result count; only the nonzero path reaches the save/call/restore/increment
sequence. Accounting for SHARC parallel-assignment timing, the gate is the
exact 2×2 determinant
`(R8 - record[3]) * (record[2] - record[5]) - (R9 - record[5]) *
(record[0] - record[3])`; the selected 12-word record is naturally four
contiguous 3-word groups, even though the later helper accesses those groups
through aliased register offsets. The handler also
maintains a result count in `R15`, publishes it through DM `I1`, and drains
queued result pairs until the count reaches zero. The per-record pair is
specifically `[helper R0, selected-record R14]`: the selected record value is
saved across the helper call, restored, and written beside the computed word.
The record staging is now explicit as well: the selected record's count at
`DM(I6,M1)` controls the outer loop; each record copies 12 words into the
scratch window, then mirrors scratch offsets `0..2` into offsets `0x0c..0x0e`
before the four-pass determinant loop. After processing, queued pairs are
drained in an `R15`-counted loop, with `FLAG1_IN` waits before each output.
These transfer and drain boundaries are enforced by
`von/tools/test_sharc_opcode_17.py`.
This establishes the packet/table/scratch-flow and output-pair shape. The
normal projected-geometry semantics are now resolved by the helper analysis
below; only the helper's sentinel meaning and the caller's downstream use of
that sentinel remain open. The structure is guarded by
`von/tools/test_sharc_opcode_17.py`.
The focused runtime probe `von/tools/probe_sharc_opcode_17.lua` now reaches
`0x2034a` after a one-word 0x0d setup and a three-word 0x17 header. With the
currently initialized table, the selected record count is zero, so the ROM
takes the `0x20357 -> 0x2037f` degenerate path and emits exactly one zero
word; helper `0x20de1` is not called. This validates the live packet boundary
and zero-record branch. The companion probe
`von/tools/probe_sharc_opcode_17_nonzero.lua` seeds the internal table and
record bank, then drives the same ROM handler through the nonzero path: a
one-record table copies 12 words into `0x3010b..0x30116`, reaches helper
`0x20de1`, and emits the count/pair stream `0x00000001`, `0xbcdd67c8`,
`0x00000000`; the first pair value is `-0.0270270258` as an IEEE float. The
asymmetric synthetic record reaches the normal helper return at `0x20e4d`,
while the static sentinel path at `0x20e51` remains separately identified.
The coordinate frame and natural four-point record format are now resolved for
the normal path. The controlled sentinel fixture gives a useful negative
result: all four records have a nonzero plane Y-normal (`-1`) yet take the
early `0xbdcccccd` path. The sentinel is therefore not
the ordinary zero-Y-normal division case; it is an earlier record-local
validation/equality condition. Transcribing the aliased-register schedule at
`0x20e32..0x20e39` gives a provisional register-level equality condition; an
earlier attempt to map it directly to record coordinates was too strong and
has been removed from the recovered model. Its caller-side meaning remains
open. A separate runtime contrast probe feeds
two independently selected normal fixtures through the same opcode-0x17
protocol: both reach `0x20e4d`, avoid `0x20e50`, and emit the stream
`0x00000002, 0xbcdd67c8, 0x00000000, 0xbf7fffff, 0x00000001`.
Together with the four sentinel captures, this supports the predicate as a
record-local branch condition across both observed paths and selector-bank
stride, but does not yet prove its universal geometric meaning or the caller's
downstream clipping role.
The contrast is replayable with `von/tools/probe_sharc_opcode_17_prevalidation_contrast.lua`
and `von/tools/verify_sharc_opcode_17_prevalidation_contrast.py`.
The instrumented 35-second twin capture
`von/captures/twin-vonj-20260901T052223Z/` also contains repeated host-side
`0x0d`/`0x17` writes, but its SHARC trace never reaches `0x2034a` or helper
`0x20de1`. Those writes are therefore a separate i960/geometry command path,
not evidence of a populated SHARC table record.
Opcode `0x1a` (`0x2039b`) is a three-input state-output
service. It consumes `R0,R1,R2`, seeds three accumulators from the persistent
tail words at offsets `0x09..0x0b`, and adds the nine input/coefficient
products in coefficient order `0,3,6,1,4,7,2,5,8`. This is therefore an
affine 3x3 transform of the form `tail + matrix * vector`. In the stored
row-major layout, output component `j` is
`tail[j] + x*state[j] + y*state[3+j] + z*state[6+j]`. It emits the three
accumulated results to the output FIFO, with the third output in the delayed
slot after `RTS (DB)`. The host selector that names this target
is established by the jump-table mapping above; the contract is tracked by target address in
`von/tools/test_sharc_service_2039b.py`.
The focused runtime probe `von/tools/probe_sharc_service_1a.lua` confirms the
live boundary: after identity initialization, a three-word `(1,2,3)` request
reaches `0x2039b` and emits exact `1.0`, `2.0`, and `3.0` words at `0x203af`,
`0x203b1`, and `0x203b4`. This validates the identity-case affine path and
output ordering. The scaled runtime probe
`von/tools/probe_sharc_service_1a_scaled.lua` then installs diagonal `(2,3,4)`
through opcode `0x13` and sends `(1,2,3)` to `0x1a`; the service emits exact
`2.0`, `6.0`, and `12.0`, confirming the coefficient order against
non-identity matrix state.
The split-packet probe `von/tools/probe_sharc_opcode_07_affine.lua` loads all
twelve state words through opcode `0x07` (identity matrix plus tail
`(10,20,30)`), then sends `(1,2,3)` to `0x1a`. Live output tracing records
`0x41300000`, `0x41b00000`, and `0x42040000` (`11.0`, `22.0`, `33.0`), directly
confirming that offsets `0x09..0x0b` are additive translation terms and that
opcode `0x07` can initialize the complete affine state in one 12-word load.
The reusable semantic model is implemented in
`von/i960/recovered_sharc_opcode_1a.c` and checked by
`von/tools/test_recovered_sharc_opcode_1a.py`. Remaining uncertainty is
limited to exceptional-value/40-bit floating behavior, which belongs to the
generic SHARC emulation work rather than this service contract.
The shared helper at `0x20de1`, called by `0x2034a` (opcode `0x17`), now has a
resolved geometric interpretation. The twelve staged words are four points
`P0..P3`, each stored as `(x,y,z)`. The normal path forms the cross product
`N = (P2-P0) × (P3-P0)`, then evaluates the plane through `P0`, `P2`, and
`P3` at the caller's `(R8,R9) = (x,z)` pair:
`R0 = (Nx*x + Nz*z - dot(N,P0)) / (-Ny)`. This is the missing `y`
coordinate, not a boolean gate or an inverse-bilinear weight. For example,
the first nondegenerate synthetic record gives `(30*x + 9*z - 1) / 37`,
while translated records produce the independently observed constants
`+36/37` and `-31/37`. A fresh long nonzero probe now captures
the complete `0x20de1..0x20e53` instruction path, not just entry/exit: it
shows the scratch-derived edge differences at `0x20de6..0x20dea`, the
reciprocal-denominator construction beginning at `0x20e3e`, reciprocal
refinement at `0x20e45..0x20e4c`, and the exact normal return `0xbcdd67c8` at
`0x20e4d`. The helper shape is guarded by
`von/tools/test_sharc_helper_20de1.py`, and the reusable plane model by
`von/tools/test_recovered_sharc_helper_20de1.py`.
The helper's branch mechanics are now pinned down further: its normal path
forms the reciprocal denominator `F8 - F12`, refines it through `RECIPS`, and
uses the refined value to produce the saved intermediate `F15`. The alternate
path performs the corresponding `F1/F5` and `F4/F2` products, then normalizes
the derived result; the equality tail permutes scratch words `6..8` back into
`3..5`, while the terminal tail returns `0xbdcccccd` (`-0.1`). These are
dataflow facts about the alternate paths; the sentinel/equality geometry and
clipping rule remain open. The
seeded nonzero opcode-0x17 probe reaches `0x20de1` with a nonzero caller
determinant and exits through `0x20e4d`, returning `0xbcdd67c8`
(`-0.0270270258`). The static `0x20e51` path returns the explicit
`0xbdcccccd` (`-0.1`) sentinel. This validates the live normal return while
leaving the sentinel vector and natural interpolation inputs for future work.
An isolated run of the deliberately zero-`Ny` record-2 fixture provides the
important counterexample: one nonzero caller determinant still enters
`0x20de1`, reaches `0x20e4d`, and emits an exact-zero result, with no
`0x20e50` sentinel return. The capture is replayable with
`von/tools/verify_sharc_opcode_17_degenerate_trace.py`; it prevents the
zero-plane condition from being conflated with the helper's separate
`F9 == F14` equality tail.
The existing controlled sweep now also confirms the sentinel mechanics: each
`0x20e50` return is reached through the `0x20e3a` equality branch, with the
compared `F2` subtraction reduced to signed zero, and does not enter the
`0x20e45` reciprocal-refinement path. This establishes the branch predicate's
floating-point shape without overclaiming that it is identical to a zero plane
normal. Replaying the parallel assignments at `0x20e32..0x20e39` sharpens the
predicate: the exact `0x20e32..0x20e39` schedule forms
`F14 = (F11 - F13) * (F11 - F15)` through the temporary aliases `F0` and
`F6`, then forms `F15 = F2_old * F4` and the compared new `F2` as
`F2_old * F4 - F14`. Therefore the `IF EQ` tests the post-schedule equality
`F9 == F14` (the subtraction result is `F2`), under SHARC signed-zero
equality. A separate zero-`Ny` record reached normal
return with exact zero, proving that the sentinel is this intermediate-product
condition, not a generic plane degeneracy test. The geometric interpretation
of the condition and its caller-side clipping role remain open.
The debug patch now also records every instruction in the helper range
`0x20de1`–`0x20e53`, all floating registers, and scratch words `0..8` with a
bounded `4096`-line budget. The fresh capture is
`von/build/disasm/von-sharc-opcode-17-nonzero-current20.trace`; its step-level
sequence is now an executable regression when that artifact is present, while
the checked-in entry/exit trace remains the portable baseline. The remaining
work is to pin down the exact sentinel/equality geometry and the caller's
clipping predicate; the normal-path coordinate mapping is resolved.
The controlled simple-plane capture
`/tmp/von-sharc-17-sentinel-geometry4.trace` varies `P1`, `P2`, and `P3`
while holding the caller at `(x,z)=(1,1)`: all four accepted helper entries
take `0x20e50` and emit `0xbdcccccd`, while the caller still rejects some
earlier samples through its determinant gate. The portable capture verifier
is `von/tools/verify_sharc_opcode_17_sentinel_geometry.py`; this is a bounded
negative result, not a generalized geometric interpretation of the sentinel.
The same four-case probe was rerun against the rebuilt local MAME target with
the headless SDL backend. All four cases completed, reproduced the four
`0x20e50` returns and selected-record zero words, and passed the portable
verifier. This confirms that the result is stable across the rebuild; it does
not by itself resolve the sentinel's caller-side geometric meaning.
In all four accepted cases, `F2` is already exact zero at `0x20e32`, so this
record family enters the later equality tail with `F11 == F15` before the
remaining product chain is evaluated.

The equality tail is now represented as an executable schedule in
`recovered_sharc_helper_20de1.c`. It takes only the inherited words
`F11`, `F13`, old `F14`, and old `F15`; `F2` and `F4` are overwritten inside
the `0x20e32..0x20e39` sequence. The model reproduces the rebuilt capture's
three `F11=0` cases and one `F11=1` case as `F9=F14` with final `F2=+0`, and
rejects the normal captured tuple `F11=8`, `F13=1`, old `F14=5`, old `F15=5`.
This narrows the continuation boundary to four inherited state words, while
the caller-level geometric meaning of that state remains open.

The helper trace was then corrected to label the previously omitted `F15`
register. A rebuilt MAME capture of the existing four-input normal sweep
records four identical `0x20e32` tuples `F11=8.0`, `F13=1.0`, `F15=5.0`, and
all four take the normal return. This makes the branch inputs directly
observable and removes a diagnostic ambiguity, but does not by itself identify
which staged point coordinates those registers represent.

The probe harness now resets opcode `0x0d` asynchronously before each case,
waits ten emulated frames, and only then reseeds `DM(0x30103)` and queues
opcode `0x17`; queuing those writes in one callback lets the completed `0x0d`
handler overwrite the seeded pointer. The corrected first eight outputs remain
bit-identical to the earlier record-1 oracle. This framing requirement is
part of the probe methodology, not a new claim about the helper's formula.
The companion nondegenerate sweep
`von/build/disasm/von-sharc-opcode-17-helper-sweep-current45-nondegenerate.trace`
adds a numeric constraint: for its fixed synthetic record, with auxiliary
inputs `a` and `b`, the normal return is exactly consistent across eight cases
with `(30*a + 9*b - 1) / 37`, including negative and greater-than-one inputs.
The emitted words are `bcdd67c8`, `3e722983`, `3f000000`, `3f83759f`,
`bf8a60dd`, `3e983759`, `3ee0dd67`, and `4005306e`. This is deliberately
record-specific evidence for an affine/interpolation result, not yet the
general coefficient formula; the degenerate record sweep independently takes
the documented `-0.1` sentinel path.
The delayed-reset trace refines that accounting: it contains twelve helper
entries, ten nonzero-return samples (the eight record-1 points and the two
later synthetic points below), followed by two later synthetic samples whose normal return is
exact zero. Those final samples are distinct from the caller's zero-count
branch; a selected record can reach `0x20e4d` while the helper result itself is
zero.
The pairing can be regenerated with
`python3 von/tools/analyze_sharc_opcode_17_trace.py <trace>`; on the delayed
reset capture it reports 12 paired normal returns and 2 exact-zero results.
The caller-level composition is now represented by
`von/i960/recovered_sharc_opcode_17_projection.c`, which connects selector
staging, the determinant gate, and the normal plane evaluation while retaining
distinct invalid, zero-gate, and helper-degenerate statuses. Its model test
passes the eight record-1 inputs above and a determinant-zero case. Replacing
ordinary C division with the recovered `RECIPS` seed and four individually
rounded quotient/correction multiplies removes the previously observed
one-ULP differences: all eight composed return words now match the ROM
(`bcdd67c8`, `3e722983`, `3f000000`, `3f83759f`, `bf8a60dd`, `3e983759`,
`3ee0dd67`, `4005306e`). This closes the reciprocal-schedule discrepancy for
the captured normal path; generic 40-bit state and broader exceptional cases
remain separate MAME work.
Changing only the first coordinate of the fixed record-1 data in the original
slot-zero sweep produced the pair `bf7fffff` (approximately `-1`) at
`(a,b)=(0,0)` and `bed89d89` (approximately `-0.4230769)` at `(0.5,0.5)`.
True-selector captures now identify those values as the separate selector-2
bank record, not as evidence that the selector-1 record had those
coefficients. The selector-1 synthetic record has a zero determinant at the
origin and an exact-zero normal helper result on its x-axis case. General
coefficient extraction still requires isolated nondegenerate records. The
selector-2 record is now independently swept at origin, x-axis, y-axis, and
diagonal inputs; its four normal returns fit the record-specific affine law
`(12*a + 3*b - 13) / 13`, producing `bf7fffff`, `bd9d89d8`, `bf44ec4e`, and
`bed89d89`. This is a second numeric constraint on the helper, not yet a
general formula for arbitrary records. A separate selector-3 sweep of record 4
also reaches the normal path at all four points and fits
`(30*a + 9*b + 36) / 37`, with outputs `3f7914c1`, `3fe45307`, `3f9bacf9`,
and `3fc00000`. The matching `30/37` and `9/37` coefficients with a changed
constant are evidence that the helper's affine coefficients are derived from
record geometry; the general derivation remains open. Record 5, which translates
every x-coordinate of record 1 by `+1`, independently fits
`(30*a + 9*b - 31) / 37`, with outputs `bf567c8a`, `bcdd67c8`, `bf183759`,
and `be9f2298`. The unchanged coefficients and constant shift of `-30/37`
are a second translation invariant for the helper's record-derived expression.
The sweep harness now supports `VON_SHARC_17_SINGLE_RECORD` plus
`VON_SHARC_17_SINGLE_POINT` for one-packet-per-process experiments. This option
selects which synthetic 12-word record the Lua harness writes; it does not add
an entry to the ROM's selector table, which remains a one-entry table with
selector value zero. A clean record-2 x-axis attempt reached the helper and
emitted a zero result, while the corresponding y-axis attempt entered the
zero-count path; these are retained as evidence that the selector/state
framing is stateful, not as additional math samples or proof of a second ROM
record index.
The sweep now also has an opt-in `VON_SHARC_17_TRUE_SELECTOR=1` mode. It keeps
the selector count at one, writes the selected value as `0`, `1`, or `2`, and
populates 16-word bank slots at the corresponding offsets. This separates a
real `M7` selector-offset experiment from the default slot-zero replacement;
the isolated capture
`von/build/disasm/von-sharc-opcode-17-true-selector-r2-x.trace` now validates
the bank stride: selector `1` advances `I5` to `0x30310`, reaches the helper on
a nonzero determinant, and emits `[1, 0.0, 1]` (count, helper result,
selected-record value). This proves the selector/staging boundary while also
showing that this record/input pair has a normal helper return of exact zero;
it does not yet identify the general helper formula.
The helper at `0x20d5d` is also bounded independently of its callers. It takes
the incoming base in `R0`, reads the two `0x10`/`0x20` offsets from that base
using `M7`, adds the controller bias `0x01c00000`, and publishes the derived
addresses at DM `0x30103` and `0x30104`. The second address write is in the
delayed slot after `RTS (DB)`; `0x20d68` begins immediately afterward. This
table/state-base contract is guarded by
`von/tools/test_sharc_helper_20d5d.py`; the executable pointer arithmetic is
also modeled and tested in `von/i960/recovered_sharc_helper_20d5d.c` and
`von/tools/test_recovered_sharc_helper_20d5d.py`. For the dumped `vonj`
`copro_data` pair, both words at ROM offsets `0x10` and `0x20` are zero, so
base zero derives `0x01c00000` for both pointers. The later
`0xbf030000` unmapped access is therefore downstream dispatcher state, not a
missing read at the helper's two table offsets.
The shared helper at `0x20d68` is bounded from that point through the final
`RTS` at `0x20dbd`, with `0x20dbe` as the next entry. It preserves the two
floating-point inputs, uses `LOGB` to compare exponent distance, and has a
reciprocal-refined main path with additional refinement after a magnitude
check. Its equality/zero, exponent-bound, and magnitude-bound branches share
dedicated delayed-return tails at `0x20db0`, `0x20db2`, and `0x20dbd`.
The listing establishes this control/dataflow contract, but not a safe
mathematical name for the reduction; it is guarded by
`von/tools/test_sharc_helper_20d68.py`.
The edge branches are now explicit: an equal/zero second input reaches the
`0x20dbb` pass-through tail and returns `F0`; exponent-distance bounds route
to the `0x20db5`/`0x20db8` exits before reciprocal refinement; and the normal
path applies the sign/threshold corrections through `R10` and the table at
DM `0x30300`. These branch destinations and correction slots are checked by
`von/tools/test_sharc_helper_20d68.py`; a direct opcode-`0x0f` zero-vector
probe emits `0x00000000` after the caller's scale/FIX stage.
The caller evidence now narrows that name substantially. Opcode `0x0f` forms
two endpoint differences, calls `0x20d68`, multiplies the result by
`0x4622f83d` (`32767/π`), and applies `FIX`. The helper's DM `0x30300` table
also begins with `2 - √3` and `√3`, the characteristic range-reduction anchors
of an atan approximation. It is therefore an atan-family ratio/direction
reducer, likely used for a direction angle, but the exact API is not yet
proven: its zero-second-input branch returns the surviving `F0` value rather
than exposing a conventional `atan2(…, 0)` result. At the caller level, an
all-zero difference vector emits `0x00000000`; the internal helper value and
SHARC edge rounding remain open. The boundary is reproducible with
`von/tools/probe_sharc_opcode_0f_zero_early.lua` and
`von/tools/probe_sharc_opcode_0f_single.lua`.
`von/tools/test_sharc_helper_20d68_angle.py` guards the caller shape and
constants.
The normal path is now runtime-instrumented by
`third_party/patches/0024-von-sharc-20d68-tracing.patch`. For the `(1,1)`
direction case, the helper enters with `F0=F1=1.0`, takes the reciprocal and
coefficient branches, and reaches `F15=0x3f490fda` (the ROM's rounded π/4
value) before the caller scale/FIX stage. The trace also records the complete
DM `0x30300..0x3030b` coefficient window, including `2-sqrt(3)`, `sqrt(3)`,
the polynomial coefficients, and the π/2 and π constants. The captured run is
checked by `von/tools/verify_sharc_20d68_trace.py`; this establishes a stronger
normal-path oracle while leaving the other exponent branches and a standalone
C implementation of the reducer for later work. A signed-normal probe with
`(F0,F1)=(-1,1)` follows the same magnitude path: `F15=0x3f490fda` at
`0x20db0`, then the late sign logic at `0x20dad`/`0x20db3` changes the result
to `0xbf490fda` at `0x20db4`. This proves the sign is applied after magnitude
reduction rather than being folded into the polynomial. The signed capture is
checked with the same verifier's `--signed` mode.
The captured `(0,1)` axis case independently takes the bounded early path
`0x20d73 -> 0x20db5 -> 0x20db7`, then passes through the common delayed return
and produces zero. It does not execute the reciprocal or polynomial body; this
boundary is checked by `von/tools/verify_sharc_20d68_axis_trace.py`.
A six-vector finite-ratio sweep adds the next partition boundary. Inputs with
the larger magnitude in `F1` reach `0x20d89` directly, while those with the
larger magnitude in `F0` visit `0x20d81` first; `R10` then records the
exponent-distance normalization (the captured 2x and 4x cases finish with
`R10=3` and `R10=2`, respectively). Sign changes preserve the magnitude path
and only alter the final returned sign. The rounded results and correction
counts are checked by `von/tools/verify_sharc_20d68_ratio_trace.py`.

```text
F0/F1                 range path  R10 at 0x20dab  F15 at 0x20db4
0x3f800000/0x40000000  0x20d89    1               0x3eed6338
0x40000000/0x3f800000  0x20d81    3               0x3f8db70d
0x3f800000/0xc0000000  0x20d89    1               0x402b6374
0xc0000000/0x3f800000  0x20d81    3               0xbf8db70d
0x3f800000/0x40800000  0x20d89    0               0x3e7adbb0
0x40800000/0x3f800000  0x20d81    2               0x3fa9b465
```

The table is a captured ROM result, not a host `atan2f` approximation; it is
therefore also a useful future MAME regression fixture for reciprocal-seed and
per-instruction rounding changes. Passing those six helper words through the
caller scale/FIX produces `0x12e3`, `0x2d1b`, `0x6d1b`, `0xffffd2e5`,
`0x09fb`, and `0x3604` for the corresponding input packets; these vectors are
now included in `test_recovered_sharc_opcode_0f.py` as a caller-level
cross-check.

A second sweep at ratios up to `256:1` provides a useful negative boundary:
none of the six inputs takes the exponent-distance exits at `0x20d70` or
`0x20d73`; every case reaches `0x20d9a` and the common result tail. The
`F0`-larger cases first visit `0x20d81` and finish with `R10=2`, while the
`F1`-larger cases use `0x20d89` and finish with `R10=0`. The exact rounded
helper results are guarded by `von/tools/verify_sharc_20d68_exponent_edges.py`.
The exact `2-sqrt(3)` threshold is now pinned down as well. With `F1=1.0`,
`F0=0x3e8930a2` (one ULP below the table constant) skips `0x20d8b` and returns
`0x3e860a91`; the exact `0x3e8930a3` and one-ULP-above `0x3e8930a4` values take
the longer path through `0x20d8b` and return `0x3e860a92` and `0x3e860a93`.
The threshold verifier is `von/tools/verify_sharc_20d68_threshold_trace.py`.
The signed `LOGB` guard has now been reached too. Ratios with 32- and 64-step
exponent separation still execute the refinement body. The exact comparator
boundary is 124 steps: the 123-step cases still refine, while
`F0=0x7d800000,F1=1.0` takes `0x20db8` and returns the π/2 word
`0x3fc90fdb`, and `F0=1.0,F1=0x7d800000` takes `0x20db5` and returns
`0x00000000`. The six 32/64/126-step limit vectors are checked by
`von/tools/verify_sharc_20d68_logb_limits.py`; the eight-vector 123-through-126
boundary capture is checked by `von/tools/verify_sharc_20d68_logb_boundary.py`.
The normal-path dataflow also exposes a useful algebraic reconstruction target:
after `0x20d9a` forms `z = F15*F15`, the paired reads stage `z*c3+c4` and
`(z+c5)*z+c6`, followed by the three-pass `RECIPS` correction schedule. The
tail multiplies the refined correction by the current ratio before adding it
back to `F15`. This is a rational atan-family correction over `z`, rather than
a primitive atan operation. The exact pipeline-latency interpretation and
branch-dependent additions from the `0x30300` table remain provisional; the
instruction boundary is guarded by `von/tools/test_sharc_helper_20d68.py` and
is a candidate for a standalone bit-exact C model and future MAME fixture. A
readable first approximation is now in
`recovered_sharc_helper_20d68_candidate.c`, with bounded captured-vector
coverage in `von/tools/test_recovered_sharc_helper_20d68_candidate.py`.
It matches the `1:2`, `1:4`, `2:1`, `4:1`, symmetric `1:1`, and signed
`1:-2`/`-2:1` helper words exactly. Its sign routing now covers both helper arguments: the first
argument supplies the Y sign and the second selects the negative-X quadrant,
with explicit zero-axis handling. The opcode-`0x0f` model consequently uses
this recovered helper instead of host `atan2f`, retaining the ROM's separately
observed negative-Y endpoint `FIX` branch. The candidate also models the normal finite `LOGB` endpoint guard:
124 exponent steps returns the signed π/2 endpoint or zero before reciprocal
refinement, while 123 steps remains on the normal path. NaNs, infinities,
subnormals, and the exact SHARC internal rounding schedule remain outside this
readable model. The eight-vector edge capture from
`von/tools/probe_sharc_opcode_0f_nonfinite.lua` now resolves the caller-side
non-normal contract: quiet NaNs arrive at the helper as canonical
`0xffffffff` and remain canonical through the full body; infinities saturate
to `0x7f7fffff`/`0xff7fffff` before entering the helper; and minimum
subnormals flush to zero. A subnormal denominator consequently takes the
zero-denominator π/2 tail. The raw runtime result is checked by
`von/tools/verify_sharc_20d68_nonfinite_trace.py`, while probe reproducibility
is checked by `von/tools/test_sharc_opcode_0f_nonfinite_probe.py`. The same
verifier records the final low `ASTAT` flags: canonical-NaN calls retain
`AI|MI|AF`, the saturated infinity endpoint has `MI|AF`, and the flushed-zero
paths distinguish `AZ` from the ordinary endpoint return.
The direct FIFO companion now compares both engines. An earlier DRC capture
returned axis-like values for the two NaN cases where the interpreter emitted
canonical `0x80000000`; the localized DRC canonical-NaN writeback path now
makes the default DRC stream match the interpreter on all eight vectors.
`verify_sharc_opcode_0f_nonfinite_poll.py` records the shared expected sequence.
The adjacent helpers at `0x20dbe` and `0x20dc4` share the reduction body at
`0x20dca`, but have distinct entry setup. `0x20dbe` takes the absolute value
of `F0`, seeds the path with π/2 (`0x3fc90fdb`), and enters through the
delayed jump; `0x20dc4` seeds `R7 = 1.0` and `R12 = 0` before entering the
same path. The common body performs signed fixed-point staging, a six-pass
correction loop, and returns through the `0x20dde` tail; `0x20de1` is the next
helper. This establishes the shared entry contract without assigning an
unsupported mathematical name, and is guarded by
`von/tools/test_sharc_helpers_20dbe.py`.

The shared body is now instrumentable at instruction granularity through
`third_party/patches/0023-von-sharc-reduction-tracing.patch`. The hook records
the floating registers and the active `0x3030c` coefficient words at
`0x20dca..0x20ddf`, including the six-pass correction loop and both delayed
return paths. A rebuilt interpreter run of `probe_sharc_opcode_1b.lua` reached
the hook for all four inputs and preserved the established outputs
`0x00000000`, `0x3f800000`, `0xb3bbbd00`, and `0x38c92eef`. The trace adds a
stronger boundary oracle: the endpoint results are produced by the ROM's
coefficient sequence and reduction loop, not by a host `sinf` substitution.
Exact quadrant routing, persistent register initialization, and SHARC
extended-precision behavior remain open; the raw run is intentionally kept
out of the source tree because the existing MAME diagnostics make it
reproducible.

The first reduction-stage snapshot also supplies a compact numeric oracle for
the fixed-point path:

```text
input       F8 at 0x20dca       output at 0x203c0
0x00000000  0x00000000          0x00000000
0x00004000  0x3fc9116d          0x3f800000
0x00007fff  0x40490fdb          0xb3bbbd00
0xffff8000  0x4049116d          0x38c92eef
```

This shows that the endpoint asymmetry is already present before the caller's
`π/32767` multiply and `FIX`; it is not introduced by the final scale. The
next numerical model can therefore be checked against both the intermediate
range-reduction lane and the emitted fixed-point word.
That bounded model is now implemented in
`von/i960/recovered_sharc_helper_20dbe.c` and tested by
`von/tools/test_recovered_sharc_helper_20dbe.py`. The visible polynomial is a
seven-term Horner chain over coefficients `c4..c10`; the effective π constant
is not the rounded `0x40491000` word alone, but its high-word/correction pair
`0x40491000 + 0xb715777a`. Reconstructing that pair before the fixed-point
quotient preserves the low correction needed at the π endpoint. With explicit
single-precision barriers around the polynomial operations, the model matches
all four captured endpoints above, including the asymmetric negative-input
case. This is a bounded normal-path model, not yet a complete all-quadrant
replacement for the SHARC helper.
The same source now exposes the `0x20dbe` phase-shifted sibling as a cosine
model: the ROM evaluates the shared sine body at `π/2 + |θ|`. This is
mathematically equivalent to cosine over the observed half-turn, but retains
the ROM's finite-polynomial rounding path. It matches
the four opcode-`0x1c` runtime words (`0x3f7fffff`, `0xb8492eef`, and the two
`0xbf7fffff` endpoints), confirming that the π/2 seed is functional phase
state rather than an unrelated coefficient. A broader live sweep adds an
important qualification: the sine service matches all eight signed samples
tested (`0x0000`, `0x2000`, `0x4000`, `0x6000`, `0x7fff`, `0x8000`, `0xa000`,
and `0xc000`) exactly, while cosine differs by two low bits at the `0x2000`
phase in the current model. The negative cosine inputs are even in the live
service, including the `0xc000` near-zero result; the model now reflects that
ABS(F0) behavior. The previously observed two-ULP discrepancy disappears when
the ROM's additive phase path is modeled, rather than the mathematically
equivalent subtractive identity; at the first nonzero phase the reducer's
intermediate high word is also one step below direct host conversion. The C
model records that bounded intermediate correction explicitly. This is a ROM
path model, not evidence that a generic `nextafterf` adjustment belongs in
MAME's core without a broader SHARC reproduction. A 32-request interpreter
sweep initially exposed two cosine low-bit mismatches. Reconstructing the
residual with the ROM's rounded high-word/correction-word subtractions now
matches every sampled sine and cosine word, without an ad-hoc correction.
The sweep is checked by `von/tools/verify_sharc_reduction_quadrants.py` and
the numerical model test, which exercises the absolute-angle words observed
at `0x20dca`.
The complete interleaved output sequence from the sweep is:

```text
0x1b/0000 = 00000000   0x1c/0000 = 3f7fffff
0x1b/2000 = 3f350610   0x1c/2000 = 3f3503d8
0x1b/4000 = 3f800000   0x1c/4000 = b8492eef
0x1b/6000 = 3f35019c   0x1c/6000 = bf35084a
0x1b/7fff = b3bbbd00   0x1c/7fff = bf7fffff
0x1b/8000 = 38c92eef   0x1c/8000 = bf7fffff
0x1b/a000 = bf35019c   0x1c/a000 = bf35084a
0x1b/c000 = bf800000   0x1c/c000 = b8492eef
```

This table is an especially useful future MAME regression fixture because it
tests sign handling and phase rounding without depending on the full game
frame loop.
The live trace can be checked directly with
`von/tools/verify_sharc_trig_quadrants.py`; it expects exactly the sixteen
output words above and rejects missing, extra, or reordered results. The Lua
stimulus and verifier together form a minimal MAME regression harness while
the eventual upstream version can move the same cases into a synthetic SHARC
CPU test.
The same fixture was also run with MAME's `-nodrc` interpreter path. It
produced the identical sixteen-word sequence, so this routine does not expose
an interpreter/DRC disagreement. The remaining precision concern is broader:
the core's `SHARC_REG` is still a 32-bit `float`, and `MODE1_RND32` is not a
complete substitute for modeling the device's extended internal format. Any
upstream precision change should therefore be tested against this fixture and
additional synthetic 40-bit cases, rather than justified by a discrepancy that
is not present in the current Virtual-On path.
The direct host-FIFO poll companion `von/tools/probe_sharc_opcode_0f_poll.lua`
also resolves a diagnostic limitation: DRC-generated SHARC memory writes do
not pass through the interpreter output hook, but the host-visible diagonal
seven-vector response sequence is
`0x00000000, 0x00003fff, 0x00001fff, 0xffffc000, 0x00007fff, 0xffffe000,
0x00000000` in both engines. The result validates DRC execution and
publication of this reduction path without promoting it to a general 40-bit
parity claim; `verify_sharc_opcode_0f_poll.py` checks captured logs.
The runtime table gives more reliable assignments for the first nontrivial
command stream. The entries are indexed by the low byte of the FIFO word:

```text
opcode  target       confirmed body
0x08    0x000201bf   reset service-state index at DM(0x30100)
0x40    0x00020af2   consume one word; store a shifted/biased value at DM(0x30148)
0x41    0x00020af9   consume one word; table-based conversion; emit one result
0x44    0x00020ba1   initialize constants at DM(0x3015c..0x3015f)
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

The integer portions of the `0x40`/`0x41` pair are now exact. At SHARC
`0x20af2`, opcode `0x40` consumes one word, shifts it left 16 bits, adds
`0x01c00000`, and stores the resulting 32-bit address at DM `0x30148`. At
`0x20af9`, opcode `0x41` consumes one word `n`, forms
`address = DM[0x30148] + (n >> 2)`, reads one 32-bit DM word, logically shifts
it right by `8 * (n & 3)`, masks to one byte, and emits that byte. The service
also reads DM `0x30146` (mask `3`) and DM `0x30147` (mask `0xff`) during this
path. The extracted contract is implemented and exhaustively lane-tested in
`von/tools/sharc_service_contract.py`; the reusable C equivalents are
`von/i960/recovered_sharc_opcode_40.c` and
`von/i960/recovered_sharc_opcode_41.c`, exhaustively covered by
`von/tools/test_recovered_sharc_opcode_40_41.py`. The floating-point handlers
consuming the returned byte remain separate.

Opcode `0x08` (`0x201bf`) is the stateful-service reset boundary: it loads zero
and stores only DM `0x30100`, then returns through the delayed-return slot. It
does not consume a payload or emit a response, and it does not clear the
coefficient/state windows used by the later services. This exact reset shape
is guarded by `von/tools/test_sharc_opcode_08.py`.

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
0x18 <word>                   one operand; 12-word state/result transfer
0x1b <word>                   one signed 16-bit operand; result observed
0x1c <word>                   one signed 16-bit operand; result observed
0x1d <word> x 2               two signed 16-bit operands; result observed
```

A representative observed sequence is:

```text
0x40 00000005
0x41 0001b100        -> reads 00000000, 00000019
0x35 00000000 00000000 00000000 c2a00000 00000000 bf800000
                     -> reads 00000000, 80000000
0x1e 00000600         -> emits 12 words; first observed values were
                     00000000, 41cdbfa3
```

The initial `0x08` at `0x0002840c` is therefore a service reset after
bootstrap, while the repeated `0x08` at `0x00003c5c` is a recurring reset or
phase command from the host UI path. The later `0x44` at `0x000bd690` is a
constant-table initialization command. The next implementation boundary is
to model these packet lengths and state transitions before attempting to port
the math bodies.

The `0x18` entry is now bounded more accurately from the extracted listing.
Its helper at SHARC `0x20e54` consumes one FIFO word, shifts it left four
bits, applies it as the `M7` offset to the table base in DM `0x30104`, and
copies 16 words into DM `0x3010b..0x3011a`. The handler at `0x2038e` (opcode
`0x18`) then
streams 12 words from DM `0x3010b` to the output FIFO. The earlier “two
operands” description came from treating the first visible output values as
inputs; it was incorrect. The instruction shape is guarded by
`von/tools/test_sharc_opcode_18.py`. The pure-C transfer model in
`von/i960/recovered_sharc_opcode_18.c` makes the recovered boundary explicit:
the shifted selector chooses a 16-word record, that record is copied to
scratch, and output words are the scratch prefix `0..11` in order. Its vectors
are checked by `von/tools/test_recovered_sharc_opcode_18.py`.
No preserved runtime trace currently dispatches opcode `0x18`; the record's
semantic fields therefore remain intentionally unnamed rather than being
inferred from the transfer shape alone.
Opcode `0x1f` (`0x203ea`) consumes six FIFO words as three endpoint pairs
(`R8/R12`, `R9/R13`, and `R10/R14`). The visible arithmetic forms `dx`, `dy`,
and `dz`, accumulates their squared magnitude, and enters `RSQRTS` at `0x3fa`.
Three visible refinement groups lead to the final multiply/output at
`0x407..0x409`. A static single-step reading of the aliased F-register fields
can appear to produce a `dz*dy` cross-term; the interpreter-backed runtime
probe resolves that apparent hazard: for differences `(3,4,12)`, `F0` is
`0x43290000` (`169.0`) and the output register is `0x414fffff`, immediately
below `13.0`. Additional forced vectors resolve the edge behavior: a unit
axis returns `1.0`, the fractional vector returns `0x406b26a8`, and the zero
vector returns canonical SHARC NaN `0xffffffff`. The service is therefore an
endpoint Euclidean-length operation with a seeded Newton refinement and
SHARC-specific rounding. The structure is guarded by
`von/tools/test_sharc_opcode_1f.py`.
The semantic model in `von/i960/recovered_sharc_opcode_1f.c` now exposes the
endpoint-distance result and implements the local SHARC core's exact 128-entry
`RSQRTS` seed selection, three Newton correction groups, and observed
zero-vector NaN behavior. It is checked by
`von/tools/test_recovered_sharc_opcode_1f.py`; the seed correspondence is
anchored to `third_party/mame-master/src/devices/cpu/sharc/compute.hxx` rather
than inferred from the game trace alone.
The shortened interpreter-backed boundary probe
`von/tools/probe_sharc_opcode_1f_rounding.lua` now adds five live vectors,
including adjacent `1.0` values and a `0x4b800000` magnitude. The returned
words are reproduced by the C model, including `sqrt(2)` at `0x3fb504f3`, the
asymmetric adjacent-ULP case at `0x3fb504f4`, and the large result at
`0x4bddb3d7`. This is the first runtime check of the model beyond ordinary
small vectors under the documented truncating/32-bit SHARC mode.
For runtime coverage, the debug MAME target must run the SHARC interpreter:
the existing instruction hooks sit in `execute_run()`, while the normal
`vonj` configuration enables the recompiler. With the interpreter enabled, a
40/100-second progression probe confirmed SHARC execution and the dispatcher
table entry at runtime (`PC 0x0200b8` contains the `0x0203ea` target), but the
gameplay window submitted only the upload/initialization traffic visible as
host command `0x44`; a separate direct FIFO stimulus then dispatched `0x1f` and
captured the state described above.
The focused output trace now also catches the handler's final DM write at
`0x20409`, confirming that the refined `F0` value is the word returned to the
host-side FIFO path rather than merely an internal accumulator snapshot.
Opcode `0x20` (`0x2040a`) is a three-word state-tail readback. It loads the
state pointer from DM `0x30101`, emits offsets `0x09` and `0x0a` with output
FIFO waits, then emits offset `0x0b` in the delayed slot after `RTS (DB)`.
This gives the affine/vector services an explicit persistent-translation
readback boundary; the structure is guarded by
`von/tools/test_sharc_opcode_20.py`.
The focused runtime probe `von/tools/probe_sharc_opcode_20_tail.lua` first
loads identity plus tail `(10,20,30)` through opcode `0x07`, then issues a
separate `0x20` request. Live output tracing records `0x41200000`,
`0x41a00000`, and `0x41f00000` at PCs `0x2040d`, `0x20410`, and `0x20414`,
confirming the three-word response ordering and the connection to the affine
translation slots.
Opcode `0x21` (`0x20415`) consumes six FIFO words into `R0..R5` and stores
them sequentially at DM `0x30136..0x3013b`. The last two stores occur in the
delayed slots after `RTS (DB)`. This is a parameter upload rather than a
computed result. Opcode `0x22` reloads these six words through `I6` and uses
them as two plane coefficients (`+0x00/+0x01`) and four interleaved clipping
thresholds (`+0x02..+0x05`) in its transformed-vector comparisons. The
consumer reloads coefficient `+0x01` before the first comparison and then
thresholds `+0x04`, `+0x05`, `+0x02`, and `+0x03` at the four comparison sites;
the `+0x00` coefficient is loaded in the paired preceding slot. This
establishes the producer/consumer role as a clip-parameter block, although
the threshold ordering's geometric names remain unassigned. The exact packet,
destination range, and consumer reloads are guarded by
`von/tools/test_sharc_opcode_21.py`.
The gameplay FIFO log must not be used as runtime coverage for opcode `0x21`
without packet-boundary correlation: the recurring words `0x21` at i960
`0x8e3e0`/`0x8e3ec` are payloads of the preceding host command `0x2e`, whose
six operands begin at the earlier writes in that same routine. The clip-block
role above is therefore established by the SHARC producer/consumer listing,
not by those apparent host-side command values.
Opcode `0x22` (`0x20429`) consumes four FIFO words, loads the persistent
3x3 state at DM `0x30101`, and evaluates three translated projection
components using coefficient groups beginning at offsets `0x02`, `0x05`,
and `0x08`, then `0x00`, `0x03`, `0x06`, and finally `0x01`, `0x04`, `0x07`.
For the first three FIFO operands `(x,y,z)`, the three accumulators are
exactly `x*s[2] + y*s[5] + z*s[8] + s[11]`,
`x*s[0] + y*s[3] + z*s[6] + s[9]`, and
`x*s[1] + y*s[4] + z*s[7] + s[10]`, respectively. The fourth operand is
consumed by the subsequent comparison/control path rather than by these dot
products. This pins the service to the same column-major affine state
convention established by opcode `0x1a`; threshold ordering and coordinate
names remain separate questions.
The fourth FIFO word is `w`; with affine components `(A,B,C)` and clip words
`(p,q,t2,t3,t4,t5)`, the finite positive-depth path tests, in order,
`(q*C-p*w)/A >= t4`, `(q*C+q*w)/A <= t5`, `(p*B-p*w)/A >= t2`, and
`(p*B+q*w)/A <= t3`. Any failed test selects `-1.0` (`0xbf800000`), while
negative `A` selects `-2.0` (`0xc0000000`); otherwise the first affine
component `A` is published. Runtime threshold flips reach the four compare
sites at `0x20453`, `0x20456`, `0x2045a`, and `0x2045d` respectively. A
nonzero-`w` capture with `(x,y,z,w)=(1,2,3,1)` and `(p,q)=(2,3)` produces
the exact intermediate values `1.333333`, `3.0`, `0.0`, and `1.666667`,
validating the coefficient roles. The zero-depth edge is now bounded from the
listing and MAME's SHARC `RECIPS` behavior: `RECIPS(+0)` produces `+infinity`,
the first correction multiplies that by zero and produces NaN, and all four
unordered clip comparisons fall through, publishing the original zero depth.
Negative depth still takes the explicit `-2.0` branch. A canonical NaN depth
follows the same unordered fall-through and publishes NaN; payload preservation
is still qualified pending a live capture. The edge model is covered by
`von/tools/test_recovered_sharc_opcode_22.py`; the runtime edge probe is
`von/tools/probe_sharc_opcode_22_depth_edges.lua`. The structure is guarded by
`von/tools/test_sharc_opcode_22.py`,
`von/tools/probe_sharc_opcode_22_edges.lua`,
`von/tools/probe_sharc_opcode_22_thresholds.lua`, and
`von/tools/probe_sharc_opcode_22_nonzero_w.lua`.
The proven affine and finite clip kernels are now isolated in
`von/i960/recovered_sharc_opcode_22.c` and checked by
`von/tools/test_recovered_sharc_opcode_22.py`. Identity input `(1,2,3)`
produces the ROM's column-major component order `(3,1,2)`; a non-identity
state with translation tail produces `(15,3,8)`. The clip predicate and
fallback/result selection remain intentionally outside this kernel.
Opcode `0x23` (`0x2046b`) consumes three FIFO words, normalizes a derived
three-component vector through two reciprocal-square-root refinement paths,
and stores the first input component at DM `0x30180`. It then follows the
persistent-state pointer in DM `0x30101` (the probe resolves it to `0x30200`)
and writes transformed values across offsets
`0x00..0x08` in the instruction's interleaved order; the final offset `0x08`
is in the delayed-return slot. The exact vector-space meaning is still
provisional, but the FIFO shape, refinement stages, scratch/output store, and
state-write boundary are guarded by `von/tools/test_sharc_opcode_23.py`.
The pre-normalization dataflow is now explicit: the first three operands are
accumulated as `x*x + y*y + z*z`; after the reciprocal-square-root refinement,
the service retains the normalized `x`, `y`, and `z` lanes while retaining the
refined magnitude in the shared `F0` lane. It then negates the normalized `y`
lane before the first state-update group. This establishes a normalized
direction/magnitude update, although the resulting basis orientation is still
not assigned a gameplay name.
The focused identity-state axis probe dispatches the service and observes the
scratch write at `0x30180`: the x-axis case returns `0x3f800000` (`1.0`),
consistent with the normalized first lane. The complete persistent-state write
interpretation still needs a direct trace of the SHARC store path.
That store-path trace is now available: with a fresh identity state, the
z-axis input writes the identity frame to `0x30200..0x30208`, while the
x-axis input writes `[0,0,1 / 0,1,0 / 0,0,0]`. The y-axis zero-component case
propagates the SHARC NaN sentinel (`0xffffffff`) through the frame. These
edge results establish the concrete write layout while leaving its gameplay
coordinate name open.
The reusable direction and state-update kernels are now in
`von/i960/recovered_sharc_opcode_23.c`, with tests in
`von/tools/test_recovered_sharc_opcode_23.py`. They reproduce the normalized
axis vectors and preserve the ROM's explicit Y negation, including
`0x80000000` negative-zero lanes; the observed `(3,4,12)` vector produces
`(0x3e6c4ec4,0xbe9d89d8,0x3f6c4ec4)`. Seeded runtime captures prove that the
state tail builds a Y-up frame with rows
`(z,0,-x)/sqrt(x*x+z*z)`, `(-x*y/h,h,-z*y/h)`, and `(x,y,z)`, then
post-multiplies the existing state by that frame. This explains the x-axis
quarter-turn, z-axis identity, diagonal frame, and the `0xffffffff` NaN
propagation when `x=z=0`.
This handler is live in the gameplay capture: the host emitter at i960
`0xcaf08` writes `0x23` with operands `0xc1baa9ac, 0x4116147b, 0x416256d4`
on both cabinets. The neighboring stream then writes `0x12` with three
operands and `0x0a` with two, matching a state-update/derived-scalar pipeline;
the later FIFO responses belong to those subsequent services, not to an
assumed output from `0x23`. This confirms runtime reachability while leaving
the alternate-state vector's geometric frame unassigned. The observed
neighboring host writes are captured as the concrete eleven-word chain
`[0x23, update[3], 0x12, tail[3], 0x0a, scalar[2]]` in
`von/i960/recovered_geometry_state_packets.c`, with the live sample and
ordering guarded by `von/tools/test_recovered_geometry_state_packets.py`.
Opcode `0x24` (`0x204bd`) consumes three FIFO words into `R0`, `R1`, and `R2`,
computes a normalized projection using the persistent state, and
updates the persistent frame through a delayed-return matrix-write tail at
`0x507..0x509`. The shared-scale, `FIX`, helper, and output-FIFO sequence
begins at `0x20522` under opcode `0x25`, not inside `0x24`. The normalized
state-update structure is guarded by
`von/tools/test_sharc_opcode_24.py`.
The opening arithmetic is now bounded as well: before consulting the matrix,
the service forms `x*x + y*y + z*z`, refines its reciprocal square root, and
retains the normalized three lanes for the two fixed-point projection paths.
This makes `0x24` the read/convert side of the normalized state pipeline next
 to `0x23`; its frame is the transpose of the `0x23` Y-up frame, and it
 post-multiplies the existing state by that transpose. Seeded runtime captures
 validate both sides of that multiply: x-axis transforms the seeded words
 `[1,2,3,4,5,6,7,8,9]` into `[-7,-8,-9,4,5,6,1,2,3]`, while z-axis preserves
 the seed. The focused identity-state probe confirms the delayed matrix tail
 in live execution: x-axis input writes `[0,0,-1 / 0,1,0 / 1,0,0]` to the
 `0x30200..0x30208` frame buffer, z-axis input preserves identity, and
 `(1,2,3)` matches the transposed `0x23` frame. Fixed-point FIFO results are
 therefore assigned to the adjacent opcode `0x25` pending their own probe.
 The reusable finite-path model is in
 `von/i960/recovered_sharc_opcode_24.c`, with regression coverage in
 `von/tools/test_recovered_sharc_opcode_24.py` and the seeded probe in
 `von/tools/probe_sharc_opcode_24_state_vectors.lua`.
Opcode `0x25` (`0x2050a`) consumes three FIFO words into `R1`, `R0`, and `R2`,
normalizes their derived magnitude with three reciprocal-refinement rounds,
and calls helper `0x20d68` before applying the shared `0x4622f83d` scale.
It emits two fixed-point results via `FIX`; the second multiply and output
occur in the delayed-return path. The precise projected fields remain
provisional, while the input order, refinement count, helper, scale, output
count, and boundary are guarded by `von/tools/test_sharc_opcode_25.py`. A
direct identity-state probe reaches both FIFO writes: x-axis input emits
`0x80000000` followed by `0x00000000`, and z-axis input emits two zero words.
An isolated diagonal probe now emits `0x00000b05` (`2821`) followed by
`0xffffe80b` (`-6133`) for `(1,2,3)`. These are exact signed output words;
their gameplay units and axis assignment remain open.
The isolated instrumented trace now captures the finite intermediates:
`0x3e8a8580` (about `0.270468`) before the first scale/FIX and
`0xbf168757` (about `-0.588012`) before the second. These match
`atan2(x,hypot(y,z))` and `-atan2(y,z)`, respectively, within the
helper's ROM approximation. The x-axis case confirms the zero-horizontal
singularity: the first result is canonical `0x80000000` while the second
singularity: the first result is canonical `0x80000000` while the second
is zero. A signed quadrant sweep now confirms the reducer's endpoint
convention: `y=0,z<0` emits signed `+32767` rather than a `-π` encoding,
while positive/negative Y axes and all four X/Z quadrants match the expected
signed angle words. The reusable finite-path model is
`von/i960/recovered_sharc_opcode_25.c`, guarded by
`von/tools/test_recovered_sharc_opcode_25.py`.
Opcode `0x2b` (`0x205f0`) is a no-input status service: after waiting for
output FIFO readiness it returns through `RTS (DB)` and writes the constant
success value `1` to `DM(I1, M0)` in the delayed slot. The next handler starts
at `0x205f4`; this compact boundary and constant result are guarded by
`von/tools/test_sharc_opcode_2b.py`.
The reusable constant contract is `von/i960/recovered_sharc_opcode_2b.c`.
Opcode `0x2c` (`0x205f4`) consumes six FIFO words into `R0`, `R1`, `R2`,
`R13`, `R14`, and `R15`. Unlike opcode `0x2e`, its `R0..R2` values feed the
matrix rebuild directly as floating-point registers; the packed-table decoder
begins at `0x2066f`, in opcode `0x2e`. It loads the persistent translation tail,
then
performs three signed-16 conversion/helper chains using scale `0x38c9116d`
and rebuilds the persistent matrix through three interleaved row passes. The
tail is written at offsets `0x09..0x0b`, while the matrix updates cover the
nine state elements; the final offset `0x08` is in the delayed-return slot.
An all-zero six-word live probe followed by opcode-`0x11` readback produces
zero tail words and an identity matrix to helper precision (`0x3f7ffffe` on
each diagonal), confirming the neutral point and state layout. Nonzero field
probes using low-byte value `0x40` then isolate the three signed fields:
`R13` produces an X-axis Y/Z-plane rotation, with the expected
`[c,0,0 / 0,c,-s / s,0,c]` pattern; `R15` produces a Z-axis X/Y-plane
rotation, `[c,-s,0 / s,c,0 / 0,0,c]`; and `R14` produces the conventional
Y-axis X/Z-plane rotation `[c,0,s / 0,1,0 / -s,0,c]`. A serialized
identity-reset probe confirms the small-angle `R14=0x0040` state words
`[0x3f7ffec4,0,0x3bc9111a / 0,0x3f7ffffe,0 / 0xbbc91118,0,0x3f7ffec4]`,
while the quarter-turn `R14=0x4000` case reads back
`[0xb8492eee,0,0x3f800000 / 0,0x3f7ffffe,0 / 0xbf7ffffe,0,0xb8492eee]`.
The prior distinct-middle interpretation came from an unsafely chained
probe; serialized execution establishes all three fields as conventional
axis rotations with SHARC helper rounding. The recovered structure is
guarded by
`von/tools/test_sharc_opcode_2c.py`.
The reusable translation/composition model is
`von/i960/recovered_sharc_opcode_2c.c`, guarded by
`von/tools/test_recovered_sharc_opcode_2c.py`.
A combined quarter-turn packet (`R13=R14=R15=0x4000`) reads back
`[0x311e1abc,0x38492eef,1 / 0xb8c92eef,-1,0x38492eef /
1,0xb8c92eef,0x311e1abc]`, matching row-major `Rx * Ry * Rz` after
helper rounding.
A mixed-angle packet (`R13=0x1000`, `R14=0x2000`, `R15=0x3000`) reads back
`[0x3e8a87e5,0xbf273d13,0x3f350610 / 0x3f750546,0x3dd3f9d8,0xbe8a8c02 /
0x3dd424dc,0x3f4000c8,0x3f273c37]`; its maximum error against the recovered
`Rx * Ry * Rz` formula is `1.2e-7` in host float comparison.
Opcode `0x2d` (`0x2065b`) consumes one FIFO word and passes it directly to
the output FIFO. It waits for input and output readiness, writes the value in
the delayed slot after `RTS (DB)`, and reaches opcode `0x2e` at `0x20661`.
This exact one-word timing contract is guarded by
`von/tools/test_sharc_opcode_2d.py`.
The reusable bit-preserving passthrough is
`von/i960/recovered_sharc_opcode_2d.c`. Both leaf models are covered by
`von/tools/test_recovered_sharc_opcode_2b_2d.py`.
Opcode `0x2e` (`0x20661`) consumes six FIFO words: `R0..R2` plus packed
parameters in `R13..R15`. It decodes the packed values through the table at
DM `0x30141`, installs the decoded translation tail at offsets `0x09..0x0b`,
and performs three signed-parameter conversion/helper chains using scale
`0x38c9116d` while rebuilding the persistent matrix. The final matrix write
is in the delayed-return slot before opcode `0x2f` at `0x206e1`. A live
identity-reset/readback probe confirms the packed-tail mapping: low-16
`0x3c00` writes exact `1.0`, low-16 `0x4000` writes exact `2.0`, and packed
zero writes `0x38000000` because this ROM path constructs the binary16-shaped
normal value without zero/denormal special handling. The signed-byte angle
fields then operate on that decoded state. A serialized runtime trace of the
`0x3c00` case shows `I6` switching to `0x30141`, the decoder constructing
exact `0x3f800000` (`1.0`), and execution reaching the final delayed state
store at `0x206e0`. The complete state-store trace is
`[0x3f7fffff,0,0 / 0,0x3f7fffff,0 / 0,0,0x3f7ffffe]` for the matrix and
`[0x3f800000,0x38000000,0x38000000]` for the translation tail, directly
confirming the packed X mapping and the ROM's zero-shaped decode for the
other two coordinates. The structure is guarded by
`von/tools/test_sharc_opcode_2e.py`.
The reusable packed-decoder/composition model is
`von/i960/recovered_sharc_opcode_2e.c`, guarded by
`von/tools/test_recovered_sharc_opcode_2e.py`. A focused field probe shows
that only the low signed byte of each packed angle field is live; it is
promoted by eight bits before the shared signed-16 helper. A combined
`R13=R14=R15=0x40` packet reads back
`[0x311e1abc,0x38492eef,1 / 0xb8c92eef,-1,0x38492eef /
1,0xb8c92eef,0x311e1abc]`, matching `Rx * Ry * Rz`.
Opcode `0x30` (`0x20711`) consumes five FIFO words into `R0`, `R1`, `R2`,
`R15`, and `R13`. It loads and updates the translation tail, resets the
persistent matrix to identity, then applies the signed `R15` parameter through
helpers `0x20dbe` and `0x20dc4` with scale `0x38c9116d`. `R13` is copied
directly into the floating-point accumulator at `0x2074d` during the later
matrix pass; it is not a second trig angle. With `R13=1.0` and `R15=0`, a
serialized state trace ends at identity (cosine residuals in the diagonal) and
tail `(0,0,1)`. With `R13=1.0` and `R15=0x4000`, it ends at the conventional
Z-axis quarter-turn `[c,-1,0 / 1,c,0 / 0,0,1]`. Conversely, `R13=0x4000`
produces raw `0x00004000` matrix words, confirming that this field is a raw
floating-point scalar input. The identity stores and first pass are
intermediate setup. Caller-level naming of the scalar remains provisional.
The full input, reset, helper, and writeback structure is guarded by
`von/tools/test_sharc_opcode_30.py` and
`von/tools/probe_sharc_opcode_30_angles.lua`.
The reusable state model is
`von/i960/recovered_sharc_opcode_30.c`, guarded by
`von/tools/test_recovered_sharc_opcode_30.py`. Scalar readback confirms that
`R13` uniformly scales the rebuilt Z rotation: neutral `R15` with scalar
`0.5`, `1.0`, and `2.0` produces the corresponding scaled identities, while
the quarter-turn cases produce the same scaled `[c,-s,0 / s,c,0 / 0,0,1]`.
Opcode `0x31` (`0x20762`) consumes eight FIFO words into `R5`, `R6`, `R7`,
`R10`, `R9`, `R13`, `R14`, and `R15`. It initializes the state block at DM
`0x30180` to identity, installs three tail words, applies two signed-parameter
helper chains using scale `0x38c9116d`, and rebuilds matrix terms from the
resulting projection. A live packet with direct tail `(1,2,3)` and all five
remaining fields zero emits exact `1.0`, `2.0`, and `3.0` at `0x207c1`,
`0x207c3`, and delayed `0x207c6`, confirming the output ordering and the
three tail slots for this neutral case. Serialized `DM 0x30180..0x3018b`
tracing shows isolated `R10=0x4000` ending in the conventional Y-axis
quarter-turn `[c,0,+1 / 0,c,0 / -1,0,c]`, while isolated `R9=0x4000`
ends in the conventional X-axis quarter-turn `[c,0,0 / 0,c,+1 / 0,-1,c]`,
with SHARC cosine residuals. Thus both signed fields are live rotations. The
remaining `R13`, `R14`, and `R15` values are direct vector components for the
final matrix-vector accumulation: with tail `(1,2,3)` and neutral rotations,
isolated `R13=1.0`, `R14=1.0`, and `R15=1.0` emit `(2,2,3)`, `(1,3,3)`, and
`(1,2,4)` respectively. The complete structure is guarded by
`von/tools/test_sharc_opcode_31.py` and
`von/tools/probe_sharc_opcode_31_direct_fields.lua`.
An additional basis-vector probe with `R10=R9=0x4000` recovers the emitted
combined transform as approximately `[0,1,0 / 0,0,1 / 1,0,0]`; the three
basis outputs confirm that the final operation is `tail + M * vector`.
An asymmetric basis run (`R10=0x1000`, `R9=0x3000`) resolves the general
form as `M = Ry(-R10) * Rx(-R9)` in the externally emitted row-major
projection. The reusable model is
`von/i960/recovered_sharc_opcode_31.c`, guarded by
`von/tools/test_recovered_sharc_opcode_31.py`.
Opcode `0x32` (`0x207c8`) consumes nine FIFO words into `R0..R3`, `R13`,
`R14`, `R15`, `R5`, and `R6`. It loads the persistent translation tail,
performs three signed-parameter/helper chains using scale `0x38c9116d`, and
rebuilds the persistent 3×3 matrix in three interleaved passes. The final
matrix write occurs in the delayed-return slot at `0x843`. An identity-seeded
all-zero live packet followed by opcode `0x11` preserves identity to helper
precision (`0x3f7ffffe` on all three diagonal words) and leaves the tail zero,
confirming the neutral point and state layout. Isolated identity-seeded
packets with `R0=1`, `R1=1`, and `R2=1` place exact `1.0` in tail slots
`0x09`, `0x0a`, and `0x0b` respectively while leaving the matrix identity;
the first three inputs are therefore direct translation values. `R3` is then
converted through the signed-16 helper path, followed by the `R5` and `R6`
signed fields. A reset-corrected serialized trace of `DM 0x30200..0x3020b`
confirms that opcode `0x32` depends on the preceding identity state from
opcode `0x10` and performs three partial matrix writeback passes. Isolated
`R3=0x4000` produces the expected Y-axis quarter-turn pattern in the first
pass, `[c,0,+1 / 0,c,0 / -1,0,c]`; later `R5` and `R6` passes overwrite parts
of that same state window. An asymmetric matrix-seeded all-angle trace
(`R3=R5=R6=0x4000`) resolves the pass order: Y, then Z, then X, equivalent to
left multiplication by `Rx*Rz*Ry`; rows `1..9` become approximately
`[-4,-5,-6 / 1,2,3 / 7,8,9]`. A neutral-angle retained-field probe shows that
`R15` and `R14` write the persistent tail X/Y slots (`0x09`/`0x0a`), while
`R13` has no observable effect in the identity case; delayed register reuse
means these fields are not yet modeled as a simple extra translation vector.
The normal translation/angle contract is modeled in
`von/i960/recovered_sharc_opcode_32.c` and covered by
`von/tools/test_recovered_sharc_opcode_32.py`.
The recovered structure is guarded by
`von/tools/test_sharc_opcode_32.py` and
`von/tools/probe_sharc_opcode_32_single_angle.lua`.
An all-angle serialized probe (`R3=R5=R6=0x4000`, neutral `R13..R15`)
reads back `[0x311e1abc,0xbf800000,0xb8492eef /
0x3f800000,0x311e1abc,0 / 0,0xb8492eef,0x3f800000]`.
This is the ROM-rounded `Rx*Rz*Ry` result; the intermediate writes are shared
window pipeline stages rather than the final matrix.
Opcode `0x33` (`0x20844`) consumes five FIFO words into `R0`, `R1`, `R2`,
`R14`, and `R13`. It loads the persistent translation tail, runs two
signed-parameter conversion/helper chains using scale `0x38c9116d`, and
updates the persistent 3×3 matrix through interleaved row writes. A live
identity-seeded packet with direct tail `(1,2,3)` and both signed fields zero
preserves the matrix to helper precision and reads back exact tail `(1,2,3)`
through opcode `0x11`. The final matrix write at offset `0x08` is in the
delayed-return slot; this state-only service reaches opcode `0x34` at
`0x20890`. Reset-corrected direct state tracing shows `R13=0x4000` producing
the conventional X-axis pattern `[c,0,0 / 0,~0,-1 / 0,+1,~0]`, while
`R14=0x4000` produces the conventional Y-axis pattern
`[~0,0,+1 / 0,~1,0 / -1,0,~0]`, with helper residuals. The two fields are
therefore live X/Y rotations; the trace also shows each pass partially
overwrites the shared state window, explaining the older non-orthonormal
snapshot. The recovered structure is guarded by
`von/tools/test_sharc_opcode_33.py`,
`von/tools/test_recovered_sharc_opcode_33.py`, and
`von/tools/probe_sharc_opcode_33_single_angle.lua`.
An identity-seeded combined probe (`R14=R13=0x4000`) reads back
`[0xb8492eef,0,1 / 1,0xb8492eef,0x38492eef /
0x38492eef,1,0x311e1abc]`, confirming the expected `Rx*Ry` composition with
SHARC helper residuals despite the interleaved write schedule.
The 12-write serialized suffix is guarded by
`von/tools/test_sharc_opcode_33_combined_trace.py`.
An asymmetric seed (`1..9`) with both fields at `0x4000` produces first-pass
rows approximately `[7,8,9 / 4,5,6 / -1,-2,-3]`, then final lower rows
`[1,2,3 / 4,5,6]`; this confirms that the second pass is the expected X
rotation on the partially updated state. Its 12-write ROM-rounded suffix is guarded by
`von/tools/test_sharc_opcode_33_asymmetric_trace.py`.
Opcode `0x34` (`0x20890`) consumes eight FIFO words into `R0`, `R1`, `R2`,
`R5`, `R6`, `R13`, `R14`, and `R15`. It loads the persistent translation tail,
performs three signed-parameter conversion/helper chains using scale
`0x38c9116d`, and rebuilds the persistent 3×3 matrix through interleaved
row writes. Identity-seeded single-field probes show that `R0`, `R1`, and `R2`
write translation X/Y/Z respectively, while `R13`, `R14`, and `R15` write a
second translation X/Y/Z group respectively; with identity state each group
is observable as a direct tail contribution. A packet with direct tail
`(1,2,3)` and all five remaining fields zero preserves the matrix to helper
precision and reads back exact tail `(1,2,3)` through opcode `0x11`. `R5` and
`R6` are signed-16 helper inputs: `R5=0x4000` produces the conventional
Y-axis quarter-turn `[c,0,+1 / 0,c,0 / -1,0,c]`, while `R6=0x4000` produces
the conventional X-axis quarter-turn `[c,0,0 / 0,c,-1 / 0,+1,c]`, with
`c` equal to the helper's near-zero residual. The final tail and matrix writes
occupy delayed-return slots before opcode `0x35` at `0x208f2`. The runtime
probes are `von/tools/probe_sharc_opcode_34_float.lua`,
`von/tools/probe_sharc_opcode_34_fields.lua`, and
`von/tools/probe_sharc_opcode_34_single.lua`; the static structure is guarded
by `von/tools/test_sharc_opcode_34.py`. The reusable model in
`von/i960/recovered_sharc_opcode_34.c` expresses the staged dataflow as
`tail += M_old * (R0,R1,R2)`, then `M_new = Rx(R6) * Ry(R5) * M_old`, then
`tail += M_new * (R13,R14,R15)`; it is covered by
`von/tools/test_recovered_sharc_opcode_34.py`.
An identity-seeded combined probe (`R5=R6=0x4000`, neutral `R13..R15`)
reads back `[0xb8492eef,0,1 / 1,0xb8492eef,0x38492eef /
0x38492eef,1,0x311e1abc]`, confirming the same `Rx*Ry` transform and
helper residuals seen in opcodes `0x32` and `0x33`.
The boundary is concrete: opcode `0x34`'s delayed slots at `0x8f0` and `0x8f1`
finish the tail stores, and opcode `0x35` begins at `0x8f2` with its first FIFO
wait. No state reset occurs between them, so the `F0`/`F2`/`F13` values consumed
by opcode `0x35` are shared continuation state rather than values initialized
inside that handler. The boundary invariant is also checked by
`von/tools/test_sharc_opcode_35.py`; the source-level geometric names remain
unassigned.
The interpreter-backed helper-sweep trace now supplies a runtime vector for
this stateful boundary. A dispatched `0x35` consumes the six words
`4321912d, 00000000, 430caea5, c2a00000, c7507c0a, c3f00103` and emits
`bdcccccd` at the handler's output site (`0x208f2..0x20908`). A following
six-word vector reaches the same handler and emits `00000001`. These are
runtime confirmations of six-word consumption, one-word output, and delayed
continuation timing; they do not yet identify the persistent-register inputs
that make the two results differ.
The rebuilt trace adds the inherited-register snapshot at the output boundary:
for the first vector, `0x20908` observes `F11=0x40000000` (`2.0`),
`F12=0x3f800000` (`1.0`), `F4=0x4321912d`, `F6=0x430caea5`, and emits
`R0=0x4306a2f7` (`134.6365814`). The next vector reaches the same boundary
with `R0=0x48435000`. This confirms that the reciprocal correction's `F11=2.0`
constant and the preceding service's register state are live inputs, while
the exact semantic roles of the six FIFO words remain provisional.
Tracing every correction slot tightens the numerical dataflow: before `0x208ff`
the denominator lane is `F12=0xc3f00103`; the three correction groups drive
the residual lane through `0xbb080000`, `0x3f807f76`, `0x3f800080`, and finally
`0x3f800000` at `0x20907`, while `F7` settles on `0x4306a2f7`. The delayed
`0x20907` multiply therefore restores the final scalar as `F0*F7` before the
`0x20908` FIFO write. The second vector shows the same shape and settles on
`0x48435000`. This rules out treating the service as a direct reciprocal
return; it is a stateful reciprocal-residual correction whose input/output
geometric interpretation remains open.
The operand roles are now resolved numerically. The register-file aliases are
important here: the fifth FIFO read into `R13` supplies the `F13` addend, and
the sixth read into `R12` supplies the `F12` denominator before `0x208ff`.
At `0x208fe`, `F0` is therefore the state-derived numerator and the sixth FIFO
word is the denominator. The `0x208ff..0x20907` sequence refines `1/F12` and
multiplies it by the saved numerator, so opcode `0x35` is a stateful
floating-point division service. For the first captured vector,
`F0=-64626.6171875` and `F12=-480.0079041`, yielding `134.6365814`; the
second vector yields exactly `200000.0` from `-200000.0 / -1.0`. The other
five FIFO words still participate in the preceding state/pipeline setup, but
they are not direct operands of the final quotient. The complete visible
quotient dataflow is now bounded. With FIFO words named `w0..w5`, the first
and third reads feed `F8 = F0_previous*w0` and `F12 = F2_previous*w2`; the
fifth read updates `F13`, and `0x208fe` forms
`F0 = F0_previous*w0 + F2_previous*w2 + w4`. The sixth read is then the
denominator `w5`. The second and fourth reads are overwritten before they can
affect the visible quotient path, so the service contract is
`(F0_previous*w0 + F2_previous*w2 + w4) / w5`, subject to SHARC rounding.
Opcode `0x36` (`0x20909`) consumes four FIFO words into `R0`, `R1`, `R2`,
and `R13`. It loads the persistent translation tail, initializes the
persistent 3×3 matrix to identity, adds `R0`, `R1`, and `R2` to tail X/Y/Z
respectively, and scales the final matrix uniformly by `R13`. Identity-seeded
single-field probes give diagonal `1.0` for `R13=1.0`, diagonal `2.0` for
`R13=2.0`, and a zero matrix for `R13=0`; the corresponding `R0/R1/R2=1.0`
probes write tail X/Y/Z respectively. The final matrix elements are written in
delayed-return slots before opcode `0x37` at `0x20940`. Runtime evidence is
captured by `von/tools/probe_sharc_opcode_36_single.lua`; the static structure
is guarded by `von/tools/test_sharc_opcode_36.py`.
The reusable model is `von/i960/recovered_sharc_opcode_36.c`, guarded by
`von/tools/test_recovered_sharc_opcode_36.py`. A chained runtime probe seeds
the tail with `(10,20,30)`, applies `(1,2,3)`, and reads back `(11,22,33)`
with a `2.0` diagonal matrix, confirming addition against nonzero state.
Opcode `0x37` (`0x20940`) consumes three FIFO words into `R13`, `R14`, and
`R15`. It resets the persistent 3×3 matrix to identity, writes `R13` into
translation-tail offset `0x09` before `RTS (DB)`, and writes `R14` and `R15`
into offsets `0x0a` and `0x0b` in the delayed-return slots before opcode
`0x38` at `0x20956`. Clean identity-seeded single-field probes confirm direct
tail mapping: `R13=1.0` writes X, `R14=2.0` writes Y, and `R15=3.0` writes Z,
while all nine matrix words remain the identity. Runtime evidence is captured
by `von/tools/probe_sharc_opcode_37_single.lua`; the static contract is
guarded by `von/tools/test_sharc_opcode_37.py`.
The reusable reset model is `von/i960/recovered_sharc_opcode_37.c`, guarded
by `von/tools/test_recovered_sharc_opcode_37.py`; it preserves the direct
`R13/R14/R15` X/Y/Z tail ordering while resetting all nine matrix elements.
Opcode `0x38` (`0x20956`) consumes three packed-vector words into `R0`, `R1`,
and `R2`. The decode masks at DM `0x30141` now identify the exact packed
coordinate format: only the low 16 bits are consumed, with bit 15 as sign,
bits 14..10 as a five-bit exponent, and bits 9..0 as a ten-bit mantissa. The
handler constructs an IEEE-754 word as
`(sign << 16) | (((exponent - 15 + 127) & 0xff) << 23) | (mantissa << 13)`;
this is a binary16-shaped normal-coordinate encoding, but the ROM path does
not implement IEEE half denormal/Inf/NaN special cases. The three decoded
components are then combined with the persistent 3×3 matrix in row-major
state order as `out[c] = x*M[0][c] + y*M[1][c] + z*M[2][c]`; this is a
row-vector `vᵀ·M` convention (the instruction groups use coefficient offsets
`0,3,6`, then `1,4,7`, then `2,5,8`). A live quarter-turn-Z probe writes
`[0,-1,0 / 1,0,0 / 0,0,1]` and opcode `0x38` emits approximately
`[2,-1,3]` for packed `(1,2,3)`, confirming the ordering. Results are
streamed through `I1`, with output waits between stores and the final store in
the delayed-return slot before opcode `0x39` at `0x2098a`. The decode,
coefficient order, and matrix instruction shape are guarded by
`von/tools/test_sharc_opcode_38.py`.
The reusable packed-vector projection is
`von/i960/recovered_sharc_opcode_38.c`, guarded by
`von/tools/test_recovered_sharc_opcode_38.py`.
Opcode `0x39` (`0x2098a`) consumes one FIFO word, converts it to a destination
address as `(input >> 2) + 0x01400000`, and copies the 12-word table at DM
`0x30141` into that destination. The first destination word is the constant
`0x05800b0b`; the remaining 12 words are copied with post-increment addressing,
and the final store occupies the delayed-return slot before opcode `0x3a` at
`0x209ac`. The recovered structure is guarded by
`von/tools/test_sharc_opcode_39.py`.
The reusable seeded-copy model is `von/i960/recovered_sharc_opcode_39.c`,
guarded by `von/tools/test_recovered_sharc_opcode_39.py`; it returns the
derived destination and writes the fixed seed followed by all 12 table words.
Opcode `0x3a` (`0x209ac`) consumes one FIFO word, derives the destination as
`(input >> 2) + 0x01400000`, and performs the same seeded copy of 12 words from
DM `0x30141`. It waits for output space, returns, and emits the final copied
word through `I1` in the delayed-return slot while also completing the final
destination store; opcode `0x3b` begins at `0x209d0`. The structure is guarded
by `von/tools/test_sharc_opcode_3a.py`.
The reusable model is `von/i960/recovered_sharc_opcode_3a.c`, guarded by
`von/tools/test_recovered_sharc_opcode_3a.py`; it returns the derived
destination, performs the seeded 12-word copy, and exposes the final copied
word emitted by the delayed-return path.
Opcode `0x3b` (`0x209d0`) reads the fixed source word at DM `0x01407fff` and
emits it through `I1`, then derives a destination from that value using
`(value >> 2) + 0x01400000` and copies the seeded 12-word table from DM
`0x30101`/`0x30141`. After the copy, it emits the post-increment destination
pointer through `I1` in the delayed-return sequence before opcode `0x3c` at
`0x209f7`. The recovered structure is guarded by
`von/tools/test_sharc_opcode_3b.py`.
The reusable bridge model is `von/i960/recovered_sharc_opcode_3b.c`, guarded
by `von/tools/test_recovered_sharc_opcode_3b.py`; it exposes the fixed source
output, seeded 12-word copy, and post-increment destination pointer
(`destination + 13` in DM words).
Opcode `0x3c` (`0x209f7`) consumes three FIFO words into `R0`, `R1`, and `R2`,
forms a normalized vector through repeated `RSQRTS` and `RECIPS` refinement
stages, and rewrites the persistent 3×3 matrix using the resulting values.
Let `h = sqrt(x*x + z*z)` and `l = sqrt(x*x + y*y + z*z)`. The recovered
row-major frame is
`[z/h, -x*y/(l*h), x/l; 0, h/l, y/l; -x/h, -z*y/(l*h), z/l]`.
Thus the third column is the normalized input direction, the first column is
its XZ-plane perpendicular, and the second column completes the orthonormal
frame. A live `(3,4,12)` probe reads back
`[0.9701425,-0.0746264,0.2307692 / 0,0.9514860,0.3076923 /
-0.2425356,-0.2985054,0.9230770]`, within the ROM's reciprocal-refinement
rounding. A live edge probe establishes the ROM boundary behavior: both
`(0,1,0)` (zero XZ length) and `(0,0,0)` write canonical SHARC NaN
`0xffffffff` to all nine matrix slots while leaving the three tail slots at
zero; `(1,0,0)` follows the regular formula and writes
`[0,0,1 / 0,1,0 / -1,0,0]`. The final matrix element is written after
`RTS (DB)` at `0x20a59`, before opcode `0x3d` begins at `0x20a5c`. The
alternate `0x3d` edge behavior remains provisional; the normal-case formula,
verified singular boundary, and writeback are guarded by
`von/tools/test_sharc_opcode_3c.py`. The reusable normal/degenerate C model is
`von/i960/recovered_sharc_opcode_3c.c`.
Opcode `0x3d` (`0x20a5c`) consumes three FIFO words into `R0`, `R1`, and `R2`,
repeats the normalized-vector refinement pipeline, and rewrites the persistent
3×3 matrix using the alternate row/column arrangement visible in its stores.
For `h = sqrt(x*x + z*z)` and `l = sqrt(x*x + y*y + z*z)`, its normal-case
frame is exactly the transpose of opcode `0x3c`'s frame:
`[z/h, 0, -x/h; -x*y/(l*h), h/l, -z*y/(l*h); x/l, y/l, z/l]`.
A live `(3,4,12)` readback confirms
`[0.9701425,0,-0.2425356 / -0.0746264,0.9514860,-0.2985054 /
0.2307692,0.3076923,0.9230770]`. The final matrix element is written after
`RTS (DB)` at `0x20abe`, before the next FIFO service at `0x20ac1`; degenerate
zero/XZ cases follow the paired ROM boundary: `(0,1,0)` and `(0,0,0)` write
canonical `0xffffffff` NaNs to all nine matrix slots and zero to the tail,
while `(1,0,0)` writes `[0,0,-1 / 0,1,0 / 1,0,0]`. The transpose relation,
verified singular boundary, and writeback are guarded by
`von/tools/test_sharc_opcode_3d.py`. The matching reusable C model is
`von/i960/recovered_sharc_opcode_3d.c`.
The model is covered by `von/tools/test_recovered_sharc_opcode_3d.py`,
including the `(3,4,12)` normal frame and the `(0,1,0)` canonical-NaN
singular boundary. NaN input follows the same canonical-NaN frame tail.
Opcode `0x3e` (`0x20ac1`) consumes four FIFO words into `R8`, `R12`, `R9`,
and `R13`, then emits the two-dimensional Euclidean distance
`sqrt((R8-R12)² + (R9-R13)²)`. The reciprocal-square-root path at
`0x20acd..0x20adb` is a three-correction SHARC implementation of that
distance, with the result written through `I1` after the output wait and
delayed return. Runtime vectors `(3,0,4,0)` and `(8,5,12,8)` both emit
`0x409fffff` (`4.9999995`), confirming the difference orientation and SHARC
rounding. Isolated runtime probes now show both zero difference and a NaN
input emit canonical `0xffffffff` NaN through the same path. The next service,
opcode `0x3f`, begins at `0x20add`. The exact normal-case operation and timing
are guarded by `von/tools/test_sharc_opcode_3e.py`. The reusable mathematical
contract is implemented in `von/i960/recovered_sharc_opcode_3e.c`; its output
can differ from the ROM by the observed final reciprocal-refinement bit.
The normal-case C contract is covered by
`von/tools/test_recovered_sharc_opcode_3e.py`, including both recorded
five-unit vectors, FIFO operand ordering, and the canonical zero/NaN boundary.
Opcode `0x3f` (`0x20add`) consumes four FIFO words into `R0`, `R12`, `R4`, and
`R12` again. The first two words are integer-converted by `FLOAT`, while the
third word is consumed as the IEEE bit-pattern in `F4`; the fourth overwrites
`F12` in the delayed input slot. The reciprocal-refined body therefore emits
`D + C * FLOAT(int32(A)) / FLOAT(int32(B))` through `I1`, after its input/output
waits and delayed return. Runtime inputs `(0x3f800000,0x40000000,3.0,4.0)` and
`(0x40000000,0x40800000,3.0,5.0)` emit `0x40df4000` (`6.9765625`) and
`0x40ff417d` (`7.9767442`), respectively. Opcode `0x40` begins at `0x20af2`;
Edge probes now establish the ROM behavior: zero or one numerator over a zero
denominator emits canonical `0xffffffff` NaN; `A=0xffffffff,B=1,C=3,D=4`
emits `1.0`; `A=0x80000000` with the same remaining fields emits `0xcfc00000`;
a NaN coefficient emits canonical NaN; and an infinite coefficient saturates to
`0x7f7fffff` rather than preserving IEEE infinity. The normal
mixed-representation operation remains guarded by
`von/tools/test_sharc_opcode_3f.py`; its reusable normal-case C contract is
`von/i960/recovered_sharc_opcode_3f.c`, with direct regression coverage in
`von/tools/test_recovered_sharc_opcode_3f.py`, including the observed
zero-denominator, NaN-coefficient, and positive-infinity saturation cases. The edge observations are
reproducible with `von/tools/probe_sharc_opcode_3f_edge.lua`.
Opcode `0x42` (`0x20b09`) consumes six FIFO words into `R0`, `R1`, `R2`,
`R13`, `R14`, and `R15`. It decodes the packed coordinates through the table
at `DM 0x30141`, builds three transformed records with the persistent state at
`DM 0x30101`, and uses the signed fixed-point helpers at `0x20dbe` and
`0x20dc4` for each record. Identity-seeded single-field probes show the
decoded `R0/R1/R2` values write tail X/Y/Z respectively; packed zero follows
the ROM's no-special-case decode and reads back as `0x38000000`. The remaining
fields are signed-16 rotations: `R13=0x4000` gives the conventional X-axis
quarter-turn, `R14=0x4000` gives the conventional Y-axis quarter-turn, and
`R15=0x4000` gives the conventional Z-axis quarter-turn when each is isolated.
Reset-corrected state tracing
shows the first pass is identity-like, the second pass contains the
Y-quarter-turn terms, and the third pass overwrites selected matrix entries;
the final state is therefore not a standalone axis matrix. Its final
matrix/state writes occupy the delayed return slots immediately before opcode
`0x43` at `0x20b89`. Runtime evidence is captured by
`von/tools/probe_sharc_opcode_42_single.lua`; the static structure is guarded
by `von/tools/test_sharc_opcode_42.py`. The normal path is modeled in
`von/i960/recovered_sharc_opcode_42.c` and covered by
`von/tools/test_recovered_sharc_opcode_42.py`: it reproduces the shared
low-16-bit packed decoder, the row-vector projection into state slots `9..11`,
and the sequential Z/Y/X angle passes. A fresh interpreter-mode trace with
`R13=0x4000` confirms the
three write passes directly: the final row-major matrix is
`[0x3f7ffffe,0,0 / 0x80000000,0xb8492eee,0xbf7fffff /
0,0x3f7fffff,0xb8492eee]` (negative zero in the first slot of row 2), i.e.
the conventional X-axis quarter-turn with the ROM's one-step trigonometric
residuals. The writes occur at PCs
`0x20b4d..0x20b58`, `0x20b66..0x20b71`, and `0x20b7f..0x20b88`; this confirms
that the first and third passes are selective matrix updates rather than one
single final assignment. The new combined probe
`von/tools/probe_sharc_opcode_42_combined.lua` shows why the full routine must
be reduced to independent single-field assignments: with all three fields set
to `0x4000`, the final state is
`[0x311e1abc,0x38492eef,0x3f800000 / 0xb8c92eef,0xbf800000,0x38492eef /
0x3f800000,0xb8c92eef,0x311e1abc]`, the ROM-rounded form of the orthogonal
`Rx*Ry*Rz` result. An asymmetric seed matrix (`1..9`) produces rows
`[7,8,9]`, `[-4,-5,-6]`, `[1,2,3]`, directly confirming sequential Z/Y/X
row rotations; the intermediate writes must therefore be read as pipeline
stages, not as the final matrix. The combined write sequence is executable-
checked by `von/tools/test_sharc_opcode_42_combined_trace.py`.
The captured combined write sequence is executable-checked by
`von/tools/test_sharc_opcode_42_combined_trace.py`.
Opcode `0x43` (`0x20b89`) consumes three FIFO words into `R0`, `R1`, and `R2`,
multiplies them against the persistent 3×3 matrix, and streams three projected
results through `I1`. With state offsets `0..8` treated as row-major matrix
entries, the outputs are the column dot products
`(x*s0 + y*s3 + z*s6, x*s1 + y*s4 + z*s7, x*s2 + y*s5 + z*s8)`. `FLAG1_IN`
waits separate the outputs, with the final store in the delayed-return slot
before opcode `0x44` at `0x20ba1`. A live opcode `0x07` upload of matrix values
`1..9`, followed by vector `(10,20,30)`, emits `300.0`, `360.0`, and `420.0`
at PCs `0x20b9a`, `0x20b9c`, and `0x20b9f`, confirming the column-dot-product
ordering. The recovered operation and output timing are guarded by
`von/tools/test_sharc_opcode_43.py`. The reusable bit-preserving C model is
`von/i960/recovered_sharc_opcode_43.c`.
Opcode `0x45` (`0x20bab`) consumes three FIFO words into `R0`, `R13`, and
`R15`, sign-extends the low 16 bits of the first two as half-turn angle units,
and applies the fixed-point sine/cosine helpers using scale `0x38c9116d`
(`π/32767`). For angles `a` and `b` and float scale `s=R15`, the three outputs
are exactly the spherical conversion
`(s*sin(a), s*cos(a)*cos(b), -s*cos(a)*sin(b))`. `FLAG1_IN` waits separate the
outputs, with the final signed result in the delayed-return slot before opcode
`0x46` at `0x20bce`. A live `(a,b)=(0x2000,0x4000), s=2` probe emits
`(1.4142475,-0.0000678,-1.4141798)` at PCs `0x20bc6`, `0x20bc9`, and
`0x20bcd`, confirming the angle units, output ordering, and negative-Z sign;
the residual is the ROM helper's fixed-point rounding. Normal operation and
timing are guarded by `von/tools/test_sharc_opcode_45.py`. A six-vector sweep
then exercised origin, both quarter turns, a diagonal, and independent
negative-A/negative-B cases at scales `1.0`, `1.5`, and `2.0`. It produced the
exact lane triples `(00000000,3f7ffffe,80000000)`,
`(40000000,b8c92eee,00000000)`, `(00000000,b8c92eee,bfffffff)`,
`(3fb50610,3f7ffcdf,bf800001)`, `(bf87c48c,3f3ffda7,bf400002)`, and
`(3f87c48c,3f3ffda7,3f400002)`. The sweep is replayable with
`von/tools/probe_sharc_opcode_45_sweep.lua` and
`von/tools/verify_sharc_opcode_45_sweep.py`; the paired negative cases confirm
that cosine is even while the sine-derived X/Z lanes change sign as expected.
The reusable normal-path C model is `von/i960/recovered_sharc_opcode_45.c`.
Opcode `0x46` (`0x20bce`) consumes seven FIFO words into `R0..R6` and uploads
them sequentially into state slots `s[0]..s[6]` at `DM 0x30150`. The first
store negates `F4` as a side effect, so the exact mapping is
`s[0..3]=R0..R3`, `s[4]=-R4`, and `s[5..6]=R5..R6`. The final two stores follow
`RTS (DB)` before opcode `0x47` at `0x20be5`; opcode `0x47`'s controlled
predicate probe validates the stored `s[4]` sign as its lower-bound input. The
recovered structure is guarded by `von/tools/test_sharc_opcode_46.py` and
`von/tools/probe_sharc_opcode_47_single.lua`.
The reusable bit-preserving C model is `von/i960/recovered_sharc_opcode_46.c`,
guarded by `von/tools/test_recovered_sharc_opcode_46.py`.
Opcode `0x47` (`0x20be5`) consumes four FIFO words into `R8`, `R10`, `R9`,
and `R13`, combines them with the `0x30150` state window, and normalizes the
resulting radial pair with `RSQRTS`. With inputs `(a,b,c,d)` in that FIFO
order and stored state words `s[0..6]`, the exact normal-case predicate is
`result = 0` iff
`c + s[5] > sqrt((a-s[0])² + (b-s[2])²)` and
`s[4] <= s[1]-d <= s[3]`; every failed comparison returns `1`. The first
opcode `0x46` store's `F4=-F4` means the uploaded word at `s[4]` is already
negated in the state, so it is the lower bound as stored. A live controlled
probe with `s[2]=0`, `s[3]=3`, `s[4]=-0.5`, `s[5]=0` and `(a,b,c,d)=(3,4,6,-2)`
reaches `0x20c09` and emits `0`; the radial-failing case reaches `0x20c0d`
and emits `1`. The three comparisons select the delayed result through `I1`;
opcode `0x48` begins at `0x20c0e`. Boundary rounding remains SHARC-specific,
and the recovered contract is guarded by `von/tools/test_sharc_opcode_47.py`.
The reusable finite-path C model is `von/i960/recovered_sharc_opcode_47.c`.
Its normal, inclusive-boundary, radial-rejection, and unordered-input cases
are covered by `von/tools/test_recovered_sharc_opcode_47.py`.
Opcode `0x48` (`0x20c0e`) consumes five FIFO words into `R0..R4` and uploads
them directly as state slots `s[0]..s[4]` at `DM 0x30157..0x3015b`; no sign or
numeric conversion occurs. The first three stores precede `RTS (DB)` and the
final two occupy its delayed-return slots; opcode `0x49` begins at `0x20c20`
and consumes predicate packets against this five-word window. The recovered
structure is guarded by `von/tools/test_sharc_opcode_48.py`. The reusable
bit-preserving C model is `von/i960/recovered_sharc_opcode_48.c`, guarded by
`von/tools/test_recovered_sharc_opcode_48.py`.
Opcode `0x49` (`0x20c20`) consumes four FIFO words into `R8`, `R9`, `R10`,
and `R15`, combines them with the five-word state window at `DM 0x30157`, and
normalizes the three-dimensional distance with `RSQRTS`. The exact predicate is
`result = 0` iff
`sqrt((x-s0)² + (y-s1)² + (z-s2)²) < s3 + threshold`; otherwise it emits `1`.
Only state offsets `0..3` and the fourth FIFO word (`R15`, the threshold) are
read; state offset `4` is untouched by this service. A live upload of state
`[0,0,0,4,5]` returns `1` for vector `(3,4,0)` (distance `5`) and `0` for
vector `(1,2,2)` (distance `3`), at output PCs `0x20c41` and `0x20c45`.
Opcode `0x4a` begins at `0x20c46`; the normalized predicate and branch timing
are guarded by `von/tools/test_sharc_opcode_49.py`. The reusable finite-path C
model is `von/i960/recovered_sharc_opcode_49.c`, with compiled normal,
strict-boundary, state-preservation, and unordered-input coverage in
`von/tools/test_recovered_sharc_opcode_49.py`.
Opcode `0x4a` (`0x20c46`) consumes four FIFO words into `R8`, `R9`, `R10`,
and `R15`, uses the `0x30157` state window, and first rejects a positive Y
difference (`y-s1 > 0`) through the early branch. That branch consumes one
additional FIFO word and returns `1`. For `y-s1 <= 0`, the normal path
normalizes the distance and emits `0` iff
`sqrt((x-s0)² + (y-s1)² + (z-s2)²) < s3 + threshold`; otherwise it emits `1`.
A live state upload `[0,0,0,4,5]` returns `1` for `(3,4,0)` through the
extra-input path at `0x20c6f`, and `0` for `(1,-2,2)` through the normal path
at `0x20c73`. Opcode `0x4b` begins at `0x20c74`; the branch, strict bound,
and FIFO timing are guarded by `von/tools/test_sharc_opcode_4a.py`. The
reusable finite-path C model is `von/i960/recovered_sharc_opcode_4a.c`, with
compiled coverage for the early Y rejection, normal strict-bound path, zero
boundary, and unordered input in
`von/tools/test_recovered_sharc_opcode_4a.py`.
Opcode `0x4b` (`0x20c74`) consumes four FIFO words into `R8`, `R9`, `R10`,
and `R13`, uses the state window beginning at `0x30157`, and first compares
`y-s[1]` with zero: the `GT` branch consumes one extra FIFO word and reaches
the output-1 fallback. Its normal path stages `dy=y-s[1]`, forms `dx²` and
`dy²`, then overwrites the temporary `dy²` with `dz²`: `c80` writes
`F2=dz`, `c81` copies it to `F4`, and `c82` computes `F12=dz*F4`. The first
radicand is therefore exactly `F1=dx²+dz²`; `R2` is not preserved caller
state, because the `c80` write has already made it the `dz` register value.
The handler then applies a
second normalized/refinement sequence using the
uploaded `s[3]` term, the fourth input, and the fixed constants at offsets
`s[5..8]` (`2.0`, `1/3`, `0.5`, and `3.0`) installed by opcode `0x44`.
Offset `s[4]` is not read by this normal path. The normal paths return delayed values
`2` or `0`. The final refined `F0` is confirmed as the full Euclidean radius:
with `y=-4`, live vectors `(x,z)=(0,1)` and `(3,4)` produce approximately
`sqrt(17)=4.1231` and `sqrt(41)=6.4031`. The normal bound-side refinement is
now recovered structurally, while exact SHARC rounding and boundary behavior
remain separately qualified. Controlled live traces show that the refined bound
contribution is linear in the fourth input but geometry-dependent: with `y=-4`,
horizontal radii `1` and `2` produce `F9≈0.582983` and `F9≈0.942809` for a unit
fourth input, while `F0` remains the full radii `sqrt(17)` and `sqrt(20)`;
doubling the fourth input doubles `F9` and shifts `F1=F9+s[3]` accordingly.
The zero-horizontal case (`x=z=0`) drives the first `RSQRTS` refinement through
zero, yielding NaN and the delayed `2` result, so it is a numerical singularity
rather than evidence for a finite bound coefficient. A timed live probe that
initializes opcode `0x48` and the
The helper-level trace makes the first call concrete: the `0x4d` caller forms
`seed = dx² + dz²`, refines its reciprocal square root, and enters `0x20d68`
with the Y difference and the refined `sqrt(seed)`. The helper returns
`θ = atan2(dy, sqrt(seed))` for the tested positive-seed cases, with the shared
reducer taking the square-rooted horizontal metric. Later in the same
handler, `F15` is the full squared radius (`5` for `(h,y)=(1,-2)` and `20`
for `(2,-4)`) before its second reciprocal-square-root refinement. The
corrected ratio cross-check is decisive: `(h,|y|)=(1,2)` and `(2,4)` share the
same angle and both produce `F9≈0.942809`, while `(1,4)` produces `F9≈0.582983`.
The coefficient therefore follows the normalized direction (the
vertical-to-horizontal ratio/angle), not horizontal radius alone. The
zero-horizontal case remains the
reciprocal-square-root singularity described above. The payload-less opcode
`0x44` separately confirms the branch outputs: positive-Y
input `(0,4,0,0)` emits `1` at `0x20cc9`, while negative-Y input
`(0,-4,0,0)` emits `2` at `0x20cbf`. Opcode `0x4c` begins at
`0x20cca`, and the structure is guarded by
`von/tools/test_sharc_opcode_4b.py`.
The reusable finite-path C model is
`von/i960/recovered_sharc_opcode_4b.c`; its regression test covers the
three normal/fallback outcomes, including the zero-horizontal singular tail,
while leaving other SHARC-specific rounding and exception behavior qualified.
Opcode `0x4c` (`0x20cca`) consumes four FIFO words into `R8`, `R9`, `R10`,
and `R11`, uses the `0x30157` state window, and first rejects `y-s[1] < 0`
through the fallback branch. Otherwise it computes
`distance = sqrt((x-s[0])² + (y-s[1])² + (z-s[2])²)` with the same SHARC
reciprocal-square-root refinement used by the neighboring predicates, then
returns `0` iff `distance < R11` and `1` otherwise. The fallback consumes one
additional FIFO word and returns `1`. Live probes with state `[0,0,0,4,5]`
and `(x,y,z)=(3,4,0)` returned `1` for bound `0` at `0x20ced` and `0` for
bound `6` at `0x20cf7`; the negative-Y path was observed waiting for its extra
input. Opcode `0x4d` begins at
`0x20cf8`, and the recovered structure is guarded by
`von/tools/test_sharc_opcode_4c.py`.
The reusable finite-path C model is `von/i960/recovered_sharc_opcode_4c.c`.
Its early Y rejection, recorded bound cases, and unordered-input rejection are
covered by `von/tools/test_recovered_sharc_opcode_4c.py`.
Opcode `0x4d` (`0x20cf8`) consumes four FIFO words into `R8`, `R9`, `R10`,
and `R13`, then gates on `y-s[1] < 0` before performing the extended
normalized/refinement sequence. Static alignment with `0x4b` shows that this
normal arithmetic pipeline is instruction-for-instruction shared: the
`0x20d68`, `0x20dbe`, and `0x20dc4` calls, the radial `F15` construction, and
the second reciprocal-square-root refinement all match. The distinct behavior
is confined to the initial Y-gate polarity and the corresponding fallback/
comparison branch destinations. The normal paths return delayed `2` or `0`;
the early fallback consumes one extra word and returns `1`. Live probes with
separated `0x48`/`0x44` initialization reached `0x20d43` with result `2` for
`(0,4,0,0)`, and `0x20d4d` with result `1` for `(0,-4,0,0)`. The final
comparison is now instrumented: immediately before `COMP(F0,F1)` at `0x20d3e`,
the handler compares refined `F0` against `F1 = F9 + state[3]`, where `F9` is
the fourth-input-dependent refined bound. A static comparison with opcode
`0x4b` corrects the earlier radial shorthand: `0x4d`'s pre-refinement seed is
`dx² + dz²`, because `0x20d00` forms `F8=dx²`, `0x20d04` forms `F2=dz`,
`0x20d05` copies `F2` into `F4`, and `0x20d06` forms `F12=dz²` before
`0x20d07` adds them. The tested vectors `(3,4,0)`, `(3,4,3)`, and
`(4,4,0)` therefore produce horizontal seeds `9`, `18`, and `16`, matching
the Euclidean horizontal metric. The temporary cross-term interpretation was
caused by reading the aliased F2/R2 register without accounting for `0x20d05`.
This exact seed is modeled by `recovered_sharc_opcode_4d_horizontal_seed.c` and
tested by `von/tools/test_recovered_sharc_opcode_4d_horizontal_seed.py`. For state
The saved pipeline traces also separate the later radial term from the bound
term: the final `F15` values are `25`, `34`, and `32` for `z0`, `x3z3`, and
`x4z0`, while final `F9` is approximately `1.2293`, `1.4731`, and `1.4337`.
The instruction sequence and controlled traces now recover the finite-seed
bound lane: with `theta = atan2(dy, sqrt(dx² + dz²))`,
`F9 = |fourth| * sqrt((2*cos(theta))² + ((1/3)*sin(theta))²)` for the tested
positive-seed cases. The constants come from the `F5`/`F6` multiplies at
`0x20d1b`/`0x20d1d`; `0x20d1f`–`0x20d2f` square, add, and refine the result.
The model is guarded by `recovered_sharc_opcode_4d_refined_bound.c`. A live
edge probe (`probe_sharc_opcode_4d_edge.lua`) shows that the zero-vector seed
produces NaN at the final comparison and output `2`. The earlier purported
negative-seed sample `(dx,dz)=(1,-2)` instead produces the valid Euclidean seed
`5` and reaches the finite normal path, correcting the prior cross-term
interpretation. Negative seeds are therefore not reachable from finite real
coordinates in this recovered path; the finite-seed model explicitly preserves
the observed zero/non-finite RSQRTS singularity. Other NaN/overflow behavior
remains provisional.
`[0,0,0,4,5]` and vector `(3,4,0)`, fourth input `0` makes
`F1` NaN and returns `2`, while fourth inputs `1.0` and `4.0` produce finite
`F1` values `0x40a75634` and `0x410eac67` and return `0`. A diagnostic run
with state offset `3=-100` still reported final `IF LT` false and result `2`,
while the result snapshot showed the changed value in `R14`; this confirms the
comparison term is independent of that diagnostic state mutation. At fixed state
`[0,0,0,4,5]` and vector `(3,4,0)`, live comparison traces for thresholds
`t=1,2,4` produce approximately `(F9,F1)=(1.229,5.229), (2.459,6.459),
(4.459,8.459)`, with `F0` approximately `5.0`. The fourth input therefore
reaches the comparison through the helper's exponent/range-reduction path;
the recovered algebraic formula is exact for the normal finite path, with only
SHARC-specific rounding and exceptional boundaries still qualified. A fixed-vector
state sweep over `state[3]=2,4,8` leaves `F9` unchanged while shifting `F1`
by exactly the state value, confirming that offset `0x03` is an additive
comparison term rather than part of the radial refinement. This is the last mapped
command-table handler: the next
table slot initializes `I0` to `0x30300` and begins a constant table rather than
pointing at another opcode routine. Exact predicate semantics remain
partly provisional, with the structure, compare boundary, and table boundary guarded by
`von/tools/test_sharc_opcode_4d.py` and `von/tools/test_sharc_dispatch_table.py`.
The terminal decision itself is now isolated in
`recovered_sharc_opcode_4d_decision.c`: negative `dy` returns `1`, while the
normal path returns `0` only for the strict comparison
`radial < refined_bound + state[3]`; equality and unordered floating-point
comparisons return `2`. The unresolved work is therefore narrowed to the
upstream production of `F9`/`refined_bound`.
Opcode `0x2f` (`0x206e1`) consumes three packed-vector words, decodes each
through the table at DM `0x30141`, and combines the resulting components with
the persistent 3×3 matrix. The decode is the same low-16-bit binary16-shaped
normal-coordinate construction used by opcode `0x38`; the tail update is
`tail[c] = x*M[0][c] + y*M[1][c] + z*M[2][c]` in row-major state order. It
updates offsets `0x09..0x0b`; offset `0x09` is written before `RTS (DB)` and
offsets `0x0a` and `0x0b` occupy the delayed slots. A live quarter-turn-Z
probe followed by opcode `0x20` readback returns approximately `[2,-1,3]`
for packed `(1,2,3)`, confirming that this is the same row-vector matrix
convention as opcode `0x38`. Caller-level naming of the tail remains
provisional; the decode, coefficient order, tail writes, and boundary are
guarded by `von/tools/test_sharc_opcode_2f.py`.
Opcode `0x26` (`0x20532`) consumes five FIFO words into `R0..R4` and uploads
them sequentially to DM `0x3013c..0x30140`. The first three stores execute
before `RTS (DB)` and the final two occupy its delayed slots. Its consumer
`0x27` establishes the visible field roles: uploaded words 0 and 2 are both
the X/Z origin values and the retained `R0/R2` distance weights, word 3 is
the weighted-magnitude threshold, and words 1 and 4 are not consumed by the
visible `0x27` path. This aliasing is modeled by
`recovered_sharc_opcode_27_uploaded_state()` and checked by
`von/tools/test_recovered_sharc_opcode_27.py`; the packet width, destination
range, delayed-store behavior, and next-handler boundary remain guarded by
`von/tools/test_sharc_opcode_26.py`.
Opcode `0x27` (`0x20543`) consumes three FIFO words into `R12..R14` and uses
the five-word block at DM `0x3013c` together with retained `R0/R2` scales.
Its first stage forms `dx = state[0]-x`, `dz = state[2]-z`, and the weighted
2D magnitude `m = sqrt(state[0]*dx² + state[2]*dz²)`; the retained `R0/R2`
registers alias those same uploaded origin/weight words. It compares `m` against state offset
`3`; the `GT` path emits three zero words at `0x2056b`, `0x2056d`, and
`0x20570`, while the normal path emits `dx/m`, `dz/m`, and the delayed
constant `1`. A live setup through opcode `0x26` with unit scales, state
`(1,*,1,10,*)`, and input `(0,0,0)` emits `0x3f3504f3` for both normalized
lanes (approximately `0.7071`) and `1` at output PCs `0x20563`, `0x20565`,
and `0x20568`. The finite normal/fallback contract is modeled in
`von/i960/recovered_sharc_opcode_27.c` and covered by
`von/tools/test_recovered_sharc_opcode_27.py`. A new unordered-input probe
shows NaN input and NaN threshold both take the three-zero fallback, so the
recovered model explicitly rejects nonfinite magnitude/threshold values rather
than relying on C relational behavior. Overflow payload details remain
qualified. The structure is guarded by
`von/tools/test_sharc_opcode_27.py`.
The reusable normal-path C contract is
`von/i960/recovered_sharc_opcode_27.c`, guarded by
`von/tools/test_recovered_sharc_opcode_27.py`.
Opcode `0x28` (`0x20572`) consumes five FIFO words into `R0`, `R1`, `R2`,
`R5`, and `R6`, loads the persistent translation tail at offsets `0x09..0x0b`,
and evaluates a projected 3×3 state expression. The listing proves three
strict gates on the derived projected component/magnitude: `F2 <= 0` branches
to the zero fallback, `F2 >= R6` branches to the same fallback, and after
reciprocal-square-root refinement `F8 >= R5` does likewise. Only the surviving
path emits delayed constant `1`; the fallback emits zero through its delayed
return tails. Identity-state probes for unit-X and unit-Z requests hit the
zero fallback, with zeros at `0x2056b`, `0x2056d`, and `0x20570`; a unit-Z
probe with `R5=R6=2` passed both strict gates and emitted `1` at `0x205a3`.
The new edge probe confirms that the zero-horizontal singularity reaches an
unordered intermediate but emits the visible fallback `0` at `0x205a7`, while
negative depth takes the first `LE` gate and emits the same `0`.
An additional unordered-input probe shows both NaN-horizontal and NaN-depth
requests also emit `0`; the SHARC arithmetic canonicalizes the intermediate
NaN words to `0xffffffff` before the fallback path. The recovered C predicate
therefore treats nonfinite projected depth, radial value, or scaled bound as
an explicit reject, matching the ROM's ordered/unordered branch behavior.
The register aliases now resolve the finite predicate. The three translated
components are `(tailX + x*s0 + y*s3 + z*s6, tailY + x*s1 + y*s4 + z*s7,
tailZ + x*s2 + y*s5 + z*s8)`; only the third component, `F2`, affects the
visible branch, while the first two are accumulated in `F8`/`F9`.
The three gates are `F2 <= 0`, `F2 >= R6`, and, after the reciprocal-square-root
refinement, `sqrt(x*x + z*F2) >= F2*R5`; each selects the zero fallback, while
the surviving path emits `1`. This explains the identity unit-Z probe: with
`R5=R6=2`, `F2=1` and the final comparison is `1 < 2`. A translated finite
path is modeled in `von/i960/recovered_sharc_opcode_28.c`, which now exposes
the full three-component projection, and covered by
`von/tools/test_recovered_sharc_opcode_28.py`. The packet shape, tail loads,
comparison branches, boolean outputs, and handler boundary remain guarded by
`von/tools/test_sharc_opcode_28.py`.
Opcode `0x29` (`0x205a9`) consumes four FIFO words into `R13`, `R14`, `R15`,
and `R2`. It resets the persistent 3×3 state at DM `0x30101` to identity,
installs the three translation-tail words at offsets `0x09..0x0b`, then
converts the signed-16 parameter in `R2` using scale `0x38c9116d` and helper
calls `0x20dbe` and `0x20dc4`. The resulting transformed terms are written
back across the matrix state, with the final write in the delayed-return
slot. A live opcode-`0x29` followed by opcode-`0x11` readback confirms that
translation `(10,20,30)` is preserved exactly in the three tail slots;
angle `0` produces the identity diagonal (within the SHARC helper's
`0x3f7fffff` rounding), while signed angle `0x4000` produces the expected
quarter-turn sine/cosine pattern including `±1.0` and a small helper residual
`0xb8492eef` at the nominal zero entries. In state order, the `0x4000` result
is `[c,0,+1 / 0,1,0 / -1,0,c]`; the signed angle `0xc000` case is
`[c,0,-1 / 0,1,0 / +1,0,c]`, with the same residual `c` and unchanged
translation tail. This identifies opcode `0x29` as the conventional row-major
Y-axis rotation initializer and establishes the signed-16 angle scale and both
quarter-turn signs; only the caller-level meaning of this initializer remains
provisional. The reset, inputs, helper chain, state writes, and boundary are
guarded by `von/tools/test_sharc_opcode_29.py`.
The reusable reset/translation/Y-rotation C model is
`von/i960/recovered_sharc_opcode_29.c`, guarded by
`von/tools/test_recovered_sharc_opcode_29.py`.
Opcode `0x2a` (`0x205da`) consumes one FIFO scalar, converts it to floating
point, and scales each of the nine elements of the persistent 3×3 state at
DM `0x30101`. It writes the transformed rows back to offsets `0x00..0x08`;
offsets `0x07` and `0x08` execute in the delayed-return slots. A live
identity-state probe with scalar `2.0` reads back exact diagonal words
`0x40000000`, zero off-diagonals, and zero translation tail, confirming the
elementwise matrix scale and readback ordering. This is a matrix-scale
service, with the caller's scalar meaning still unresolved, and is guarded
by `von/tools/test_sharc_opcode_2a.py`.
The reusable nine-element C model is
`von/i960/recovered_sharc_opcode_2a.c`, guarded by
`von/tools/test_recovered_sharc_opcode_2a.py`.
The pure data-movement model in `von/tools/sharc_service_contract.py` keeps
the copied 16-word state window distinct from the 12 words immediately
emitted; the downstream floating-point interpretation remains unresolved.

Opcode `0x44` (`0x20ba1`) is now bounded as a four-constant initializer rather
than a payload-bearing math command. It writes, at DM offsets `0x0c..0x0f`
from base `0x30150`, the raw IEEE-754 words `0x40000000`, `0x3eaaaaab`,
`0x3f000000`, and `0x40400000` (2.0, approximately 1/3, 0.5, and 3.0).
The fourth write is in the delayed-return slot, so it must be included in the
service contract. The reusable exact-word model is
`von/i960/recovered_sharc_opcode_44.c`, guarded by
`von/tools/test_recovered_sharc_opcode_44.py`; the listing-shape audit remains
in `von/tools/test_sharc_opcode_44.py`.

The neighboring fixed-point entries are bounded at their service boundaries.
Opcode `0x0a` (`0x20211`) is now bounded as the two-word floating-point angle
service immediately before this fixed-point group. `R1` receives the first
word, the delayed `R0` read supplies the helper's first argument, and the
handler computes `atan2(second, first) * 0x4622f83d` before `FIX`. A post-boot
MAME probe returns `0x00000000`, `0x00003fff`, `0x00001fff`, and `0x00005fff`
for `(1,0)`, `(0,1)`, `(1,1)`, and `(-1,1)`, establishing the operand order
and signed 16-bit angle scale. The executable model is
`von/i960/recovered_sharc_opcode_0a.c`; broader helper edge behavior remains
provisional.
Opcode `0x1b` (`0x203b6`) and opcode `0x1c` (`0x203c2`) each consume one word,
sign-extend its low 16 bits by the `<<16`/arithmetic-`>>16` pair, convert it
to floating point, and emit one result after their sibling helper and the
shared scale constant `0x38c9116d`. Opcode `0x1d` (`0x203ce`) consumes two
words, but only the first is sign-extended and angle-converted. The delayed
second read targets `R15`; the final `F0 = F0 * F15` uses that word's raw
IEEE-754 register alias as a multiplier. A direct post-boot probe sends
`(0x4000, 0x3f800000)`, `(0x2000, 0x40000000)`,
`(0xffffc000, 0x3f000000)`, and `(0x7fff, 0x3f800000)` and receives
`0x3f800000`, `0x3fb50610`, `0xbf000000`, and `0xb3bbbd00`, respectively.
Standalone wrappers for the two single-word services are
`von/i960/recovered_sharc_opcode_1b.c` and
`von/i960/recovered_sharc_opcode_1c.c`, guarded by
`von/tools/test_recovered_sharc_opcode_1bc.py`. The recovered model is
`von/i960/recovered_sharc_opcode_1d.c`, with the
runtime contract guarded by `von/tools/test_recovered_sharc_opcode_1d.py`;
broader helper rounding and non-finite multiplier behavior remain provisional.
Opcode `0x1e` (`0x203dc`) is the cosine sibling: it sign-extends and scales
the first word, calls `0x20dbe`, then multiplies by the delayed raw `F15` word.
The post-boot probe returns `0x3f7fffff`, `0xb8c92eef`, and `0x3f3503d8` for
`(0,1.0)`, `(0x4000,2.0)`, and `(0x2000,1.0)`. The matching model is
`von/i960/recovered_sharc_opcode_1e.c`; negative-angle and non-finite multiplier
coverage remain provisional.
The helper entry points are now bounded: `0x1b` and `0x1d` call `0x20dc4`,
while `0x1c` calls `0x20dbe`; all use the `0x38c9116d` scale word. The shared
helper cluster reads coefficients from DM `0x3030c` and executes a six-iteration
reduction loop. Those constants now identify the operation: the table begins
with `1/π` and a π range-reduction pair, then contains the odd sine-series
coefficients `-1/6`, `1/120`, `-1/5040`, through `x^15/15!`. The shared input
scale `0x38c9116d` is `π/32767`, so the signed-16 services are angle
converters over a half-turn. The `0x20dbe` entry additionally establishes `ABS(F0)`,
`0x3fc90fdb` (`π/2`), and the DM `0x3030d` coefficient value (`0.5`), whereas
`0x20dc4` seeds the common path with `R7 = 1.0` and `R12 = 0`. This narrows
the unresolved question to exact SHARC rounding and quadrant/sign routing:
the `0x20dc4` caller is the sine-shaped path, while `0x20dbe` adds the π/2
phase needed for the cosine-shaped sibling. The raw constants and scale are
now also runtime-backed by `von/tools/probe_sharc_opcode_1b.lua`: opcode `0x1b`
returns `0x00000000` for input `0`, exact `0x3f800000` (`1.0`) for `0x4000`,
and near-zero endpoint values `0xb3bbbd00` and `0x38c92eef` for `0x7fff` and
`0x8000`, respectively. The canonical quarter-turn and half-turn samples
confirm the sine interpretation; only implementation-specific endpoint
rounding remains open.
The sibling probe `von/tools/probe_sharc_opcode_1c.lua` provides the matching
phase-shift check for the cosine-shaped path: inputs `0`, `0x4000`, `0x7fff`,
and `0x8000` emit `0x3f7fffff`, `0xb8492eef`, `0xbf7fffff`, and `0xbf7fffff`.
Those results establish the cosine-shaped routing while preserving the ROM's
distinct endpoint rounding; the static constant interpretation remains
guarded by `von/tools/test_sharc_trig_constants.py`.

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

The producer is now represented by
`von/i960/recovered_geometry_35_producer_6f600.c`. Its exact boundary is
distinct from `0x6ece0`: after the `0x41` lookup it reads the returned
20-byte record and emits record offsets `+0x04`, original `x` bits, `+0x0c`,
original `y` bits, `+0x10`, and bitwise-not of `+0x08`, then returns one final
FIFO word. The same `0..1023` truncation/bounds and half-coordinate index are
shared. The packet order, rejection sentinel, and callback behavior are
checked by `von/tools/test_recovered_geometry_35_producer_6f600.py`.

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

The listing gives an explicit parallel-slot contract: the first operand loads
`R4` and participates in `F8 = F0(previous) * F4`; the third loads `R6` and
participates in `F12 = F2(previous) * F6`; the next slot forms `F8 + F12`,
then `F0 = F8 + F13(previous)`, while the second operand is copied from `R0`
into `R7` for reciprocal correction. The fifth and sixth reads still feed
surrounding state through `R13` and `R12`, but do not appear in the visible
scalar output path. These slot relationships are enforced by
`von/tools/test_sharc_opcode_35.py`; persistent-register values and FIFO timing
remain runtime questions.

The extracted SHARC listing makes the handler's live data path more precise.
With the six inputs named `(a, b, c, d, e, f)` in the FIFO order above, the
parallel operations are:

```text
F8  = F0(previous) * a
F12 = F2(previous) * c
F0  = F8 + F13(previous)       # pipeline-side state update
R7  = b
```

The next instruction replaces `F0` with `RECIPS(F12)`. The ADSP-2106x manual
specifies this as an 8-bit reciprocal seed selected from a mantissa ROM table,
with seed exponent `-e-1` for input exponent `e`; it also documents the exact
Newton sequence used by this handler. Three repeated
correction stages then update `F12 = F0 * F12`, `F7 = F0 * R7`, and
`F0 = F11 - F12`; the delayed-return path performs the final `F7` update,
followed by `F0 = F0 * F7` and one FIFO write of `R0` at SHARC instruction
`0x908`. The manual's division primitive requires `F11 = 2.0` and returns a
quotient accurate to one LSB in the selected 32- or 40-bit mode. Inputs `d`,
`e`, and `f` are consumed into `R2`, `R13`, and `R12` for the surrounding
parallel pipeline, but do not enter the scalar result after this handler's
visible arithmetic. The remaining work is to validate persistent-register
staging and FIFO timing against a paired runtime trace.
The reusable normal-case algebra is now explicit in
`von/i960/recovered_sharc_opcode_35.c`, with direct coverage in
`von/tools/test_recovered_sharc_opcode_35.py`. The model now includes the
ADSP-2106x `RECIPS` mantissa table and the three visible Newton corrections;
an audit against MAME found and corrected a missing `0x00390000` entry at
table index 49, which had shifted every later reciprocal seed in the recovered
model. That table correction does not change the current live reference vector
(its denominator selects index 112), so the remaining one-ULP discrepancy is
still a precision-boundary question rather than a lookup-table mismatch.
The remaining discrepancy was then resolved by matching the ROM's actual
rounded lane schedule: F7 carries the quotient and F12 carries the residual,
with each correction multiplying both lanes before the next correction. The
model now reproduces the live `0x4306a2f7` result. It also preserves the observed canonical
`0xffffffff` result for zero/infinite/NaN denominators. Denormals and the
remaining inherited-register staging are still qualified.

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

## Shared Object-State Transition Helper: `0x00079050`

The `0xc5130` object-pool creator is now statically closed. It scans the
37-entry pool at `0x576c50`, using a `0x2c`-byte stride and the signed
halfword at slot `+0x04` as the free/occupied sentinel. On the first free
entry it copies input bytes and words into slot offsets `+0x01`, `+0x02`,
`+0x10`, `+0x14`, and `+0x18`; writes the two ROM-derived values at `+0x04`
and `+0x28`; clears `+0x1c`, `+0x20`, and `+0x24`; and stores the source
handle, sequence number, and incremented global sequence counter at `+0x0e`,
`+0x06`, and `0x5770a0`. The byte/halfword lookup chain is exact: the input
type and mode select `0x13e170`, the same pair selects a byte at `0x13db08`,
that byte AND the input type selects `0xc4f40`, and the resulting signed
halfword becomes the occupancy/key field. The helper call at `0xf5058` is
preserved as an external bookkeeping boundary; its caller context is the
value copied to slot `+0x08`. The pure layout model and pool-full behavior
are host-tested in `von/i960/recovered_object_pool_create.c`.

The adjacent creator at `0xc5240–0xc5304` shares this pool and lifecycle
commit, but receives its selector in `g2` and its derived word in `g1` from
the caller. It copies only the three value words, `+0x0c`, and the shared
sequence/source fields; it writes the selector's low byte at slot `+0x00`
and selects the signed `0xc4f40` halfword with the selector masked to eight
bits. It does not repeat the type/mode table lookup or overwrite the other
small fields. Both creators therefore describe one record format with two
distinct construction paths. The sibling model is included beside the
primary creator and covered by the same focused test.

The third pool creator at `0xc5310–0xc53e0` is a rebasing/update path over
the same records. It copies input words `+0x14`, `+0x18`, and `+0x1c` into
slot `+0x10`, `+0x14`, and `+0x18`; selects `+0x28` from the mode/selector
table at `0x13e170`; selects the slot type from `0x13db08`; and resolves the
occupancy halfword through `0xc4f40` using that type byte directly. It clears
the three work words and copies the preserved caller context into slot
`+0x08`, `+0x0a`, and `+0x0c`. Because `g0` is replaced with the input
`+0x1c` word before the final commit, slot `+0x0e` receives that word's low
half rather than the input pointer. This path is now modeled and tested;
the table-derived field names remain intentionally neutral.

The pool consumer at `0xc5530–0xc5598` is a complete type dispatcher. It
preserves the caller handle, scans every `0x2c`-byte record, ignores free
records (`+0x04 <= 0`) and records whose type byte exceeds `60`, then loads
the handler from the eight-byte-stride table at `0xc4f44` and calls it with
the record address. The model exposes that indirect call as a callback and
returns a host-only dispatch count for testing; the ROM's observable work is
the handler side effect and the subsequent diagnostic/status write.

The communication-board routine at `0xc5870–0xc5b10` is a retrying state
machine rather than a simple status read. If `0x5770b0` is already nonzero it
reports the terminal node-count error path; otherwise it samples timing,
checks bit 0 of `0x1a14000` for the immediate missing-board failure, performs
a 60-sample handshake delay, asserts the board-start byte, waits for bit 7 of
`0x1a14002`, clears the two `0x700`-byte communication buffers, and queries
the board through the external communication helpers. Byte `0x5770b1` then
selects exactly five role messages: 0 relay, 1 master, 2 slave, 3 standalone,
and all other values illegal. The pure role/status selectors are modeled in
`von/i960/recovered_comm_status.c`; mapped I/O, timing, formatting, and retry
side effects remain explicit hardware boundaries.

The pool reset at `0xc55a8–0xc55f8` invalidates all 37 records by writing
`0xffff` to each `+0x04` key and zero to each type byte, then fills the eight
words at `0x577070–0x57708c` with `0xffffffff`. The communication control
reset at `0xc5608–0xc5624` independently clears the two mapped bytes at
`0x1a14000` and `0x1a14002`; both are now represented by focused pure models.

The profile initializer at `0xc8fa0–0xc9084` is now structurally closed. For
profiles other than `13`, it calls the profile configuration entry from
`0xc8ed0`, publishes the `-1` completion sentinel at `0x504d10`, and retains
the returned handle. It then invokes the first handler column at `0xc8e10`,
clears `0x5770f4` and `0x577118`, loads the profile-specific long pair from
`0x142fd4` and word from `0x142fdc`, runs the external initialization and
format helpers, and publishes the handle to `0x577110` and `0x577114`.
Profile `13` skips the configuration call and uses a zero handle. The model
keeps all indirect/helper calls as callbacks while testing their exact order
and the shared-state writes.

The wrapper at `0xc8f10–0xc8f54` selects the middle handler column for the
current communication/geometry profile. It extracts bits 13–15 of the signed
halfword at `0x504baa`, masks them to `0..7`, and stores the result at
`0x5770f4`; it computes table index `profile * 3 + 1` in the three-column
table beginning at `0xc8e10`; then it calls the `0xc5d70` packet builder with
`0x577114` and calls the selected handler with that same input. The pure model
keeps both calls as callbacks and returns the table index only for host tests.

Its sibling at `0xc8f60–0xc8f94` selects the third column (`profile * 3 + 2`)
from the same table, calls that handler with `0x577114`, then increments
`0x577114` exactly once. The increment occurs after the indirect call, so the
handler observes the pre-increment value.

The geometry packet builder at `0xc5d70–0xc5f18` has byte-accurate framing
despite an unresolved extended-FPU subexpression. When profile `0x5770f0` is
3, it writes 14 FIFO words: tags `28, 27, 28, 28, 28, 43` with the exact
masked input values `(g0 << 7) & 0xffff` and `(g0 << 6) & 0xffff`, two repeated
intermediate `g4` values, and the final `g6/g1/g5` values. Other profiles emit
four words: tag `43` followed by the long value at `0x577100` and the word at
`0x577108`. The common tail writes the mapped FIFO result three times to the
output stream, followed by the caller's output tag. The model in
`von/i960/recovered_geometry_profile_packet.c` keeps the FPU intermediates
and mapped result as explicit oracle inputs while preserving this framing.

The helper at `0xc5d48–0xc5d6c` is an exact fixed-size clear: it writes zero
to 16 consecutive bytes beginning at `g0`, then returns through the saved
continuation in `g14`. It has no protocol state or alignment dependency and is
modeled directly by `von/i960/recovered_zero_16.c`.

The highest-frequency untriaged attract target is a shared state-transition
routine, not a renderer leaf. Static control flow gives a complete boundary of
`0x79050–0x7962c` (exclusive `0x79630`), with ten indirect states selected from
the table at `0x7907c`. The entry receives an object pointer in `g0`; it saves
that pointer in `r5`, reads the object state at offset `0x64`, and invokes the
common time/update helper at `0xf5058` before dispatching.

The routine's observable contract is now concrete:

- `0x504d60` is read as a signed/floating timing value in several state arms.
- `0x504d68`, `0x504d94`, `0x504d9c`, `0x504e30`, and `0x504e4c` participate in
  mode, role/status, and object-state gating.
- The selected transition is written to `0x504d98`; the routine emits only
  states `1`, `2`, `7`, `8`, `9`, `10`, `11`, and `12` in the observed arms.
- The state-`7` and state-`8` arms use timing thresholds `0x40590000`,
  `0x40690000`, `0x4072c000`, and `0x40740000`, corresponding to float values
  `3.390625`, `3.640625`, `3.79296875`, and `3.8125`.
- The first dispatch guard rejects object states above `9` through the common
  return at `0x795c4`; later state arms can still assign the higher transition
  values listed above.

The target is called from the attract/menu object paths at `0x73e9c`,
`0x74904`, `0x75378`, `0x76cb4`, and `0x76d64`, and is itself called by the
following state helper at `0x796f0`. The 60-second attract worklist records 11
distinct callers and 15 direct-call edges. This establishes it as a central
candidate for scheduler/object-state closure. The arm semantics are now
isolated and tested; the remaining work is caller-side integration: correlate
the `g0` object pointer and the `0x74`-derived related pointer with
input-driven progress traces before enabling the dispatcher in startup.

The entry contract is now more precise than the earlier caller note implied:
the routine receives the object pointer in `g0`, copies it to `r5`, then loads
`0x74(r5)` and calls `0xf5058`; that helper returns the related pointer in
`r4`. The dispatcher reads the object state from `0x64(r5)`, while the common
tail reads the related tag at `0x172(r4)` and the caller state at `0x64(r5)`
before applying the `0x504d98` remap. A bounded i960 diagnostic now samples
these exact points, including the input pointer, both derived pointers,
object state, related tag, and emitted transition, so the next input-driven
capture can test the integration without guessing from the indirect jump
table alone.

The caller audit supports that interpretation across the wider call set. The
explicit setup sites copy `r4`, `r5`, `r6`, `r8`, `r12`, or `g10` into `g0`
immediately before the call (including `0x74900`, `0x7536c`, `0x76ca8`,
`0x76d50`, `0x7cfb8`, `0x7e9e0`, `0x7efb8`, `0x7f08c`, `0x7f7e8`,
`0x7f8e8`, `0x7fc7c`, `0x7fec8`, `0x806e0`, `0x80c9c`, `0x80f2c`,
`0x81008`, `0x81670`, `0x827dc`, and the four `0x82fe8–0x83030`
sites). This is consistent with an object-pointer argument; the object state
used for the indirect jump is loaded separately from `0x64(r5)`. The remaining
callers inherit `g0` from their surrounding object-selection paths and are the
ones that still need runtime correlation.

The visited-PC log provides the first runtime branch constraint. In the
input-free 60-second attract capture, the state-table entries reached were:

```text
state 0 -> 0x790a4
state 5 -> 0x79400
state 8 -> 0x795a8
state 9 -> 0x795b8
```

The entries for states `1–4`, `6`, and `7` were not visited in that scenario.
This does not prove those arms are dead; it does establish that the first
behavioral reconstruction can be regression-tested against four concrete arms
before input-driven and match-state captures expand the closure.

The static transition inventory narrows the next capture substantially. The
state arms do not write arbitrary values: direct writes to `0x504d98` are only
`1` (state 3/6 paths), `2` (state 3's special path), `7` (the state 8/9
fallback arms), `8` (several timer-and-mode paths), and `9` (state 3/5 paths).
The common tail at `0x795c4` is the only place that produces `10`, `11`, or
`12`, and only after the object tag/state/caller triple `(31, 3, 6)` matches.
This separates scheduler transition selection from the later object-specific
remap and gives the runtime worklist concrete values to watch for.

The two visited terminal arms are now isolated in
`recovered_object_state_terminal.c`. At `0x795a8` (state 8) and `0x795b8`
(state 9), the ROM writes exactly `7` to `0x504d98` and falls through the
common tail. The terminal arms have no timer, mode, or object-field reads of
their own; the exhaustive host test covers the dispatch value domain and
confirms that all other state values leave the caller's transition unchanged.

The visited state-5 arm at `0x79400` is also isolated in
`recovered_object_state_five.c`. Its signed timing bands are `< 0`, `[0,
3.640625)`, and `>= 3.640625`. The first band selects `8` when mode bit 1 is
set and otherwise `7`. The middle band selects `9` only when the caller state
is greater than `3` and mode bit 2 is set. In the final band caller state `0`
always selects `7`; caller states `1..4` select `9` on mode bit 2; and caller
states `5..9` prioritize mode bit 1 (`8`) before the mode-bit-2 `9` path. All
other cases select `7`. The boundary test covers negative zero, both sides of
the exact `3.640625` constant, all ten caller states, and all mode-bit
combinations.

The state-4 arm at `0x79374–0x79400` is isolated in
`recovered_object_state_four.c`. In negative time, caller states above `5`
with mode bit 2 select `9`; otherwise caller states `0..2`, clear mode bit 1,
or role values `>= 6` select `7`, and the remaining cases select `8`. For
nonnegative time, mode bit 1 combined with role `< 6` selects `8`, otherwise
`7`. The ROM-loaded `0x4072c000` (`3.79296875`) is not used by the first
compare, so the effective boundary is the sign of the timing value rather than
that apparent threshold. The test covers both sides of the dead-threshold
constant, signed zero, all callers, mode combinations, and role values.

The state-2 arm at `0x791fc–0x7928c` is isolated in
`recovered_object_state_two.c`. Global state `0x504d9c == 5` combined with
mode bit 1 immediately selects `8`. Otherwise, negative timing first selects
`9` for caller states `0..4` with mode bit 2; remaining callers select `8` only
when mode bit 1 is set and role `0x504d68` is greater than `6`, otherwise `7`.
For nonnegative timing, caller states above `2` with mode bit 2 select `9`, and
all other cases select `7`. The loaded `0x4072c000` value is dead in the
effective compare. Tests cover the global fast path, sign boundary, apparent
threshold, all caller/mode combinations, and role values.

The state-1 arm at `0x79178–0x791fc` is isolated in
`recovered_object_state_one.c`. Clear mode bit 1 or role values `0..6` select
`7`. With mode bit 1 and role `> 6`, negative timing selects `8`; nonnegative
timing selects `9` only for caller states `0..2` with mode bit 2, otherwise
`8`. The ROM-loaded `0x40590000` (`3.390625`) is dead because the effective
compare is against zero. Tests cover the sign boundary, apparent threshold,
all caller/mode combinations, and both sides of the role cutoff.

The state-6 arm at `0x794ac–0x7953c` is isolated in
`recovered_object_state_six.c`. Role values `5` and `6` select transition `1`;
roles `0`, `4`, and `>=7` select `8` on mode bit 1 and otherwise `7`. Roles
`1..3` use the same fallback except for the guarded `(related tag == 31,
related state == 3, global 0x504e4c in {1,3,4,6,7})` case, where only global
values `3` and `6` can select `8` when mode bit 1 is set. Because this arm's
current state is `6`, the common tail remaps guarded `7 -> 10` and `8 -> 11`.
Tests cover every role/mode/tag/state/substate combination in the modeled
domains.

The state-7 arm at `0x7953c–0x795a8` is isolated in
`recovered_object_state_seven.c`. A related object state other than `4`
always selects `7`. For global state `0x504d9c <= 3`, related state `4` uses
mode bit 2 to select `9`, otherwise `7`. For global state above `3`, caller
states `0..3` with mode bit 1 select `8`; all remaining callers select `9`
only when greater than `1` with mode bit 2, otherwise `7`. This arm's current
state is `7`, so the common tail performs no higher-state remap. Tests cover
all modeled global/related/caller/mode combinations.

The visited state-0 arm at `0x790a4–0x79178` is isolated in
`recovered_object_state_zero.c`. Nonnegative timing, and negative timing with
mode bit 1 clear, write transition `7`. For negative timing with mode bit 1
set, roles `1..3` fall through without a write; roles `0` and `>=7` write `8`
only when `0x504d68 >= 8`; role `4` writes `8` for values `0..5` or `>=8`;
roles `5` and `6` write `8` for values `0..3` or `>=8`. The remaining cases
preserve the pending transition. The pure model and test explicitly retain
that no-write contract rather than converting fallthroughs into transition 7.

The state-3 arm at `0x7928c–0x79374` is now reduced in
`recovered_object_state_three.c`. For role `4`, caller states above `5` select
`7`; caller states `0..5` select `9` when mode bit 1 is set, or when the caller
is `0..2` with mode bit 2 set, and otherwise select `7`. For all other roles,
only caller states `0..2` with mode bit 2 set select `9`; every other case is
`7`. The related-object state and the loaded timer do not alter that reduced
result because their alternate branch is guarded by caller states already
forced into the `7` path. The downstream `0x79358` check is also represented:
when global state `0x504d9c` is `3` and the selected value is `8`, it routes to
the state-7 arm. Exhaustive tests cover related states, roles, callers, mode
bits, and both sides of that global check.

The state-entry report is reproducible with:

```sh
python3 von/tools/analyze_object_state_coverage.py \
  von/build/attract-coverage/vonj-attract-60s.pcs
```

The shared return tail at `0x000795c4-0x00079630` is now isolated. It only
acts when the object halfword at `+0x172` is `31`, the current object's state
at `+0x64` is `3`, and the caller object's state is `6`. Under those guards it
maps pending transitions `8 -> 11`, `7 -> 10`, and `9 -> 12`; all other
transitions return unchanged. The pure mapping is implemented in
`recovered_object_state_tail.c` and exhaustively tested across the guard and
transition domains. All ten state arms now have separate pure models (states
0 through 7 plus the terminal state-8/9 routes), each tested against the
static branch reduction. They remain separate from one unified pointer-based
dispatcher and from input-driven runtime correlation; those are the remaining
integration boundaries rather than missing arm semantics.

The arm models are now exposed through the context-based
`recovered_object_state_dispatch()` entry point. It carries the ROM-derived
object fields, global words, timer bits, and caller state explicitly, dispatches
all ten table entries, and preserves the state-0 no-write result for callers
that already have a pending transition. This is behavioral integration only:
the production startup does not yet call it because the original pointer
relationships and input-driven object lifecycle still need runtime correlation.

The random-role tail at `0x79664–0x796ec` is isolated in
`recovered_object_state_random_selector.c`. The preceding `0xf5058` call
supplies a nonnegative 31-bit random value; the ROM's align/subtract sequence
therefore reduces it to `random & 7`, then selects roles `[1, 1, 2, 2, 3, 3,
5, 6]`. The selector is exhaustive-tested over one million values. The
`0x504dfc` timer gate and the subsequent object-pointer call remain separate.

The local MAME executable and staged ROMs are present, but the existing capture
wrapper requires the external `toolbox` command, which is unavailable in this
environment. Consequently, no new pointer-provenance trace is being treated
as runtime evidence; the caller integration boundary remains static until a
toolbox-backed input-driven capture is available.

### Secondary Object-State Dispatcher: `0x00079d60`

The nearby five-edge target at `0x79d60` is a separate ten-entry dispatcher,
with its own table at `0x79d8c`; it must not be merged with the `0x79050`
scheduler. Its state-0 arm first requires bit 1 of `0x504e30`, converts the
integer field at `0x504e0c` into floating-point state, and compares that value
against the timing field at `0x504d60` and the embedded boundary `0x40140000`
before selecting the success/failure transition paths. The remaining arms use
different timing constants and mode bits, so this dispatcher is recorded as a
separate follow-up rather than treated as an alias of the first state machine.
The jump-table, pointer handoff, and state-0 guard are locked by
`von/tools/test_secondary_object_state_dispatch.py`; input-driven pointer
correlation remains the next runtime step. The same oracle now pins the
high-confidence portions of state 1 (`0x79e10`): negative timing is split
by related-object tag bands `0x15..0x19`, then the `0x4062c000` timing band
routes caller states 2, 4, and 5 to distinct common exits. State 5
(`0x79ff4`) is likewise confirmed to read the shared selector, use the
`0x40590000`/`0x40690000` timing bands, and write selector values 13, 14,
or 15 at `0x504d98` according to caller state and mode bit 1. States 2–4
are now covered as well. State 2 (`0x79e8c`) has the
`0x4062c000`/`0x40790000` timing bands and mode-bit 2/1 exits. State 3
(`0x79ef4`) gates caller states 2/3, related states 6/3, and mode bits 2/1
before reaching the common selectors. State 4 (`0x79f5c`) reads the prior
selector, uses the `0x40590000`/`0x40690000` bands, computes the absolute
caller state, and writes 13/14/15 at `0x504d98`. These are all
static instruction-level facts; the object-pointer meaning and runtime
frequency of each route remain unvalidated. State 6 (`0x7a098`) adds a
related-object state-3 gate, a `0x504e4c` value-3/6 gate, the
`0x40568000..0x405b8000` timing window, and a mode-bit-1 path that writes
14. State 7 (`0x7a150`) adds the related tag `0x15..0x19` range and the
related-object state/`0x504d9c` combinations before the common mode-bit-2
and mode-bit-1 exits. The oracle checks these instruction fragments and
their exact common targets, but does not infer higher-level object names.
The terminal arms are now pinned too: state 8 (`0x7a204`) writes selector
13, state 9 (`0x7a214`) returns immediately, and the shared exits at
`0x7a1e4`/`0x7a1f4` write selectors 15/13 respectively. This completes the
static control-flow audit of all ten table entries; only runtime pointer
correlation and frequency remain open for this dispatcher.

The helper cluster immediately before it (`0x00079c10-0x00079d50`) is likewise
distinct from the dispatcher body. These leaves convert the threshold words at
`0x504e04` and `0x504e06`, compare them with the shared timing value at
`0x504d60`, and route to the existing transition handlers at `0x783c8` and
`0x78408`. The active transition setup writes `1` to `0x504d98`, `10` to
`0x504db8`, clears `0x504d94`, and writes `1` to `0x504d84`; the final helper
selects transition `1` or `2` when `0x504dc8 == 1` and the object state is `7`.
This gives the secondary scheduler a concrete timing/setup boundary while the
exact floating-point comparison polarity is still being checked against an
input-driven trace.

The terminal leaf at `0x00079d20-0x00079d50` is now isolated. When
`0x504dc8 == 1`, it writes transition `2` for object state `7` and transition
`1` for every other state; otherwise it performs no transition write. This
exact gate/state mapping is implemented in `recovered_secondary_transition.c`
and exhaustively tested over representative gate and state values.

### Geometry Slot Pools: `0x0006fa40-0x0006fb80`

The geometry setup immediately following the projection validators contains
two bounded slot cursors. The 64-entry pair at `0x6fa40` / `0x6fa90`
increments before reading a slot and decrements before storing a released
value. Counts above 63 return `0xffffffff` without changing the cursor. The
parallel 32-entry pair at `0x6fb10` / `0x6fb50` has the same contract with a
31 maximum. The acquire/release primitives are implemented in
`recovered_geometry_slot_pool.c` and tested across every valid count and the
full-pool boundary; the larger allocator that populates these tables remains
separate.

The allocator at `0x0006fb90-0x0006fd4c` now has a bounded record-init model.
An allocated slot selects an 84-byte destination record. Eleven template words
are copied into the record's header and geometry fields; offsets `0x1c` through
`0x2c` and `0x48` through `0x50` are cleared, while the association fields use
`999` when the source association is empty and otherwise preserve its value
alongside a `999` sentinel. The deterministic portion is implemented in
`recovered_geometry_record_init.c` and tested for both association branches.
The subsequent free-list head/count mutation is deliberately not included
until its linked-record semantics are correlated.

The paired release routine at `0x0006fd50-0x0006fe6c` now has an explicit
association-repair plan. It releases a 32-pool entry, then processes the
source record's `0x14` and `0x18` links symmetrically: a non-`999` link updates
the referenced record's opposite field (`0x18` or `0x14`), while a `999` link
updates the corresponding side table at `0x51c5c8` or `0x51c5c4`. The source
reference count is decremented with 32-bit wraparound. The plan is implemented
in `recovered_geometry_link_release.c` and tested across sentinel, ordinary,
and wrapped-count cases; actual mapped-memory writes remain outside the pure
plan.

The shared return tail at `0x000795c4-0x00079630` is now isolated. It only
acts when the object halfword at `+0x172` is `31`, the current object's state
at `+0x64` is `3`, and the caller object's state is `6`. Under those guards it
maps pending transitions `8 -> 11`, `7 -> 10`, and `9 -> 12`; all other
transitions return unchanged. The pure mapping is implemented in
`recovered_object_state_tail.c` and exhaustively tested across the guard and
transition domains. The preceding ten state arms remain separate because
their timing and mode predicates still need input-driven traces.

## Indexed Video-Tile Expanders: `0x000e1f20` and `0x000e2040`

Two frequently called routines in the video setup path now have a complete
behavioral translation. Both accept a tile number in `g0` and a source pointer
in `g1`. The tile number selects a slot at `tile * 0x200` bytes in each of
three video planes rooted at `0x01810000`, `0x01814000`, and `0x01818000`.

Each routine consumes exactly 192 bytes as 64 groups of three indexed bytes.
Every byte is masked to eight bits and expanded through the 256-entry 16-bit
lookup table at `0x005775b0`; the three words are written to the matching
plane at successive two-byte offsets. The `0xe1f20` variant writes one 8x8
plane triplet. The `0xe2040` variant additionally writes the same 64 words at
`+0x100` bytes in every plane slot. This is a copy/mirror operation, not a
second lookup or a change in source traversal.

The production translation is in `von/i960/recovered_video_tiles.c`, with
randomized multi-tile coverage in `von/tools/test_recovered_video_tiles.py`.
The test verifies source consumption, lookup masking, tile-slot addressing,
plane separation, and that only the mirrored variant touches the second half
of each slot.

The four-edge wrapper at `0x000e2120` is now attached to that implementation:
it loads a source pointer from `0x142e94[g1*4]` and invokes the mirrored
`0xe2040` expansion with the caller's tile selector in `g0`. The wrapper adds
no transform of its own; its source-table selection and delegation are tested
through the existing randomized tile suite.

The lookup producer at `0xe1e08` is now translated in
`von/i960/recovered_video_palette.c`. For selector values `1..10`, after the
firmware subtracts one, it selects these `(step, offset)` pairs:

```text
1: (0xfa,  5)    2: (0xf5, 10)    3: (0xf0, 15)    4: (0xeb, 20)
5: (0xe6, 25)    6: (0xe6, 40)    7: (0xeb, 32)    8: (0xf0, 24)
9: (0xf5, 16)   10: (0xfa,  8)
```

The generated entry is `initial + offset + floor(accumulator / 255)`, with
the accumulator starting at zero and increasing by `step` for each of the 256
entries. Selectors outside `1..10` use `(0xff, 0)`, matching the default arm.
The implementation stores the selected step and offset through optional
outputs so the table-generation contract can be tested independently of the
firmware's fixed work-RAM addresses. Exhaustive selector and edge-value tests
are in `von/tools/test_recovered_video_palette.py`.

The surrounding loader at `0x000e2130` is now bounded as a deterministic
asset plan in `von/i960/recovered_video_setup.c`. It always calls the lookup
producer, then selects the first four odd-numbered tiles from bank A or bank B.
Bank A is selected when `0x503a08 == 0`, or when the exact secondary condition
holds: `0x503a08 == 2`, `0x5039f4 == 1`, `0x503a7c == 0`, and the masked board
byte equals `0x5770d0 - 0x5770d1`. The remaining ten shared tiles are loaded
in both cases, after which the routine publishes the six observed video bases
(`0x2f8d890` plus offsets `0x60c0`, `0xc180`, `0x12240`, `0x18300`, and
`0x1e3c0`) and stores `0xff` to `0x577590`. The ROM source addresses and tile
sequence are covered by `von/tools/test_recovered_video_setup.py`; actual
mapped-RAM writes remain delegated to the existing tile and palette models.

The common prefix of the following dispatcher at `0x000e2330` is separately
isolated in `von/i960/recovered_video_dispatch.c`. It recomputes the same
video-bank flag, then gates `0x577590`: `0xff` returns without dispatch,
`0..0x81` selects the corresponding entry in the table at `0xe23b4`, and any
larger value takes the default route at `0xe33f4`. The table arms begin at
`0xe25bc` and remain an explicit follow-up because they perform differing
subsets of mirrored tile expansion. The common gate and boundary values are
covered by `von/tools/test_recovered_video_dispatch.py`.

Jump-table arm 0 (`0x000e25bc-0x000e25fc`) is also recovered as a descriptor:
it invokes the mirrored tile expander for tiles `11`, `21`, `23`, and `25`,
using ROM sources `0x02fb75d0`, `0x02fb5b90`, `0x02fb5c50`, and `0x02fb5d10`,
then joins the common `0xe33f4` exit. The exact four-entry plan is tested with
the dispatcher-prefix test; the mapped tile writes remain covered by the
existing mirrored-expander model.

Jump-table arm 1 (`0x000e2600-0x000e2660`) follows the same shape with six
mirrored expansions: tile `11` uses `0x02fb75d0`, followed by tiles `21`, `23`,
`25`, `27`, and `29` from `0x02fb5dd0`, `0x02fb5e90`, `0x02fb5f50`,
`0x02fb6010`, and `0x02fb60d0`. It then joins `0xe33f4`; both arm plans are
covered by `von/tools/test_recovered_video_dispatch.py`.

Arm 2 (`0x000e2664-0x000e26c4`) is the five-call variant: tile `11` uses
`0x02fb75d0`, followed by tiles `23`, `25`, `27`, and `29` from
`0x02fb6190`, `0x02fb6250`, `0x02fb6310`, and `0x02fb63d0`. It also joins the
common `0xe33f4` exit and is covered by the same descriptor test.

Arm 3 (`0x000e26c8-0x000e2718`) is another five-call mirrored expansion:
tile `11` uses `0x02fb75d0`, followed by tiles `23`, `25`, `27`, and `29` from
`0x02fb6550`, `0x02fb6610`, `0x02fb66d0`, and `0x02fb6790`. It joins the
common `0xe33f4` exit and is covered by the dispatcher test.

Arm 4 (`0x000e271c-0x000e276c`) completes the next five-call family: tiles
`11`, `23`, `25`, `27`, and `29` use `0x02fb75d0`, `0x02fb6850`, `0x02fb6910`,
`0x02fb69d0`, and `0x02fb6a90`, respectively, before the common `0xe33f4`
exit. The descriptor is covered by the dispatcher test.

Arm 5 (`0x000e2770-0x000e27a0`) is the shorter three-call variant: it expands
tiles `11`, `27`, and `29` from `0x02fb75d0`, `0x02fb6b50`, and `0x02fb6c10`,
then joins `0xe33f4`. This exact descriptor is covered by the dispatcher test.

Arm 6 (`0x000e27a4-0x000e27f4`) expands five mirrored tiles: `11`, `21`,
`23`, `25`, and `27` from `0x02fb75d0`, `0x02fb6cd0`, `0x02fb6d90`,
`0x02fb6e50`, and `0x02fb6f10`. It joins the common `0xe33f4` exit and is
covered by the dispatcher test.

Arm 7 (`0x000e27f8-0x000e2808`) performs one mirrored expansion for tile `11`
from `0x02fb75d0`, then joins the common `0xe33f4` exit. This one-entry plan
is covered by the dispatcher test.

Arm 8 (`0x000e280c-0x000e282c`) performs two mirrored expansions: tile `11`
from `0x02fb75d0`, then tile `29` from `0x02fb7450`, before joining the common
`0xe33f4` exit. This exact descriptor is covered by the dispatcher test.

The arm at `0x000e2830-0x000e2870` performs four mirrored expansions for tiles
`21`, `25`, `27`, and `29`, using ROM sources `0x02fb6cd0`, `0x02fb7e10`,
`0x02bfed8c`, and `0x02fb6fd0`, then joins `0xe33f4`. This is distinct from
the following plain `e1f20` arm beginning at `0xe2874`; the mirrored sequence
is covered by the dispatcher test.

The following arm (`0x000e2874-0x000e2904`) switches to the plain `e1f20`
expander. It loads nine tiles in order: `11`, `1`, `3`, `5`, `7`, `21`, `25`,
`27`, and `29`, from ROM sources `0x02fb75d0`, `0x02fb7a50`, `0x02fb7b10`,
`0x02fb7bd0`, `0x02fb7c90`, `0x02fb6cd0`, `0x02fb7e10`, `0x02bfed8c`, and
`0x02fb6fd0`. Its descriptor is separate from the mirrored arms and is covered
by the dispatcher test.

The next plain arm (`0x000e2908-0x000e2918`) performs only the tile `11`
expansion from `0x02fb75d0` before joining `0xe33f4`. It is covered by the
same dispatcher test using the separate plain-expansion descriptor.

The `0xe29a4-0xe2a3c` plain arm loads tiles `1`, `3`, `5`, `7`, and `9` from
`0x02fb7a50`, `0x02fb7b10`, `0x02fb4090`, `0x02fb4150`, and `0x02fb7bd0`,
then sets tile `11` before sharing `0xe2a30`, which supplies source
`0x02fb7c90`. The sibling arm at `0xe29fc-0xe2a3c` loads only tiles `1`, `3`,
`5`, and `7`, with the same final shared source. Both shared-tail variants are
covered by the dispatcher test.

The `0x000e2a40` arm is a bank-dependent plain-expansion selector. A nonzero
bank flag routes tiles `5` and `7` to sources `0x02fb4990` and `0x02fb4a50`;
zero routes them to `0x02fb4b10` and `0x02fb4bd0`. Both branches continue into
shared downstream arms (`0xe2ea4`/`0xe2ec8`), so only this exact two-tile gate
is isolated in the descriptor and test.

The adjacent `0x000e2a48` arm is another bank-dependent plain-expansion
sequence. Bank A loads tiles `9`, `11`, `1`, and `3` from `0x02fb5290`,
`0x02fb5350`, `0x02fb3d90`, and `0x02fb3e50`; bank B uses
`0x02fb5410`, `0x02fb54d0`, `0x02fb3f10`, and `0x02fb3fd0`. The two branches
converge at the existing downstream paths and are covered by the dispatcher
test.

The conditional family at `0x000e2ad4` has two complete plain `e1f20`
sequences. With the bank flag set, it expands tiles `1`, `3`, `5`, `7`, `9`,
and `11` from `0x02fb3d90`, `0x02fb3e50`, `0x02fb4990`, `0x02fb4a50`,
`0x02fb4c90`, and `0x02fb5350`, then continues at `0xe30a8`. With the bank
flag clear, the same tile sequence uses `0x02fb3f10`, `0x02fb3fd0`,
`0x02fb4b10`, `0x02fb4bd0`, `0x02fb4e10`, and `0x02fb4ed0`, then continues at
`0xe30cc`. Both source banks and exit addresses are covered by the dispatcher
test.

The `0x000e2b88` family is bank-dependent and uses plain `e1f20` expansion.
Bank A emits tiles `5`, `7`, `9`, and `11` from `0x02fb4990`, `0x02fb4a50`,
`0x02fb4c90`, and `0x02fb4d50`, then continues at `0xe2f24`. Bank B emits the
same tiles from `0x02fb4b10`, `0x02fb4bd0`, `0x02fb4e10`, and `0x02fb4ed0`,
then continues at `0xe2f48`. Both source banks and continuation addresses are
covered by the dispatcher test.

The `0x000e2c14` family is another bank-dependent plain `e1f20` sequence.
Bank A expands tiles `9`, `11`, `1`, and `3` from `0x02fb4c90`, `0x02fb4d50`,
`0x02fb4390`, and `0x02fb4450`, then continues at `0xe2f70`. Bank B uses
`0x02fb4e10`, `0x02fb4ed0`, `0x02fb4510`, and `0x02fb45d0`, then continues at
`0xe2f94`. Both branches are covered by the dispatcher test.

The `0x000e2ca0` family is bank-dependent plain `e1f20` expansion. Bank A
loads tiles `1`, `3`, `5`, and `7` from `0x02fb4390`, `0x02fb4450`,
`0x02fb4090`, and `0x02fb4150`, then continues at `0xe2fbc`; bank B uses
`0x02fb4510`, `0x02fb45d0`, `0x02fb4210`, and `0x02fb42d0`, then continues at
`0xe2fe0`. The source banks and continuation addresses are covered by the
dispatcher test.

The `0x000e2d2c` family is a six-tile plain `e1f20` bank split. Bank A emits
tiles `5`, `7`, `9`, `11`, `13`, and `15` from `0x02fb4090`, `0x02fb4150`,
`0x02fb5290`, `0x02fb5350`, `0x02fb4f90`, and `0x02fb5050`; bank B uses
`0x02fb4210`, `0x02fb42d0`, `0x02fb5410`, `0x02fb54d0`, `0x02fb5110`, and
`0x02fb51d0`. Both paths join the common `0xe33f4` exit and are covered by the
dispatcher test.

The `0x000e2df8` family is a bank-dependent two-tile plain `e1f20` sequence.
Bank A expands tiles `9` and `11` from `0x02fb5290` and `0x02fb5350`, then
continues at `0xe3008`; bank B uses `0x02fb5410` and `0x02fb54d0`, then
continues at `0xe304c`. Both branches are covered by the dispatcher test.

The `0x000e2e44` entry is a control-only bank gate: a set bank flag branches
to `0xe3008`, while a clear flag continues at `0xe304c`. It performs no tile
expansion itself; both continuation targets are represented directly by
`recovered_video_dispatch_arm24()` and covered by the dispatcher test.

The payload paths in the nested `0x000e2e4c` region are now isolated without
flattening its adjacent branch scheduling. The bank-A path at `0xe2e58`
expands plain tiles `1` and `3` from `0x02fb3d90` and `0x02fb3e50`; the bank-B
path at `0xe2e7c` uses `0x02fb3f10` and `0x02fb3fd0`. Both return through
`0xe33f4`. The source pairs are covered by the dispatcher test; the exact
entry-level branch-delay interpretation remains a separate follow-up.

The downstream `0x000e2ea0` split independently repeats the two plain
expansions for tiles `5` and `7`: bank A uses `0x02fb4990` and `0x02fb4a50`,
while bank B uses `0x02fb4b10` and `0x02fb4bd0`. Both paths join `0xe33f4`; this
is kept as a separate arm despite sharing source addresses with `0xe2a40`.

The `0x000e2eec` family is a bank-dependent two-tile plain `e1f20` payload.
Bank A expands tiles `9` and `11` from `0x02fb4c90` and `0x02fb4d50`, while
bank B uses `0x02fb4e10` and `0x02fb4ed0`; the branches continue through the
same `0xe30a8`/`0xe30cc` downstream targets as the earlier two-tile family.
Both source pairs and continuation addresses are covered by the dispatcher
test.

The downstream `0x000e3004` gate selects another four-tile plain payload.
Bank A expands tiles `1`, `3`, `5`, and `7` from `0x02fb4f90`, `0x02fb5050`,
`0x02fb4690`, and `0x02fb4750`; bank B uses `0x02fb5110`, `0x02fb51d0`,
`0x02fb4810`, and `0x02fb48d0`. Both paths join `0xe33f4` and are covered by
the dispatcher test.

The later `0x000e3090` gate selects a separate two-tile plain payload. Bank A
expands tiles `1` and `3` from `0x02fb4c90` and `0x02fb4d50`; bank B uses
`0x02fb4e10` and `0x02fb4ed0`. Both paths join `0xe33f4` and are covered by
the dispatcher test.

The `0x000e30dc` arm is a mirrored five-tile pointer-table sequence. It loads
the five source pointers at `0x00577598`, `0x0057759c`, `0x005775a0`,
`0x005775a4`, and `0x005775a8` and expands tiles `21`, `23`, `25`, `27`, and
`29` through `e2040`, then joins `0xe33f4`. The pointer-table addresses are
kept as sources rather than misidentified as direct ROM assets.

The selector-driven `0x000e319c` arm uses `e1fb0` and dynamic addresses from
the `0x00142f34` table. Bank A emits tile `1` from `table + selector*16` and
tile `3` from `table + ((selector<<2)|1)*4`. Bank B normally emits tiles `1`
and `3` from the `|1` and `|3` table slots; selector `5` instead emits tile
`5` from fixed address `0x00142f8c`, followed by tile `7` from the `|3` slot.
The descriptor records computed source addresses, helper identity, and the
common `e33f4` exit while leaving table contents to the runtime data model.

The `0x000e3314` arm combines the selector logic with three trailing mirrored
updates. Its first two calls use `e1fb0`: bank A uses table base `0x00142e94`
for tiles `1` and `3`, while bank B normally uses `0x00142f34`; bank-B
selector `5` substitutes tile `5` from `0x00142f8c` and tile `7` from the
`|3` table slot. All paths then use `e2040` for fixed tiles `25`, `27`, and
`29` from `0x00143704`, `0x001437c4`, and `0x02fb8590`, before `e33f4`.
The mixed helper sequence and computed source addresses are tested together.

The complete `0xe33f4` sentinel-match subpath is also isolated. Sentinel
`0x200` selects two `e2040` calls from `0x02fb5890` and `0x02fb5950`; bank A
uses tiles `5,7`, bank B uses `1,3`, and both continue at `0xe35a0`. A
nonmatching sentinel branches to `0xe3444` with no tile calls represented by
this pure plan; the later stateful path remains separate.

Within that stateful family, the `0x21f` sentinel payload at `0x000e349c`
is independently complete: bank A emits tiles `5,7`, bank B emits `1,3`,
both through `e2040` from `0x02fb5a10` and `0x02fb5ad0`, then continue at
`0xe35a0`. The descriptor treats the preceding `g5-0x200` range gate as the
caller-side condition and records this payload separately.

The unsigned range partition at `e3444` is represented independently:
sentinels `0x200..0x21d` route to the lower payload, exact `0x21f` routes to
the dedicated family, only `0x400..0x41e` reaches the middle payload, and
`0x420..0x43f` reaches the high payload. Values in the unsigned-wrap gaps,
including `0x21e` and `0x41f`, bypass tile work to `e35a0`. Boundary cases are
covered by the dispatcher test.

The later `0x000e34e4` payload is a sentinel-indexed `e2040` pair. It loads
sources from `0x02bfd544 + sentinel*4` and `0x02bfd5c4 + sentinel*4`; bank A
uses tiles `5,7`, bank B uses `1,3`, and both converge at `e35a0`. The
preceding `g5-0x400` range gate and its alternate `e353c` path remain outside
this pure payload descriptor.

The common `0x000e35a0` terminal writes `0xff` to the dispatch sentinel at
`0x00577590` and returns. It is represented by a pure reset-value function;
the mapped store is kept at the caller/integration boundary.

The higher-range `0x000e353c` payload is another sentinel-indexed `e2040`
pair. It loads sources from `0x02bfd5c4 + sentinel*4` and
`0x02bfd644 + sentinel*4`; bank A uses tiles `5,7`, bank B uses `1,3`, and
both converge at `e35a0`. The preceding `g5-0x420` range check can bypass the
pair to `e35a0` and remains separate from this payload descriptor.

The following `0x000e314c` arm uses the sibling `e1fb0` expander for five
unconditional tiles: `21` from `0x02fb3d90`, `23` from `0x00142dd4`, `25` from
`0x02fa5ad0`, `27` from `0x02fabb90`, and `29` from `0x02fb1c50`. It joins
`0xe33f4`. The descriptor records the helper address explicitly because
`e1fb0` uses a different destination base arrangement from `e1f20`.

The short `0x000e3130` arm sets tile `3`, branches immediately to `0xe313c`,
and expands from `0x02fb7d50` through `e2040` before joining `0xe33f4`. The
intervening `mov 7` at `0xe3138` is not executed: the local MAME i960 core
updates the instruction pointer directly for `b`, with no delay slot. This
arm is tested separately so the apparent fall-through does not become a
false second tile write.

The lower-range `0x000e3444` payload indexes two source tables by the
sentinel: `0x00129e28 + sentinel*4` and `0x00129ea8 + sentinel*4`. Bank A
uses tiles `5,7`, bank B uses `1,3`, and both paths converge through the
`e35a0` tail. The preceding `g5-0x200`/`29` comparison selects the separate
`0x21f` family above this range and is not folded into the pure payload.

The untriaged `0x000786d0` action arm is now reduced to a pure timing split:
after the normalized-difference guard, `current >= threshold` routes to the
action-5 helper and the remaining comparable case routes to action 10; an
unordered/NaN-like normalized result is rejected. The preceding `0x784c8`
state update and the action-helper mapped writes remain outside this adapter
and are recorded as integration work.

The `0x000784c8` helper is now represented at its selector-dispatch boundary:
unsigned selectors `0..9` target the ten handlers at `0x78508` through
`0x78618`, while selectors above `9` return immediately. The handler-local
mode-bit tests and their `0x504d84` writes remain separate from this pure
target map.

The selector target and predicate are combined in a pure plan: valid selectors
retain their handler address and expose a conditional flag-1 write, while an
out-of-range selector produces a zero target and no write. This forms the
integration boundary for the mapped `0x504d84` update without performing that
store in host tests.

The adjacent transition data is also decoded: `0x72690` contains the action-5
values `[8,12,12,12,12,13,13,13,19,8]`, and `0x72750` contains the action-10
values `[9,16,12,12,12,13,13,13,17,9]`. Both ten-entry tables are exposed
through bounded accessors and checked against the listing.

Those table values are now applied by pure action-state adapters: action `5`
and action `10` populate the transition value and action code for selectors
`0..9`, while out-of-range selectors are rejected. The actual mapped stores
at `0x504d94` and `0x504db8` remain outside host execution.

The selector handlers are also reduced to one predicate: selectors `0` and
`6` require mode bit `1`, selectors `1` and `3` require mode bit `2`, and the
remaining selectors require either bit. A true predicate writes `1` to
`0x504d84`; false predicates perform no write. The predicate is exhaustively
tested for all eight combinations of the two relevant mode bits.

The bank-split `0x000e3248` arm emits eight `e1fb0` expansions. Both banks
use tiles `1`, `3`, `5`, and `7` first; bank A sources are
`0x02fb3d90/0x02fb3e50/0x02fb4990/0x02fb4a50`, while bank B uses
`0x02fb3f10/0x02fb3fd0/0x02fb4b10/0x02fb4bd0`. Both then append tiles `21`,
`25`, `27`, and `29` from `0x02fb6cd0`, `0x02fb7e10`, `0x02bfed8c`, and
`0x02fb6fd0`, joining `0xe33f4`. The complete order is covered by the
dispatcher test.

The following mirrored group (`0x000e291c-0x000e294c`) expands tiles `23`,
`25`, and `27` from `0x02fb8350`, `0x02fb8410`, and `0x02fb84d0`. Unlike the
preceding arms, it joins the special `0xe33e4` exit; that exit address is kept
explicit in the descriptor and covered by the dispatcher test.

The next mirrored arm (`0x000e2950-0x000e29a0`) expands five tiles in order:
`21`, `23`, `25`, `27`, and `29`, from `0x02fb7f90`, `0x02fb8050`,
`0x02fb8110`, `0x02fb81d0`, and `0x02fb8290`. It joins the normal `0xe33f4`
exit and is covered by the dispatcher test.

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
### Geometry Coordinate Lookup and 0x35 Submitter: `0x0006ece0`

The frequently called helper at `0x6ece0` converts two IEEE-754 float
arguments with `cvtzri`, rejecting either coordinate when its truncated value
is outside `0..1023`. For valid inputs it forms
`(y >> 1) * 512 + (x >> 1)`, sends opcode `0x41`, sends that index, and uses
the FIFO response as an index into the table whose base pointer is loaded from
`0x51bb24`. Each record is 20 bytes:

```text
offset 0x00: output halfword written through g2
offset 0x02: output halfword written through g3
offset 0x04: packet word 1
offset 0x08: packet word 2
offset 0x0c: packet word 3
offset 0x10: packet word 4
```

The continuation packet is written as `53, word1, x_bits, word3, y_bits,
word4, word4, word2 ^ 0x80000000`; the final FIFO read is returned. Rejects
return the raw float constant `0x47c34f80` (`99999.0`) without touching the
FIFO. The callback-backed reconstruction and packet/edge vectors are in
`von/i960/recovered_geometry_coordinate.c` and
`von/tools/test_recovered_geometry_coordinate.py`.

### Fixed-Record Occupancy Scan: `0x000bf0c0`

The helper at `0xbf0c0` scans a caller-provided array of 32-byte records from
the supplied count downward. Its `not 31` instruction produces `-32`, so the
indexed byte load at `base + (count << 5) - 32` tests the first byte of the
current zero-based record. It returns the highest occupied slot, or `-1` when
the count is zero or all tested header bytes are zero. The many callers use
this result to select an existing command slot before writing its status and
payload fields. The reconstruction and randomized boundary vectors are in
`von/i960/recovered_record_scan.c` and
`von/tools/test_recovered_record_scan.py`.

### Shared ABI Tail-Return Trampoline: `0x000027d8`

The frequently reached entry at `0x27d8` is a four-instruction i960 control
flow helper, not a data transformation. It copies the return address held in
`g14` by the preceding `bal` into `g0`, clears `g14`, and executes `bx (g0)`;
the following `ret` is the target reached after that indirect branch. The ROM
uses this trampoline throughout the text/texture setup loops, which accounts
for its 13 observed attract-mode call edges. It is tracked as ABI scaffolding
in the reconstruction ledger rather than translated into misleading C logic.

### Geometry Projection Packet Core: `0x0006f6f0`

The sibling geometry helper at `0x6f6f0` repeats the 0..1023 float-coordinate
validation and 512x512 half-coordinate index used by `0x6ece0`. It emits
opcode `0x41`, then uses the returned table record to derive the integer
quotients `x/40` and `y/40`. Its continuation opcode is `53`, followed by the
record fields and original coordinates in this exact order:

```text
53, record+0x04, x_bits, record+0x0c,
y_bits, record+0x10, record+0x10, record+0x08 ^ 0x80000000
```

After the packet read, the routine indexes a mode-dependent callback table at
`0x6eb70` using a byte map rooted at `0x51bb20`; the callback may update the
stored result. The final output is either the `y/40` quotient shifted left by
8 or a state-dependent bit mask sourced from `0x562c80/0x562c84`. The exact
packet core is reconstructed and vector-tested in
`von/i960/recovered_geometry_projection.c` and
`von/tools/test_recovered_geometry_projection.py`; the callback/output tail
remains intentionally separate until its runtime state is captured.

The callback table is an array of six-word records at `0x6eb70`, selected by
`mode * 24` where `mode` is the global at `0x5770f0`. Its first-word targets
are:

```text
mode  0  1  2       3       4       5  6       7  8  9       10 11 12 13 14 15
entry eb40 eb40 e8f0  e6f0  e7f0  eb40 ea40  eb40 eb40 ea40  eb40 eb40 eb40 eb40 eb40 eb40
```

The companion setup leaf at `0x6f900` is now statically audited by
`von/tools/test_geometry_projection_mode_setup.py`. It scales the selected
mode by three words, reads the six-word record at `0x6eb60`, and publishes
the record's first/second/fourth/sixth fields through `0x51bb24`,
`0x51bb28`, `0x51bb20`, and the geometry FIFO. The oracle checks this store
contract and all 16 first-word targets above, including the five nontrivial
validator targets (`0x6e6f0`, `0x6e7f0`, `0x6e8f0`, `0x6e940`, `0x6ea40`).
The selected byte-map values and their runtime mode changes remain open.

The mask globals are likewise runtime-built, not fixed ROM constants. The
high-fanout initializer at `0x9baa0` selects a mode-specific descriptor from
`0x9b8d0`, derives lookup coordinates from object offsets `+0x10` and `+0x08`
using the shared `+31` bias, then stores computed words into `0x562c80` and
`0x562c84`. Its invalid/disabled path clears both globals at `0x9bd6c` and
`0x9bd74`. This storage boundary is checked by
`von/tools/test_geometry_projection_mask_storage.py`; the remaining work is
to assign higher-level geometric names to the recovered table codes.
The raw image resolves the descriptor stride as 20 bytes. The primary words
are populated for modes `0`, `1`, `2`, `4`, `5`, `6`, and `7`; mode 3 retains
only a trailing pair (`0x00000008`, `0x0009b810`), while modes 8 onward in
this block are zero. The complete first-eight-record image values are pinned
by `von/tools/test_geometry_projection_descriptor_table.py`. These are ROM
layout facts, not names for the pointed-to tables or callbacks.
The pointed-to blocks are 16-byte records shaped as three raw
IEEE-looking words followed by an integer tag. Their observed counts are
8/7/9/8/7/8/6 for modes `0/1/2/4/5/6/7`; the tag sequences are respectively
`[0,4,2,3,4,5,6,7]`, `[8,8,8,8,8,8,9]`, `0x13..0x1b`,
`[0xa,0xb,0xa,0xb,0xc,0xd,0xe,0xf]`, `0xc..0x12`, `0x1c..0x23`, and
`0x24..0x29`. The oracle checks these blocks directly against the raw ROM;
the coordinate units and tag semantics remain to be established.
The descriptor second-word pointers resolve to separate mask-entry tables in
the geometry ROM at `0x2f00000`. Their raw entries are now checked for modes
`0`, `1`, `2`, `4`, `5`, `6`, and `7` by the same oracle; this is the data
actually loaded into `g6`/`g5` before the stores to `0x562c80`/`0x562c84`.
Mode 2's pointer (`0x00143884`) addresses the low window of the same
geometry ROM, rather than main-CPU RAM. The table values are preserved as
raw words because their low-bit mask role is clear while their packed
geometry meaning is not. The coordinate normalization at
`0x9bb04`/`0x9bb0c` and bound `0x23f` establish a 576-word (`0x240`-entry,
`0x900`-byte) grid for each checked table; the oracle checks both the first
entries and the final four words, including mode 2 through its low ROM
window. The tables are not all contiguously packed: the mode-5 and mode-6
bases have an additional gap, so the descriptor pointers remain
authoritative. Their consumer at `0x9bc48` makes the packed representation
explicit: each loaded word supplies sixteen consecutive 2-bit fields, using
`(mask >> (2 * slot)) & 3`; the selected field is then shifted left by 14
bits. The complete per-slot test is now known: with the signed 16-bit sample
`s` loaded from the geometry record, the routine computes
`(0x4800 + (field << 14) - s) & 0xffff` and accepts it when the result is at
most `0x8fff`. This field and threshold behavior is covered by
`recovered_geometry_projection_mask_field()`,
`recovered_geometry_projection_mask_threshold()`, and their tests. The
numeric codes are therefore established as four quantized offsets, while
their higher-level geometric names remain unresolved.

The coordinate units are now more constrained. The `addrl` instructions at
`0x9baf0` and `0x9bb00` operate on register pairs; `r12:r13` contains
`0x407e000000000000`, exactly the double `480.0`. Thus each source float is
promoted through the i960 long-real path, offset by `480.0`, truncated by
`cvtzri`, and divided by `31+r9`. The resulting index is
`first_quotient*3 + second_quotient`, with the caller's `r9` retained as an
explicit parameter because only the common observed value makes the divisor
`40`. `recovered_geometry_projection_grid_index()` models this arithmetic;
the fields are identified as normalized lookup coordinates, but their
application-level axis names remain open.

The callback gate at `0x6f820` is now isolated as well: byte-map entries with
bit 5 clear, or the sentinel `0xff`, bypass the callback; all other entries
select quadrant `((map_byte - 0x20) >> 6)`. The selector is exhaustively
checked in `von/tools/test_recovered_geometry_projection.py`, while the
callback target and final mask still depend on runtime mode/state.

`0x6eb40` is a shared indirect-return trampoline. The nontrivial validators
at `0x6e6f0`, `0x6e7f0`, `0x6e8f0`, `0x6e940`, and `0x6ea40` dispatch on the
quadrant value `((map_byte - 0x20) >> 6)` and compare the two float arguments,
toggling the sign bit of the first argument in the negative quadrants. A
failed comparison stores the `99999.0` sentinel (`0x47c34f80`) through the
callback result pointer. This narrows the remaining work to recovering the
runtime byte-map/mode combinations and the final output-mask interpretation.

The float-looking constants loaded into `g5` on these paths are dead: the
following arithmetic consumes only `g4` and `fp0`. The effective comparisons
are therefore `x >= y` in quadrants 0 and 3, and `-x <= y` in quadrants 1 and
2. The sign transform, quadrant routing, and sentinel behavior are captured
by `recovered_geometry_projection_validate()`; runtime selection and the final
output-mask branch remain state dependent.

The immediate consumer of the `0x35` result is now connected as well. At
`0x6f87c`, the i960 compares the returned scalar against zero: nonnegative
results publish the previously computed `x/40` quotient shifted left by eight,
while negative results—including the SHARC helper's `-0.1` word
`0xbdcccccd`—enter the `0x6f8a4` mask-selection tail. That tail chooses
`0x562c80` for object `0x503ad0`, `0x562c84` when `0x503a7c` is nonzero, or
zero otherwise, then applies the packed mask transform already recovered.
`recovered_geometry_projection_result_route()` and its test encode this
boundary. This establishes the sentinel's caller-side control meaning as a
negative-result mask request; the mask's higher-level geometric names remain
open.

The negative-result mask branch at `0x6f8b8` is also deterministic once its
selected halfword is known. It computes `slot = (lookup_response - 1) & ~1`,
selects `mask & (3 << slot)`, sign-extends the selected 16-bit value, shifts
it by `slot - 14`, and stores the low halfword. The special object uses
`0x562c80`; other objects use `0x562c84` when `0x503a7c` is nonzero, otherwise
they store zero. `recovered_geometry_projection_mask_source()` captures this
deterministic selector, while `recovered_geometry_projection_output_mask()`
captures the bitfield transform; device response values and table contents
remain runtime-dependent.

The recorded `von/build/disasm/vonj-geometry-select-50s.trace` now has a
small runtime oracle for this path in
`von/tools/test_geometry_projection_runtime_trace.py`. It contains 1,677
complete response triplets at the instrumented PCs `0x6f7ac`, `0x6f7b4`, and
`0x6f818`. In this capture the lookup and final values are always zero; the
middle value is 13 in 1,606 triplets, 0 in 68, and 6 in 3. This validates the
live triplet ordering and observed selector domain, but does not by itself
identify the geometry board's response encoding or prove that the distribution
is universal across scenes. The same check correlates the middle value with
the preceding table request index: representative pairs are
`0x0000be7c -> 0`, `0x0000c079 -> 13`, `0x000138af -> 6`, and
`0x00023d04 -> 13`. This is evidence that the middle word is a board-returned
classification associated with the coordinate lookup, not an arbitrary host
constant; the classification's geometric meaning is still open.

The opt-in `VON_PROGRESS_GEOMETRY_STATE_LOG` logger in
`von/tools/gameplay_progress.lua` has now captured that state dependency in an
elevated linked twin run. At frame 2070 both cabinets selected mode `7`, with
byte-map pointer `0x02fc0d50`, record pointer `0x02bef690`, auxiliary pointer
`0x02bf039c`, special mask `0x000000a0`, and general mask `0x000002a8`.
The first 32 map bytes were all `0x80`, which takes the callback-gate bypass;
the sampled selector records 0, 6, and 13 were identical across cabinets.
The general mask changed during the run, including `0x000003a4`,
`0x000001a4`, and `0x000000a0`. These are now concrete runtime anchors for
future varied-scene captures, while the callback's application-level names
remain provisional.

### Geometry Control Selector: `0x0006fec0`

The short helper at `0x6fec0` is a selector-gated geometry control pulse. It
returns immediately for every selector other than zero. For selector zero it
writes `0x303` to `0x00800030`, then sends this exact sequence to the geometry
control FIFO at `0x00804000`:

```text
0x00000080
0x00f80140  (also written to 0x00804008 and 0x0080400c)
0x00f80140
```

The first `0x80` is produced by setting bit 7 in a zero word. A nearby load of
`0x01f40204` is dead in this routine; it is not part of the observed write
sequence. This preserves the host-side command contract, while the meaning of
the geometry-board words remains hardware-specific.

### Geometry Result Builder: `0x0009e050`

The high-fanout helper at `0x9e050` is a shared geometry-result builder. Its
`g3` selector expands as `g3 * 12`, then three signed halfwords are loaded
from `0x562436 + selector*12` at offsets `0`, `2`, and `4`. It emits a fixed
`0x38` request followed by those values, records three returned FIFO words in
a local result block, and copies them into paired caller records at offsets
`0`, `4`, and `8` / `0x10`, `0x14`, and `0x18`.

The object's flag byte at `object + 0xa0` selects the post-processing branch.
When set, the helper uses i960 `subr` to compute the object's three reference
values at offsets `0x74 + 0x14/0x18/0x1c` minus the returned/local values, then
sends that delta tuple through a second geometry request; its returned values
update the paired records. When clear, it selects a halfword from the static `0x562cde`
table using the output record's byte selector, combines object halfwords at
`+0x184` and `+0x34`, and writes those derived fields. Both paths then clear
common status fields, select a word from `0x562cb0`, issue the fixed `31`
request with object references, and store the final FIFO response at output
offset `0x28`.

This isolates the host-side record layout and branch structure; the later
object-generation consumer at `0x38c6c` loads `+0x20/+0x24/+0x28` as a
transformed `(x,y,z)` triplet and passes all three to `0xbc3b0`. Thus the
common `+0x28` field is specifically transformed Z in this object layout,
not an independent scalar threshold.
One response detail is now resolved in the flag-set branch: after the
four-word `31` delta request, the first two returned words are stored with
`STOS` at paired-record byte offsets `+0x06` and `+0x08`. Only their low 16 bits
are retained; this placement is implemented by
`recovered_geometry_result_delta_response_copy()` and covered by
`von/tools/test_recovered_geometry_result_delta.py`. The later common `31`
request still has a separate full-word response at output offset `+0x28`.

The existing generic response logger is capped at 256 reads and is consumed by
earlier bootstrap traffic. Patch `0014-von-geometry-response-tracing.patch`
adds independently capped 8192-entry `vonj_geometry_response` streams for host
reads in the `0x6f7ac-0x6f81c` and `0x9de9c-0x9ebff` ranges. This keeps the
high-rate projection traffic from starving the result-builder samples.

The high-fanout entry at `0x9de50` is the first result-builder variant used
by the object constructors. It is behaviorally the same builder family as
`0x9e050`/`0x9e250`: selector `g3` indexes `0x562436` in 12-byte steps,
the initial request is command `0x38` plus three signed halfwords, responses
land in local offsets `0x40/0x44/0x48` and are copied to paired records at
`0/4/8` and `0x10/0x14/0x18`, and the common final request is decimal command
`31` (SHARC opcode `0x1f`) with seven words and a response at offset `0x28`.
Object flag `+0xa0` selects the reference-minus-response delta request versus
the `0x562cde` fallback branch. The actual opcode-`0x1f` handler is at
`0x203ea`, consumes exactly six FIFO operands as three endpoint pairs, and
returns one refined Euclidean length at `0x20409`; this matches the six
post-command words emitted by the i960 tail and the one host read at
`0x9e240`. In packet-index notation (including the command at index zero),
the handler computes differences `(1-4, 2-5, 3-6)`: the three reference
words at `+0x14/+0x18/+0x1c` are paired with the three response-scratch words
at `+0x40/+0x44/+0x48`. The earlier association with `0x20762` was a dispatch-table
numbering error: `0x20762` is the separate opcode-`0xca` matrix/projection
handler, whose eight-input direct-tail behavior does not belong to this
builder. The entry-specific contract is captured in
`recovered_geometry_result_builder_9de50.c`.

The sibling entry at `0x9e250` is not byte-for-byte interchangeable with
`0x9de50`. Its flag-set arm sign-extends the already stored paired-record
halfword at `+0x06`, compares it against the primary `0x562cb0` table value,
and only loads the alternate table value when the primary value is greater.
Its flag-clear arm writes the immediate `0xffffe000` to output offset `+0x0c`
and the paired-record halfword at `+0x06`, instead of indexing `0x562cde`.
The common command-31 tail remains the same, with its final host read at
`0x9e438`. This distinct branch contract is represented by
`recovered_geometry_result_builder_9e250.c` and
`test_recovered_geometry_result_builder_9e250.py`.

The next sibling at `0x9e450` is a larger state/result builder. It shares the
four-word `0x38` request and the seven-word command-31 distance request, but
its flag-set arm loads the linked record pointer at `object+0x74` and emits a
four-word dynamic command-31 packet. If `L[i]` are linked-record fields
`+0x14/+0x18/+0x1c` and `R[i]` are the three projected responses, the packet
is `[(L0-R0)+31, L0-R0, L1-R1, L2-R2]`, with i960 wraparound. Its clear arm
uses `object+0x184` directly. The
intermediate response is stored at output `+0x0e` and paired-record `+0x08`.
After the distance response at `+0x28`, it emits command `29` with the paired
`+0x08` halfword and a selector-table value, stores the sign-bit-toggled
response at output `+0x18` (`NOTBIT 31`), then emits command `30` with the masked paired
halfword (zero-extended low 16 bits) and a second raw selector-table value,
storing its response at `+0x20`.
It also stores selector-table values at output `+0x14` and `+0x24`. This
packet and placement contract is represented by
`recovered_geometry_result_builder_9e450.c` and
`test_recovered_geometry_result_builder_9e450.py`; the host command words are
kept as observed and are not yet assigned higher-level geometry names. The
follow-up packet/response model is executable: command 29 receives the
sign-extended `+0x08` halfword, command 30 receives its masked low halfword,
command-29 response storage toggles only bit 31, and command-30 response
storage is raw.
All four follow-up table reads use the same scaled state-byte index:
`0x562cb0 + state*3*16`, with `+0x10` and `+0x14` selecting the two output
table fields. The address helper is covered by the same regression test.
The record-array operand is now bounded at its callers: the inspected
`0x9e450` call sites seed local `r6` with `lda 0x58(g2),r6`, then add that base
to the slot-derived offset in `addo r6,g2,g2` before dispatch. Thus `r6` is the
base of the selected record array, not an arbitrary scalar. The callee uses
that preserved record-base address in its first `SUBR`; the exact meaning of
that base selects the output slot, while the flag-set packet’s three
subtractions use the linked record fields loaded through `object+0x74`, not
the base register itself. The packet helper and boundary vectors are checked
by the result-builder test.

The sibling at `0x9e880` preserves that follow-up packet sequence but changes
the intermediate clear arm: it writes `object+0x184 + object+0x34` to output
`+0x0e` and paired-record `+0x08`, whereas the flag-set arm emits
`[10, linked.+0x1c-response2, linked.+0x14-response0]` using the linked
record at `object+0x74`. Its command-29/30 response placements and table
outputs match `0x9e450`, and its `NOTBIT 31` follow-up toggles only bit 31.
This variant is represented by
`recovered_geometry_result_builder_9e880.c` and checked by
`test_recovered_geometry_result_builder_9e880.py`.

The following sibling at `0x9eab0` shares the same command-`0x38`, command-31,
and command-29/30 pipeline, but first initializes output `+0x0c` and paired
record `+0x06` to `0xffffe000`. Its flag-set arm may replace that default with
the three-word command-10 response `[10, linked.+0x1c-response2,
linked.+0x14-response0]`, while its clear arm reads `object+0x184` directly
(without the `+0x34` addition used by `0x9e880`). Its sign-bit-only command-29
response transform and final response/selector-table placements match the
other siblings. This fourth variant is
represented by `recovered_geometry_result_builder_9eab0.c` and checked by
`test_recovered_geometry_result_builder_9eab0.py`.
The same patch now logs a bounded `vonj_geometry_write` stream for nonzero
geometry-window writes; startup's large zero-fill is deliberately excluded so
future captures can preserve gameplay command words for request/response
pairing.

On 2026-08-31, the locally rebuilt binary with patch `0014` was run directly
for 150 emulated seconds with `gameplay_progress.lua` and the staged `vonj`
ROMs. The script reached frame 6960 and executed its movement schedule, but
the trace contained zero `vonj_geometry_response` reads and zero geometry
object/matrix/polygon events. This confirms that the local scripted path does
not reach the result-builder ranges yet; it is not evidence for FIFO response
values, so the helper's board-facing semantics remain unpromoted.
The follow-up 60-second run with the geometry object/matrix/polygon trace set
enabled reached the same conclusion: only startup geometry parsing and the
known command writes appeared, with no object callbacks, copro FIFO reads, or
communication errors. The missing transition is therefore upstream of the
instrumented result-builder boundary.
An additional 20-second two-cabinet run using `scripts/run-twin.sh` initially
failed because the sandbox denied the local socket operations; it was not a
protocol failure. An elevated 60-second two-cabinet run on 2026-09-01 with the
same rebuilt binary established both links, reached gameplay, and produced
8,192 projection-range response reads plus 236 result-builder-range reads per
cabinet. The result-builder samples include bursts at `0x9e09c`, `0x9e0a4`,
`0x9e0a8`, `0x9e0b0`, `0x9e0bc`, then the flag/final sites at `0x9e130`,
`0x9e140`, and `0x9e240`; recurring first words are zero while the other
words vary as IEEE-looking coordinates or signed integer deltas. This confirms
the host-side call sequence is live and gives us real response vectors, but it
does not yet identify the geometry board's response encoding.

A follow-up interpreter-mode probe used MAME's `-nodrc` option and logged the
first 64 SHARC program counters. Both cabinets began at `0x020005` and entered
the uploaded bootstrap at `0x020080`, confirming that the listing's `0x020de1`
helper address is in the live program address space. Neither cabinet reached
`0x02034a` (opcode `0x17`) or `0x020de1` during the 20-second probe, despite
still producing the host-side geometry response stream. The negative result is
therefore a coverage limitation of this gameplay window, not an address-map
failure; the next capture should target a scene or command path that emits the
streamed table service.
Changing the machine selector by one step (`VON_PROGRESS_SELECT_STEPS=1`) and
repeating the passive 60-second twin capture produced the same result: the
bootstrap prefix was identical, no `0x02034a`/`0x020de1` execution was observed,
and each cabinet still produced 8,192 projection-range responses. Selector
choice is therefore not sufficient to reach this service; a later scene or
command transition is required.

The longer 120-second capture initially appeared to contradict this because it
contained 7,414 exact FIFO writes of the word `0x17`. Correlating their i960
write PCs with the disassembly resolves the apparent contradiction: in the
object packet prefix, the sequence is `0x16, value`, `0x15, value`, `0x14,
value`, and the observed `0x17` is the value paired with the `0x15` tag (the
static halfword at `0x56243e`). It is not a geometry command tag. All three
emitters share this ten-word prefix; the `0x3403c` and `0x346f0` paths then
append a second tagged `0x15`/`0x14` pair and `0x3a` copy-target word, while
the `0x34de8` path takes a different `0x20` continuation. These forms are
captured by
`von/i960/recovered_geometry_object_packet.c` and its vectors. The live
`-nodrc` SHARC sampler reached `0x0203b6` repeatedly (the opcode-`0x1b`
handler) but never entered `0x02034a` (opcode `0x17`). This separates the i960
geometry-packet layer from the SHARC service layer and explains why the host
word count did not predict helper calls. The `0x34de8` form consumes a board
response after its standalone `0x20` request before continuing with `0x06`;
that response is intentionally outside the packet-builder model.

The first emitter's next boundary is now visible in the same capture. After
the `0x3a` target it emits `0x06`, conditionally emits `0x05`, and then emits
`0x1f` followed by six payload words. This matches the SHARC `0x1f` service
shape (three endpoint pairs), but the host-side payload construction and the
response consumed before the following `0x0a` request remain unresolved. The
`0x346f0` emitter instead enters an `0x10`/`0x12` state setup sequence after
its `0x3a` target. These are separate branch contracts, not one padded packet.
The observed `0x3403c` sequence narrows that boundary further: the six
`0x1f` payloads are followed by a board response, and the next outgoing
request is `0x0a` with that response as its first input and the second live
geometry-window value as its other input. The profile initializer at
`0xc9020` loads a direction triple from `0x142fd4 + profile*12` into
`0x577100/104/108`. Pipeline-aware write tracing resolves the six payloads as
`[0, x, 0, 0, 0, z]`: opcode `0x1f` therefore returns the XZ projection length,
while `y` feeds the second operand of opcode `0x0a`. The two request shapes are
captured by `recovered_geometry_object_profile_length_request()` and
`recovered_geometry_object_scalar_request()`; the latter now synthesizes the
response-dependent packet word, while board-side production of the `0x1f`
response remains outside the host packet model.

The new 2026-09-01 instrumented twin capture (`twin-vonj-20260901T022433Z`)
made that dependency observable. Around the `0x3403c` branch, the response
trace records `pc=0x343f4 -> 0`, then `pc=0x343fc -> 0x3f000003`; the outgoing
`0x0a` request carries `0x3f000003` as its first operand. The next response
trace records `pc=0x34494 -> 0`, then `pc=0x3449c -> 0xffffeaaa`; the following
`0x15` packet carries `0xffffeaaa`. This establishes the response-forwarding
chain; the i960 pipeline's PC attribution is now explained by the delayed
first zero write in the six-word packet. The same capture records the
`0x34de8` response burst at
`0x34e98..0x34ebc`; the three state-tail values are stored at object offsets
`+0x20`, `+0x24`, and `+0x28` after the standalone `0x20` readback. The
preceding host `0x2f` packet invokes SHARC opcode `0x2f`, which transforms a
packed vector through the persistent matrix and writes state offsets
`0x09..0x0b`; opcode `0x20` then returns those offsets in order. The exact
host placement is captured by `recovered_geometry_object_response_copy()`.
The forwarded values provide a useful semantic cross-check: `0x3f000003` is
approximately `0.5` as an IEEE-754 value, matching the established vector-
length behavior of SHARC `0x1f`; `0xffffeaaa` is signed `-5462`, approximately
`-π/6` when interpreted with the established `π/32767` fixed-point scale used
by the angle-family services. This supports a length-to-angle pipeline. The
late triplets have the same state-tail component order, although their host
record placement remains path-specific (`+0x20/+0x18/+0x28` in one path and
`+0x158..+0x160` or `+0x164..+0x16c` in later paths).
The later `0x346f0` branch repeats a standalone `0x20` after its second
`0x2f` transform and places the returned state-tail components at `+0x20`,
`+0x18`, and `+0x28`; this distinct layout is captured by
`recovered_geometry_object_state_response_copy()`.
Its subsequent `0x34b00` continuation emits `0x05`, a second `0x2f` plus
three base words and tagged `0x16/0x15/0x14` fields, then a standalone `0x20`.
The three returned state-tail components are stored at the separate late-record offsets
`+0x158/+0x15c/+0x160`, immediately followed by `0x06`; this placement is
captured by `recovered_geometry_object_late_response_copy()`.
The routine immediately repeats the tagged-field-plus-`0x20` pattern and
stores a second response triplet at `+0x164/+0x168/+0x16c`, followed by a
second `0x06`; that follow-up placement is captured by
`recovered_geometry_object_late_followup_response_copy()`.
The same gameplay capture shows this cadence with live values: the first
group is `05, 2f 4928 4557 4a49, 16 fffffafc, 15 fffff42b, 14 ffffee8e,
20, 06`; the follow-up group is `2f c3bc 4a15 4520, 16 18ca, 15 fffff321,
14 0665, 20, 06` in the PC-attributed log.
The rebuilt response tracer now covers those read sites. In both cabinets it
reports the same three nonzero response words for the first block,
`0x4124ffff, 0x40aa9fff, 0xc23db800`, and the same three for the follow-up,
`0xc0777ffe, 0x41427ffe, 0xc25b8000`. Each block also contains two
pipeline-attributed zero reads interleaved with those values; the static
three-load sequences and the cross-cabinet repetition identify the nonzero
triplets, while the extra zero-read attribution is an emulator pipeline
artifact. The preceding `0x2f` transform writes the persistent state tail and
the following `0x20` returns it, so these are transformed state-tail vectors,
not independent board response fields.
The downstream consumer at `0xdf0cc` supplies the missing layout rule: its
object field at `+0x02` selects the earlier local vector at
`+0x14/+0x18/+0x1c` for selector `0`, the first late response vector for
selector `1`, and the follow-up late vector for selector `2`; all other
selector values become a zero vector. The selected three words are then
copied into a common frame and used by the same threshold and weighted-
residual checks. Before that work, `0xdf120` applies an inclusive signed
fixed-point Y-window gate: selected Y must satisfy
`window_base <= selected_y <= window_base + window_extent`, where the base is
object `+0x0c` and the extent is object `+0x54` in the related record. This
exact gate is modeled by `recovered_geometry_projection_y_window_passes()` and
tested by `test_recovered_geometry_projection_interval_gate_df120.py`. This
selector contract is captured by
`recovered_geometry_object_select_response_vector()`.

The first post-gate transform is also now unambiguous at the host/SHARC
boundary. i960 `0xdf218` emits decimal command `26` with the selected vector's
X component, literal zero, and Z component. The dispatch table maps that host
word to SHARC opcode `0x1a` at `0x2039b`, whose three outputs are the affine
transform `tail + matrix * (x,0,z)`. This is distinct from SHARC opcode
`0x26` at `0x20532`, the five-word parameter upload service. The host packet
specialization is captured by
`recovered_geometry_object_xz_state_output_request()` and the object-packet
test.

The residual tail at `0xdf2f4` is now bounded as a strict comparison of two
more SHARC opcode-`0x1f` lengths. The first six-word packet represents the
axis-separated endpoints `(g6,0,0)` and `(0,g5,0)`; the second represents
`(g3,0,0)` and `(0,g12,0)`. The host reads both scalar results and rejects on
`first >= second` at `0xdf380`, leaving the strict predicate `first < second`.
The acceptance rule, including NaN rejection, is modeled by
`recovered_geometry_dual_distance_accepts()` and tested by
`test_recovered_geometry_dual_distance_predicate_df2f4.py`. The preceding
decimal commands 10, 28, and 27 dispatch to SHARC opcodes 0x0a, 0x1c, and
0x1b; after the two angle results, the register flow is `g6 = (+0x58) *
opcode_0x1c_result` and `g5 = (+0x58) * (+0x5c) * opcode_0x1b_result`. The
second packet uses selected Z (`g3`) and affine-transformed Z (`g12`). This
packet specialization is modeled by
`recovered_geometry_residual_distance_requests()` and tested by
`test_recovered_geometry_residual_operand_flow_df2f4.py`; the semantic names
of the related record's scale fields remain provisional. Their provenance is
now narrowed: object initialization at `0x278b4` copies descriptor words
`0x67c/0x680/0x684/0x688` into related-record offsets `+0x54/+0x58/+0x5c/+0x60`,
so `0x67c -> +0x54` is the same inclusive Y-window extent consumed by the
earlier gate, while `0x680 -> +0x58` and `0x684 -> +0x5c` are per-geometry
descriptor multiplicands rather than newly computed residual values. The
`+0x60` copy is adjacent descriptor state whose residual-tail role is not yet
established.
An exact-offset search of the current main-CPU listing finds no direct load of
related-record `+0x60`; it is therefore excluded from the reconstructed
residual predicate pending a new consumer trace.
The same multiply motif recurs in the sibling handlers beginning at `0xdf6a0`,
`0xdf948`, `0xdfbf0`, and the later `0xe00cc` family: `+0x58` scales each
primary angle-derived component, while `+0x5c` participates only in the
companion `(+0x58)*(+0x5c)` product. This supports a provisional
global-scale/secondary-axis-ratio interpretation, but the field labels remain
inference rather than recovered names.

The `0x346f0` emitter's continuation is also bounded: after its `0x3a` target,
it emits the no-payload `0x10` identity reset, then `0x12` with three state-tail
words, followed by `0x2a` with one scale word. The live fragment
`10, 12, 0, 80000000, c2700000, 2a, 3f800000` matches the SHARC handler
widths exactly and is captured by `recovered_geometry_object_state_setup()`.
The following live words are `0x15, derived-value, 0x05`, followed by the
three base words of a new `0x2f` packet (for example
`15, 0, 05, 2f, 2ff9, 4996, b20c`). This bridge is captured by
`recovered_geometry_object_state_bridge()`; the tagged fields after that new
`0x2f` header remain branch data.
The next tagged-field continuation emits `0x16`, then `0x1a` with three
inputs; in the live stream those inputs begin `0x2f, 0xaff9, 0xc997`, so the
first one is payload data rather than another header. This four-word request
is captured by `recovered_geometry_object_affine_request()` and matches the
three-input SHARC `0x1a` service.

A focused `-nodrc` capture with SHARC FIFO tracing removed that ambiguity. At
the live dispatcher read site `0x02012b`, neither cabinet consumed any
`0x17`, `0x18`, or `0x1a` command words. The observed nonzero command counts
included `0x1b`/`0x1c`/`0x23` (28 each), `0x2a` (55), `0x2f` (1,034), `0x3a`
(1,009), and `0x44` (1); the SHARC execution trace correspondingly entered
the neighboring `0x0203b6` and `0x0203f0` service paths. Thus opcode `0x17`
and helper `0x20de1` are not merely determinant-gated in this runtime: their
command is absent from the actual SHARC input stream. The i960 words labeled
`0x17` belong to a different geometry packet layer.

### CRC-CCITT Table Checksum: `0x00003120`

The four-edge target at `0x3120` is a seeded table checksum over `g2` input
bytes. `g0` is the data pointer, `g1` is sign-extended from a 16-bit stride,
and the accumulator starts at `0xDEBDEB00`. Each byte selects the high-byte
index of the current accumulator from the 256-entry `0x1021` table at
`0x2f20`, then updates the state as
`((state + byte) << 8) ^ (table[index] << 16)`. The return value combines the
final table entry with the middle 16 bits of the accumulator. The model and
independent reference vectors cover empty input, contiguous bytes, and a
non-unit stride.

### Alternate Glyph-String Writer: `0x0001d9e0`

The four-edge text helper at `0x1d9e0` is the mode-2/mode-3 sibling of the
existing `0x1da90` mode-0/mode-1 writer. It ignores the first byte while
classifying the string, scans the remainder for lowercase ASCII (`0x61–0x7a`),
and emits every byte through `0x1d310` with zero attributes. Lowercase present
selects glyph bank 2; otherwise bank 3. The selector is implemented and
boundary-tested independently of the mapped glyph data.

The adjacent status-string helper at `0x1d880` uses the same lowercase scan
but selects mode `0` when lowercase appears after the first byte, otherwise
mode `1`. Empty strings produce no glyph calls and retain mode `1`. This
classifier is implemented in `recovered_text_status_string.c`; its per-byte
`0x1d310` calls remain a separate side-effect boundary.

### Text Tile-Block Writer: `0x0001de80`

The four-edge target at `0x1de80` writes a rectangular tile block into plane
`0x01004000`. It takes the current column and row from `0x504ce0` and
`0x504ce4`, uses `g1` as width and `g2` as height, reads source halfwords from
`g0` row-contiguously, and stores each value with bit 15 set. Destination rows
advance by 64 tiles while source rows advance by the supplied width. The pure
model and tests cover nonzero offsets, row stride, forced attributes, and zero
width/height no-op cases.

The neighboring `0x1dc10` writer uses the same width-by-height and 64-tile
row geometry, but targets plane `0x01000000` and applies no `0xc000` bank
attribute: each source halfword is stored with only bit 15 forced. Its
per-cell address and attribute plan is implemented in
`recovered_text_plane0_block.c` and tested independently.

The adjacent `0x1dd10` helper accepts an explicit `(column,row,width,height)`
instead of reading the text position globals. It uses plane `0x01000000` and
the same 64-tile row stride, but forces the `0xc000` attribute on each source
halfword. Its per-cell plan is implemented in
`recovered_text_plane0_attributed_block.c`.

The `0x1df70` sibling keeps the explicit `(column,row,width,height)` ABI but
fills rather than copies: it targets plane `0x01000000`, uses the 64-tile row
stride, and stores preserved `g14` unchanged at every cell. The address/value
plan is implemented in `recovered_text_plane0_fill.c`.

The larger renderer beginning at `0x1e030` saves eight general-register words,
`g13/g14`, and `fp0–fp3` in a `0x50`-byte frame and restores them on every
exit. Its stable nonzero-`0x1d00034` entry route sends source `0x02fd81ec`
through `0x1dd10` at `(column=1,row=g13+31,width=19,height=2)`. That route
and the frame contract are represented by
`recovered_text_status_render_route.c`; the remaining status branches stay
unresolved.

The paired wrapper at `0x1f0d0` is now reduced to a complete route plan. Both
branches preserve the same `0x50`-byte register/FP frame and use column `10`,
row `g6+31`, width `g10+31`, and height `3`. Nonzero `g0` calls `0x1dd10`
with source `0x02fd8238`; zero `g0` calls `0x1df70` after loading a zero fill
value. The route is implemented in
`recovered_text_status_panel_route.c`.

The sibling wrapper at `0x1f1b0` preserves the same frame and geometry shape,
but uses column `2`, row `g6+31`, width `g27+31`, and height `3`. Its nonzero
route sends source `0x2fd832e` through `0x1dd10`; its zero route fills through
`0x1df70` with zero. This separate route is represented by
`recovered_text_status_panel2_route.c`.

The third sibling starts at `0x1f290` (`0x1f2a0` is inside its prologue) and
keeps the same route shape as `0x1f1b0`: column `2`, row `g6+31`, width
`g27+31`, height `3`, and a `0x50`-byte preservation frame. Nonzero `g0`
copies source `0x2fd848a` through `0x1dd10`; zero `g0` fills through `0x1df70`
with zero. The corrected function boundary and route are represented by
`recovered_text_status_panel3_route.c`.

The status helper at `0x1f3b0` sets column/origin to `g9+31` and row to
`g13+31`, then calls `0x1d210` with either the fixed `PRESS START BUTTON`
string at `0x1f370` or the blank string at `0x1f390`. It sets bit 2 of
`0x502484` for the nonzero path and clears that bit for the zero path. The
pure message, position, and flag plan is implemented in
`recovered_press_start_renderer.c`.

The neighboring `0x1f470` renderer sets the text column/origin to `g5+31`
and row to `g13+31`, then calls `0x1d9e0` with `INSERT COIN(S)` at `0x1f440`
for nonzero input or the blank string at `0x1f450` for zero input. It has no
additional mapped-state flag mutation; the pure plan is implemented in
`recovered_insert_coin_renderer.c`.

### Action Dispatcher: `0x00077e60`

The four-edge target at `0x77e60` is a complete 44-entry indirect dispatcher.
It loads the selector from `0x504d80`, rejects values above `43` to the common
fallback at `0x78084`, and indexes the table at `0x77e7c` otherwise. Slot 12
also points to `0x78084`; all other slots route through the one-instruction
wrappers at `0x77f2c–0x7807c`. The exact selector-to-target map is captured in
`recovered_action_dispatch.c` and exhaustively tested, while the semantics of
the individual action bodies remain separate.

### Transition Action Wrapper: `0x000783c8`

The four-edge wrapper at `0x783c8` preserves its return address, indexes the
table at `0x72690` with the global selector `0x504d68`, stores that table value
as `0x504d94`, and always stores action code `5` at `0x504db8`. Its exact
side-effect contract is implemented and tested with the table kept as an
explicit input; the table contents and neighboring action bodies remain
separate slices.

### Timing-Sample Extrema Wrapper: `0x00018ab0`

The four-edge wrapper at `0x18ab0` calls the hardware polling leaf `0x28de8`
and always records its returned poll count at `0x504c80`. When the profile word
at `0x5039f4` equals 4, it also updates the low-water mark at `0x1d00210`
when the sample is smaller and the high-water mark at `0x1d0020c` when it is
larger. Other profiles leave both extrema unchanged. The deterministic update
is implemented and tested separately from the hardware-dependent poll loop.

### Byte-Range Compare Helper: `0x000f5c58`

The four-edge target at `0xf5c58` is a bounded byte comparison. It receives
left pointer `g0`, right pointer `g1`, and byte count `g2`; equal bytes advance
both pointers until the count reaches zero and return zero. On the first
mismatch it returns the unsigned difference `left_byte - right_byte` without
consuming the rest of the range. This is implemented in
`recovered_byte_compare.c` and checked at the zero-length, prefix, equal,
reverse-order, and `0x00`/`0xff` boundaries.

### Text Startup Table Copy Wrapper: `0x00002330`

The four-edge helper at `0x2330` is a fixed wrapper around the recovered
forward-copy primitive at `0xf5d40`. It copies exactly `0x20c` bytes from
`0x01d00000` to `0x01d0020c`; the source and destination are derived directly
from the two `lda` instructions, so there is no selector or hidden length
argument. The wrapper is represented as a call-site contract and deliberately
reuses `recovered_memory_copy_forward()` rather than introducing a second
copy implementation.

### Two-Digit Result Formatter: `0x000e3a10`

The entry at `0xe3a10` is a thin wrapper around `0xe3830`, which renders a
nonnegative integer as two decimal glyphs using the existing glyph writer at
`0x1d310`. Values `0` through `99` produce their ordinary tens and ones;
any value above `99` selects the embedded `"99"` string. The observed
callers use this for compact result/status fields, and the exact digit
selection is captured by `recovered_text_two_digit()` with boundary vectors
for `0`, `9`, `42`, `99`, and saturation at `100`.

### Alternate Glyph Sink: `0x0001d570`

The result/status path's three callers use `0x1d570`, a glyph sink distinct
from the already recovered `0x1d310` writer. It masks the character to seven
bits, subtracts the printable-space origin, and clamps values outside the
96-entry range to glyph index zero. Indices `41` and `42` select explicit
two-row glyph data at `0x02fd7c90` and `0x02fd7c98`; all other indices use
the descriptor table at `0x02ea14d0`, whose entries provide a source pointer
and row width. The sink copies each row as 16-bit tile words with bit 15 set,
advances by the descriptor width, and applies the special trailing-column
adjustment encoded at `0x02ea11d4`. This closes the character normalization
and table-selection contract while leaving the alternate mapped-RAM writes
outside the current pure-C slice.

The selection boundary is now executable as
`recovered_text_status_glyph_plan`: it exposes the normalized index, the
special sources for indices `41`/`42`, the descriptor address for all other
indices, and the fixed two-row count. Descriptor contents and final tile
writes remain outside the plan. The current text-control regression additionally
validates all 384 ROM descriptors: each source pointer lies in the SHARC
text-data range, each width is one or two words, and both tile planes map to
the expected row stride. Descriptor contents and tile-address planning are
therefore resolved; final mapped tile-RAM writes remain outside the pure plan.

The allocator bookkeeping tail at `0x0006fd1c-0x0006fd4c` is also isolated.
It stores the allocated slot into the source record's association field,
increments the source count, advances the free-list head by `0x30`, and stores
the negated next-node word as the available-count value. The pure commit plan
in `recovered_geometry_allocator_commit.c` is tested across ordinary and
32-bit wraparound inputs; pointer-linked memory traversal remains outside the
model.

### Geometry Command Packet: `0x0006ff20-0x0006fff8`

The first command builder after the selector pulse is now represented as a
pure packet plan. It writes control word `0x202`, followed by 18 FIFO words:
the caller values, `g1-g3` and `g0-g3`, fixed words `0x01540601`,
`0x7f000000`, raw IEEE `1.0f`, then `g0+g3`, `g1+g3`, and the remaining caller
values. Arithmetic is unsigned 32-bit modulo behavior matching the i960
register operations. The plan is implemented in
`recovered_geometry_command_packet.c` and tested with wraparound vectors; the
geometry device's interpretation of the packet remains a separate boundary.

The first three responses from the shared `0x38` request are copied verbatim
into both paired result records: response words land at offsets `0`, `4`, and
`8` in the left record and `0x10`, `0x14`, and `0x18` in the right record. This
placement is implemented in `recovered_geometry_result_copy.c` and tested with
raw-word vectors. The later flag-dependent delta and table branches remain
separate.

The sibling at `0x00070000-0x000700d8` uses the same control/18-word framing
but changes the first payload block to `g4, g0, g1+g3, g2, g0, g1+g3, g2`, then
emits the fixed constants and the tail `g0-g3, g1-g3, g2, g0+g3, g1-g3, g2,
0`. Its exact modulo-32-bit packet plan is implemented and tested separately
in `recovered_geometry_command_packet_variant.c`.

### Geometry Clip Dispatch: `0x000701a0-0x000704f4`

The next command family begins with a signed four-way branch classifier. The
first path is selected only when `g0 < g3` and `g1 < g4`; the second when
`g0 < g3` and `g1 > g4`; the third when `g0 > g3` and `g1 < g4`; and the fourth
when both are greater. Equality on either comparison follows the shared
boundary path. This exact dispatch is implemented in
`recovered_geometry_clip_region.c` and exhaustively tested over a signed
7-by-7-by-7-by-7 domain. The four floating-point packet bodies remain
separate until their device-side effects are correlated.

All four branches reconverge through `0x00070950`, which writes the common
three-word FIFO tail `(g4, g5, 0)` and returns. That tail is represented by
`recovered_geometry_packet_tail.c` and tested independently; branch-specific
floating-point values remain outside this shared slice.

The two result-builder variants at `0x0009e050` and `0x0009e250` share two
deterministic request encoders. Their initial request is exactly four words
`(0x38, value0, value1, value2)`. Their common final request is seven words
`(31, ref14, ref18, ref1c, scratch40, scratch44, scratch48)`; the
selector-derived table value is stored into the paired output record at
`+0x14` before this request and is not a FIFO operand.
These host-side framings are implemented in
`recovered_geometry_result_packets.c` and tested with raw-word vectors; FIFO
responses and the table-derived values remain hardware/state dependent, but
the final scalar operation is now bounded: the six command-31 operands are
paired as the three reference coordinates against the three `0x38` response
coordinates, and SHARC opcode `0x1f` returns their Euclidean length.
The first three responses are now bounded by the SHARC contract: command
`0x38` decodes the three packed inputs and returns the row-vector projection
`(x,y,z)ᵀ·M` in X/Y/Z order. The result-builder's local `0x40/0x44/0x48`
scratch block and paired-record copies therefore preserve those three
projection words without reinterpretation. The later command-31 response is
the single Euclidean-length result produced by SHARC opcode `0x1f`; the host
consumes that one returned word at `0x9e240`.

The neighboring sinks at `0x0001ce00` and `0x0001cea0` are separate
two-row glyph emitters. Both mask the character to seven bits, subtract the
printable origin, clamp outside values to glyph index zero, and write rows at
`(row << 6) + column` and the following `0x40`-tile row. The first uses only
bit 15 on each tile; the second additionally ORs `0xc000`. Both advance the
column only when the incoming column is at most 30. This write plan is
implemented and exhaustively checked for all 256 byte values in
`recovered_text_alt_glyph.c`.

## Geometry response boundary at `0x76240`

The authoritative original-ROM capture in
`/tmp/von-original-28f-debug-local/mame.log` now covers the FIFO traffic
through `0x76240-0x76498`. The smallest stable fixture is the framing
sequence, not a response algorithm: command 29/30 requests use masked
`0xe000`, `0x2000`, and `0x8000) operands, with the corresponding
constant words `0x41700000) or `0x44bb8000). Each read returns an initial
`0x00000000) followed by a state-dependent word:
`c129b5af/4129b39a), `4129b5af/4129b39a), or
`3e1359e0/c4bb7fff), respectively.

The listing shows those returned words immediately feeding later masked
coordinates and a floating-point cross-product/sign-selection sequence
(`0x763a4-0x76498)); the captured FIFO data alone does not determine the
response function or the object-relative inputs. Therefore this boundary is
documented as captured evidence, not promoted to a pure model.

The next minimal capture must log `g0), the object words at
`g0+0x14`, `g0+0x1c), and `g0+0x184), plus each FIFO read/write
`(PC,direction,data)) for the same range. That correlates request operands
and returned words without broad instruction tracing and is required before
modeling the transform.

## Text-mode setup at `0x1f010`

The wrapper initializes the text timing globals before selecting a glyph
helper. It stores `g10+31` at `0x504cdc` and `0x504ce0`, and `g13+31` at
`0x504ce4`, with unsigned 32-bit arithmetic. Nonzero `g0` calls `0x1dc90`
with source `0x02fd0cd4` and dimensions `19` by `2`. Zero `g0` calls the
`0x1df00` fill helper with dimensions `19` by `2`; that path takes its tile
word from preserved `g14` and does not load a source pointer. The pure setup
plan and wraparound cases are covered by
`von/tools/test_recovered_text_mode_setup.py`.
