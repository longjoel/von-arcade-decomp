# i960 symbol map

Names for the addresses the reconstruction refers to. These replace the raw
"magic numbers". Confidence is `KNOWN` when it comes from the reset structure,
the recovered routines, or observed read/write patterns, and `candidate` when
the role is inferred from usage.

## Boot / root entry

| Symbol | Address | Meaning | Confidence |
| --- | ---: | --- | --- |
| `VON_SAT` | `0x00000000` | i960 system address table (MAME `m_SAT = read_dword(0)`); PRCB pointer at `+0x04`, start IP at `+0x0c` | KNOWN |
| `VON_PRCB` | `0x000000b0` | Processor control block (`read_dword(4)`), copied to `0x501800` | KNOWN |
| `VON_RESET_IP` | `0x00000930` | Reset handler (`read_dword(0x0c)`) | KNOWN |
| `VON_RUNTIME_INIT` | `0x000009f0` | C runtime init: grows `sp`, `fp = 0x500400`, calls main | KNOWN |
| `VON_MAIN` | `0x000186f0` | Program main | KNOWN |
| `VON_MAIN_LOOP` | `0x00018724` | Main loop top | KNOWN |
| `VON_MODE_TABLE` | `0x00018680` | 16-entry game-mode handler table, indexed by `VON_GAME_MODE & 15` | KNOWN |
| `VON_MAIN_STACK` | `0x000500400` | `fp` set by the runtime init | KNOWN |

## Game mode

| Symbol | Address | Meaning | Confidence |
| --- | ---: | --- | --- |
| `VON_GAME_MODE` | `0x005039f4` | Current game mode; advanced by `+= 1` on completion, forced to `5` for play | KNOWN |
| `VON_MODE_PHASE` | `0x00503a00` | Per-mode phase/frame counter; zeroed on every mode change | KNOWN |
| `VON_MAIN_HOLD` | `0x005039f0` | Main-loop hold/pause gate | candidate |
| `VON_START_REQUEST` | `0x005024f4` | Start/coin request register (compared against `0x50` in the loop) | candidate |
| `VON_MODE_TABLE_LEN` | `16` | Mode index mask is `& 15` | KNOWN |

Mode handlers (from `VON_MODE_TABLE`): `0x003c40` (UI record walker),
`0x02b9e0` (mode 1/2 candidate scan), `0x018650`, `0x0190d0`, `0x019180`,
`0x0f3f00`, `0x0f3fe0`, `0x0f3d30`, `0x018620` (shared 8/15). Modes 3 and 4
reach gameplay.

## Key functions

| Symbol | Address | Meaning | Confidence |
| --- | ---: | --- | --- |
| `VON_FN_INPUT_RESET` | `0x00024f98` | Per-object input-substructure reset | KNOWN |
| `VON_FN_INPUT_CONSUMER` | `0x00025040` | Per-object input consumer (decodes command) | KNOWN |
| `VON_FN_OBJECT_UPDATE` | `0x00026cb8` | Per-object gameplay update; calls frame step then backbone | KNOWN |
| `VON_FN_HW_INIT` | `0x000294b0` | Hardware/audio init (writes `0x800xxx`) | candidate |
| `VON_FN_BACKBONE` | `0x00032810` | Per-object update backbone (`0x32560` table) | KNOWN |
| `VON_FN_ACTION_COMMIT` | `0x00036460` | Committed action -> state 31 (state 0 of `0x37130`) | KNOWN |
| `VON_FN_FRAME_STEP` | `0x000371e0` | Per-object frame step (`0x37130` table) | KNOWN |
| `VON_FN_PROJECTION` | `0x0006f6f0` | Geometry projection / ground contact | KNOWN |
| `VON_FN_CONFIG_COPY` | `0x00018ab0` | Config/table service called each loop iteration | candidate |

## Tables

| Symbol | Address | Meaning | Confidence |
| --- | ---: | --- | --- |
| `VON_BACKBONE_STATE_TABLE` | `0x00032560` | `VON_FN_BACKBONE` state -> handler (43 entries, 16-byte stride) | KNOWN |
| `VON_ACTION_TABLE` | `0x00032968` | `VON_FN_BACKBONE` action -> arm (14 entries) | KNOWN |
| `VON_FRAME_STEP_TABLE` | `0x00037130` | `VON_FN_FRAME_STEP` state -> handler | KNOWN |
| `VON_DIR_TABLE_18350` | `0x00018350` | Committed-action -> direction/speed index (`+0x176`/`+0x188`) | KNOWN |
| `VON_DIR_TABLE_18360` | `0x00018360` | Committed-action -> turn delta (`+0x3c`) | KNOWN |
| `VON_DIR_TABLE_18370` | `0x00018370` | Committed-action -> half heading (`+0x186`) | KNOWN |

## Objects and globals

Base player object `0x00503ad0`, CPU object `0x005040d0`.

| Symbol | Address | Meaning | Confidence |
| --- | ---: | --- | --- |
| `VON_CONFIG_PTR` | `0x0051ab14` | Global pointer to the active per-kind config (set from `object+0x6c`) | KNOWN |
| `VON_INPUT_WORD_A` | `0x0050249c` | Raw controller word A copied into `object+0xec` | KNOWN |
| `VON_INPUT_WORD_B` | `0x005024a4` | Raw controller word B copied into `object+0xf0` | KNOWN |
| `VON_INPUT_MA` | `0x00504dac` | Signed MA lane published by the input service | KNOWN |
| `VON_INPUT_MB` | `0x00504db0` | Signed MB lane published by the input service | KNOWN |

Object field offsets (`VON_OBJ_*`) are defined in `von_symbols.h` and documented
in `state-semantics.md`.

## Wire-up (current)

The reconstructed image's `_start_ip` (`start_reconstructed.s`) currently calls
`_i960_reconstructed_main` and never enters `VON_MAIN` / the mode loop. The real
chain is:

```
reset VON_RESET_IP -> VON_RUNTIME_INIT -> VON_MAIN
  -> loop: g0 = VON_MODE_TABLE[VON_GAME_MODE & 15]; callx (g0)
  -> mode 3/4 -> VON_FN_OBJECT_UPDATE -> VON_FN_FRAME_STEP + VON_FN_BACKBONE
```
