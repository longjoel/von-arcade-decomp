# Recovered camera

> `recovered:<ram-telemetry>`; the camera state was read from live i960 work
> RAM, not integrated. Open questions are listed at the end.

## Method

MAME's Model 2 geometry command set has no explicit view/projection command, so
the camera is baked into the per-object matrices. The camera state is also
mirrored in i960 work RAM, which is the authoritative source used here.

```sh
# Join the first bout, force AIRPORT (ordinal 1), and drive a turn/move pattern
# while logging the player object, heading, and camera cells every frame.
VON_CAMERA_HOLD=":IN1,0x20,2100,4200" \
VON_CAMERA_STATE="0x503ad8,0x10e0,5" \
  scripts/trace-camera.sh
```

`von/tools/probe_camera.lua` drives the twin sticks (`:IN1` left stick,
`:IN2` right stick) and dumps a float window; `scripts/trace-camera.sh` pairs it
with the `-oslog` geometry trace. The camera also appears in the trace as the
matrix reused across the family-`0x80` world statics each frame, but that modal
extraction is noisy; prefer the RAM cells.

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

- The eye sits at a fixed **world-axis-aligned** offset from the player:
  `eye = (player.x, 29.445, player.z - 77.2)`.
- The look target is the player's x/z at height **18.0**:
  `target = (player.x, 18.0, player.z)`.
- The resulting pitch is `atan2(29.445 - 18.0, 77.2) = -8.44 deg`.
- The horizontal eye-to-target distance is a constant **77.2** (nominal cell
  `0x504bc8` = 78.0).

The decisive observation: across driven runs the eye stayed at offset
`(0, -77.2)` while the player's heading swung over roughly `-220..162 deg`
(and while it strafed across the arena). **The heading does not rotate the
camera.** This is a world-oriented follow camera, not a heading-locked chase.

## Open questions

- The eye offset was world-fixed in every clean segment, but late in one run it
  departed `(0, -77.2)` while the player sat against the `-x/-z` arena corner.
  Whether that is wall avoidance, a target switch to the opponent, or a reset
  is unresolved; re-probe with a longer in-bounds walk.
- The projection (focal length / FOV) is not recovered; only the extrinsic
  transform above.
- The companion value at `0x504bc8` (78.0) and the `y=1` triple at
  `0x503b78`/`0x504178` are unclassified.

## Application

`von-godot/scripts/match_view.gd` uses this model directly
(`CAMERA_DISTANCE = 77.2`, `CAMERA_HEIGHT = 29.445`,
`CAMERA_LOOK_HEIGHT = 18.0`), replacing the earlier heading-locked heuristic.
