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

## U-0005 — missing development captures

The smoke gate fails on absent development captures (not regressions),
and the SHARC sweep producers plus the exact 50s geometry oracle
capture are still missing. Trace-derived fixtures are blocked on these.
Related: smoke suite, `VON_GEOMETRY_SELECT_SECONDS` traces.
