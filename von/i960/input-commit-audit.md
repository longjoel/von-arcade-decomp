# Input-commit audit

Where does the reconstruction ignore input while it is "doing work" (running a
timer/animation)? Tracked against the recovered kernel's states.

| kernel state | input policy | recovered evidence |
| --- | --- | --- |
| jump (`RV_ST_AIR`) | **committed**: no attack/dash, fixed arc | `recovered-jump-state.md` (proven) |
| idle/walk release | **stops within ~1 frame**, no coast | `recovered-movement-cadence.md` (proven) |
| attack (`RV_ST_ATTACK`) | kernel freezes horizontal velocity; turn allowed; recovery cancelable | inconclusive (see below) |
| guard (`RV_ST_GUARD`) | kernel freezes horizontal velocity | not probed |
| hit (`RV_ST_HIT`) | no turn/move/attack until hitstun ends | not probed |
| knockdown (`RV_ST_KNOCKDOWN`) | 42 frames, no input | not probed |
| land (`RV_ST_LAND`) | 6 frames, but action allowed | not probed |
| round-end / match-end | timer freeze, no input | not probed |

## Attack movement (inconclusive)

`probe_attack_commit.lua` holds forward and taps the left shot. After the tap
the mech's speed dropped to a steady **~0.51 u/f for ~42 frames** before
resuming, which looks like a reduced-movement attack state (the kernel instead
freezes to 0). But `object+0x174` (the action) stayed **0**, so it is not proven
the shot actually fired; the plateau could be a walk-cadence phase. Re-probe
with a confirmed fire (watch the ordnance pool / cooldown cell) before changing
the kernel.

## Next probes

1. Confirm the attack fires (ordnance/cooldown) and measure movement/turn through
   startup/active/recovery.
2. Guard: can the mech move or turn while guarding?
3. Landing: is there a landing lock, and for how many frames?
4. Round-end: when does input stop being accepted relative to the win banner?
