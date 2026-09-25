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
first audio evidence pack. Display that in `von-data-tool` before attempting to
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
  VS/intro noises `SDE_new_noise2` and `SDE_frame_01`, ~110/~72
  frames before spawn), NOT per-stage BGM as previously read. The
  per-stage third ID (S1 `4b` … S5 `4f`) is the arena announce
  voice `SDE_new_voice5..9`, not BGM; the arena BGM is the
  `SDB_bgm_*` word carried in the same `0x195e0` record and sent at
  `0x1a45c` (see "Stage intro selection" below).
- Stage entry and death-continue both play the full intro cluster
  (stop `[AE,00,02]`, `3f`, `41`, per-stage announce voice,
  `[AE,11,11]` = `SDE_type_05` x2, stage FIGHT call). The
  `[AE,11,15]` observed at a stage win is `SDE_hit_13`, so it reads
  as the winning impact rather than a separate victory jingle; the
  catalogue also provides `SDB_win1`/`SDB_win2` (`0x1014`/`0x1015`)
  for the win shell.
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

Open: bind each named ID to the 68k `$603dbc` handler and then to a concrete
SCSP descriptor/sample. The i960 asset names are now resolved (see the next
section), so the remaining gap is 68k-side handler mapping, not vocabulary.
The 68000 program is now disassembled and the full
`i960 command ID -> 68000 sample/sequence` resolution is extracted in
`von/audio-command-map.json`; see [68000 sound program](audio-68000.md). The
static 16-byte sample descriptor table (347 records) is extracted in
`von/audio-sample-descriptors.json`, which binds a descriptor index to a
source pointer and byte length in the 8 MiB sample region and can dump PCM8
WAVs. The trigger conditions for the shared effect IDs (`SDE_hit_13`,
`SDE_bom_*`, `SDE_beam_*`) are decoded in
[68000 sound program](audio-68000.md#sound-effect-trigger-map-known-conditions):
impact fires from the effect-type dispatch tables `0xc4f40`/`0x41c50`, and
the explosion stages fire from the per-type lifetime countdown against
`0x3eca0`. The final `command -> clip` hop is also closed:
`ae HH LL -> packet OP SAMPLE -> effect track (0x39/0x3a/0x3b) -> descriptor
-> PCM range`, extracted with 0 unresolved in `von/audio-clip-map.json`.

## i960 action -> sound binding (static, 2026-09-18)

This pass connects the gameplay code that *chooses* a command to the host
producer, so the command IDs no longer float free of the game. It is static
evidence from `von/build/disasm/vonj-maincpu.lst`; nothing here is a claim
about which 68000 stream or sample a value selects.

Producer boundary (confirmed, see [symbols](../i960/symbols.md)):

- `0x2a4e0` frames a 16-bit value as `ae, high, low` (or a lone `ff`) into the
  64-byte ring at `0x51aa80`; `0x2a5f0` is the idle-gated sibling, and
  `0x2a580` is entered from the input/retry paths. `0x2a690`/`0x2a870` send
  `a0`-framed level/value pairs.
- The recovered framing and queue are in `recovered_audio_queue.c`.

### Per-fighter profile sounds (KNOWN)

The global profile pointer `0x51ab14` (initialized from `object+0x6c`) is the
per-roster config block. The roster table at `0x19360` holds ten profile
pointers; each stores eight 16-bit command words at `+0x488..+0x4a4`:

| offset | action | resolved name (profile 0) | confirmed call site(s) |
| --- | --- | --- | --- |
| `+0x488` / `+0x48c` | primary weapon fire | `SDE_tem_rifle` / `SDE_2_tem_rifle` | `0x34d9c` / `0x34dac` (guarded by `object+0x1ab`) |
| `+0x490` / `+0x494` | jump / air | `SDE_jump_01` / `SDE_2_jump_01` | `0x2fe6c`/`0x2fe74` (state 22), `0x31060`/`0x31068` (state 35), `0x3147c`/`0x31484` (state 37) |
| `+0x498` / `+0x4a0` | dash loop | `SDE_dash_01_loop` / `SDE_2_dash_01_loop` | `0x34300` / `0x34310` |
| `+0x49c` / `+0x4a4` | move-end / stop (unnamed) | `0x1123` / `0x1147` | `0x34354` / `0x34364`, reused from `0x4dc20..0x67c50` |

Every site is the same shape: `ld 0x51ab14 -> ld field -> mov g4,g0 ->
call 0x2a4e0`, with `object+0x68` choosing the second field of each pair
(zero takes the first). The second field is always the `SDE_2_*` variant of
the same action, so `object+0x68` selects the sound bank, not left/right.
The dash pair is a genuine `object+0x196` toggle: state 31 or 34 entering
sends `+0x498`/`+0x4a0`, leaving sends `+0x49c`/`+0x4a4`
(`0x342d4..0x34374`).

The extracted command words are reproduced in `recovered_audio_actions.c`
and locked by `von/tools/test_recovered_audio_actions.py`, which re-derives
them from the assembled original and cross-checks the resolved names when
present. Profile jump words: `0x1117/0x113b` (0,6), `0x1118/0x113c`
(1,3,5), `0x1119/0x113d` (2,4,7,8,9) — i.e. `SDE_jump_01/02/03`. Profile
weapon words: `0x1200/0x1228` (Temjin), `0x120a/0x1232` (Viper),
`0x120d/0x1235` (Belgdor), `0x1206/0x122e` (Raiden), `0x1216/0x123e`
(Dorkas), `0x121d/0x121d` (Fei-Yen), `0x1211/0x1239` (Apharmd),
`0x1218/0x1240` (Bal-Bas-Bow), `0x1220/0x1220` (Jagrandi).

### Sound-ID -> asset names (KNOWN)

The i960 image carries packed records of a 16-bit command word followed by a
NUL-terminated ASCII asset name. Extracting them names essentially the entire
host vocabulary (287 distinct commands): `SDE_*` effects/voices and `SDB_*`
shell music/announcements. Run:

```sh
python3 von/tools/extract_sound_id_names.py -o von/sound-id-names.json
```

The committed `von/sound-id-names.json` and
`von/tools/test_sound_id_names.py` pin the map and re-derive it from the
assembled image when present. Resolved families:

- `0x10xx` — 68000 shell/BGM (`SDB_*`): `0x1000` `SDB_continue`, `0x1001`–
  `0x1019` `SDB_bgm_01..14`, `0x100b` `SDB_select1`, `0x100d` `SDB_start1`,
  `0x1011`–`0x1015` `SDB_lose1..3`/`SDB_win1..2`, `0x101a` `SDB_title`,
  `0x101b` `SDB_demo`, `0x101e`–`0x1022` `SDB_end*`/`SDB_comp*`.
- `0x11xx` — effects and announcer voices (`SDE_*`): `0x1101`–`0x1106`
  `SDE_bom_*`, `0x1107`/`0x1108` `SDE_dash_*_loop`, `0x1112`–`0x1116`
  `SDE_hit_*`, `0x1117`–`0x111a` `SDE_jump_*`, `0x111b`/`0x111c`
  `SDE_fse_*`, `0x1120`/`0x1121` `SDE_bom_new*`, and the second bank
  `0x1125`–`0x1150` (`SDE_2_*`). `0x1152`–`0x115a` are the Zigrad
  locomotion set (`SDE_zig_*`).
- `0x12xx` — per-mech weapon/attack SFX, mirroring the profile weapon
  fields: `SDE_tem_rifle`, `SDE_rai_baz`, `SDE_vip_gun`, `SDE_bel_gun`,
  `SDE_aph_shotgun`, `SDE_dor_phalanx_shoot`, `SDE_bbb_r_laser`,
  `SDE_fei_handbeam`, `SDE_jag_bazooka`, plus `SDE_2_*` duplicates.
- `0x13xx` — announcements/voices/music shell: `0x1300`–`0x1337`
  `SDE_round_01..10` and `SDE_voice_*`, the mech-name calls `0x132a`
  `SDE_apharmd` … `0x1333` `SDE_zigrad`, `0x133a`–`0x133d`
  `SDE_presented_by_SEGA`, `0x133e`/`0x133f` `SDE_new_noise*`, `0x1343`–
  `0x135e` `SDE_new_voice*`, `0x1361`/`0x1362` `SDE_super_bang_*`, and
  `0x1363`–`0x1366` `SDE_click_0..3`.

### Per-mech move-script SFX (KNOWN)

The fixed `0x12xx` words selected in the `0x4b264..0x67c50` clusters and
stored to `object+0x1fc` resolve to per-mech weapon/move effects, which makes
those clusters the move-script families:

| command | name | owner |
| --- | --- | --- |
| `0x1200`/`0x1228` | `SDE_(2_)tem_rifle` | Temjin |
| `0x1229`/`0x122a`/`0x122b`/`0x122c` | `SDE_2_tem_sword_on/hit/cut/off` | Temjin sword |
| `0x1208`/`0x1230`/`0x1231` | `SDE_(2_)vip_sevenway`/`SDE_2_vip_homing` | Viper |
| `0x1206`/`0x122e`/`0x122f` | `SDE_(2_)rai_baz`/`SDE_2_rai_leaser` | Raiden |
| `0x120d`/`0x1235` | `SDE_(2_)bel_gun`, `0x1233`/`0x1234` `SDE_2_bel_napalm`/`missile` | Belgdor |
| `0x120f`/`0x1236`/`0x1237` | `SDE_2_aph_ton_on/shake` | Apharmd |
| `0x1216`/`0x123c`/`0x123d`/`0x123e` | `SDE_(2_)dor_phalanx_shoot`, `SDE_2_dor_hammer_*` | Dorkas |
| `0x1218`/`0x1240`/`0x1241`/`0x1244` | `SDE_(2_)bbb_r_laser`, `SDE_2_bbb_h_bit_on`, `SDE_2_bbb_fireball` | Bal-Bas-Bow |
| `0x121d`/`0x1245`/`0x1246`/`0x1247` | `SDE_(2_)fei_handbeam`/`bowgun`/`lovebeam` | Fei-Yen |
| `0x1220`/`0x1221`/`0x1222`/`0x1248`–`0x124a` | `SDE_(2_)jag_*` | Jagrandi |

### Stage intro selection (KNOWN)

Slot 7 (`0x19830`) selects an arena by index: it stores the index at
`0x5770f0` and copies the 8-byte record at `0x195e0[index*8]` to `0x504cc0`.
The record is `{u16 bgm, u16 pad, u16 announce, u16 pad}`. Mode 4 then sends:

- the arena BGM word (`0x504cc0` low half) at `0x1a45c`–`0x1a474`;
- the fight announce word (`0x195e4[index*8]`) at `0x1a190`/`0x1a1cc`;
- a `SDE_round_NN` announcement from `0x19480[round]` at `0x1a178`/`0x1a1b4`.

A parallel 4-byte record table at `0x21180` holds `{intro voice, fight
announce}` for the same selectors; the status screen loads its low half at
`0x21d78` (or fixes `0x1322` when `0x503a7c == 0`). Its high half matches the
fight announce of the `0x195e0` records for all ten selectors.

Selector→records (from `von/sound-id-names.json`):

| selector | BGM (`0x195e0`) | fight (`0x195e0`/`0x21180`) | intro voice (`0x21180`) |
| ---: | --- | --- | --- |
| 0 | `SDB_bgm_10` | `SDE_new_voice11` | `SDE_new_voice6` |
| 1 | `SDB_bgm_06` | `SDE_new_voice18` | `SDE_new_voice3` |
| 2 | `SDB_bgm_09` | `SDE_new_voice12` | `SDE_new_voice7` |
| 3 | `SDB_bgm_01` | `SDE_new_voice13` | `SDE_new_voice8` |
| 4 | `SDB_bgm_11` | `SDE_new_voice14` | `SDE_new_voice9` |
| 5 | `SDB_bgm_12` | `SDE_new_voice16` | `SDE_new_voice1` |
| 6 | `SDB_bgm_14` | `SDE_new_voice17` | `SDE_new_voice2` |
| 7 | `SDB_bgm_08` | `SDE_new_voice10` | `SDE_new_voice5` |
| 8 | `SDB_bgm_13` | `SDE_new_voice19` | `SDE_new_voice4` |
| 9 | `SDB_bgm_04` | `SDE_new_voice15` | `SDE_penalty_stage` |

All ten BGM words are now rendered offline and staged as
`music_arena00..09.wav` (selector → file; see `audio-68000.md` and
`export_audio_manifest.py` `BGM_FILES`).

This corrects the earlier reading of the runtime tap. The observed per-stage
`AE 13 4b/4c/4d/4e/4f` are the `0x21180` intro voices for selectors
7/0/2/3/4 = `SDE_new_voice5/6/7/8/9`, not BGM; the observed `AE 13 5x` are
the fight announces for those selectors. The arena BGM is the `SDB_bgm_*`
word in the `0x195e0` records, sent at `0x1a45c`. The per-stage goldens
remain in `recovered_audio_stage_script.c`.

### `object+0x1fc` current-command field (LIKELY)

Many action paths store the chosen word to `object+0x1fc` immediately before
sending it. The object initializer `0x27350..0x273a0` copies profile `+0xe6`
to `object+0x1fa` and `+0xe8` to `object+0x1fc`, and replays `+0x1fc` through
`0x2a4e0` when it changes and `object+0x2 == 1`. Treat `+0x1fc` as the
object's last/pending command word, useful as a tap point when correlating
runtime audio to an object.
