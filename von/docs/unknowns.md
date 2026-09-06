# Open unknowns register

Unknowns are first-class artifacts. Record them instead of guessing them
away. Units reference U-IDs in their `unresolved` template field and
ledger `unresolved_behavior`.

## U-0001 — upload-cluster re-arm source

After a `0x29c08` clamp zeroes `0x51a264`, the `0x29d50` uploader is
parked (counter 0 < 3) until something re-seeds the state. The re-arm
mechanism is now identified: the `0x29c50` entry forces counter
`0x29c9c` (active, huge bank) with a zero-floor clamp
(`maincpu.rearm-store-29c50`), and its `0x29c58` entry takes the
caller's link instead (link-valued at `0x1a7c0`, `0xdc338`, `0xdc77c`).
What stays open is the trigger: no direct caller of the `0x29c50`
entry is visible in maincpu.
Related: `maincpu.clamp-store-29c08`, `maincpu.upload-select-29d50`,
`maincpu.upload-state-init-29d2c`, `maincpu.park-store-1b960`,
`maincpu.rearm-store-29c50`.

## U-0002 — pair-2 stride asymmetry rationale

Blend-path pair 2 advances `0x380` per outer pass while pairs 0/1
advance `0x200`; the direct path is uniform at `0x200`. The layout
reason (plane size, interleave, or padding) is unestablished.
Related: `maincpu.blend-stride-schedule-29e4c`.

## U-0003 — `mulo` fault semantics on overflow

The blend kernel models products as low-32-bit wraps. If the i960
`mulo` faults on overflow instead, bright-pixel/large-factor inputs
would trap rather than wrap. No capture exercises that corner.
Related: `maincpu.blend-kernel-29dec`.

## U-0004 — device-window provisioning for a live cluster call

The executable driver (`von/i960/recovered_upload_cluster.c`) ships in
the image build but is not called from `reconstructed_main`: the
`0x181xxxx` windows and completion expectations are unprovisioned on
the development path, the same reason the neighboring `0x29ca0` copy
stays modeled. A live call needs provisioned windows plus MAME-side
observation of the 768-store run.
Related: all seven upload-cluster units.

Update (M2 live run): the 50s original-ROM oracle trace
(`von/build/disasm/vonj-geometry-select-50s.state.log`, ignored build
output) shows `live_last` (`0x01814e7c`) changing across frames
(`00850084` -> `00ff00ec` -> `00ff00eb`) while `live_first`
(`0x01814000`) stays zero, so the `0x181xxxx` windows are writable on
the MAME map and the real game streams the tail word. The
`stores`/`counter` slots stay zero there as expected (original code
does not write our `state[]` words). A vonjdev live run wrote
`stores=0/counter=0` to the observed slots, root-caused to a base
bug: `WORKRAM + 0x20` on a `u32 *` lands on `0x00500080`, so
`state[12..15]` hit `0x005000b0..bc` instead of the observed
`0x00500050..5c`; fixed to byte-relative `+0x20` in
`reconstructed_main.c`. Rerun against a rebuilt image is pending.

Verdict (M2 complete): rebuilt image + 50s vonjdev trace gives
`upload-state: frame 30 stores=00000300 counter=00000005` and
`check_upload_state.py` reports `PASS: frame 30 stores=768 counter=5
dst==scale(src) on both samples`, matching the harness oracle exactly.
Caveat: on vonjdev the `0x0181xxxx` source windows read zero, so the
scale check holds trivially (`0==0`); a nonzero-source live
confirmation still wants the original-ROM stream comparison.

## U-0006 — model-table header and subgroup markers

