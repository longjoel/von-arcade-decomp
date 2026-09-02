# C-Only i960 Attract Integration Workflow

The single active delivery objective is a 60-second C-only i960 `vonjdev`
attract run. MAME's existing SHARC, audio, and communication implementations
remain available. Byte matching is a research metric, not this milestone's
delivery gate.

## Authoritative commands

```sh
./scripts/status.sh                 # ledger, queue, tests, and evidence
./scripts/test.sh                   # fast MAME-independent unit + contract gate
python3 von/tools/run_tests.py trace
python3 von/tools/run_tests.py smoke --jobs 1
python3 von/tools/run_tests.py attract --jobs 1
```

`unit`, `contract`, and `trace` never require private ROMs. `smoke` validates
MAME and performs a short clean-image boot. `attract` runs the bounded full
milestone and rejects every i960 PC outside generated code.

## Work-unit lifecycle

One work unit moves through this sequence in one focused change:

1. State a hypothesis and the expected discriminating result.
2. Perform bounded capture or static analysis.
3. Add a recovered model and focused test.
4. Integrate the model into the replacement image.
5. Compare runtime state or trace behavior.
6. Update the ledger and evidence links in the same commit.

Use `planned`, `modeled`, `integrated`, `trace-validated`, `byte-validated`, or
`blocked` exactly. Do not open another modeled-only unit while a modeled unit
can be integrated. Order work by the earliest failing runtime checkpoint and
then by dependency order.

## Evidence

Canonical evidence is registered in `von/evidence/manifest.json`. It must name
a complete stimulus, pinned MAME revision and patch profile, execution engine,
artifact hash, passing verifier, outcome, and at least one ledger consumer.
Raw captures are compressed under the ignored
`von/build/evidence/sha256/`; incomplete and duplicate results are retained in
`von/build/evidence/quarantine/`. Aliases remain in the manifest. File presence
alone never satisfies a ledger evidence claim.

## SHARC freeze

Broad SHARC probing is closed. A new SHARC probe is permitted only when a named
attract-integration failure depends on one missing behavior, existing static
and captured evidence cannot discriminate it, the hypothesis predicts a
specific result, the run is bounded, and a verifier or recovered-model test
will consume the result. Precision fixes remain separate from Virtual-On
diagnostics through the patch profiles in `third_party/patches/patchsets.json`.

## Current integration blocker

The clean 60-second run currently reaches only generated i960 code but ends in
MAME with `I960: 0: Unhandled 00`. This is the earliest named integration
failure. The passing PC audit is evidence about code provenance, not permission
to mark the attract suite passing; the process exception remains a milestone
failure until its control-flow cause is integrated and trace-validated.
