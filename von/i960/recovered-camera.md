# Recovered camera

> `recovered:<ram-telemetry>`; the camera state and projection were read from
> live i960 work RAM and the emulated geometry path, not integrated. Open
> questions are listed at the end.

## Method

MAME's Model 2 geometry command set has no explicit view/projection command, so
the camera is baked into the per-object matrices. The camera state is also
mirrored in i960 work RAM, which is the authoritative source for the extrinsics.

```sh
# Join the first bout, force AIRPORT (ordinal 1), drive a scripted input
# battery, and log the player, opponent, heading, and camera cells.
VON_CAMERA_SEQ="IN1,0x20,3600,4200;IN2,0x80,4200,4800;..." \
VON_CAMERA_STATE="0x503ad8,0x1128,2" VON_CAMERA_SECONDS=150 \
  scripts/trace-camera.sh
```

`von/tools/probe_camera.lua` drives the twin sticks (`:IN1` left stick,
`:IN2` right stick): `VON_CAMERA_SEQ` runs a list of `port,mask,from,to`
holds, `VON_CAMERA_HOLD` holds one, and the default is a turn/move pattern.
`scripts/trace-camera.sh` pairs it with the `-oslog` geometry trace.

## Projection (FOV)

Model 2 command `0x09` sets the focal distance; `apply_focus` multiplies the
view-space x/y by it before the `1/z` divide (`src/mame/sega/model2_v.cpp`).
Patch `0052-von-focal-logging.patch` logs it:

```sh
VON_HACK_OUT=/tmp/focal VON_HACK_SECONDS=45 scripts/hack-bout.sh
grep vonj_focus /tmp/focal/mame.log   # vonj_focus: ... x=600.000000 y=600.000000
```

The focal is a constant **600.0 / 600.0**. On the Model 2 viewport
`(8,90)-(504,474)` = 496x384 the field of view is:

| axis | half-extent | focal | full FOV |
| --- | --- | --- | --- |
| horizontal | 248 | 600 | **44.9 deg** |
| vertical | 192 | 600 | **35.5 deg** |

## Recovered state cells

| quantity | address | notes |
| --- | --- | --- |
| player position | `0x503ad8` (x), `0x503adc` (y), `0x503ae0` (z) | y is ground height (0) |
| player heading | `0x503c28` | float degrees (see `recovered-turn-rate.md`) |
| opponent position | `0x5040d8`/`dc`/`e0` | bout mirror, player `+0x600` |
| camera eye | `0x504b98` (x), `0x504b9c` (y), `0x504ba0` (z) | y = **29.445**, constant |
| camera target | `0x504bb4`/`b8`/`bc` | = player x/z, y = **18.0** |
| camera target (copy) | `0x504bc0`/`c4`/`c8` | same value repeated |
| camera distance | `0x504bc8` | **78.0** nominal |

## Recovered model

- **Target**: the player's x/z at height 18.0 — `0x504bb4` tracks `0x503ad8`.
- **Distance**: constant **77.2** horizontal eye-to-target in normal play.
- **Heights**: eye 29.445, target 18.0, pitch `atan2(29.445-18.0, 77.2) =
  -8.44 deg`.
- **Yaw**: the eye is placed behind the player along the horizontal
  player->opponent axis, so the camera faces the enemy. Over 1046 in-play
  samples the camera-forward angle tracks the player->opponent bearing with
  mean error **13.5 deg** and 49% within 10 deg, versus mean error 46.5 deg
  against the player heading. The residual is consistent with a smoothed
  first-order follow.

An earlier run looked like a *world-axis-aligned* follow (offset `(0, -77.2)`);
that run simply had the opponent along +Z, so the enemy axis coincided with
world -Z. Corrected here.

## Motion- and state-dependent changes (live-match probe)

A controlled sweep (`VON_CAMERA_FIELD_SEQ`, see below) and the clean
`action-roster` captures (idle opponent) answer the earlier open questions:

- **Grounded base is stable.** Idle, forward/back, strafe, turn, **dash**,
  guard, and ranged fire all hold eye `29.445`, target y `18.0`, horizontal
  `|eye - target|` `77.2`, pitch `8.44 deg`, even at point-blank player->opponent
  range. So the camera distance does **not** scale with the fighter range in
  normal play.
- **Jump/air: the target rides the mech.** The look target follows the player's
  height (`target.y ~ 18 + player.y`): jump 45-frame median `target.y 44`
  (player y ~26) and the post-jump landing window `70.3` (player y ~52, close to
  the recovered ~51 jump apex). The eye rises too but lags through the smoothing,
  so the eye-target vertical offset temporarily grows from `11.4` to ~`18-27`
  during fast vertical motion.
- **Close/lock pulls the camera in.** Melee (stab/cross-slash) and the center
  chord reduce the horizontal distance to ~`53-66` (min ~`41`) and lower the
  target to y ~`12`; single left/right shots (unlocked) stay `77.2 / 18`.
- **Cell correction.** `0x504bc8` duplicates the target z (the `dist` field of
  the old camera log), not a distance cell. Use `|eye - target|` horizontal.

A 10-stage idle sweep with `probe_camera.lua` shows several stages/windows with
alternate poses (e.g. distance `40` with eye y `8-23`, or `49`), while others
match the standard `77.2 / 29.445 / 18`. The fixed stage-force probe is
confounded by round-intro/attract phases (a stage can show two poses at
different times), so whether this is stage geometry or match state is **not yet
separated**; it needs a probe that holds the round in COMBAT.

Probe tooling added for this: `probe_camera.lua` accepts
`VON_CAMERA_FIELD_SEQ="from,to,PORT:FIELD[,PORT:FIELD];..."` (named inputs, e.g.
jump = left-stick-left + right-stick-right), and `analyze_camera_probe.py`
summarizes a `state` dump's player/eye/target cells and base pose.

## Open questions

- Separate stage- from match-state-dependence of the alternate camera poses
  (phase-controlled probe that stays in COMBAT).
- Fit the vertical target/eye smoothing time constants during a jump.
- The lock/close pull-in curve: is it keyed on the lock latch, the melee action,
  or the player->opponent range?
- The late frames with `|eye-target|` far from `77.2` when parked in a corner are
  yaw lag (the eye is off the player->opponent axis), not a distance change.

## Application

The kernel now owns the camera: `von_recovered_kernel.c` keeps a `cam_yaw`
smoothed first-order follow of the horizontal player->opponent bearing (snapping
while the lock latch is active), and each tick derives the eye behind the player
along that bearing and the player as the look target, using `RV_CAM_DISTANCE =
77.2`, `RV_CAM_HEIGHT = 29.445`, `RV_CAM_LOOK_HEIGHT = 18.0`, `RV_CAM_FOV =
35.48`. `cam_yaw` is hashed and saved/loaded with the rest of the state, so the
camera is deterministic and rollback-safe.

The snapshot exposes `camera_eye`, `camera_target`, and `camera_fov` (optional,
`bytes`-guarded appends) and `von-godot/scripts/match_view.gd` renders from them,
falling back to its own chase only when the fields are absent. The smoothing gain
`RV_CAM_YAW_SMOOTH = 0.18` is still provisional (see the open question above).
