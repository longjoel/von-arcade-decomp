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
- `0x608004`: `audio_voice_descriptor_table_ptr`, a pointer cell resolving to
  the descriptor table at `0x60b5e0` (maximum descriptor ID `0x41`);
- `0x608008`: `audio_sequence_table_ptr`, a pointer cell resolving to the
  sequence table at `0x609da8` (maximum observed event ID `1`);
- `0x605e24`: `audio_pitch_table_index`;
- `0x602d9e`: `audio_tempo_lookup`.

The sequence table entries at `0x609dae` and `0x609de2` are 16-bit relative
offsets from `0x609da8`; `0x608008` is only the pointer cell and must not be
treated as the table base. `von/tools/analyze_sound_rom.py` emits the resolved
pointer/table information as JSON for the offline music-renderer work.

The normal command handlers consume three-byte packets (command plus two
payload bytes); `von/tools/decode_sound_sequences.py` exports those packets
for renderer development. The packet field meanings are still being mapped
to voice/sample selection and timing.

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
