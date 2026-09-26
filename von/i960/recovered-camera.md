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

## Open questions

- Distance and height were constant in normal play, but the probe's
  jump/dash/shot segments did not move the mech (the match had not started),
  so any motion-dependent distance/height change is **not yet measured**.
  Re-probe with the schedule inside the live match and a stationary opponent.
- The yaw smoothing time constant is not fitted; only the tracking statistic.
- Whether the target follows player y during a jump is unmeasured (target y
  was a constant 18).
- Late frames with `|eye-target|` far from 77.2 (player parked in a corner) are
  unclassified: possible wall avoidance, death cam, or a stale cell.

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
