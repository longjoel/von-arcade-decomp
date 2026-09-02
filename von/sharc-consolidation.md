# SHARC Consolidation Checkpoint

This checkpoint closes the continuous broad opcode-probing pass. It preserves
the resulting evidence while separating established recovered contracts from
raw emulator observations and unfinished experiments.

## Current result

SHARC is frozen as a modeled evidence library for the active C-only i960
attract milestone. Current counts come from `./scripts/status.sh`; this document
does not duplicate them. No SHARC work unit is promoted merely because a probe
or recovered model exists.

The historical local evidence snapshot taken at consolidation contained 249 generated SHARC
artifacts (566,363,342 bytes), 69 recovered C models, 133 probe stimuli, 18
trace verifiers, and 68 focused recovered-model tests. Twenty-three small probe
logs started without a completion marker; the inventory labels these incomplete
rather than allowing their existence to imply a result.

The schema-v2 ledger separates non-overlapping physical ranges from nestable
semantic work units. `python3 von/tools/validate_reconstruction_ledger.py` must
report zero errors before a checkpoint.

The strongest reusable results are:

- scalar, reciprocal, fixed-point, state-window, matrix, vector, projection,
  normalization, predicate, and table-access service contracts;
- finite-input models for the shared `0x20d68`, `0x20dbe`, and `0x20de1`
  helpers;
- opcode `0x35`'s per-instruction quotient/residual rounding schedule;
- interpreter/DRC FIFO agreement for the ordinary opcode `0x0f` vectors;
- trace-backed geometry packet and caller boundaries used by the host recovery;
- a guarded 40-bit arithmetic seam and neutral precision fixtures for eventual
  MAME work.

These results are represented by the recovered C files in `von/i960`, their
focused tests in `von/tools`, the SHARC entries in
`von/reconstruction_ledger.json`, and the precision boundary document in
`von/i960/mame-sharc-precision-upstream.md`.

## Evidence tiers

1. **Recovered model:** a maintained C or Python contract with focused tests.
   This is the preferred input to host integration.
2. **Verified trace:** a raw capture with a checked-in verifier and stable
   expected words. This can refine a model but remains emulator evidence.
3. **Exploratory probe:** a Lua stimulus, raw trace, or root-level probe log
   without a closed verifier/model relationship. Keep it for provenance, but do
   not treat it as an established semantic contract.
4. **Incomplete output:** a probe that started without a completion marker or
   usable response. This records a diagnostic dead end, not a result.

Generated traces remain ignored repository artifacts. They are intentionally
not moved or deleted by consolidation. To index the current local corpus:

```sh
python3 von/tools/inventory_sharc_evidence.py \
  --json von/build/sharc-evidence-inventory.json \
  --markdown von/build/sharc-evidence-inventory.md
```

The inventory records every generated SHARC trace/log, groups it by service,
reports disk use and incomplete small probe outputs, and lists the maintained
models, probes, verifiers, tests, and MAME patches. It does not hash multi-GB raw
captures or promote ledger statuses.

## Stable checkpoint command

Run the maintained recovered models independently of MAME and private ROMs:

```sh
./scripts/test-sharc-recovered.sh
```

At this checkpoint all 71 selected model/contract tests pass. The 71 comprise
the 68 recovered-model tests plus the service-contract, precision-fixture, and
standalone 40-bit-reference tests.

The broader `scripts/test.sh` remains the integration gate when MAME and the
private ROM set are available.

## Stop rule and next boundary

Do not resume a broad opcode sweep. A new probe should be added only when all of
the following are true:

- an end-to-end host/geometry integration path is blocked by one named SHARC
  behavior;
- the existing listing, model, and captures cannot answer it;
- the stimulus has a predicted discriminating result;
- a verifier or recovered-model test will absorb the result; and
- the probe has a bounded run count and explicit completion condition.

The next project phase is to consume the recovered contracts in one integrated
geometry path and let concrete mismatches select any further SHARC work.
