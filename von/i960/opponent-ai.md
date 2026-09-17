# Opponent (CPU) AI annotations

> Address-level notes for the Virtual-On opponent logic, recovered from
> `von/build/disasm/vonj-maincpu.lst`. Confidence tags: `KNOWN` when an
> instruction mapping is direct, `LIKELY` when the role is inferred from the
> surrounding state machine.

The opponent is not a separate program: it is the fighter object at
`0x005040d0` (player `0x00503ad0`), each pointing at the other through
`+0x74`. The AI reuses the same per-fighter state machine as the player and
adds a small perception→class→command pipeline. It never reads raw controller
input; it reads the opponent's *state* and *class*.

## 1. Perception — bearing to the opponent (`0x76590`, `KNOWN` shape)

`0x76590` (geometry object band pair) is the "where is he" step:

1. `0x765a0`-`0x765d8`: SHARC `0x884000` service `0xFFFF` with own/other
   `+0x08`/`+0x10` (x/z); the response is stored to `0x504d60`.
2. `0x76600`-`0x7661c`: SHARC service `10` with `(other - self)`; response `g0`.
3. `0x76624`-`0x7662c`: `g0 -= self+0x184` (own facing) -> relative bearing,
   stored at `0x504d64`.
4. `0x76634` `bal 0x73508`: classify the bearing into a sector.

`0x73508` is a signed sector map (i960 angle units: `0x10000` = 360°). Index
in `g0 = (s16)bearing`:

| sector | range | bound used |
| ---: | --- | --- |
| 0 | 0°..5° | `< 0x38D` |
| 1 | 5°..30° | `< 0x1554` |
| 2 | 30°..90° | `< 0x3FFF` |
| 3 | 90°..135° | `< 0x5FFF` |
| 4 | 135°..180° | else |
| 5 | -180°..-135° | `>= -0x6000` |
| 6 | -135°..-90° | `>= -0x4000` |
| 7 | -90°..-30° | `>= -0x1555` |
| 8 | -30°..-5° | `>= -0x38E` |
| 9 | -5°..0° | else |

The sector is stored at `0x504d68` (`0x76638`). Note `0x504d60` is a SHARC
geometry response, not a wall-clock timer, even though the state machine uses
it as a threshold.

## 2. Class dispatch (`0x735f0`, `KNOWN`)

`0x735f0` loads the current behavior class from `0x504d94`, rejects `> 33`
(takes `0x74848`), and jumps through the `0x73618` table:

| class | handler | class | handler |
| ---: | ---: | ---: | ---: |
| 0 | `0x74848` | 17 | `0x74110` |
| 1 | `0x736a0` | 18 | `0x7411c` |
| 2 | `0x737c8` | 19 | `0x74138` |
| 3 | `0x73900` | 20 | `0x7415c` |
| 4 | `0x73a34` | 21 | `0x74178` |
| 5 | `0x73b68` | 22 | `0x74194` |
| 6 | `0x73c98` | 23 | `0x745bc` |
| 7 | `0x73dcc` | 24/25 | `0x74848` |
| 8 | `0x74148` | 26 | `0x745e4` |
| 9 | `0x744ec` | 27 | `0x7460c` |
| 10 | `0x73fdc` | 28 | `0x74634` |
| 11 | `0x73ffc` | 29 | `0x74674` |
| 12 | `0x7402c` | 30 | `0x746f4` |
| 13 | `0x7408c` | 31 | `0x74754` |
| 14 | `0x740ec` | 32 | `0x7479c` |
| 15 | `0x740f8` | 33 | `0x747e4` |
| 16 | `0x74104` | | |

Every handler writes the fighter command word at **`object+0x108`** through
`r6 = object+0xec` (`stos rX,0x1c(r6)`, set once at `0x73604`). This is the
same command the input consumer produces for a human, so the AI injects a
synthesised input rather than bypassing the state machine.

### Class semantics (`LIKELY`)