Model part tables are located and record-decoded (`main_data`
0xbed828: 19 `[tpa, tha, oba]` records, all trace-verified). Marker
semantics are decoded from the 0xc9b50 consumer: the walker strides
records 12 bytes at a time and a record whose oba word is `<= 5`
(unsigned) takes the filing body, storing the parallel pose entry
into dispatch slot `3*oba` at `0x562430`; larger obas skip it. A
10-entry, 24-byte directory at maincpu 0xc9100 (`[range_end,
range_start, struct_a, aux0, struct_b, aux1]`, struct count bounds
the walk) indexes the table ranges. Loop-entry check closed: `r6`
advances 12/iter (`ca12c`) so the zero-word test fires on the
terminator. Tables are contiguous (`0xffffffff` separator, next
table at 0xbed948); table 2 repeats the marker rhythm
(11 triples, `[0,0,3]`, `[0,0,2]`, 1 triple, `[0,0,4]`, rest) and
shares part 008964ba byte-identical across tables. Still open: the
10-word header at 0xbed800 (its `0x91xxxx` values appear in no
capture), `range_start`'s role, and variant-B's X field at 0xbed700
(trace tpa sometimes equals the previous record's X).
Related: `decode_model_part_table.py`.

## U-0008 — fighter/stage selection chain into the model directory

Static chain recovered end to end: caller state → permutation table
at maincpu 0xc9278 (`[0,0,0,4,5,2,1,7,6,3,0,4,3,7,1,2,6,5,...]`,
three callers at 0xcb7dc/0xcbc24/0xcc084) → 0xc9b50 walker. Mapped
value 5/7 selects special tables 0xc91c0/0xc91d8 when mode global
0x503a08 is 0, else directory entry `g0` (10 entries, roster-sized).
Values never exceed 7, so bosses 8/9 (Jaguarandi, Z-Gradt) arrive by
another path. Mode writers at 0x18a34-0x18a98 store 1/3/loop values
from NVRAM byte 0x1d00028; exact mode semantics open, as is which
game-state field feeds the permutation index.
Related: roster block at 0x181f0, stage banners at 0x210xx.

Closed end to end by live select experiments (single-tap series with
1-frame holds plus held-stick runs, work-RAM snapshots at
0x503a00/256, geometry time-distribution):
- Coin at frame 900 opens machine select; the cursor starts on Temjin
  (table-1 preview serves from boot). One-frame stick taps do NOT move
  the cursor (Temjin preview continues uninterrupted, latch quirk
  below); held stick moves it with key-repeat and the 3D preview
  follows: cursor leaves Temjin ~frame 1230 and 00a1-family parts
  start submitting at t=20.5s.
- Start at frame 1500 confirms: P1 IS the previewed fighter. Its parts
  submit continuously from preview (20.5s) through the VS screen into
  the match (to tracer cap ~44.5s). The stage-1 enemy is fixed Temjin
  per the level order: Temjin-exclusive parts vanish while the cursor
  is away and return at t=35s when the enemy enters; the default run
  (no cursor motion) is a Temjin mirror.
- The walker disassembly (0xc9b50, see vonj-maincpu.lst) is fully
  decoded: `g4=[0x503a08]`; if mode==0 and g0==5 use special table
  0xc91c0, if mode==0 and g0==7 use 0xc91d8, else entry g0 of the
  24-byte directory at 0xc9100 (`g0*24`; entry0 heads [02bed8dc,
  02bed81c, ...] in the table-1 neighborhood). The record loop strides
  the table,
  files pose entries on oba<=5 markers, stops on the zero-word
  terminator, and streams everything to the geometry board at
  0x884000. Callers: 0xcb7dc takes the perm index in g1 (then zeroes
  g1/g2/g3); 0xcbc24/0xcc084 load it from a fighter-struct field
  (`ld 0x48(g5)[g6],g4`) with g1=r6/r7 and g3&1.
- Special table 0xc91d8 references 0x02a1c7e4 (the 00a1 family);
  0xc91c0 heads [02bee530, 02bee488, ...] in chips the table decoder
  does not load yet. Enemy-side Temjin body parts (0x9e52xx-0x9e56xx)
  come from variant-C program-image tables (e.g. 0x5694), not
  main_data: P1 serves main_data tables, the enemy serves variant-C.
- Stage 1 is fixed regardless of P1 pick: non-fighter arena/effect
  families are identical across default and picked runs (the only
  match-1 delta, four 008f31xx obas, appears in every capture: window
  timing, not content). VS-screen text ("ENCOUNTER!" at 0x21050) is
  rendered by 0x21ebc/0x220e0 double-indirectly via RAM pointer
  0x5770f0.
Still open: exact cursor start/repeat math, the semantics of the
confirm-time byte at 0x503a98 (0/4/5 across tap runs but NOT the table
selector: a run latched 0 yet served the picked fighter), the stage-1
banner name, and which caller serves the arena (caller 1 takes a
constant-style index, callers 2-3 struct fields: P1/enemy/arena
assignment unproven).

## U-0009 — roster and stage order

Program image holds a 10-name roster at 0x181f0 (TEMJIN, VIPER2,
BELGDOR, RAIDEN, DORKAS, FEIYEN, APHARMD, BAL-BAS-BOW, JAGUARANDI,
Z-GRADT) with a name-pointer table after it, 16-byte fighter slots
at 0x19380, and 10 stage banners at 0x210xx (AIRPORT, DEATH TRAP,
WATERFRONT, GREEN HILLS, RUINS, SPACE DOCK, MOON BASE, FLOODED CITY,
NIRVANA, SECRET BASE) followed by a glyph-ID table. Bosses sit at
roster positions 8-9. Stage↔fighter pairing unproven: no capture has
printed a banner, and the tracer cap (131072 object events, MAME
patch 0007) blinds every trace past ~50s.
Related: U-0008, `trace-geometry-select.sh`.

## U-0007 — trace slot families are not models

Proven by measurement: a 404-family slot-co-occurrence export put 19
parts from three ROM regions (`0x89xxxx`, `0x9exxxx`, `0xa6xxxx`)
with 19 distinct per-frame body transforms into one "family". Slot
co-occurrence groups screen-sharing strangers, never models. Model
identity comes from ROM part tables (U-0006); trace supplies
per-part transforms and textures only.
Related: `fingerprint_geometry_assemblies.py`, showcase pack.

## U-0005 — missing development captures

The smoke gate fails on absent development captures (not regressions),
and the SHARC sweep producers plus the exact 50s geometry oracle
capture are still missing. Trace-derived fixtures are blocked on these.
Related: smoke suite, `VON_GEOMETRY_SELECT_SECONDS` traces.
