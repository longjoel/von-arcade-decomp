# Audio recovery and validation

## Current position

The original `vonj` audio system contains a 68000 SCSP program and an 8 MiB
sample region. Current tools can capture MAME output, extract sample windows
from register descriptors, retain chronological runtime key-on events, and
produce a provisional offline reconstruction.

Treat all pre-baseline generated WAVs and catalogs as `legacy-unreviewed` until
they are regenerated through the evidence-pack process. In particular, the
offline level-select/music reconstruction is provisional: DSP effects and the
SCSP envelope path are not reproduced exactly.

## What is established

- The static register table yields eight non-silent PCM16 calibration/test
  tones. They are not the game's music.
- Runtime tracing reached match entry and captured SCSP slot writes.
- One retained event catalog contains 953 chronological key-ons from trace
  time 16 onward; 593 have a direct or DSP route.
- Runtime descriptors include SA, LSA, LEA, PCM mode, OCT/FNS, attenuation,
  pan, routing, and first-order envelope fields.
- A 60-second host audio-queue sample showed consistent ring advancement but
  did not capture producer arguments reliably enough to promote a new model.

These are historical findings to reproduce, not grandfathered validation.

## Regeneration

Static register-table samples:

```sh
python3 von/tools/extract_scsp_register_table.py \
  von/artifacts/epr-18670.31 \
  von/artifacts/mpr-18652.32 von/artifacts/mpr-18653.34 \
  -o von/captures/audio-recovery/register-table-tracks
```

Runtime descriptors and chronological events:

```sh
python3 von/tools/extract_runtime_scsp_tracks.py \
  /path/to/vonj-scsp-registers.log \
  von/artifacts/mpr-18652.32 von/artifacts/mpr-18653.34 \
  --min-time 16.0 \
  --output von/captures/audio-recovery/runtime-tracks-events
```

Provisional sequence render:

```sh
python3 von/tools/render_runtime_scsp_music.py \
  von/captures/audio-recovery/runtime-tracks-events/catalog.json \
  von/artifacts/mpr-18652.32 von/artifacts/mpr-18653.34 \
  --output /tmp/vonj-sequence.wav
```

## Evidence tiers

| Product | Required claim |
| --- | --- |
| MAME WAV | `reference-capture`, with isolated scenario and artifact hash. |
| Extracted sample | Descriptor-validated SA/LSA/LEA, format, rate, loop state, key-on event, and exact PCM/WAV hashes. |
| Reconstructed sequence | Ordered key events, pitch, loop, gain, pan, envelope, routing, and DSP behavior match; waveform comparison passes declared thresholds. |

Do not give a clip a semantic name based only on listening. Identity is a
separate claim from descriptor and byte validation.

## Next useful experiment

Recapture one small SCSP key-on under a canonical scenario. Package its event
excerpt, complete descriptor, extracted WAV, source hashes, and verifier as the
first audio evidence pack. Display that in `von-viewer` before attempting to
promote a complete song.

The full pack schema, cleanup policy, and viewer rollout are in
[Evidence and assets plan](evidence-and-assets-plan.md).

## i960 audio-queue command correlation (manual bout, 2026-09-07)

Run: `SDL_VIDEODRIVER=dummy bin/von vonj -playback manual-01.inp
-autoboot_script von/tools/replay_input_health.lua -seconds_to_run 260`
with `VON_IH_LOG`, `VON_IH_POS=1`, and a write tap over the queue header
plus ring (`VON_IH_WTAP_ADDR=0x51aa70`, `VON_IH_WTAP_END=0x51aabf`).
Log: `von/build/audio-queue/manual-02/input-audio.log` (14957 frames,
7593 queue writes, 2116 input/health lines; fresh NVRAM).

Protocol (new producer-side facts):

- Enqueue PC is always `0x2a4cc`; index commits from `0x2a4d4`;
  consumer acks trail in the same frame from PC `0x1720`, so commands
  take effect near-immediately. Queue init (fill `0x99`, one `0xff`)
  runs from `0x2a8b8`-`0x2a8c4` at f=271; `0x99` is the idle marker.
- Each datum byte is stored through a widening u16/u24/u32 idiom at
  the same slot, one index bump per store. Group stores per
  (frame, slot) and read the significant byte of each store.
- Vocabulary is an `AE`-prefixed family (`AE`, `AE 11`, `AE 11 XX`,
  `AE 12`, `AE 12 XX`) plus lone suffixes (`11 15`, `15`, `12 00`,
  `00`, `1f`, `21`, ...). The 68k `decode_sound_sequences.py`
  3-byte packet shape matches the 3-datum groups.

Stage structure of this run (teleports to spawn): S1 f=3178,
S2 f=8009, S3 f=12841 (~4830 frames each, inputs live throughout).

Findings (corrected and extended by the stage-5 bout,
`von/build/stage5-fleet/stage-trace.log`, FIGHT frames
4430/8073/10572/13983/16305/18879/21713/24277):

- FIGHT call, timing-exact one frame before every spawn, IDs ascend
  per stage: S1 `50`, S2 `51`, S3 `52`, S4 `53`, S5 `54`
  (`[AE,13,5x]`). Stages are single-round: no mid-attempt `50`
  round-starts appear in-playback.
- `[AE,13,3f]` and `[AE,13,41]` fire before EVERY stage (shared
  VS/intro jingles, ~110/~72 frames before spawn), NOT per-stage
  BGM as previously read. Only the third ID is per-stage BGM:
  S1 `4b`, S2 `4c`, S3 `4d`, S4 `4e`, S5 `4f`.
- Stage entry and death-continue both play the full intro cluster
  (stop `[AE,00,02]`, `3f`, `41`, per-stage BGM, `[AE,11,11]` radar
  blips x2, stage FIGHT call). A stage WIN first plays victory
  jingle `[AE,11,15]` plus stop pair `[AE,00,03]`+`[AE,00,02]`;
  continues skip the victory jingle.
- Bout map of the stage-5 run: S1, S2 win, S3 x4 attempts (3 death
  continues), S3 win, S4 win (2563f), S5 reached, recording ends
  mid-S5. Round-start posts (0,0,-60)/(0,0,+60) snap 3 frames
  after the FIGHT call with a ~130-frame control lock.
- Hit SFX are NOT isolated: no vocabulary item clusters within ±8
  frames of the 51 damage events above chance, and input proximity
  is at chance. Impact sounds likely enqueue at attack launch
  (frames before the health drop), so the next pass must correlate
  against button-bit presses with a launch-to-impact window, using
  `von/tools/map_input_bits.py` to isolate buttons from stick
  wiggles.

Open: name every ID through the 68k `$603dbc` high-nibble dispatch
(handler -> sequence/stream -> sample); confirm BGM-vs-jingle
assignment of the `[AE,13,XX]` IDs against SCSP key-ons.
