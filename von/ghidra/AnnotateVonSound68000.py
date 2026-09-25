# Ghidra Jython annotations for the Virtual-On sound 68000 ROM.
#
# Import the raw, word-swapped sound ROM as 68000 big-endian at 0x600000
# before running this script.  Addresses below are CPU addresses, not file
# offsets.  Names describe observed behavior and table roles; unresolved
# sample/music semantics are deliberately left unresolved.

from ghidra.program.model.symbol import SourceType


def label(address, name, comment=None):
    addr = toAddr(address)
    symbols = currentProgram.getSymbolTable()
    existing = symbols.getPrimarySymbol(addr)
    if existing is None or existing.getSource() != SourceType.USER_DEFINED:
        symbols.createLabel(addr, name, SourceType.USER_DEFINED)
    if comment:
        unit = currentProgram.getListing().getCodeUnitAt(addr)
        if unit:
            unit.setComment(unit.PLATE_COMMENT, comment)


def function(address, name, comment=None):
    label(address, name, comment)
    entry = toAddr(address)
    if currentProgram.getFunctionManager().getFunctionAt(entry) is None:
        disassemble(entry)
        createFunction(entry, name)


# Confirmed sound-CPU code paths.
function(0x603dbc, "audio_command_stream_decode",
         "Decodes the sound event stream and emits normal commands as three-byte packets.")
function(0x601a20, "audio_command_fifo_tick",
         "Timed FIFO consumer; dispatches command high nibbles to voice, pitch, pan, and level handlers.")
function(0x6047a4, "audio_sequence_tick",
         "Event-stream dispatcher/tick path.")
function(0x604a20, "audio_sequence_tempo_command")
function(0x604ad0, "audio_sequence_select_stream")
function(0x6027f0, "audio_voice_start_from_command",
         "Voice-start handler; indexes the relocated sequence/track table (from 0x608004) by the track field.")
function(0x602938, "audio_voice_pitch_from_command")
function(0x602146, "audio_sample_upload",
         "Lazy sample loader: copies the descriptor's ROM range into SCSP sound RAM and keys the slot.")
function(0x601af8, "audio_sample_trigger_command",
         "Nibble-9 handler: searches the track's [lo,hi] range table for the sample index and selects a descriptor.")
function(0x6034b8, "audio_host_command_resolve",
         "Host `ae HH LL` resolver; indexes the two-level command table at [0x60801c] by HH then LL.")
function(0x6035a0, "audio_voice_one_shot",
         "Control-0x80 path: queues the inline sample stream on a free voice slot.")
function(0x6015dc, "audio_table_init",
         "Copies the descriptor table to RAM 0x5000 and walks the eager-upload list at [0x608020].")
function(0x602bb8, "audio_voice_pan_command")
function(0x602c94, "audio_voice_level_command")

# Pointer cells and their resolved targets.  The cells are not themselves
# the tables: each contains a 68000 longword ROM address.  Corrected table
# roles (2026-09-18): 0x60b5e0 is the sequence/track table, not the descriptor
# table; the descriptor table is at 0x60a012 via [0x608000].
label(0x608004, "audio_sequence_table_ptr",
      "Pointer cell containing 0x60b5e0, the sequence/track table base (65 tracks, copied to RAM 0x9000).")
label(0x60b5e0, "audio_sequence_table",
      "Sequence/track table: u16 count, then per-track relative offsets to [lo,hi]+12-byte-entry range tables.")
label(0x60801c, "audio_host_command_table_ptr",
      "Pointer cell containing 0x60ca1a, the two-level host command table (HH then LL).")
label(0x60ca1a, "audio_host_command_table",
      "Per-`ae HH LL` records: control 0 selects a sequence pointer, control 0x80 queues an inline sample stream.")
label(0x608000, "audio_sample_descriptor_table_ptr",
      "Pointer cell containing 0x60a010; u16 size then 16-byte descriptor records at 0x60a012.")
label(0x60a012, "audio_sample_descriptor_table",
      "347 descriptors: {u32 rom source, u32 length-1, u32 end, u32 loop flag}; copied to RAM 0x5000.")
label(0x608008, "audio_voice_assignment_table_ptr",
      "Pointer cell containing 0x609da8, the 16-entry voice/sample assignment table (built into RAM 0x1600).")
label(0x609da8, "audio_voice_assignment_table",
      "16 entries selected by the 16-byte header at base-0x10; assigns voice/sample slots.")
label(0x608020, "audio_sample_upload_index_ptr",
      "Pointer cell containing 0x60b5c2, the eager sample-upload index list (terminated immediately on this ROM).")
label(0x608080, "audio_effect_channel_records",
      "Six 16-byte records for the sample banks: +1 = command low nibble, +2 = sequence/track index.")
label(0x6080e2, "audio_init_mode_script",
      "Init script bytes that emit `a0 NN` ring setup commands and channel-record templates.")
label(0x608028, "audio_byte_index_table_ptr",
      "Pointer cell containing 0x60d966, a byte-indexed effect parameter table.")

# Supporting tables referenced by the handlers.
label(0x601100, "audio_static_scsp_register_table",
      "Eight 16-byte SCSP register records. Resolved ranges are short PCM16 calibration/test tones, not music tracks.")
label(0x605be4, "audio_voice_sample_table",
      "128-byte per-voice field table used during voice setup; exact asset naming remains unresolved.")
label(0x604fb4, "audio_pitch_parameter_table")
label(0x605e24, "audio_pitch_table_index")
label(0x602d9e, "audio_tempo_lookup")
