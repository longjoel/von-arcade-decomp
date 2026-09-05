# Open unknowns register

Unknowns are first-class artifacts. Record them instead of guessing them
away. Units reference U-IDs in their `unresolved` template field and
ledger `unresolved_behavior`.

## U-0001 — upload-cluster re-arm source

After a `0x29c08` clamp zeroes `0x51a264`, the `0x29d50` uploader is
parked (counter 0 < 3) until something re-seeds the state. No caller in
the recovered set has been shown to perform that re-seed.
Related: `maincpu.clamp-store-29c08`, `maincpu.upload-select-29d50`,
`maincpu.upload-state-init-29d2c`.

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

## U-0005 — missing development captures

The smoke gate fails on absent development captures (not regressions),
and the SHARC sweep producers plus the exact 50s geometry oracle
capture are still missing. Trace-derived fixtures are blocked on these.
Related: smoke suite, `VON_GEOMETRY_SELECT_SECONDS` traces.
