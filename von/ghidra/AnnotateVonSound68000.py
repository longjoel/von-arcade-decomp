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
         "Voice-start command handler; descriptor selection uses the table pointed to by 0x608004.")
function(0x602938, "audio_voice_pitch_from_command")
function(0x602bb8, "audio_voice_pan_command")
function(0x602c94, "audio_voice_level_command")

# Pointer cells and their resolved targets.  The cells are not themselves
# the tables: each contains a 68000 longword ROM address.
label(0x608004, "audio_voice_descriptor_table_ptr",
      "Pointer cell containing 0x60b5e0, the voice descriptor table base.")
label(0x60b5e0, "audio_voice_descriptor_table",
      "Resolved descriptor table; maximum observed descriptor ID is 0x41 (66 entries).")
label(0x608008, "audio_sequence_table_ptr",
      "Pointer cell containing 0x609da8, the sequence table base.")
label(0x609da8, "audio_sequence_table",
      "Resolved sequence table; maximum observed event ID is 1. Entries use 16-bit relative offsets.")
label(0x609dae, "audio_sequence_entry_00")
label(0x609de2, "audio_sequence_entry_01")

# Supporting tables referenced by the handlers.
label(0x601100, "audio_static_scsp_register_table",
      "Eight 16-byte SCSP register records. Resolved ranges are short PCM16 calibration/test tones, not music tracks.")
label(0x605be4, "audio_voice_sample_table",
      "Voice/sample lookup table used during voice setup; exact asset naming remains unresolved.")
label(0x604fb4, "audio_pitch_parameter_table")
label(0x605e24, "audio_pitch_table_index")
label(0x602d9e, "audio_tempo_lookup")
label(0x609e66, "audio_sequence_default_envelope")
label(0x609ee6, "audio_sequence_default_state")
