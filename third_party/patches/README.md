# MAME patch set

`patchsets.json` holds the ordered MAME instrumentation patches and named
profiles. `scripts/prepare-mame.sh` resets `third_party/mame-master` to the
pinned ref and applies a profile in `order`; `scripts/build.sh` builds the
reduced `von` target with the ambient `VON_MAME_PATCH_SET`.

## Reconciliation status

Several tracked patches had drifted from a clean stack and were regenerated
(against the then-current tree, preserving their intent) so they apply cleanly:
`0014`, `0016`, `0017`, `0018`, `0019`, `0020`, `0021`. The regenerated files
have refreshed context/line numbers.

Still corrupt / incomplete:

- **`0022-von-opcode-09-caller-tracing.patch` is unrecoverable**: its `+`/`-`
  diff markers were stripped, so the hunk is all context and neither the anchor
  nor the change can be recovered from the file (`i960.cpp` also has no
  `0x00041fbc` / `vonj_opcode` anchor to place it). Everything after it in
  `order` is untested until it is rebuilt.
- The `full` profile therefore does **not** currently apply end to end. It is
  kept as the intended union and should be rebuilt once `0022` (and any later
  drifted patches: `0023`-`0026`, `0028`, `0030`, `0036`, `0038`, …) are
  reconstructed.

## Profiles

- `smoke` is the working union for the smoke tests (core + geometry tracing +
  `0015` + `0017` + `sharc-precision` + `0033`). `VON_MAME_PATCH_SET=smoke
  scripts/build.sh` builds `bin/von` for it; `run_tests.py smoke` passes.
- Focused profiles (`core`, `geometry`, `texture`, `sharc-diagnostics`,
  `sharc-precision`, …) are unchanged. `all` still aliases `debug`.
