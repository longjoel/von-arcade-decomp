# Milestones

A milestone is done only when every criterion is observably true. Do not
redefine success around completed work; the criteria below are the contract.

## M1 — upload-cluster closeout (done 2026-09-05)

Scope: the `0x29c08`/`0x29d50` IO upload cluster.

- [x] All cluster ranges modeled as pure units with focused tests
      (clamp, prologue, seed, kernel, loop schedule, both strides).
- [x] End-to-end chain test: seed, park, reseed, bank select, both
      paths, 768-store budget.
- [x] Worklist entries `0x00029c08`/`0x00029d50` triaged to their units.
- [x] Executable driver plus host harness; driver and kernel ship in
      the i960 image source list.
- [x] All 7 units promoted to integrated with image, checkpoint, and
      test evidence; ledger validation 0 errors; strict lifecycle adds
      zero new errors (36 pre-existing remain).
- [x] Full check green (317 unit / 143 contract); status regenerated.
- [x] Reconstructed image builds clean with the new sources.
- [x] Branch pushed.

## M2 — live cluster call (done 2026-09-05)

Wire the shipped driver into the reconstructed runtime and observe it.

- [x] Provision `0x181xxxx` windows on the development path (U-0004):
      original-ROM oracle trace streams the window tail word, so the
      windows are writable on the MAME map; the vonjdev live run
      stored through them with no fault.
- [x] Call the driver from `reconstructed_main` frame service
      (startup-once call; results in `state[12..15]`).
- [x] MAME-observed 768-store run matches the harness oracle words:
      `stores=00000300 counter=00000005`, `check_upload_state.py`
      PASS (`dst==scale(src)` on both samples).
- [x] Smoke gate unaffected (MAME exit 0, no hang, no bus fault).
- [x] Committed (`dc56eb5`, `086bfcf`, `7942ed7`, `dbadad1`).
- [ ] Branch pushed (4 commits ahead of origin).
- [x] Status regenerated.
