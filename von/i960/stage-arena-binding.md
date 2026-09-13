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
