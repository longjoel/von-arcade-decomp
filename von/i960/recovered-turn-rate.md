# Recovered turn rate

> `observed:<ram-telemetry>`; measured, not integrated.

## Method

The player's heading is a float in the low workram at **`0x503c28`** (degrees).
It was found by per-frame RAM telemetry (`VON_FUZZ_STATELOG`) over the player
workspace `0x5039c0..0x503dc0` during a held right-stick turn, then confirmed
by the opposite direction:

```sh
# single-cabinet solo-vs-CPU, hold the right stick for 120 frames
VON_FUZZ_ONLY=r_right VON_FUZZ_HOLD=120 VON_FUZZ_STATELOG="0x5039c0,0x400,1" \
  bin/von vonj -rompath .../rompath -video none -sound none -nothrottle \
  -autoboot_script von/tools/fuzz_battle_ram.lua
```

The heading cell ramps linearly after a short onset transient, symmetrically
for `r_right` and `r_left`.

## Result

| quantity | value |
| --- | --- |
| steady heading rate | **0.7568 deg/frame** (45.4 deg/s) |
| in radians | **0.01321 rad/frame** |
| onset | ~10-frame transient (peaks ~4.4 deg/frame) then settles |

The kernel previously used a provisional `0.060 rad/frame` (≈4.5x too fast);
it now uses `RV_TURN_RATE = 0.01321f` (`native/kernels/von_recovered_kernel.c`,
exposed for the native test as `rv_test_turn_rate`).

## Notes

- Side cell `0x503b54` (signed 16-bit-ish integer) tracks the turn too but was
  not needed; `0x503c28` is the clean float heading.
- Onset transient is not yet modeled (the kernel applies the rate instantly).
