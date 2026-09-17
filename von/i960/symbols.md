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

Mode handlers (from `VON_MODE_TABLE`):

| mode | handler | role |
| ---: | ---: | --- |
| 0 | `0x003c40` | attract/UI: hw init `0x294b0`, SHARC opcode 8, walks the UI record list at `0x2ea2918` rendering with the `0x1c618`/`0x1cac8`/`0x1cc40` text helpers, then advances the phase |
| 1 | `0x02b9e0` | attract sequence / select: gates on `0x503a08` and the `0x1d00034`/`0x1d00038` hardware, dispatches the phase table at `0x2b960` (phase & 31) |
| 2 | `0x018650` | idle advance: helper `0x1ccf8`, `mode += 1`, `phase = 0` |
| 3 | `0x0190d0` | play setup: resets the play globals, then advances to mode 4 |
| 4 | `0x019180` | gameplay: SHARC opcodes 8/16, `VON_FN_OBJECT_UPDATE` -> frame step + backbone |
| 5 | `0x0f3f00` | diagnostic setup: sets `VON_MAIN_HOLD=1`, clears the `0x5784f8` diagnostic record |
| 6 | `0x0f3fe0` | diagnostic state machine: `0xf3ec0` table, counter `mod 11` |
| 7 | `0x0f3d30` | diagnostic |
| 8, 15 | `0x018620` | reset back to attract (`mode = 0`, `phase = 0`) |

Modes 0, 2, 3, 4 and 8/15 are modeled in `reconstructed_main_loop`. Mode 0
(attract) is runnable: it resets the text console, walks the UI record list in
main_data at `0x2ea2918`, and runs the `0x234`-frame countdown; on the
reconstructed image this writes the tile nametable (`0x1000000`, the Sega
System 24 tile device) and advances to mode 1. Mode 1 and the diagnostics
5/6/7 are not yet runnable.

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

`_start_ip` (`start_reconstructed.s`) still calls `_i960_reconstructed_main`
directly, but `i960_reconstructed_main` now enters the reconstructed
`reconstructed_main_loop`, which mirrors `VON_MAIN_LOOP`: it dispatches
`VON_MODE_TABLE[VON_GAME_MODE & 15]`. Mode 3 (`reconstructed_mode_3`) resets the
play globals and advances to mode 4; mode 4 (`reconstructed_mode_4`) runs the
gameplay tick (the recovered input -> frame-step -> velocity -> backbone path).
The gameplay tick now enters `VON_FN_FRAME_STEP` through the recovered
`0x37130` dispatch (`recovered_framestate_dispatch_run`, 0x37350-0x37388):
it gates on the signed `+0x172` phase and calls the non-null arm, so state 0
reaches the committed-action transition (0x36460) and states 15/16/17/19/
23/24/26/28/29/31/33/35/37 run their recovered arms. The frame-step heading
prefix (`recovered_framestep_heading_run`, 0x37240-0x3734c) slews the
`+0x32`/`+0x34` facing pair toward the `+0x186` half-heading and latches the
`+0x198` descent timer; it was recovered bit-exactly from the original attract
capture. Other mode handlers, the input-selection/config/timer prefix, and the
in-arm helper calls (`0x2a4e0`, `0x1c618`, `0x1bda0`, `0x295d0`) are not yet
runnable.

The original chain, for reference:

```
reset VON_RESET_IP -> VON_RUNTIME_INIT -> VON_MAIN
  -> loop: g0 = VON_MODE_TABLE[VON_GAME_MODE & 15]; callx (g0)
  -> mode 3/4 -> VON_FN_OBJECT_UPDATE -> VON_FN_FRAME_STEP + VON_FN_BACKBONE
```
