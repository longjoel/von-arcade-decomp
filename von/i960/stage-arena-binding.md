# Stage ordinal -> banner and arena binding (probe 2026-09-12)

Method: `von/tools/probe_stage_binding.lua` joins the deterministic first match
(fresh NVRAM, Coin@900, 1P Start@1500), forces `0x503a80` only from frame 1200,
and logs the published descriptor (`0x504ca0/cb0/cc0`), the banner page word
`0x5770f0`, and the selector timers. Each run pairs with the instrumented
geometry trace (patch 0007, `-oslog`); the arena OBAs are censused in the
settled match window `t=42..70s`. One run per ordinal 0-9.

## Ordinal -> banner

`0x503a80` selects record `0x194a0[ord*32]`; the record's **word1** is the
banner index into the ROM banner order at `0x21065`. Live `0x5770f0` equals
word1 for all ten ordinals:

| ord | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| word1 / banner | 7 | 0 | 2 | 3 | 4 | 9 | 5 | 6 | 1 | 8 |
| name | FLOODED CITY | AIRPORT | WATERFRONT | GREEN HILLS | RUINS | SECRET BASE | SPACE DOCK | MOON BASE | DEATH TRAP | NIRVANA |

`ca0` = record word0, `cc0` = `0x195e0[banner].word0`; both track the mapping.
This corrects the earlier identity assumption (`stage 0` is FLOODED CITY, not
AIRPORT) and matches the ord3/ord4 banner warp in
`disassembly-annotations.md`.

## Ordinal -> arena

Each ordinal serves a distinct arena OBA set (lead static shown); the shared
`0x84553f` set is constant, not the arena:

| ord | banner | arena family / lead OBA | recovered export? |
| --- | --- | --- | --- |
| 0 | FLOODED CITY | `0x81` / `0x8158f6` | no |
| 1 | AIRPORT | `0x80` / `0x80060e`, `0x80341b`, … | **yes — `stage2_arena.glb`** |
| 2 | WATERFRONT | `0x80` / `0x80e1d5` + `0x91`/`0x93`/`0x99` | no |
| 3 | GREEN HILLS | `0x80` / `0x80b59c` + `0x93` | no |
| 4 | RUINS | `0x80` / `0x80d07f` | no |
| 5 | SECRET BASE | `0x81` / `0x81e74c` + `0x93` | no |
| 6 | SPACE DOCK | `0x80` / `0x8083f9` + `0x93`/`0x9a` | no |
| 7 | MOON BASE | `0x80`/`0x81` / `0x81084a` | no |
| 8 | DEATH TRAP | `0x80` / `0x8044b4` | no |
| 9 | NIRVANA | `0x83` / `0x833943` + `0x93` | no |

The recovered family-`0080` statics match ordinal 1 exactly: 12/15 of the
`stage2_arena.glb` arena OBAs appear for ordinal 1, 0/15 for every other
ordinal. So `stage2_arena.glb` is **AIRPORT (ordinal 1)**, not the first match.
The kernel's recovered 7-box collision profile moves to ordinal 1 to match; the
other ordinals keep provisional profiles until their boxes are recovered.

## Recovered collision boxes

The collision boxes are the render AABBs of each arena's solid statics, measured
at **match start** (`t=33..37s`) so destructible blocks are still present. For
AIRPORT this reproduces the movement-confirmed set (`recovered_stage_obstacle_boxes.c`);
for the other measured stages the bounds are render-measured and the kind is
assumed solid (no box contains a spawn point). GREEN HILLS, RUINS, SECRET BASE
and NIRVANA keep provisional profiles: no clean low-block set is present at
match start (their arenas are large structures / morphing).

