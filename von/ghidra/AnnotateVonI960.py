# Ghidra post-analysis annotations for the Virtual-On i960 host image.
#
# The ROM is imported as raw i960:LE:32:default. Keep these labels in source
# control instead of relying on a binary Ghidra project file.

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.address import AddressSet


def label(address, name, comment=None):
    addr = toAddr(address)
    symbol_table = currentProgram.getSymbolTable()
    existing = symbol_table.getPrimarySymbol(addr)
    if existing is None or existing.getSource() != SourceType.USER_DEFINED:
        symbol_table.createLabel(addr, name, SourceType.USER_DEFINED)
    if comment:
        listing = currentProgram.getListing()
        code_unit = listing.getCodeUnitAt(addr)
        if code_unit:
            code_unit.setComment(code_unit.PLATE_COMMENT, comment)


def ensure_function(address, name, end=None):
    """Seed code entry points the raw-binary analyzer cannot discover."""
    start = toAddr(address)
    function_manager = currentProgram.getFunctionManager()
    if end is not None:
        finish = toAddr(end - 1)
        overlapping = function_manager.getFunctionsOverlapping(AddressSet(start, finish))
        while overlapping.hasNext():
            other = overlapping.next()
            if other.getEntryPoint() != start:
                function_manager.removeFunction(other.getEntryPoint())
        currentProgram.getListing().clearCodeUnits(start, finish, False)
        current = start
        while current.getOffset() < end:
            instruction = currentProgram.getListing().getInstructionAt(current)
            if instruction is None:
                disassemble(current)
                instruction = currentProgram.getListing().getInstructionAt(current)
            if instruction is None:
                break
            current = instruction.getMaxAddress().next()
    else:
        currentProgram.getListing().clearCodeUnits(start, toAddr(address + 0x20), False)
        disassemble(start)
    function = function_manager.getFunctionAt(start)
    if function is None:
        function = createFunction(start, name)
    elif function.getName().startswith("FUN_"):
        function.setName(name, SourceType.USER_DEFINED)
    if function is not None and end is not None:
        function.setBody(AddressSet(start, toAddr(end - 1)))


# i960 reset/vector structure.
label(0x00000004, "prcb_base_candidate")
label(0x0000000c, "reset_entry", "Confirmed reset entry candidate.")
label(0x00000010, "reset_system_metadata")
label(0x000000b4, "prcb_field_0x0c")
label(0x000000c4, "prcb_table_candidate")
label(0x000000c8, "interrupt_stack_table_candidate")
label(0x00000930, "i960_reset_entry")
ensure_function(0x00000930, "i960_reset_entry", 0x000009e8)

# Confirmed host-code anchors.
label(0x00003c40, "ui_warning_table_walker")
label(0x0001cac8, "ui_text_state_helper")
label(0x0001cc40, "ui_tile_writer")
label(0x0001ccd0, "ui_string_walker")
label(0x000282e0, "sharc_bootstrap_upload")
label(0x00028600, "geometry_upload_message")
label(0x000284b0, "geometry_command_window_clear")
label(0x000284e8, "geometry_command_window_init")
label(0x00028470, "geometry_command_init_table")
label(0x00028de8, "geometry_frame_submission")
label(0x00028e88, "geometry_function_command_submit")
label(0x00028c00, "geometry_command_batch_submit")
label(0x00028c80, "geometry_command_batch_loop")
label(0x00028d80, "geometry_pipeline_startup")
label(0x00028b40, "geometry_float_conversion_helper")
label(0x00028b80, "geometry_buffer_prepare")
label(0x00028418, "geometry_initial_handshake")
label(0x00028d08, "geometry_register_clear")
label(0x00028548, "texture_initializer")
ensure_function(0x00003c40, "ui_warning_table_walker")
ensure_function(0x00028620, "geometry_program_upload", 0x00028758)
ensure_function(0x000284b0, "geometry_command_window_init", 0x00028538)
ensure_function(0x00028de8, "geometry_frame_submission", 0x00028e7c)
ensure_function(0x00028e88, "geometry_function_command_submit", 0x00028efc)
ensure_function(0x00028c00, "geometry_command_batch_submit", 0x00028cf4)
ensure_function(0x00028c80, "geometry_command_batch_loop", 0x00028cf4)
ensure_function(0x00028d80, "geometry_pipeline_startup", 0x00028ddc)
ensure_function(0x00028b40, "geometry_float_conversion_helper", 0x00028b7c)
ensure_function(0x00028b80, "geometry_buffer_prepare", 0x00028c00)
ensure_function(0x00028418, "geometry_initial_handshake", 0x00028464)
ensure_function(0x00028d08, "geometry_register_clear", 0x00028d24)
ensure_function(0x00028548, "texture_initializer", 0x000285f4)

# Static hardware/data references used by the annotated notes.
label(0x00028170, "texture_load_done_message")
label(0x0002812c, "texture_load_message")
label(0x0000c57a0, "result_node_id_format_string")

print("Virtual-On i960 annotations applied")
