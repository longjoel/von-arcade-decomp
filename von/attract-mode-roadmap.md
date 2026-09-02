# C-Only i960 Attract Milestone

## Acceptance boundary

The first playable reconstruction milestone is deliberately narrower than a
match. A newly linked i960 image must boot `vonjdev`, reach the input-free
attract presentation, exercise graphics/video/audio startup, and remain alive
for 60 emulated seconds. Original asset ROMs and MAME's existing 68000, SHARC,
and communication-board implementations remain available. Original i960
instructions must not execute.

Credit handling, machine selection, battle setup, battle logic, results,
versus play, and service menus are later milestones.

## Active measurements

Three percentages are kept separate:

1. **ROM classification**: classified bytes divided by the 2 MiB i960 image.
2. **Attract closure recovery**: validated weighted work-unit points divided
   by all currently known points required by the input-free attract trace.
3. **Runtime integration**: passed checkpoints divided by the checkpoint list
   below.

The closure denominator is expected to grow as indirect calls and previously
unobserved branches are discovered. Every denominator change is recorded. The
older byte-match and provisional-byte reports remain useful engineering
measurements, but are not project completion percentages.

The tracked [generated status](generated-status.md) and
[attract worklist](attract_worklist.md) contain the current closure totals.
They are regenerated from the ledger and the canonical 60-second coverage
input; this roadmap intentionally carries no copied totals.

Work units receive 1, 2, 3, or 5 points for simple leaf, ordinary control,
complex algorithm, or stateful/hardware-facing behavior. A unit counts only
after its C implementation is integrated and trace-validated.

## Runtime checkpoints

- Generated ROM reset and register-stack initialization.
- Board I/O self-test and persistent-memory/profile setup.
- SHARC and geometry upload/initialization.
- Texture, palette, tile, and text initialization.
- Main scheduler enters the attract state machine.
- Legal/title presentation is rendered.
- Audio command activity begins through the original audio subsystem.
- Video/geometry state continues changing during attract.
- Sixty emulated seconds complete without exception, reset, deadlock, or
  device-command stall.
- Runtime PC audit contains only generated code and approved data/trampoline
  ranges.

## Work-unit loop

1. Prove the function boundary, callers, exits, data references, and presence
   in the attract trace.
2. Record readable assembly semantics and unresolved behavior.
3. Implement one production C routine or tightly coupled state transition.
4. Compare key RAM transitions and ordered MMIO/command writes with the
   original trace.
5. Link it into the clean replacement image and rerun all earlier checkpoints.
6. Mark it validated only when both focused trace and integrated runtime pass.

## Current engineering order

1. Integrate the modeled queue before opening another modeled-only unit.
2. Triage remaining direct-call units in earliest failing-checkpoint and
   dependency order, assigning boundaries, responsibilities, and weights.
3. Recover scheduler, interrupts, timers, UI/title state, rendering commands,
   and audio commands in closure order.
4. Extend runtime PC auditing into the final 60-second equivalence regression.

Resolved foundation: replacement startup now initializes the i960 ABI
register-stack spill area, and the complete recovered zero-mode geometry
pipeline reaches INIT without the former PC-zero `Unhandled 00` failure.
The clean replacement image now contains generated code plus five
hash-verified original data ranges; every other byte is `0xff`. It passes the
same bounded startup regression, so the recovered startup path no longer
depends on dormant original i960 instructions.
An eight-emulated-second debugger audit observed 564 distinct i960 PCs; all
were inside the generated `0x00000000-0x00002520` extent.
The original-ROM 60-second capture and its generated worklist are reproducible
with `./scripts/trace-i960-attract-coverage.sh`.
