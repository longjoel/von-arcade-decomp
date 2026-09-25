# Ghidra i960 Analysis

The local Ghidra 11.3.1 installation does not ship with an i960 processor
definition. Install the pinned Apache-licensed community module with:

```sh
GHIDRA_HOME=/path/to/ghidra_11.3.1_PUBLIC ./scripts/install-ghidra-i960.sh
```

Then import and analyze the reconstructed `vonj` host ROM with:

```sh
GHIDRA_HOME=/path/to/ghidra_11.3.1_PUBLIC ./scripts/ghidra-i960.sh
```

The script reconstructs `von/build/disasm/vonj-maincpu.bin`, imports it as
`i960:LE:32:default`, runs normal Ghidra analysis, and applies the labels in
`AnnotateVonI960.py`. It then writes a focused reset/UI/geometry report using
`ReportVonI960.py`. The Ghidra project and report are generated under the
ignored `von/build/ghidra/` directory and should not be committed.

The processor module is an external dependency. Keep the pinned revision and
the import/annotation scripts under version control; do not copy the generated
Ghidra database into the repository.

## Audio and SFX annotations

`AnnotateVonI960.py` labels the host-side SCSP boundary: the 64-byte FIFO,
producer framing, service request, interrupt consumer, SCSP command/status ports,
and the recovered initialization and level/selector helpers. These annotations
describe confirmed host behavior; they do not assign names to sound effects or
music that have not yet been recovered from the separate 68000 sound ROM.

The sound ROM uses SCSP voice descriptors. A descriptor must be decoded before
assigning an asset name or length: `SA`, `LSA`, `LEA`, PCM8/PCM16 (`PCM8B`), loop
mode, and pitch (`OCT`/`FNS`). The ROM-only Python catalog therefore marks
silence-gap results as heuristic candidates and keeps SFX/music naming
unresolved until those descriptors and sequencer tables are identified.

The separate 68000 sound program is statically labeled by
`AnnotateVonSound68000.py`. Import the word-swapped sound ROM as a raw
68000 big-endian image at CPU address `0x600000`, run normal analysis, and
then run that script. The confirmed code entry points include:

- `0x6047a4`: `audio_sequence_tick`, the event-stream dispatcher;
- `0x603dbc`: `audio_command_stream_decode`, the variable-length command
  decoder that feeds the SCSP FIFO;
- `0x601a20`: `audio_command_fifo_tick`, the timed command-consumer path;
- `0x604a20`: `audio_sequence_tempo_command`;
- `0x604ad0`: `audio_sequence_select_stream`;
- `0x6027f0`: `audio_voice_start_from_command`;
- `0x602938`: `audio_voice_pitch_from_command`;
- `0x602bb8`: `audio_voice_pan_command`;
- `0x602c94`: `audio_voice_level_command`;
- `0x602146`: `audio_sample_upload`, the lazy component that copies a
  descriptor's ROM range into SCSP sound RAM and keys the slot;
- `0x601af8`: `audio_sample_trigger_command`, the nibble-9 sample handler;
- `0x6034b8`: `audio_host_command_resolve`, the `ae HH LL` resolver;
- `0x605e24`: `audio_pitch_table_index`;
- `0x602d9e`: `audio_tempo_lookup`.

### Sound ROM table map (corrected 2026-09-18)

The pointer block at `0x608000` resolves the driver's tables. Earlier notes
swapped the roles of `0x60b5e0` and `0x609da8`; the current reading is:

| pointer cell | target | role |
| --- | --- | --- |
| `0x608000` | `0x60a010` | sample descriptor table: `u16` size then 16-byte records at `0x60a012` (`{src, len-1, end, loop}`, 347 records); copied to RAM `0x5000` |
| `0x608004` | `0x60b5e0` | sequence/track table: `u16` count (65) then relative offsets to `[lo,hi]` + 12-byte-entry range tables; copied to RAM `0x9000` |
| `0x608008` | `0x609da8` | 16-entry voice/sample assignment table, selected by the header at base-`0x10`; built into RAM `0x1600` |
| `0x60800c` | `0x6080e2` | init/mode script emitting `a0 NN` ring setup commands |
| `0x608010` | `0x608080` | effect-channel records (six 16-byte records; `+1` = command low nibble, `+2` = track) |
| `0x608018` | `0x609884` | SCSP DSP microprogram copied to `0x100700` |
| `0x60801c` | `0x60ca1a` | two-level host command table indexed by `ae HH LL` |
| `0x608020` | `0x60b5c2` | eager sample-upload index list (terminated on this ROM) |
| `0x608028` | `0x60d966` | byte-indexed effect parameter table |

`von/tools/analyze_sound_rom.py` resolves the sequence table from `0x8004`
(not `0x8008`) and emits it as JSON; `von/tools/extract_audio_command_map.py`
resolves the `ae HH LL` command table; `von/tools/extract_audio_sample_table.py`
resolves the descriptor table.

### Command -> clip chain (resolved)

- `0x6034b8` indexes `[0x60801c]` by `HH` then `LL`; `control == 0x00` gives a
  sequence pointer, `control & 0x80` queues the inline stream at `A2+1`.
- The inline packet is `OP SAMPLE PARAM` (`0x9a`/`0x9b`/`0x9c`). The low nibble
  of `OP` selects an effect-channel record (`0x608080`); `+2` is the track.
- `0x601af8` searches that track's `[lo,hi]` range table for `SAMPLE`; the
  entry's first word is the descriptor index.
- `0x602146` uploads the descriptor's PCM range from the sample region.

The join is extracted as `von/audio-clip-map.json`
(`extract_audio_clip_map.py`, `test_audio_clip_map.py`): 275 commands with
0 unresolved, e.g. `0x1115 SDE_hit_13 -> descriptor 0xb5 -> 0x468b84, 37381
bytes`. `--extract DIR` writes a PCM8 WAV per command.

The normal command handlers consume three-byte packets (command plus two
payload bytes); `von/tools/decode_sound_sequences.py` exports those packets
for renderer development.

Existing MAME logs can preserve part of that evidence without another run:
`von/tools/extract_scsp_midi_trace.py` extracts timestamped three-byte MIDI
packets. The 30-second original-title trace includes the level-select music
commands, but does not include the later SCSP `SA`/`LSA`/`LEA` writes needed to
assign exact sample ranges.

The runtime register trace closes that gap. `von/tools/extract_runtime_scsp_tracks.py`
consumes `vonj_scsp_reg` records from a level-select-to-match run and emits
authoritative, exact-length WAVs plus their slot, timestamp, format, pitch, and
ROM range in `catalog.json`. The current capture produced 213 true key-on
descriptors and 32 unique sample ranges.

`von/tools/extract_scsp_register_table.py` extracts the initial static SCSP
register table at sound-ROM offset `0x1100`. Its first eight valid records
resolve to exact, very short PCM16 ranges at sample offsets `0x500` through
`0xc00`; listening confirms these are calibration/test tones, not music.
