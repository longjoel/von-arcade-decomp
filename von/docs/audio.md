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
