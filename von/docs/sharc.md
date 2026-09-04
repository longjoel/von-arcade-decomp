# SHARC recovery boundary

## Current policy

The broad SHARC opcode-probing campaign is closed. Existing recovered models,
fixtures, and probes are a legacy evidence library to inventory and revalidate
as consumed. They do not advance the active i960 attract milestone merely by
existing or passing an isolated model test.

New SHARC work is allowed only when:

1. a named host integration failure depends on one missing SHARC behavior;
2. static analysis and existing captures cannot discriminate it;
3. the experiment predicts a specific result;
4. it is bounded by events, vectors, or time; and
5. a maintained model, verifier, or active integration unit will consume it.

## Strongest retained results

- Scalar, reciprocal, fixed-point, state-window, matrix, vector, projection,
  normalization, predicate, and table-access contracts.
- Finite-input models for helpers `0x20d68`, `0x20dbe`, and `0x20de1`.
- Opcode `0x35` quotient/residual rounding behavior.
- Ordinary opcode `0x0f` interpreter/DRC FIFO agreement.
- Geometry packet and response boundaries used by host-side reconstruction.
- A guarded 40-bit arithmetic seam and focused precision fixtures.

Run the maintained MAME-independent collection with:

```sh
./scripts/test-sharc-recovered.sh
```

Inventory local generated evidence with:

```sh
python3 von/tools/inventory_sharc_evidence.py \
  --json von/build/sharc-evidence-inventory.json \
  --markdown von/build/sharc-evidence-inventory.md
```

Generated probe logs are not canonical solely because they are present. The
zero-trust cleanup in [Evidence and assets plan](evidence-and-assets-plan.md)
classifies them by producer, consumer, completeness, and hash.

## MAME boundary

MAME remains a runtime oracle and source of generic Model 2 infrastructure.
The ADSP-2106x extended internal representation and `MODE1_RND32` behavior may
still merit an upstream CPU-core improvement, but Virtual-On-specific probe
results are not sufficient by themselves to justify a general precision
change. Keep reusable CPU tests separate from game instrumentation.

The detailed architectural and upstream contribution record remains in
[mame-sharc-precision-upstream.md](../i960/mame-sharc-precision-upstream.md).
