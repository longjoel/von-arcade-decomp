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
- [ ] Branch pushed (credential handoff pending).

## M2 — live cluster call (proposed)

Wire the shipped driver into the reconstructed runtime and observe it.

- [ ] Provision `0x181xxxx` windows on the development path (U-0004).
- [ ] Call the driver from `reconstructed_main` frame service.
- [ ] MAME-observed 768-store run matches the harness oracle words.
- [ ] Smoke gate unaffected (no hang, no bus fault).
- [ ] Commit, push, regenerate status.