| ord | banner | boxes | source |
| --- | --- | --- | --- |
| 0 | FLOODED CITY | 6 | measured |
| 1 | AIRPORT | 7 | recovered (movement-confirmed) |
| 2 | WATERFRONT | 5 | measured |
| 3 | GREEN HILLS | - | provisional |
| 4 | RUINS | - | provisional |
| 5 | SECRET BASE | - | provisional |
| 6 | SPACE DOCK | 3 | measured |
| 7 | MOON BASE | 8 | measured |
| 8 | DEATH TRAP | 2 | measured |
| 9 | NIRVANA | - | provisional |

Measured boxes `min=(x,y,z) max=(x,y,z)`, kind block unless noted
(`AIRPORT` pads are the two `z +/-[44,76]` boxes):

```text
FLOODED CITY : (-197,0,-198)-(-163,18,-162)  (-196,0,164)-(-164,19,196)
               (-116,0,-36)-(-84,18,36)      (84,0,-36)-(116,18,36)
               (163,0,-198)-(197,18,-162)    (164,0,164)-(196,19,196)
WATERFRONT   : (-275,0,45)-(-205,26,75)      (-235,0,70)-(-205,26,115)
               (-115,0,205)-(-45,25,275)     (-114,0,-114)-(-46,11,-46)
               (205,0,45)-(275,24,115)
SPACE DOCK   : (-155,0,-234)-(-85,18,-86)    (-152,0,6)-(-88,18,154)
               (126,0,-154)-(195,26,72)
MOON BASE    : (-240,0,-120)-(-200,27,-80)   (-240,0,40)-(-200,20,120)
               (-120,0,-200)-(-40,20,-160)   (-120,0,160)-(-80,20,200)
               (40,0,-200)-(120,20,-160)     (80,0,160)-(120,20,200)
               (200,0,-120)-(240,27,-80)     (200,0,40)-(240,20,120)
DEATH TRAP   : (-40,0,-40)-(40,20,40)        (-20,0,-20)-(20,20,20)
```

The kernel embeds these in `RV_ARENAS` (`von-godot/native/kernels/von_recovered_kernel.c`);
Godot mirrors them in `VonStages` and a test compares box counts against the
loaded kernel.

## Terrain stages

GREEN HILLS (ordinal 3) and RUINS (ordinal 4) are not flat box arenas. GREEN
HILLS is rolling terrain: many mid-size, non-flat statics (y 0..52 over
~150-460-unit footprints). `von/tools/extract_stage_heightfield.py` samples the
top surface onto a 17x17 grid over +/-320; the kernel embeds it
(`RV_TERRAIN_GREEN_HILLS`) for ground height and the host renders the same grid
as `assets/generated/arena/stage_03_arena.gltf`. RUINS is a stepped central
platform (14 -> 7 -> 0) plus thin pillars; its terrain is not modelled yet
(provisional).

## Movement validation

Forcing a stage and logging the game's fighter positions (attract demo) shows
the fighter blocked exactly at the edge of AIRPORT box6 and FLOODED CITY box3
(min distance 0.0, zero penetration), supporting those measured boxes. The
demo path does not traverse the other boxes, so the rest remain render-measured
rather than movement-confirmed. The sub-cell work-RAM position words
(`0x503ad8`) read zero/degenerate in the demo, so a full per-box check needs a
joined, input-driven bout.

## Reproduction

```sh
cd von-arcade-decomp
for ord in 0 1 2 3 4 5 6 7 8 9; do
  out=/tmp/stage-bind-$ord; mkdir -p "$out/nvram"
  VON_STAGE_LOG="$out/state.log" VON_STAGE_ORDINAL=$ord \
  VON_STAGE_FORCE_MIRROR=0 VON_STAGE_FORCE_FROM=1200 VON_STAGE_FORCE_TO=4000 \
  VON_STAGE_SECONDS=58 VON_GEOMETRY_OBJECT_MAX=400000 \
    ./bin/von vonj -rompath von/build/disasm/rompath \
    -nvram_directory "$out/nvram" -video none -sound none -skip_gameinfo \
    -oslog -nothrottle -seconds_to_run 58 \
    -autoboot_script von/tools/probe_stage_binding.lua > "$out/trace.log" 2>&1
done
```
