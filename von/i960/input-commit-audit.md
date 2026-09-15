# Input-commit audit

Where does the reconstruction ignore input while it is "doing work" (running a
timer/animation)? Tracked against the recovered kernel's states.

| kernel state | input policy | recovered evidence |
| --- | --- | --- |
| jump (`RV_ST_AIR`) | committed: no attack/dash (fixed arc), but **reduced air movement** (~0.8 u/f, ~0.38x) | `recovered-jump-state.md`, `probe_landing` (proven) |
| idle/walk release | **stops within ~1 frame**, no coast | `recovered-movement-cadence.md` (proven) |
| attack (`RV_ST_ATTACK`) | **reduced movement ~0.33x** (not frozen); turn allowed; recovery cancelable | `probe_attack_commit` (proven) |
| land (`RV_ST_LAND`) | **~20-frame freeze**, movement ignored with stick held | `probe_landing` (proven) |
| guard (`RV_ST_GUARD`) | kernel freezes horizontal velocity | not probed (guard input conflicts with move sticks) |
| hit (`RV_ST_HIT`) | no turn/move/attack until hitstun ends | not probed |
| knockdown (`RV_ST_KNOCKDOWN`) | 42 frames, no input | not probed |
| round-end / match-end | timer freeze, no input | not probed |

## Attack movement (proven)

`probe_attack_commit.lua` walks forward (settling at 2.81 u/f), then fires. The
shot is confirmed by the player ordnance (`shots=1`) and the left cooldown timer
(`object+0x1ea` jump to 300) starting ~25 frames after the tap. At the tap the
speed **snaps 2.81 -> 0.92 u/f and holds for the attack** (~43 frames), then
returns to full. So attack movement is reduced (~0.33x), not frozen.

## Landing lock (proven)

`probe_landing.lua` holds forward through a jump. In the air the mech moves at
**~0.8 u/f** (~0.38x). On touchdown it **freezes horizontal movement for ~20
frames** (z stayed at 17.59 f9726-9745 with the stick still held) before resuming.

## Next probes

1. Guard: can the mech move or turn while guarding?
2. Hit / knockdown: recovery timing and whether turn is allowed.
3. Round-end: when does input stop being accepted relative to the win banner.