| class | output | role |
| ---: | --- | --- |
| 1 | service 29 with facing + 0 | move forward |
| 2 | service 29 with facing + `0x2000` (+45°) | veer right |
| 3 | service 29 with facing - `0x2000` (-45°) | veer left |
| 4 | service 29 with facing - `0x8000` (180°) | move backward |
| 5 | service 29 with facing + 0 | forward (alt speed) |
| 6 | service 29 with facing - `0x4000` (-90°) | side-step |
| 7 | distance/state gate, then command | approach/retreat |
| 8 | `0` / `0x707` / `0x303` / `0x505` by class | neutral or move |
| 9 | `0x404`, own/other class + `+0x184` compare | turn/aim |
| 10 | `0x72b40[sector]` = `0x0202` | hold direction 2 |
| 11 | `0x72b60[sector]` = `0x0606` | hold direction 6 |
| 12 | `0x400`; if sector < 3 -> class 26 | attack/steer |
| 13 | `4`; if sector < 3 -> class 27 | attack/steer |
| 14 | `0x400` (setbit 8) | guard/block |
| 15 | `7` | move |
| 16 | `0x405` | move |
| 17 | `0x304` | move |
| 18 | `0x101`, or `0` when own class is 3/8 | move |
| 19 | `0x707` | move |
| 20 | `0x303`, or `0` when own class is 3/8 | move |
| 21 | `0x505`, or `0` when own class is 3/8 | move |
| 22 | `0x602` when own state `+0x172` is 11, else table `0x741d8` | state branch |
| 23 | `0x400` (setbit 10) + class 12 when sector >= 3 | attack/steer |
| 26 | `0x400` + class 12 when sector >= 3 | attack/steer |
| 27 | `4` + class 13 when sector >= 3 | attack/steer |
| 28 | `0x206` | attack variant |
| 29 | command per `+0x170`; `0xffff` + reset `0x504db4 = 1` on 0/4/5/6 | attack/timeout |
| 30 | `0xffff` + reset `0x504db4 = 1` when state `+0x172` not in 0/4/5 | timeout |
| 31 | `0x404` | attack variant |
| 32 | `0x202` | attack variant |
| 33 | `0x606` | attack variant |
| 0/24/25 | `0xffff` (invalid/no-op) | idle |

The command word is two nibble lanes; `0x0202`/`0x0606` set both lanes to
direction 2/6, and `0x101`..`0x707` are the paired movement levels. Classes 10
and 11 are the only sector-table lookups (`0x72b40`/`0x72b60`, both uniform
across sectors), so the class table above is the real decision content.

The service-29 calls are the SHARC trig/velocity service (see
`von_movement.h`), so classes 1-6 are facing-relative movement primitives.

## 3. Sector -> class tables (`KNOWN` contents)

The action-5/action-10 wrappers select a table and index it by the sector
(`0x504d68`); the value is written to `0x504d94` (the next class):

| wrapper | table | values by sector 0..9 |
| --- | ---: | --- |
| `0x783c8` (action 5) | `0x72690` | `8, 0x12, C, C, C, D, D, D, 0x13, 8` |
| `0x78408` (action 10) | `0x72750` | `9, 0x10, C, C, C, D, D, D, 0x11, 9` |
| `0x78448` (action 10) | `0x72990` | `A, A, C, C, C, D, D, D, A, A` |
| `0x78488` (action 10) | `0x729f0` | `B, B, C, C, C, D, D, D, B, B` |
| `0x78a58` (0x78a30) | `0x72a20` | `0x12, C, C, C, C, D, 0x13, 0x13, 8, 0x12` |
| `0x78830` (0x78818) | `0x72690` | action-5 table (mode-gated) |
| `0x78be8` (0x78bd8) | `0x72690` | action-5 table (mode-gated) |

`A/B/C/D` = classes 10/11/12/13. Classes `C`/`D` (12/13, the weapon/action
variants of `state-semantics.md`) cover the front and side sectors; only the
near-ahead (0/1) and near-behind (8/9) sectors get the specialised entries.

## 4. Feedback and randomness

- `0x504d94` is written by the action wrappers above, by the match-phase
  selectors (`0x752xx`, `0x753xx`), and by the class handlers (`0x736xx`), then
  read back by the state machine (`recovered_object_state_runtime`) and by
  `0x735f0` itself.
- The state machine also consumes a random role from `0x79664`
  (`recovered_object_state_random_selector`): `[1,1,2,2,3,3,5,6]` indexed by
  `random & 7`, so identical situations can select different transitions.
- `0x7a3e0` (route head) compares own `+0x64` against the opponent's `+0x64`
  and routes to mode 11 / ratio paths before the class selection.

## 5. Summary

The opponent is a **10-sector reactive classifier**:

```
opponent position -> SHARC -> bearing -> 10 sectors (0x73508)
sector + situation -> table (0x72690/... ) -> class (0x504d94)
class -> handler (0x73618) -> command word at object+0x108
                       (movement via SHARC service 29, or canned attack)
```

No pathing, prediction, or input reading; 10-way spatial resolution with two
dominant attack classes and a random role. This is consistent with the
observed weak but "reactive" behaviour.

## Open items

- The command-word encoding at `object+0x108` (values `0x0202`, `0x0606`,
  `0x101`..`0x707`, `0x400`, `4`) maps through the input-consumer nibble
  tables at `0x3d70`/`0x3da0`; the exact direction/strength semantics are not
  yet assigned.
- `+0x64` class vs control-mode semantics (it flips 0 -> 5 for a ~4.5 s window
  in the input-free attract capture).
- The `0x504d60` SHARC response's physical meaning (distance, height, or
  projection) is unconfirmed.
