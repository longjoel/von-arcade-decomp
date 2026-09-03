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

# Reset's register-stack handoff.  The call at 0xa0c enters this helper;
# execution returns to 0xa10, which establishes the runtime frame and calls
# the first main-data startup routine at 0x186f0.
label(0x00000a30, "_start_ip",
      "Reset register-cache setup: flush registers, mark PFP, and establish the first spill frame.")
ensure_function(0x00000a30, "_start_ip", 0x00000a58)
label(0x000009f0, "reset_startup_continuation",
      "Continuation after _start_ip returns; establishes the runtime frame before entering startup_main_data_entry.")
label(0x00000a10, "reset_runtime_frame_setup")
label(0x000186f0, "startup_main_data_entry",
      "First post-register-stack startup call reached from reset continuation at 0xa28.")
ensure_function(0x000186f0, "startup_main_data_entry", 0x00018904)
label(0x00018680, "startup_mode_dispatch_table",
      "Indirect startup dispatch table indexed by low nibble of 0x5039f4.")
label(0x00018684, "startup_mode_arm_1")
label(0x00018688, "startup_mode_arm_2")
label(0x0001868c, "startup_mode_arm_3")
label(0x00018690, "startup_mode_arm_4")
label(0x00018694, "startup_mode_arm_5")
label(0x00018698, "startup_mode_arm_6")
label(0x0001869c, "startup_mode_arm_7")
label(0x000186a0, "startup_mode_arm_8")
label(0x000186a4, "startup_mode_arm_9_null")
label(0x000186a8, "startup_mode_arm_10_null")
label(0x000186ac, "startup_mode_arm_11_null")
label(0x000186b0, "startup_mode_arm_12_null")
label(0x000186b4, "startup_mode_arm_13_null")
label(0x000186b8, "startup_mode_arm_14_null")
label(0x000186bc, "startup_mode_arm_15")
label(0x000186c0, "startup_pre_dispatch_helper")
label(0x00018a10, "startup_video_or_device_helper")
label(0x00018ab0, "startup_state_service")
label(0x00018538, "startup_status_service")
label(0x000294b0, "startup_warning_or_text_service")
label(0x000f50a8, "startup_input_formatter")
label(0x000188a0, "startup_device_write_loop")

# RAM and memory-mapped locations touched by the reset/startup slice.
# Names intentionally describe observed use, not guessed hardware ownership.
label(0x005039f0, "startup_state_flag_5039f0")
label(0x005039f4, "startup_mode_state")
label(0x005039f8, "startup_state_5039f8")
label(0x00503a00, "startup_service_counter")
label(0x00503a04, "startup_state_503a04")
label(0x00503a08, "startup_hardware_mode")
label(0x00503a0c, "startup_saved_state_503a0c")
label(0x00503a10, "startup_saved_state_503a10")
label(0x00503a20, "startup_state_503a20")
label(0x00503ab4, "startup_delay_100")
label(0x00503ab8, "startup_delay_600")
label(0x00503b48, "startup_saved_video_base")
label(0x00504c80, "startup_service_result")
label(0x00504c84, "startup_initialized_flag")
label(0x00504c88, "startup_mode_latch")
label(0x00504c94, "startup_pending_count")
label(0x00504c98, "startup_retry_count")
label(0x00504d10, "startup_initial_state_ffffffff")
label(0x005024b4, "startup_input_status_word")
label(0x00502490, "input_history_bytes")
label(0x00502498, "input_port_d_latch")
label(0x0050249c, "input_active_low_status")
label(0x005024a0, "input_state_work_a0")
label(0x005024a4, "input_state_work_a4")
label(0x005024a8, "input_state_work_a8")
label(0x005024ac, "input_state_work_ac")
label(0x005024b0, "input_state_work_b0")
label(0x005024b8, "input_state_work_b8")
label(0x005024bc, "input_state_work_bc")
label(0x005024f4, "startup_input_state_word")
label(0x005023f0, "startup_input_status_byte")
label(0x005770b0, "startup_device_command")
label(0x005770b1, "startup_device_mode")
label(0x005770c0, "startup_device_command_buffer")
label(0x008000f0, "startup_device_register_8000f0")
label(0x00884000, "startup_device_register_884000")
label(0x01400000, "startup_device_register_1400000")
label(0x01d00028, "startup_hardware_status_byte")
label(0x01d0020c, "startup_timing_limit_low")
label(0x01d00210, "startup_timing_limit_high")

# Trace-promoted early I/O and validation helpers.
label(0x00002040, "rom_signature_compare")
label(0x0001ef70, "text_status_region_initialize")
label(0x0001f0d0, "text_status_context_render")
label(0x00002080, "rom_signature_crc_check")
label(0x000022f0, "indexed_device_register_write")
label(0x00002330, "device_timing_register_setup")
label(0x00002440, "io_self_test_wrapper")
label(0x00002850, "controller_command_upload")
label(0x00002990, "controller_indexed_command_upload")
label(0x00002c70, "input_initializer_select")
label(0x00002cb0, "failure_input_sampler_select")
label(0x00002d60, "input_sampler_select")
label(0x00002da0, "input_controller_sample_and_pack",
      "Per-frame 315-5649 sample: averages the eight-byte history at 0x502490, reads controller ports, and packs the active-low state into 0x502498-0x5024bc.")
label(0x000034c0, "input_state_reset_fields")
label(0x00003540, "input_state_bit_update")
label(0x00003a38, "input_byte_state_parser")
label(0x00003ae0, "input_dual_byte_parser")
label(0x00003ba0, "controller_timing_status_check")
label(0x000183b8, "device_address_classify")
label(0x00018438, "device_mode_pair_validate")
label(0x00018488, "host_byte_queue_initialize")
label(0x0001c2c0, "text_video_transfer_wrapper")
label(0x0001cbb8, "text_control_character_handler")
label(0x0001d090, "text_special_glyph_writer")
label(0x0001d1d0, "text_alternate_string_walker")
label(0x0001d210, "text_special_glyph_string_walker")
label(0x0001d570, "text_glyph_block_writer")
label(0x0001d880, "text_glyph_table_match_writer")
label(0x0001dc10, "text_tile_plane_writer")
label(0x0001dc90, "text_attributed_tile_plane_writer")
label(0x0001dd10, "text_patterned_tile_plane_writer")
label(0x0001df00, "text_tile_region_clear")
label(0x0001df70, "text_plane_region_clear")
label(0x0001e030, "text_status_render_context")
label(0x00029a80, "audio_device_table_clear")
label(0x00029ae8, "audio_service_table_reset")
label(0x00029b20, "audio_device_table_upload")
label(0x00029c08, "audio_command_value_clamp")
label(0x00029ca0, "audio_device_buffer_copy")
label(0x000292d8, "geometry_command_stream_upload")
label(0x000295d0, "geometry_profile_upload_variant")
label(0x000296d0, "geometry_service_state_initialize")
label(0x00029738, "geometry_pointer_table_initialize")
label(0x00029778, "geometry_pointer_table_initialize_alt")
label(0x00029d50, "geometry_tile_buffer_transform")
label(0x0002b430, "geometry_object_record_dispatch",
      "Match capture confirms repeated polygon-ROM object submission through the 0x00800101 command class; this routine indexes the 0x51c5b0 record table, dispatches each record, and increments its per-slot count. In the verified post-start window, all 109 observed OBAs retain one stable tpa/tha pair; this supports a stable submission tuple without assigning semantic model names.")
label(0x0002be30, "geometry_frame_service_initialize",
      "Post-start original-ROM capture reaches this frame-service path before sustained match geometry; initialization emits the 8/16 FIFO prefix and dispatches the twelve frame-service arms.")
label(0x0002d9a0, "geometry_transform_dispatch")
label(0x0002e1c8, "geometry_status_render_route")
label(0x0002e1e8, "geometry_status_render_route_alt")
label(0x00027550, "geometry_record_transform_service",
      "Runtime match geometry uses the associated object-record path; this service stores the record transform fields before calling the 0x6f600 geometry producer.")
ensure_function(0x00027550, "geometry_record_transform_service", 0x00027c50)
label(0x000281f0, "texture_profile_dispatch_table")
label(0x000284b8, "geometry_command_window_clear_route")

# Fine-grained startup control-flow anchors.  These are instruction-site
# labels for the first 100 instructions after startup_main_data_entry; they
# make branch/call navigation stable while semantic names are recovered.
label(0x0001870c, "startup_clear_state_block",
      "Clears the startup state/counters after the one-count stack-frame delay loop.")
label(0x00018710, "startup_site_18710")
label(0x00018714, "startup_site_18714")
label(0x00018718, "startup_site_18718")
label(0x0001871c, "startup_site_1871c")
label(0x00018720, "startup_site_18720")
label(0x00018724, "startup_reset_service_state")
label(0x00018728, "startup_site_18728")
label(0x0001872c, "startup_site_1872c")
label(0x00018730, "startup_site_18730")
label(0x00018734, "startup_site_18734")
label(0x00018738, "startup_site_18738")
label(0x0001873c, "startup_site_1873c")
label(0x00018740, "startup_site_18740")
label(0x00018744, "startup_site_18744")
label(0x00018748, "startup_site_18748")
label(0x0001874c, "startup_site_1874c")
label(0x00018750, "startup_site_18750")
label(0x00018754, "startup_site_18754")
label(0x00018758, "startup_site_18758")
label(0x0001875c, "startup_site_1875c")
label(0x00018760, "startup_site_18760")
label(0x00018764, "startup_site_18764")
label(0x00018768, "startup_site_18768")
label(0x0001876c, "startup_site_1876c")
label(0x00018770, "startup_site_18770")
label(0x00018774, "startup_site_18774")
label(0x00018778, "startup_site_18778")
label(0x0001877c, "startup_site_1877c")
label(0x00018780, "startup_site_18780")
label(0x00018784, "startup_call_controller_init")
label(0x00018788, "startup_call_system_setup")
label(0x0001878c, "startup_call_hardware_mode_check")
label(0x00018790, "startup_site_18790")
label(0x00018794, "startup_site_18794")
label(0x00018798, "startup_site_18798")
label(0x0001879c, "startup_site_1879c")
label(0x000187a0, "startup_site_187a0")
label(0x000187a4, "startup_site_187a4")
label(0x000187a8, "startup_site_187a8")
label(0x000187ac, "startup_site_187ac")
label(0x000187b0, "startup_site_187b0")
label(0x000187b4, "startup_site_187b4")
label(0x000187b8, "startup_site_187b8")
label(0x000187bc, "startup_site_187bc")
label(0x000187c0, "startup_call_frame_service")
label(0x000187c4, "startup_site_187c4")
label(0x000187c8, "startup_site_187c8")
label(0x000187cc, "startup_site_187cc")
label(0x000187d0, "startup_site_187d0")
label(0x000187d4, "startup_site_187d4")
label(0x000187d8, "startup_site_187d8")
label(0x000187dc, "startup_site_187dc")
label(0x000187e0, "startup_call_input_formatter")
label(0x000187e4, "startup_service_iteration")
label(0x000187e8, "startup_call_status_service")
label(0x000187ec, "startup_site_187ec")
label(0x000187f0, "startup_site_187f0")
label(0x000187f4, "startup_site_187f4")
label(0x000187f8, "startup_site_187f8")
label(0x000187fc, "startup_site_187fc")
label(0x00018800, "startup_call_warning_service")
label(0x00018804, "startup_site_18804")
label(0x00018808, "startup_dispatch_mode_arm")
label(0x0001880c, "startup_site_1880c")
label(0x00018810, "startup_site_18810")
label(0x00018814, "startup_site_18814")
label(0x00018818, "startup_site_18818")
label(0x0001881c, "startup_site_1881c")
label(0x00018820, "startup_site_18820")
label(0x00018824, "startup_site_18824")
label(0x00018828, "startup_site_18828")
label(0x0001882c, "startup_site_1882c")
label(0x00018830, "startup_site_18830")
label(0x00018834, "startup_invalid_mode_recovery")
label(0x00018838, "startup_site_18838")
label(0x0001883c, "startup_site_1883c")
label(0x00018840, "startup_site_18840")
label(0x00018844, "startup_site_18844")
label(0x00018848, "startup_device_gate")
label(0x0001884c, "startup_site_1884c")
label(0x00018850, "startup_site_18850")
label(0x00018854, "startup_site_18854")
label(0x00018858, "startup_site_18858")
label(0x0001885c, "startup_site_1885c")
label(0x00018860, "startup_site_18860")
label(0x00018864, "startup_site_18864")
label(0x00018868, "startup_site_18868")
label(0x0001886c, "startup_capture_pending_state")
label(0x00018870, "startup_site_18870")
label(0x00018874, "startup_site_18874")
label(0x00018878, "startup_site_18878")
label(0x0001887c, "startup_site_1887c")
label(0x00018880, "startup_site_18880")
label(0x00018884, "startup_site_18884")
label(0x00018888, "startup_site_18888")
label(0x0001888c, "startup_site_1888c")
label(0x00018890, "startup_site_18890")
label(0x00018894, "startup_site_18894")
label(0x00018898, "startup_device_wait_or_retry")

# Startup mode handlers.  The low-nibble table above is data, so these
# entries are explicitly seeded as functions rather than left as indirect
# call targets for Ghidra's analyzer to guess.
label(0x00003c40, "startup_mode_handler_0")
label(0x0002b9e0, "startup_mode_handler_1_status_dispatch",
      "Checks hardware/status mode, updates the startup counter, then dispatches a 32-entry service table.")
label(0x00018650, "startup_mode_handler_2")
label(0x000190d0, "startup_mode_handler_3")
label(0x00019180, "startup_mode_handler_4")
label(0x000f3f00, "startup_mode_handler_5")
label(0x000f3fe0, "startup_mode_handler_6")
label(0x000f3d30, "startup_mode_handler_7")
label(0x00018620, "startup_mode_handler_8_and_15")
ensure_function(0x00003c40, "startup_mode_handler_0", 0x00003d64)
ensure_function(0x0002b9e0, "startup_mode_handler_1_status_dispatch", 0x0002bb5c)
ensure_function(0x00018620, "startup_mode_handler_8_and_15", 0x00018648)
ensure_function(0x00018650, "startup_mode_handler_2", 0x00018678)
ensure_function(0x000f3f00, "startup_mode_handler_5", 0x000f3fbc)

# Second-level status/service dispatch table selected by the low five bits of
# 0x503a00 from startup_mode_handler_1_status_dispatch.
label(0x0002b960, "startup_status_dispatch_arm_0")
label(0x0002b964, "startup_status_dispatch_arm_1")
label(0x0002b968, "startup_status_dispatch_arm_2")
label(0x0002b96c, "startup_status_dispatch_arm_3")
label(0x0002b970, "startup_status_dispatch_arm_4")
label(0x0002b974, "startup_status_dispatch_arm_5")
label(0x0002b978, "startup_status_dispatch_arm_6")
label(0x0002b97c, "startup_status_dispatch_arm_7")
label(0x0002b980, "startup_status_dispatch_arm_8")
label(0x0002b984, "startup_status_dispatch_arm_9")
label(0x0002b988, "startup_status_dispatch_arm_10")
label(0x0002b98c, "startup_status_dispatch_arm_11")
label(0x0002b990, "startup_status_dispatch_arm_12")
label(0x0002b994, "startup_status_dispatch_arm_13")
label(0x0002b998, "startup_status_dispatch_arm_14")
label(0x0002b99c, "startup_status_dispatch_null_15")
label(0x0002b9a0, "startup_status_dispatch_null_16")
label(0x0002b9a4, "startup_status_dispatch_null_17")
label(0x0002b9a8, "startup_status_dispatch_null_18")
label(0x0002b9ac, "startup_status_dispatch_null_19")
label(0x0002b9b0, "startup_status_dispatch_null_20")
label(0x0002b9b4, "startup_status_dispatch_null_21")
label(0x0002b9b8, "startup_status_dispatch_null_22")
label(0x0002b9bc, "startup_status_dispatch_null_23")
label(0x0002b9c0, "startup_status_dispatch_null_24")
label(0x0002b9c4, "startup_status_dispatch_null_25")
label(0x0002b9c8, "startup_status_dispatch_null_26")
label(0x0002b9cc, "startup_status_dispatch_null_27")
label(0x0002b9d0, "startup_status_dispatch_null_28")
label(0x0002b9d4, "startup_status_dispatch_arm_29")
label(0x0002b9d8, "startup_status_dispatch_arm_30")
label(0x0002b9dc, "startup_status_dispatch_arm_31")

label(0x0002b500, "startup_status_arm_video_reset")
label(0x0002b550, "startup_status_arm_geometry_workspace")
label(0x0002b660, "startup_status_arm_geometry_service")
label(0x0002b7b0, "startup_status_arm_counter_plus_two")
label(0x0002b7e0, "startup_status_arm_counter_plus_one")
label(0x0002b810, "startup_status_arm_text_asset_reset")
label(0x0002b870, "startup_status_arm_progress_text")
label(0x0002dc50, "startup_status_arm_geometry_init")
label(0x0002dd30, "startup_status_arm_geometry_build")
label(0x0002ded0, "startup_status_arm_geometry_frame_service",
      "Advances geometry frame/service state, submits both record workspaces, and refreshes the text/status plane.")
label(0x000e3ab0, "startup_status_arm_device_state_cycle")
label(0x000e3d00, "startup_status_arm_score_render")
label(0x000e3f30, "status_favorite_machines_render",
      "Builds an eight-entry ranking work array from the 0x1d00000 device table, renders FAVORITE MACHINES, and advances the status counter.")
label(0x000e3b30, "status_today_best_pilots_string")
label(0x000e3b50, "status_today_best_pilots_format_table")
label(0x000e3b60, "status_today_best_pilots_suffix")
label(0x000e3da0, "status_today_top_wins_string")
label(0x000e3ee0, "status_favorite_machines_string")
label(0x000e3f00, "status_loading_dots_strings")
label(0x000e3f22, "status_separator_string")
label(0x000e4190, "status_machine_name_alphabet_table_a")
label(0x000e41c0, "status_machine_name_alphabet_table_b")
label(0x000e41f0, "status_machine_name_alphabet_table_c")
label(0x000e4220, "status_machine_name_alphabet_table_d")
label(0x000e4250, "startup_runtime_status_prepare",
      "Builds the runtime status table, resets startup workspaces, and enters service state 23; early mode exits use 0xe4700.")
label(0x000e4700, "startup_runtime_status_prepare_early_exit")
label(0x000e4720, "startup_runtime_status_prepare_alt",
      "Alternate runtime status-table preparation path using the same machine-name alphabet tables.")
label(0x000e4abc, "startup_runtime_status_prepare_alt_early_exit")
label(0x000e4ae0, "startup_runtime_match_service",
      "Startup-dispatch service that updates mode/timing state, services both player object paths, and invokes geometry/status helpers.")
label(0x000e5440, "status_token_translation_table",
      "Fixed-width three-byte status-token table scanned by the token normalization helper.")
label(0x000e54a0, "status_token_normalize_and_publish",
      "Scans the token table, normalizes the active three-byte token, and publishes it into the selected status buffers.")
label(0x000e5650, "status_runtime_state_dispatch",
      "Dispatches the current runtime status state to its renderer or advances the state machine.")
label(0x000e56a0, "status_blank_row_string",
      "Space-filled fallback row used when a status record is inactive.")
label(0x000e56e0, "status_record_list_render",
      "Renders the active status record list, including ordinal/count fields and blank inactive rows.")
label(0x000e5a90, "status_record_list_render_alt",
      "Alternate status record-list renderer using the same ordinal and token helpers.")
label(0x000e5bb4, "status_record_list_render_variant_b",
      "Third record-list renderer using the alternate runtime record buffer and blank-row fallback.")
label(0x000e5d30, "status_service_state_dispatch",
      "Checks hardware enable state and dispatches the current status counter to a state-specific handler.")
label(0x000e5da0, "status_transition_render_gateway",
      "Dispatches timer-derived status transitions and joins the common renderer continuation.")
label(0x000e61c0, "status_transition_render_variant",
      "Alternate timer-derived transition renderer joining the common e6410 continuation.")
label(0x000e6500, "status_profile_selector_dispatch",
      "Maps a bounded selector through the local table at 0xe651c before the profile renderer loop.")
label(0x000e651c, "status_profile_selector_table",
      "Eight-entry local dispatch table for the status profile renderer.")
label(0x000e6648, "status_blank_dot_strings",
      "Fallback dot strings used by the status profile renderer for empty entries.")
label(0x000e6660, "status_record_grid_frame_build",
      "Builds the eight-by-thirteen status record grid, renders its columns, and updates video state.")
label(0x000e6d40, "status_record_word_copy_continuation",
      "Copies a 0x200-word status buffer and returns through the caller-supplied continuation.")
label(0x000e6d80, "geometry_status_emit_variant_a",
      "Converts the shared status phase into fixed-point values and emits a geometry command packet.")
label(0x000e6ef0, "geometry_status_emit_variant_b",
      "Alternate fixed-point status-to-geometry packet emitter with the same phase source.")
label(0x000e7060, "geometry_status_emit_variant_c",
      "Third fixed-point status-to-geometry packet emitter for the adjacent profile path.")
label(0x000e71d0, "geometry_status_emit_variant_d",
      "Fourth fixed-point status-to-geometry packet emitter used by the status-state dispatcher.")
label(0x000e7340, "geometry_status_emit_dispatch",
      "Selects one of the four status-to-geometry emitters from the shared mode word.")
label(0x000e7390, "geometry_object_packet_dispatch",
      "Builds and submits an object geometry packet, selecting direct or queued hardware paths by mode.")
label(0x000e79f0, "geometry_status_scene_dispatch",
      "Renders the status scene's object groups and dispatches the final scene mode through the local arm table.")
label(0x000e8920, "geometry_status_scene_arm_table",
      "Six-entry local dispatch table for the status scene's final geometry arms.")
label(0x000d24b0, "startup_status_arm_text_status_init",
      "Initializes status-text counters/assets, resets the video context, and advances the service counter.")
label(0x000d2560, "startup_status_arm_profile_dispatch",
      "Initializes the profile and dispatches the selected status submode.")
label(0x000d25b0, "startup_status_arm_profile_service",
      "Dispatches the selected status submode without reinitializing the profile.")
label(0x000d0820, "startup_profile_handler_0_geometry_setup",
      "Builds the profile-0 geometry records and resets its status workspace.")
label(0x000d0d10, "startup_profile_handler_1_geometry_setup",
      "Builds the profile-1 geometry records and resets its status workspace.")
label(0x000d1280, "startup_profile_handler_2_geometry_setup",
      "Builds the profile-2 geometry records and resets its status workspace.")
label(0x000d1ab0, "startup_profile_handler_3_geometry_setup",
      "Builds the profile-3 geometry records and resets its status workspace.")
label(0x000de670, "startup_geometry_status_workspace_init",
      "Initializes status/geometry workspace fields and emits setup packets.")
label(0x0006f600, "geometry_fixed_point_record_producer",
      "Converts two geometry inputs to fixed-point coordinates and emits the associated FIFO record.")
label(0x0006f900, "geometry_profile_table_loader_a",
      "Loads one profile record from the ROM table at 0x6eb60 into the shared geometry profile words.")
label(0x0006f970, "geometry_profile_table_loader_b",
      "Loads the alternate profile record into the shared geometry profile words.")
label(0x000e2120, "text_asset_selector_upload",
      "Selects an asset through 0x142e94 and delegates expansion to the three-plane uploader.")
ensure_function(0x000e2040, "text_byte_to_three_tile_planes", 0x000e20d8)
label(0x000423a8, "startup_record_table_clear",
      "Clears the two startup record tables and seeds record sentinels.")
label(0x0009b498, "startup_geometry_record_pool_clear",
      "Clears the 16-entry geometry record pool and its allocation index.")
label(0x000c55a8, "startup_device_table_clear",
      "Clears the mapped device table and initializes its sentinel fields.")
ensure_function(0x0002b500, "startup_status_arm_video_reset", 0x0002b54c)
ensure_function(0x0002b550, "startup_status_arm_geometry_workspace", 0x0002b65c)
ensure_function(0x0002b660, "startup_status_arm_geometry_service", 0x0002b6f4)
ensure_function(0x0002b7b0, "startup_status_arm_counter_plus_two", 0x0002b7dc)
ensure_function(0x0002b7e0, "startup_status_arm_counter_plus_one", 0x0002b80c)
ensure_function(0x0002b810, "startup_status_arm_text_asset_reset", 0x0002b864)
ensure_function(0x0002b870, "startup_status_arm_progress_text", 0x0002b934)
ensure_function(0x0002dc50, "startup_status_arm_geometry_init", 0x0002dd2c)
ensure_function(0x0002dd30, "startup_status_arm_geometry_build", 0x0002dec8)
ensure_function(0x0002ded0, "startup_status_arm_geometry_frame_service", 0x0002e140)
ensure_function(0x000e3ab0, "startup_status_arm_device_state_cycle", 0x000e3b2c)
ensure_function(0x000e3b70, "status_today_best_pilots_render", 0x000e3d00)
ensure_function(0x000e3d00, "startup_status_arm_score_render", 0x000e3d98)
ensure_function(0x000e3dc0, "status_top_wins_render", 0x000e3ee0)
ensure_function(0x000e3f30, "status_favorite_machines_render", 0x000e418c)
ensure_function(0x000e4250, "startup_runtime_status_prepare", 0x000e4700)
ensure_function(0x000e4700, "startup_runtime_status_prepare_early_exit", 0x000e4718)
ensure_function(0x000e4720, "startup_runtime_status_prepare_alt", 0x000e4abc)
ensure_function(0x000e4abc, "startup_runtime_status_prepare_alt_early_exit", 0x000e4adc)
ensure_function(0x000e4ae0, "startup_runtime_match_service", 0x000e5434)
ensure_function(0x000e54a0, "status_token_normalize_and_publish", 0x000e564c)
ensure_function(0x000e5650, "status_runtime_state_dispatch", 0x000e569c)
ensure_function(0x000e56e0, "status_record_list_render", 0x000e5a8c)
ensure_function(0x000e5a90, "status_record_list_render_alt", 0x000e5bb4)
ensure_function(0x000e5bb4, "status_record_list_render_variant_b", 0x000e5d30)
ensure_function(0x000e5d30, "status_service_state_dispatch", 0x000e5d80)
ensure_function(0x000e5da0, "status_transition_render_gateway", 0x000e61c0)
ensure_function(0x000e61c0, "status_transition_render_variant", 0x000e6500)
ensure_function(0x000e6500, "status_profile_selector_dispatch", 0x000e6644)
ensure_function(0x000e6660, "status_record_grid_frame_build", 0x000e6d40)
ensure_function(0x000e6d40, "status_record_word_copy_continuation", 0x000e6d7c)
ensure_function(0x000e6d80, "geometry_status_emit_variant_a", 0x000e6ef0)
ensure_function(0x000e6ef0, "geometry_status_emit_variant_b", 0x000e7060)
ensure_function(0x000e7060, "geometry_status_emit_variant_c", 0x000e71d0)
ensure_function(0x000e71d0, "geometry_status_emit_variant_d", 0x000e7334)
ensure_function(0x000e7340, "geometry_status_emit_dispatch", 0x000e738c)
ensure_function(0x000e7390, "geometry_object_packet_dispatch", 0x000e79e4)
ensure_function(0x000e79f0, "geometry_status_scene_dispatch", 0x000e913c)
ensure_function(0x000d24b0, "startup_status_arm_text_status_init", 0x000d2560)
ensure_function(0x000d2560, "startup_status_arm_profile_dispatch", 0x000d25b0)
ensure_function(0x000d25b0, "startup_status_arm_profile_service", 0x000d25f0)
ensure_function(0x000d0820, "startup_profile_handler_0_geometry_setup", 0x000d0964)
ensure_function(0x000d0d10, "startup_profile_handler_1_geometry_setup", 0x000d0e5c)
ensure_function(0x000d1280, "startup_profile_handler_2_geometry_setup", 0x000d13ac)
ensure_function(0x000d1ab0, "startup_profile_handler_3_geometry_setup", 0x000d1bd8)
ensure_function(0x000de670, "startup_geometry_status_workspace_init", 0x000de988)
ensure_function(0x0006f600, "geometry_fixed_point_record_producer", 0x0006f6f0)
ensure_function(0x0006f900, "geometry_profile_table_loader_a", 0x0006f968)
ensure_function(0x0006f970, "geometry_profile_table_loader_b", 0x0006f9d8)
ensure_function(0x000e2120, "text_asset_selector_upload", 0x000e2130)
ensure_function(0x000e2130, "startup_status_text_initialize", 0x000e2324)

label(0x0051bb20, "geometry_profile_word_0")
label(0x0051bb24, "geometry_profile_word_pair")
label(0x0051bb28, "geometry_profile_word_2")
label(0x0006eb60, "geometry_profile_record_table",
      "Sixteen 0x18-byte ROM records consumed by the profile table loaders.")
label(0x00142e94, "text_asset_pointer_table_bank_a")
label(0x00142f34, "text_asset_pointer_table_bank_b")
label(0x02fb3d90, "text_asset_record_bank_a_base",
      "First of 32 sequential 0xc0-byte source records selected by the 0x142e94 pointer table.")
ensure_function(0x000e1f20, "text_byte_to_tile_planes", 0x000e1fa8)
ensure_function(0x000e1fb0, "text_byte_to_tile_planes_offset_100", 0x000e2038)
ensure_function(0x000423a8, "startup_record_table_clear", 0x00042460)
ensure_function(0x0009b498, "startup_geometry_record_pool_clear", 0x0009b4c0)
ensure_function(0x000c55a8, "startup_device_table_clear", 0x000c55fc)

# Trace-confirmed call sites inside the system-setup helper.
label(0x00018960, "startup_call_io_self_test")
label(0x00018968, "startup_call_video_bootstrap")
label(0x00018970, "startup_call_asset_transfer")
ensure_function(0x00018960, "startup_system_setup", 0x00018a0c)

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
label(0x00028d30, "geometry_auxiliary_submit_select")
label(0x00028120, "texture_loader_profile_setup")
label(0x00027e50, "texture_decompressor")
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
ensure_function(0x00028120, "texture_loader_profile_setup", 0x000281dc)
ensure_function(0x00027e50, "texture_decompressor", 0x000280bc)
ensure_function(0x00028d30, "geometry_auxiliary_submit_select", 0x00028d7c)

# Static hardware/data references used by the annotated notes.
label(0x00028170, "texture_load_done_message")
label(0x0002812c, "texture_load_message")
label(0x0002a4e0, "command_mode_validator")
label(0x0006ece0, "geometry_float_to_fixed_helper")
label(0x000bf0c0, "packed_bit_search_helper")
label(0x000e1f20, "text_byte_to_tile_planes")
label(0x000e1fb0, "text_byte_to_tile_planes_offset_100",
      "Same 64-triplet expansion as 0xe1f20, writing each plane into the +0x100 destination bank.")
label(0x000f5058, "runtime_prng_next")
label(0x000f5d40, "memcpy_aligned")
label(0x000f5c58, "memcmp_bytes")
label(0x000f5100, "text_string_render_dispatch")
label(0x000f5190, "text_format_parser_core")
label(0x0002a430, "short_countdown_delay")
label(0x0002a458, "command_queue_space_check")
label(0x0002a4a8, "command_queue_byte_push")
label(0x0002a5f0, "command_mode_validator_alt")
label(0x0002a990, "geometry_command_packet_submit")
label(0x00079050, "randomized_record_state_dispatch",
      "The first original-ROM diagnostic observes object 0x5040d0, related 0x503ad0 via object + 0x74, object state 0, and common-tail transition 7; the reconstructed runtime adapter is bounded to this capture-derived tick until pool rotation is traced.")
label(0x00079d60, "randomized_record_state_dispatch_alt")
label(0x000790a4, "object_state_zero_classifier",
      "Recovered state-0 classifier; recognizes role values 1 through 6 and tests mode bit 1.")
label(0x00079178, "object_state_one_classifier")
label(0x000791fc, "object_state_two_classifier",
      "Loads float bits 0x4072c000 and gates on global state 5 plus mode bit 1.")
label(0x0007928c, "object_state_three_classifier")
label(0x00079374, "object_state_four_classifier",
      "Loads float bits 0x4072c000 in the negative-time path.")
label(0x00079400, "object_state_five_classifier",
      "Also loads float bits 0x40590000; recovered compare path is retained separately.")
label(0x000794ac, "object_state_six_classifier",
      "Recognizes values 1, 3, 4, 6, and 7; related-tag path uses tag 31 and related state 3.")
label(0x0007953c, "object_state_seven_classifier")
label(0x000795a8, "object_state_terminal_classifier")
label(0x000795c4, "object_state_common_remap_tail")
label(0x0001c618, "video_plane_state_initialize")
label(0x0001c220, "ascii_font_video_bootstrap",
      "Computes source 0x02ea0bb8 from 0x01040000 + 0x01e60bb8, then calls 0x1c730 with destination 0x01080000, 0x80 blocks, and color mode 1; clears tile/video state through 0x1c618.")
label(0x0001c730, "ascii_font_lane_expand")
label(0x0001ccf8, "video_command_byte_write")
label(0x0001d310, "text_glyph_render_core")
label(0x0009e050, "geometry_record_upload_helper")
label(0x0001bb90, "text_bitplane_unpack")
label(0x000e2040, "text_byte_to_three_tile_planes")
label(0x000e1e08, "geometry_output_mode_dispatch")
label(0x000e2130, "startup_status_text_initialize",
      "Expands the selected status tile bank, then publishes derived asset pointers from 0x2f8d890 into runtime slots 0x577594-0x5775a8.")
label(0x000df070, "geometry_object_transform_update")
label(0x000e37f0, "startup_device_table_copy")
label(0x000e2120, "text_asset_plane_upload")
label(0x000e3a70, "text_render_three_byte_token")
ensure_function(0x000e39c0, "text_indexed_status_label", 0x000e39ec)
ensure_function(0x000e39f0, "text_status_string_render", 0x000e39f8)
ensure_function(0x000e3a00, "text_status_glyph_match", 0x000e3a08)
ensure_function(0x000e3a10, "text_render_two_digit_value", 0x000e3a18)
label(0x000e3a30, "status_render_win_loss_row")
ensure_function(0x000e3a30, "status_render_win_loss_row", 0x000e3a60)
label(0x000e3a60, "status_render_count_wrapper")
ensure_function(0x000e3a60, "status_render_count_wrapper", 0x000e3a68)
ensure_function(0x000e3a70, "text_render_three_byte_token", 0x000e3aa8)
label(0x000e39c0, "text_indexed_status_label")
label(0x000e39f0, "text_status_string_render")
label(0x000e3a00, "text_status_glyph_match")
label(0x0006fec0, "geometry_device_command_initialize")
label(0x000027d8, "indirect_return_trampoline")
label(0x00073508, "geometry_range_classify")
label(0x000017c8, "startup_device_mode_select")
label(0x00001348, "startup_device_mode_enable")
label(0x00001380, "startup_device_mode_transition")
label(0x00001bb8, "startup_hardware_reset")
label(0x0001bc20, "asset_word_byte_swap")
label(0x0001bc90, "asset_tiled_row_copy")
label(0x0001d1b0, "text_string_walk_control")
label(0x0001ce00, "text_character_tile_write")
label(0x0001cea0, "text_character_tile_write_alt")
label(0x0001d9e0, "text_printable_string_render")
label(0x0001da90, "text_printable_string_render_alt")
label(0x0001de80, "text_attributed_tile_copy")
label(0x0001f010, "ui_text_region_update")
label(0x00020210, "ui_text_assets_initialize")
label(0x0001f060, "ui_asset_tile_load")
label(0x00003120, "crc16_buffer_update")
label(0x000e3a10, "text_render_two_digit_value")
label(0x0006f6f0, "geometry_float_transform_helper",
      "Match-phase object transforms feed this fixed-point/float helper; preserve the raw IEEE-754 conversions until a numeric post-start oracle distinguishes the caller arms. The clean-base original-ROM control is no longer matrix-saturated, but its stream still does not identify caller inputs versus persistent geometry state, so repeated-object transforms are not promoted from the latest observed matrix alone.")
label(0x000237ac, "geometry_object_branch_dispatch",
      "Object flag is masked with 0xff; wrapped windows add 0x17ff and 0x1ff and compare against 0x2ffe and 0x3fe; signed response lower bounds are -0xdff and -0xbff.")
label(0x0002381c, "geometry_object_transform_update",
      "Reads parent fields at offsets 0x14, 0x18, 0x1c, 0x1c8, 0x150, and 0x1cc; applies a floating scale and its square, then sets the output flag to 1.")
label(0x00023670, "geometry_object_initializer",
      "Emits command selectors 0x0a, 0x1d, and 0x1e to 0x884000; uses float bits 0x43200000 and 0x40200000 and updates object offsets 0x08, 0x90, 0x94, and 0x9c.")
label(0x00023ef0, "geometry_response_selector",
      "Indexes table 0x2be0008 with state-derived values masked to 31; fallback pointers are 0x49c980 and 0x40005c, selected by the low state bit.")
label(0x0006ff20, "geometry_command_packet_builder",
      "Builds an 18-word packet containing literals 0x01540601, 0x7f000000, and 0x3f800000 plus register sums/differences.")
label(0x000c5d70, "geometry_profile_packet_builder",
      "Masks shifted input values with 0xffff; profile 3 emits selectors 28, 27, and 43, while the fallback emits selector 43.")
label(0x00070950, "geometry_packet_tail",
      "Appends a zero after two pending packet words.")
label(0x0009e250, "geometry_result_builder_variant",
      "Uses parameter table 0x562436 with 12-byte stride, request sink 0x884000, paired offsets 0/4/8 and mirrors 0x10/0x14/0x18, common request 31, and clear immediate 0xffffe000.")
label(0x0009e450, "geometry_result_builder",
      "Uses common request 31 with seven words and follow-up commands 29/30; response offsets are 0x18/0x20, table base is 0x562cb0, and command-29 response toggles bit 31.")
label(0x0009eab0, "geometry_result_builder_variant_alt",
      "Shares the 0x562436/0x562cb0 tables and command 29/30 follow-ups; flagged arm emits command 10.")
label(0x00028840, "geometry_profile_constant_selector",
      "Reads backup byte 0x1d00027 and publishes profile words to 0x512bd4/0x512bd8/0x512bdc; default words are 0x3f0ccccd, 0x3f59999a, and 0x3e19999a. Nine indexed raw triples are recovered: (3f000000,3f4ccccd,3e4ccccd), (3ee66666,3f400000,3e800000), (3ee66666,3f266666,3eb33333), (3eb33333,3f0ccccd,3ee66666), (3eb33333,3ee66666,3f0ccccd), (3f800000,3f59999a,0), (3f733333,3f59999a,0), (3f59999a,3f59999a,3d4ccccd), (3f400000,3f59999a,3dcccccd).")
label(0x000c8fa0, "command_profile_initializer",
      "Uses 14-entry profile tables, skips setup for profile 13, initializes selector/pending fields to zero, and publishes the setup handle twice.")
label(0x000c8f10, "command_profile_dispatch",
      "Uses middle-column index profile*3+1 and extracts control-word bits 13..15.")
label(0x000c8f60, "command_profile_advance",
      "Uses last-column index profile*3+2 and increments the input after the callback.")
label(0x0009d0d0, "geometry_global_countdowns",
      "Updates counters at 0x562c9c/0x562ca0/0x562ca4; masks object flags to 0xff, replaces on nonzero flags, and decrements only positive counters otherwise.")
label(0x0009d170, "geometry_board_update_gate",
      "Tests state bit 0, writes 0x909 to 0x800090, uses frame addresses 0x804000/0x804004, and emits enabled prefix 5, 55, 0x3e23d70a, 0xbdf92c60, 0x3f800000 to 0x884000.")
label(0x00023d60, "geometry_board_setup_prefix",
      "Emits 20 words to 0x884000 with selectors 5, 16, 18, and 19 plus 58; fixed bits include 0xbd5a740e, 0x3e8f5c29, 0x3ada740e, 0x41100000, and 0x3f800000, then publishes a pointer at 0x801008 with offset 0x34.")
label(0x0006fd1c, "geometry_allocator_commit",
      "Advances the allocation head by 0x30, increments the source count, and derives availability as 0 minus the next-head word.")
label(0x0006fd50, "geometry_link_release",
      "Uses 999 as the no-record sentinel; redirects record offsets 0x14/0x18 or side-table offsets 0x5c4/0x5c8 and decrements the reference count.")
label(0x00023ca0, "geometry_cleanup_helper",
      "Clears object bytes 0xa0, 0xa1, and 0xa2; publishes float bits 0x41200000 to 0x504d54 and 0x504d58; returns through 0x23cd8.")
label(0x00023954, "geometry_object_lifecycle_tail",
      "Increments byte offset 0x19 only when byte offset 0x18 is zero and the prior value is at most 31; otherwise preserves it.")
label(0x000783c8, "transition_wrapper",
      "Indexes table 0x72690 with selector 0x504d68 and sets action 5.")
label(0x000784c8, "transition_selector_dispatch",
      "Has ten targets from 0x78508 through 0x78618; selectors at or above 10 return immediately. Action-5 values are 8,12,12,12,12,13,13,13,19,8; action-10 values are 9,16,12,12,12,13,13,13,17,9.")
label(0x000786d0, "object_action_timing_split",
      "Uses a floating absolute-difference validity check; valid values route to action 5 when current is at least threshold, otherwise action 10, while nonfinite differences reject.")
label(0x00024690, "geometry_command6_dynamic_loop",
      "Starts at index 0, increments by 1, requires active-mask bit 2, and emits six-word packets with header 5,19 and trailer 1,58; readback is at 0x802008, publish is at 0x801008, and computed values divide by 600.")
label(0x000df0cc, "geometry_object_response_vector_selector",
      "Sign-extended related-object halfword selects triplet 0, 1, or 2; other selectors write three zero words.")
label(0x00077e60, "action_jump_dispatch",
      "Uses a 44-entry jump table at 0x77e7c; selectors at or above 44 fall back to 0x78084, with table targets spanning 0x77f2c through 0x7807c.")
label(0x000e2330, "video_dispatch_prefix",
      "Treats dispatch state 0xff as no-op, values above 0x81 as default, and other values as table indices; bank-A special case uses geometry mode 0 or mode 2/palette 1/gate 0/equal board and palette values.")
ensure_function(0x000e2330, "video_dispatch_prefix", 0x000e23b4)
label(0x000e23b4, "video_dispatch_table",
      "Dispatch targets indexed by the normalized status value in g4; entries route into the asset expansion arms below.")
label(0x000e25bc, "video_dispatch_arm0",
      "Emits four entries: tiles 11,21,23,25 from sources 0x2fb75d0, 0x2fb5b90, 0x2fb5c50, 0x2fb5d10.")
label(0x000e2600, "video_dispatch_arm1",
      "Emits six entries beginning tile 11 and ending tiles 27,29; sources include 0x2fb75d0, 0x2fb6010, and 0x2fb60d0.")
label(0x000e2664, "video_dispatch_arm2")
label(0x000e26c8, "video_dispatch_arm3")
label(0x000e271c, "video_dispatch_arm4")
label(0x000e2770, "video_dispatch_arm5")
label(0x000e27a4, "video_dispatch_arm6")
label(0x000e27f8, "video_dispatch_arm7")
label(0x000e280c, "video_dispatch_arm8")
label(0x000e2830, "video_dispatch_arm9",
      "Emits four entries for tiles 21,25,27,29 from sources 0x2fb6cd0, 0x2fb7e10, 0x2bfed8c, 0x2fb6fd0.")
label(0x000e2874, "video_dispatch_arm10",
      "Emits nine non-mirrored entries for tiles 11,1,3,5,7,21,25,27,29.")
label(0x000e2908, "video_dispatch_arm11",
      "Emits one non-mirrored tile 11 from source 0x2fb75d0.")
label(0x000e291c, "video_dispatch_arm12",
      "Emits tiles 23,25,27 from sources 0x2fb8350, 0x2fb8410, 0x2fb84d0 and exits through 0xe33e4.")
label(0x000e2950, "video_dispatch_arm13",
      "Emits five tiles 21,23,25,27,29 from the recovered 0x2fb7f90-0x2fb8290 source sequence and exits through 0xe33f4.")
label(0x000e29a4, "video_dispatch_arm14",
      "Emits six tiles 1,3,5,7,9,11 from the recovered non-mirrored source set.")
label(0x000e29fc, "video_dispatch_arm15",
      "Emits four tiles 1,3,5,7 from the recovered non-mirrored source set.")
label(0x000e2a40, "video_dispatch_arm16",
      "Emits tiles 5,7 with bank-dependent sources 0x2fb4990/0x2fb4a50 or 0x2fb4b10/0x2fb4bd0.")
label(0x000e2a48, "video_dispatch_arm17",
      "Emits tiles 9,11,1,3 with bank-dependent source sets beginning 0x2fb5290 or 0x2fb5410.")
ensure_function(0x000e25bc, "video_dispatch_arm0", 0x000e2600)
ensure_function(0x000e2600, "video_dispatch_arm1", 0x000e2664)
ensure_function(0x000e2664, "video_dispatch_arm2", 0x000e26c8)
ensure_function(0x000e26c8, "video_dispatch_arm3", 0x000e271c)
ensure_function(0x000e271c, "video_dispatch_arm4", 0x000e2770)
ensure_function(0x000e2770, "video_dispatch_arm5", 0x000e27a4)
ensure_function(0x000e27a4, "video_dispatch_arm6", 0x000e27f8)
ensure_function(0x000e27f8, "video_dispatch_arm7", 0x000e280c)
ensure_function(0x000e280c, "video_dispatch_arm8", 0x000e2830)
ensure_function(0x000e2830, "video_dispatch_arm9", 0x000e2874)
ensure_function(0x000e2874, "video_dispatch_arm10", 0x000e2908)
ensure_function(0x000e2908, "video_dispatch_arm11", 0x000e291c)
ensure_function(0x000e291c, "video_dispatch_arm12", 0x000e2950)
ensure_function(0x000e2950, "video_dispatch_arm13", 0x000e29a4)
ensure_function(0x000e29a4, "video_dispatch_arm14", 0x000e29fc)
ensure_function(0x000e29fc, "video_dispatch_arm15", 0x000e2a40)
ensure_function(0x000e2a40, "video_dispatch_arm16", 0x000e2a48)
ensure_function(0x000e2a48, "video_dispatch_arm17", 0x000e2ad4)
label(0x000e2ad4, "video_dispatch_arm18",
      "Emits six tiles 1,3,5,7,9,11 with bank-dependent six-source sets; exits through 0xe30a8 or 0xe30cc.")
ensure_function(0x000e2ad4, "video_dispatch_arm18", 0x000e2b88)
label(0x000e2b88, "video_dispatch_arm19",
      "Emits four tiles 5,7,9,11 with bank-dependent four-source sets; exits through 0xe2f24 or 0xe2f48.")
ensure_function(0x000e2b88, "video_dispatch_arm19", 0x000e2c14)
label(0x000e2c14, "video_dispatch_arm20",
      "Emits four bank-dependent entries for tiles 9,11,1,3; exits through 0xe2f70 or 0xe2f94.")
ensure_function(0x000e2c14, "video_dispatch_arm20", 0x000e2ca0)
label(0x000e2ca0, "video_dispatch_arm21",
      "Emits four bank-dependent entries for tiles 1,3,5,7; exits through 0xe2fbc or 0xe2fe0.")
ensure_function(0x000e2ca0, "video_dispatch_arm21", 0x000e2d2c)
label(0x000e2d2c, "video_dispatch_arm22",
      "Emits six bank-dependent entries for tiles 5,7,9,11,13,15; exits through 0xe33f4.")
ensure_function(0x000e2d2c, "video_dispatch_arm22", 0x000e2df8)
label(0x000e2df8, "video_dispatch_arm23",
      "Emits tiles 9,11 with bank-dependent sources 0x2fb5290/0x2fb5350 or 0x2fb5410/0x2fb54d0; exits through 0xe3008 or 0xe304c.")
ensure_function(0x000e2df8, "video_dispatch_arm23", 0x000e2e44)
label(0x000e2e44, "video_dispatch_arm24",
      "Performs only the bank-dependent continuation choice 0xe3008 or 0xe304c.")
ensure_function(0x000e2e44, "video_dispatch_arm24", 0x000e2e4c)
label(0x000e2eec, "video_dispatch_arm27",
      "Emits tiles 9,11 with bank-dependent sources 0x2fb4c90/0x2fb4d50 or 0x2fb4e10/0x2fb4ed0; exits through 0xe30a8 or 0xe30cc.")
label(0x000e2e4c, "video_dispatch_arm25",
      "Emits tiles 1,3 with bank-dependent source pairs and exits through 0xe33f4.")
ensure_function(0x000e2e4c, "video_dispatch_arm25", 0x000e2ea0)
label(0x000e2ea0, "video_dispatch_arm26",
      "Emits tiles 5,7 with bank-dependent source pairs and exits through 0xe33f4.")
ensure_function(0x000e2ea0, "video_dispatch_arm26", 0x000e2eec)
ensure_function(0x000e2eec, "video_dispatch_arm27", 0x000e2f20)
label(0x000e3004, "video_dispatch_arm28",
      "Emits tiles 1,3,5,7 with bank-dependent sources and exits through 0xe33f4.")
ensure_function(0x000e3004, "video_dispatch_arm28", 0x000e3090)
label(0x000e3090, "video_dispatch_arm29",
      "Emits tiles 1,3 with bank-dependent sources and exits through 0xe33f4.")
ensure_function(0x000e3090, "video_dispatch_arm29", 0x000e30dc)
label(0x000e30dc, "video_dispatch_arm30",
      "Reads five words from 0x577598 through 0x5775a8 for tiles 21,23,25,27,29.")
ensure_function(0x000e30dc, "video_dispatch_arm30", 0x000e3130)
label(0x000e3130, "video_dispatch_arm32",
      "Emits one tile 3 from 0x2fb7d50; the following mov 7 is unreachable after the immediate branch.")
ensure_function(0x000e3130, "video_dispatch_arm32", 0x000e314c)
label(0x000e314c, "video_dispatch_arm31",
      "Emits five tiles 21,23,25,27,29 through helper 0xe1fb0 from sources 0x2fb3d90, 0x142dd4, 0x2fa5ad0, 0x2fabb90, 0x2fb1c50.")
ensure_function(0x000e314c, "video_dispatch_arm31", 0x000e319c)
label(0x000e3248, "video_dispatch_arm33",
      "Emits eight tiles 1,3,5,7,21,25,27,29 with helper 0xe1fb0 and exits through 0xe33f4.")
ensure_function(0x000e319c, "video_dispatch_arm34", 0x000e3248)
ensure_function(0x000e3248, "video_dispatch_arm33", 0x000e3314)
label(0x000e319c, "video_dispatch_arm34",
      "Uses table 0x142f34 with selector shift 2, special selector 5, helper 0xe1fb0, and exits through 0xe33f4.")
label(0x000e3314, "video_dispatch_arm35",
      "Uses bank-A table 0x142e94 or bank-B table 0x142f34, fixed sources 0x143704/0x1437c4/0x2fb8590, and helper 0xe2040.")
ensure_function(0x000e3314, "video_dispatch_arm35", 0x000e33f4)
label(0x000e33f4, "video_dispatch_sentinel_gate",
      "Compares sentinel against 0x200 and continues at 0xe3444 or 0xe35a0.")
ensure_function(0x000e33f4, "video_dispatch_sentinel_gate", 0x000e3444)
label(0x000e3444, "video_dispatch_post_sentinel_gate",
      "Post-sentinel path uses helper 0xe2040; arm 40 scales its sentinel by 4 from bases 0x129e28/0x129ea8, arm 37 handles sentinel 0x21f, and indexed arm 38 scales from bases 0x2bfd544/0x2bfd5c4.")
ensure_function(0x000e3444, "video_dispatch_post_sentinel_gate", 0x000e349c)
label(0x000e349c, "video_dispatch_sentinel_21f",
      "Uses sources 0x2fb5a10/0x2fb5ad0 and bank-selected tiles 5,7 or 1,3; continues at 0xe35a0.")
ensure_function(0x000e349c, "video_dispatch_sentinel_21f", 0x000e34e4)
label(0x000e34e4, "video_dispatch_sentinel_indexed_pair",
      "Uses source bases 0x2bfd544/0x2bfd5c4 with sentinel*4 offset and bank-selected tiles 5,7 or 1,3.")
ensure_function(0x000e34e4, "video_dispatch_sentinel_indexed_pair", 0x000e353c)
label(0x000e353c, "video_dispatch_sentinel_indexed_pair_high",
      "Uses source bases 0x2bfd5c4/0x2bfd644 with sentinel*4 offset, helper 0xe2040, and continuation 0xe35a0.")
ensure_function(0x000e353c, "video_dispatch_sentinel_indexed_pair_high", 0x000e35a0)
label(0x000e35a0, "video_dispatch_terminal_reset",
      "Terminal side effect returns 0xff; post-route ranges begin at 0x200, 0x400, and 0x420 with bounds 29, 30, and 31, plus exact sentinel 0x21f.")
ensure_function(0x000e35a0, "video_dispatch_terminal_reset", 0x000e35ac)
label(0x000e35b0, "status_asset_descriptor_table",
      "Ten 8-byte descriptor records containing the repeated MSB tag and source value 0x464d0.")
label(0x000e3600, "status_asset_descriptor_table_alt",
      "Ten 12-byte alternate descriptor records containing the MSB tag, value 5, and a zero field.")
label(0x000e3680, "status_ordinal_suffix_table",
      "Ten fixed-width ordinal strings: 1ST through 9TH and 10.")
label(0x000e36c0, "status_ordinal_number_table",
      "Ten fixed-width numeric strings: 1 through 10.")
label(0x000e3700, "status_ordinal_word_table",
      "Ten fixed-width suffix strings: ST, ND, RD, then TH variants.")
label(0x000e3a18, "status_win_loss_strings",
      "Two fixed-width status strings: WINS and LOSSES.")
label(0x000e3740, "status_asset_tables_initialize")
ensure_function(0x000e3740, "status_asset_tables_initialize", 0x000e37ac)
label(0x000e37b0, "status_asset_tables_reset")
ensure_function(0x000e37b0, "status_asset_tables_reset", 0x000e37ec)
label(0x000e37f0, "startup_device_table_copy")
ensure_function(0x000e37f0, "startup_device_table_copy", 0x000e3824)
label(0x000e3830, "status_render_small_value")
ensure_function(0x000e3830, "status_render_small_value", 0x000e387c)
label(0x000e3880, "status_render_percentage")
ensure_function(0x000e3880, "status_render_percentage", 0x000e391c)
label(0x000e3920, "status_render_count")
ensure_function(0x000e3920, "status_render_count", 0x000e39bc)
label(0x0001f680, "status_code_record_table",
      "Contains 9 records with 16-byte stride; index 8 is blank and invalid indices return zero. Text-position fields are column 8 and row 14.")
label(0x0001f710, "status_code_dispatch",
      "Clamps selectors above 7 to case 8, indexes messages at 0x1f680 with 16-byte stride, uses helpers 0x1df00/0x1dc90, and selects recovered sources 0x2fe321c, 0x2fe350e, 0x2fe35e6, 0x2fe343c, 0x2fe37fa, 0x2fe33b4, 0x2fe32d0, and 0x2fe3746.")
label(0x0001f1b0, "status_panel_pair_route",
      "Mode 0 uses helper 0x1df70/source 0; other modes use helper 0x1dd10/source 0x2fd832e; rectangle column is 2, height 3, row/width add 31, and stack frame size is 0x50.")
label(0x0001f290, "status_panel_parallel_route",
      "Shares helpers 0x1df70/0x1dd10, zero fill, column 2, height 3, row/width add 31, and 0x50-byte frame; nonzero-mode source is 0x2fd848a.")
label(0x0001f470, "insert_coin_renderer",
      "Selects message 0x1f440 or 0x1f450, calls text helper 0x1d9e0, and adds 31 to both caller position fields.")
label(0x0001f3b0, "press_start_renderer",
      "Selects message 0x1f370 or 0x1f390, calls helper 0x1d210, adds 31 to both positions, and updates flag 0x502484 with set mask 4 or clear mask 0xfffb.")
label(0x0001f540, "status_panel_three_stage_sequence",
      "Derives positions with offsets +2, -1, +12, -7; stage sources are 0x2fde9d0, 0x2fe1606, and 0x2fe158e, with dimensions 55x8, 34x2, and 30x2 and helpers 0x1dc10/0x1dc90/0x1df00 by mode.")
label(0x0001fba0, "status_panel10_transfer",
      "Calls helper 0x1dc10 with source 0x2fe0404 at rectangle column 10, row 20, width 31, height 5.")
label(0x0001fad0, "status_panel7_transfer",
      "Calls helper 0x1dc10 with source 0x2fe1350 at column/row 10,10, width caller value plus 31, and height 5.")
label(0x0001fb10, "status_panel8_transfer",
      "Calls helper 0x1dc90 with source 0x2fe1170 at column/row 7,10, width caller value plus 31, and height 5.")
label(0x0001fb50, "status_panel9_transfer",
      "Uses source 0x2fe0d42/helper 0x1dc10 when source-present, otherwise fill helper 0x1df00 with zero source; column/row 5,10, width caller value plus 31, height 5.")
label(0x0001fdf0, "status_panel11_transfer",
      "Uses sources 0x2fd892e/0x2fd894a with helpers 0x1dc90/0x1dc10 at rectangle 20,20,7,2.")
label(0x0001fe60, "status_panel12_transfer",
      "Uses source 0x2fe0cb0/helper 0x1dc10 when present, otherwise fill helper 0x1df00; uses current position with dimensions 20 by 2.")
label(0x0001fe90, "status_multi_region_clear",
      "Calls fill helper 0x1df00 three times for rectangles (4,10,33x8), (22,10,38x8), and (20,10,24x8), in that order.")
label(0x0001ff20, "status_panel13_source_fill",
      "Uses source 0x2fe0b5c/helper 0x1dc10 when present, otherwise fill helper 0x1df00; preserves current position, uses height 5, and width caller g3 plus 31.")
label(0x0001ff50, "status_panel14_lookup_renderer",
      "Masks (g0-48) to four bits, selects a 2-byte entry from table 0x2ea2090, transfers it as 1x2 through 0x1dc10, and advances the current column when within the bound.")
label(0x0001ffb0, "status_panel15_source_fill",
      "Uses explicit position (4,17), height 5, and width g23 plus 31; nonzero g0 transfers 0x2fe0f54 through 0x1dd10, while zero g0 clears through 0x1df70.")
label(0x0001fff0, "status_panel16_source_fill",
      "Uses explicit position (11,21), height 8, and width caller g9 plus 31; nonzero g0 transfers source 0x2fdff54 through 0x1dc90, while zero g0 clears through 0x1df00.")
label(0x00020060, "streak_status_renderer",
      "Initializes a 22x2 clear at (g11+31,g11+31), then routes values through message 0x20040/helper 0x1d1f0, digit helper 0x1ff50, or the two tile sources 0x2fdfc00/0x2fdfbfc.")
label(0x00020a20, "text_strip_builder",
      "Builds a centered strip at 0x100c000+(row<<6): empty fill repetitions, clamped input*scale repetitions of a caller-supplied three-word pattern, then trailing fill repetitions.")
label(0x00020300, "attribute_pair_writer",
      "Selects one of two source attribute pairs, writes to 0x1001288/0x1001290 destinations with index*14 byte offset, and applies attribute bits 0xc000.")
label(0x000203d0, "profile_upload_panel_wrappers",
      "Uploads 0x40 halfwords per row from 0x1004000 to a profile-selected destination using helper 0x1bc90, then renders the (11,21) panel through 0x1dc90 or clears it through 0x1df00.")
label(0x00020390, "video_upload_panel17",
      "Uploads 0x40 halfwords per row from 0x1004000 to 0x1fccd20 through helper 0x1bc90, then transfers source 0x2fe0864 as a current-origin 31x5 panel through 0x1dc90.")
label(0x00020460, "video_upload_panel18",
      "Uploads 0x40 halfwords per row from 0x1004000 to 0x1fd89d0 through helper 0x1bc90, then advances the current column by 4 for an 8x4 source-or-clear panel using source 0x2fcf468.")
label(0x000204d0, "status_repeated_route0",
      "Advances the current column by 4, then transfers source 0x2fcf2c8 through 0x1dc10 or clears through 0x1df00; rectangle width 8, height 4.")
label(0x00020520, "status_repeated_route1",
      "Advances the current column by 2, then transfers source 0x2fcf528 through 0x1dc10 or clears through 0x1df00; rectangle width 12, height 4.")
label(0x00020570, "status_repeated_route2",
      "Advances the current column by 2, then transfers source 0x2fcf828 through 0x1dc10 or clears through 0x1df00; rectangle width 12, height 4.")
label(0x000205c0, "status_repeated_route3",
      "Advances the current column by 2, then transfers source 0x2fcf628 through 0x1dc10 or clears through 0x1df00; rectangle width 12, height 4.")
label(0x00020610, "status_repeated_route4",
      "Advances the current column by 2, then transfers source 0x2fcf928 through 0x1dc10 or clears through 0x1df00; rectangle width 12, height 4.")
label(0x00020660, "status_block_route0",
      "Preserves the current origin and transfers source 0x2fcf9e4 through 0x1dc10 or clears through 0x1df00; width 16, height 4.")
label(0x00020690, "status_block_route1",
      "Preserves the current origin and transfers source 0x2fcf308 through 0x1dc10 or clears through 0x1df00; width 16, height 4.")
label(0x000206c0, "status_block_route2",
      "Preserves the current origin and transfers source 0x2fcf388 through 0x1dc10 or clears through 0x1df00; width 28, height 4.")
label(0x000206f0, "status_block_route3",
      "Preserves the current origin and transfers source 0x2fcf4a8 through 0x1dc10 or clears through 0x1df00; width 16, height 4.")
label(0x00020720, "status_block_route4",
      "Preserves the current origin and transfers source 0x2fcf7a8 through 0x1dc10 or clears through 0x1df00; width 16, height 4.")
label(0x00020750, "status_block_route5",
      "Preserves the current origin and transfers source 0x2fcf688 through 0x1dc10 or clears through 0x1df00; width 16, height 4.")
label(0x00020780, "status_block_route6",
      "Preserves the current origin and transfers source 0x2fcf588 through 0x1dc10 or clears through 0x1df00; width 20, height 4.")
label(0x000207b0, "status_block_route7",
      "Preserves the current origin and transfers source 0x2fcf888 through 0x1dc10 or clears through 0x1df00; width 20, height 4.")
label(0x000207d8, "status_block_route8",
      "Preserves the current origin and transfers source 0x2fcf708 through 0x1dc10 or clears through 0x1df00; width 20, height 4.")
label(0x000207e0, "status_transition_route",
      "Preserves the current origin; attributed mode transfers 0x2fcf988 through 0x1dc90 as 23x2, while the other mode transfers 0x2fcf708 through 0x1dc10 as 20x4; absent sources clear through 0x1df00.")
label(0x00020840, "attributed_status_routes",
      "Eight current-origin source-or-clear routes use sources 0x2fcfa64 through 0x2fd0634, helper 0x1dc90 or 0x1df00, widths 24,31,g5+31,g3+31,28,24,29, and heights 8 except route 3 height 4.")
label(0x000209c0, "attributed_status_routes_alt",
      "Two current-origin source-or-clear routes use sources 0x2fd09a4/0x2fd07f4 through 0x1dc90 or 0x1df00, with widths 28/27 and height 8.")
label(0x000218f0, "status_loop_entry_reset",
      "Clears the entry fill value, conditionally resets for nonnegative status, writes 0x8000 to the four latch markers at 0x504d2c..0x504d32, and clears 0x1800000.")
label(0x0002196c, "status_low_latch_upload",
      "For latch <= 8, uploads source 0x2fe8fc4 through 0x1de80 at column 0, row latch-8, as 0x40x8 with attribute mask 0x40.")
label(0x000219a8, "status_mid_latch_route",
      "Handles latches 9..20 at row latch*4-36, uploads source 0x2feab34 through 0x1de00 as 0x40x4, and updates masked 0x1ff generator state.")
label(0x00021a1c, "status_upper_latch_routes",
      "Renders latches 21..95 from source 0x2fda1d0 through 0x1dc10 at column 0, row latch*4-84, as 0x40x4; latches above 95 clear eight marker words at 0x504d24..0x504d32.")
label(0x000211f0, "weapon_record_dispatch",
      "Clamps the asset selector to 0..9, indexes records at 0x20b50 with 0x68-byte stride, selects one of eight handlers, and falls back to handler 0x218a0.")
label(0x00021240, "weapon_three_point_handler",
      "Renders a 31x(selector+31) status block at (3,8), then writes three marker points using table offsets 0x114, 0x118, or 0x110 and the selected text plane.")
label(0x000214bc, "weapon_five_marker_handler",
      "Renders at (1,8), then writes five marker entries from table offset 0x114 starting at the supplied coordinate with value 0x2674.")
label(0x00021580, "weapon_irregular_marker_handler",
      "Renders at (3,8) and, for the active handler kind, writes marker value 0x2674 in runs of 2, 4, and 4 from table offset 0x114.")
label(0x00021784, "weapon_three_quad_marker_handler",
      "Renders at (2,8) and writes three four-entry marker runs from table offset 0x110 at the supplied coordinates.")
label(0x000228f0, "status_tile_pattern_writer",
      "Writes a 16x7 tile pattern (112 entries) to plane 0x1000000 with values 0xc000|(0x1488+index), wrapping rows modulo 64.")
label(0x00022970, "status_wide_tile_pattern_writer",
      "Writes one of three 2-row patterns at bases 0x1000000/0x1000034 with widths 23/29/19 and attribute mask 0xc000.")
label(0x00023410, "status_mode_renderer",
      "For modes 0..4, 7, or 9 with gate 0, draws a 2x4 block through 0x1dd80 from table 0x2ea289c when the status low nibble is zero, and advances masked generator/status state.")
label(0x00023510, "status_strip_reset",
      "Uploads a 0x40x4 zero-source strip through 0x1dfd0, clears 0xfff halfwords at 0x100c000, and resets latch state at 0x504d26/0x504d24.")
label(0x00023560, "status_string_glyph_selector",
      "Scans the NUL-terminated status string for lowercase characters, selects its first or second character for font mode 0/1, and renders through 0x1d310 with attributes 0x4000 while preserving origin 0x504d40/44.")
label(0x0009d334, "geometry_flagged_state_packet",
      "When object flag bit 1 is set, emits a 13-word packet at FIFO 0x884000 using the masked state nibble and derived word, then publishes the board pointer at 0x801008+0x34.")
label(0x0009d454, "geometry_clear_flag_packet",
      "Emits a fixed 9-word packet at FIFO 0x884000, reads board state, publishes pointer 0x801008+0x34, and writes frame slot 0x804000 with flag-dependent tail 0x40005c/0x40002c.")
label(0x0009d730, "geometry_second_flagged_state_packet",
      "When object flag 0x1dd bit 1 is set, emits the 13-word command-29/19/18 packet at 0x884000 using the masked state nibble and derived word, then publishes frame value with tail 0x40009c.")
label(0x0009d858, "geometry_second_clear_flag_packet",
      "Emits the fixed 9-word FIFO packet and writes frame slot 0x50 or 0x60, selecting tail offsets 0x58/0x68 from object flag 0x1dd.")
label(0x0009dc64, "geometry_third_clear_flag_packet",
      "Emits the fixed 9-word FIFO packet and writes frame slot 0x80 or 0x90, selecting tail offsets 0x88/0x98 from object flag 0x1df.")
label(0x0009db3c, "geometry_third_flagged_state_packet",
      "When object flag 0x1df bit 1 is set, emits the same 13-word command-29/19/18 packet at 0x884000 with the third route's derived word and frame tail 0x40009c.")
label(0x0009ddac, "geometry_post_state_gate",
      "Writes FIFO command 6, updates the frame gate from the three countdowns at 0x562c9c/0xa0/a4, and calls startup argument 0x114c only when all are 30 and the gate was clear.")
label(0x000238a0, "geometry_object_alternate_update",
      "Sends FIFO commands 0x1d and 0x1e at 0x884000, applies the 0x40200000 float bias, updates object offsets from the two responses, and clears object state bytes 0x18/0x19.")
label(0x00023980, "geometry_object_variant_preamble",
      "Sends command 0x0a to FIFO 0x884000 and selects the transform path when object fixed-point field 0x172 is in (0x150000,0x190000] and response delta exceeds 0x1b800000.")
label(0x00023ce8, "geometry_position_delta_clamp",
      "Clamps the signed position delta against the halfword limit, suppresses negative motion when global 0x503a60 is clear, stores the result as a halfword, and returns through 0x23d5c.")
label(0x00024460, "geometry_object_response_selector",
      "Selects table 0x2be0088 using state-derived indices doubled, direct, or halved under signed position thresholds; otherwise returns fixed fallback pointers 0x40002c, 0x49c980, or 0x49c984.")
label(0x00024eb4, "geometry_object_state_packet",
      "Looks up fields with helper 0x1cac8(10,24), emits a seven-word command-31 packet at 0x884000, consumes the response through 0x1e370, and updates status via 0x1f080 when active or uninitialized.")
label(0x0009de50, "geometry_result_builder_primary",
      "Uses selector records at 0x562436 with 12-byte stride, exchanges four-word request 38 data at 0x884000, mirrors three response fields at offsets 0/4/8 and 0x10/14/18, then emits request 31 and consumes one result at 0x9e240.")
label(0x0009e880, "geometry_result_builder_followup",
      "Handles flag-dependent request 10 or fallback fields at object offsets 0x184/0x34, emits common request 31, then follows with requests 29 and 30; request 29 toggles IEEE sign bit 31 and request 30 reads table 0x562cb0.")
label(0x000240dc, "geometry_clip_call_sequence",
      "Issues four seven-word clip calls through 0x701a0 using fixed geometry base 0x400028, then publishes frame data at 0x804000+0x400028 under control 0x800010=0x101.")
label(0x00024cc8, "geometry_mode_zero_clip_sequence",
      "Emits a 15-word FIFO prefix at 0x884000, initializes frame offsets 0xb0/0xbc, and issues four fixed clip calls through 0x701a0 before publishing the frame.")
label(0x00024540, "geometry_object_clip_sequence",
      "Issues four command-6 clip calls through 0x701a0 using frame offsets 0x50/0x54, FIFO 0x884000, and geometry base 0x400028, then publishes at 0x804000/04.")
label(0x0003403c, "geometry_object_profile_projection_emitter",
      "Observed object-packet emitter: follows the shared 0x2f/0x16/0x15/0x14 prefix with 0x3a, then issues the 0x1f XZ-length request and forwards its response into the 0x0a scalar request.")
label(0x000346f0, "geometry_object_state_transform_emitter",
      "Observed object-packet emitter: follows the shared tagged prefix with 0x3a and enters the 0x10/0x12 state setup before the later 0x2f/0x20 response copies modeled in recovered_geometry_object_packet.c.")
label(0x00034de8, "geometry_object_state_response_emitter",
      "Observed object-packet emitter: follows the shared tagged prefix with a standalone 0x20 readback; the returned state-tail words are copied into the local object record.")
label(0x00034b00, "geometry_object_late_response_continuation",
      "Observed continuation of the 0x346f0 path: emits the second 0x2f/0x20 groups and stores response triplets at record offsets 0x158..0x160 and 0x164..0x16c.")
label(0x00070000, "geometry_command_packet_variant",
      "Builds an 18-word packet with paired coordinates around g3, header 0x01540601/0x7f000000/0x3f800000, and a zero trailer; g6 is unused by this variant.")
label(0x00079d20, "secondary_transition_selector",
      "When gate equals 1, selects transition 2 for object state 7 and transition 1 otherwise; all other gates return without selecting a transition.")
label(0x0009d1ec, "geometry_command19_branch_primary",
      "Emits command 19 at FIFO 0x884000 with constants 0x3ada740e/0x3f800000; zero object flags use 0x3bc49ba6 and countdown 0x90, while rearm uses 0x3b03126f and display helper 0x1d210.")
label(0x0009d59c, "geometry_command19_branch_mirror",
      "Mirrored command-19 route first emits 0xbe962fc9/0xbdf92c60, then uses 0x3ada740e or 0x3bc49ba6/0x3b03126f based on flags and counters 0x94/0xa0.")
label(0x0009d9a0, "geometry_command19_branch_third",
      "Third command-19 route first emits 0xbd888889/0xbdf92c60, then uses the shared 0x3ada740e and rearm constants with counters 0xa4/0x98 and display helper 0x1d210.")
label(0x000df2f4, "geometry_dual_distance_predicate",
      "Accepts only when the first floating-point residual distance is strictly less than the second; equality, greater-than, and NaN reject.")
label(0x000df120, "geometry_projection_y_window_gate",
      "Accepts selected Y only within the inclusive signed interval [window base, window base plus extent].")
label(0x0006fb90, "geometry_record_initializer",
      "Clears a 0x54-byte record, copies eleven template words into aligned fields, stores association or sentinel 999, and initializes the second association field to 999.")
label(0x00020ae0, "hardware_strip_clear",
      "Fills 0x5ff words at 0x100d000 with either 0xffff or zero based on mode, then returns through stub 0x20b48 with the fill register cleared.")
label(0x00022d30, "hud_reset_route",
      "Fills 4-halfword groups at 0x100c940 for caller g1+31 groups, clears four status fields, reduces the generator modulo 5, and uses fallback 0x503a98+4 only when the result exceeds 3.")
label(0x00022c70, "plane_full_clear_thunks",
      "Clears 0xfff words at either plane base 0x1000000 or 0x1004000, with variant-specific return stubs 0x22ca4/0x22ce4.")
label(0x000e3830, "text_two_digit_formatter",
      "Formats nonnegative values as two decimal digits, saturating values above 99 to 99; negative values produce no output.")
label(0x000201a0, "video_profile_upload",
      "Uploads from 0x1004000 through helper 0x1bc90 to the profile-selected destination 0x1fcfd20/0x1fd49d0/0x1fd1520 using 0x40 halfwords per row and caller g17+31 rows.")
label(0x0001fbe0, "status_value_renderer",
      "Negative values use block source 0x2fe17ec and glyph table 0x2ea1fd0 with 4x3 glyphs and index ((value-0x30)&0xf); nonnegative values clear 25x3 with helper 0x1df00.")
label(0x0001fc30, "status_scoreboard_renderer",
      "Normalizes sign-bit 0x8000 values to zero, uses digit table 0x2ea1e50 with 4-byte entries, and early-returns for state 0/mode 4; separator/suffix sources are 0x2fe158a/0x2fe157a.")
label(0x0001fa00, "continued_message_renderer",
      "Selects message 0x1f9e0, calls helper 0x1da90, preserves the caller column, and uses row 20.")
label(0x0001fa30, "status_panel5_source_fill",
      "Uses source 0x2fe053a/helper 0x1dc10 when present, otherwise fill helper 0x1df00; column/row 2,20, width caller value plus 31, height 5.")
label(0x0001fa80, "status_panel6_source_fill",
      "Uses source 0x2fe099a/helper 0x1dc90 when present, otherwise fill helper 0x1df00; column/row 8,10, width caller value plus 31, height 5.")
label(0x0001f4c0, "status_panel_two_block_builder",
      "Uses source 0x2fe01d4 at rectangle 4,10,5,5; selects table 0x2ea2010 by low nibble after subtracting 0xd0; second rectangle is 28,20,8,5.")
label(0x0001f640, "fixed_panel_transfer",
      "Calls helper 0x1dc90 at the current position with dimensions 6 by 8 from source 0x2fded40.")
label(0x0001f660, "fixed_panel_transfer_alt",
      "Calls helper 0x1dc90 at the current position with dimensions 6 by 8 from source 0x2fdeda0.")
label(0x0001f9c0, "clear_g14_indirect_return",
      "Clears g14, branches through g0, and returns through stub 0x1f9d4.")
label(0x00020160, "clear_g14_indirect_return_alt",
      "Clears g14, branches through g0, and returns through stub 0x20174.")
label(0x00023620, "status_indexed_glyph_wrapper",
      "Calls helper 0x1cd18 and saves/restores origin globals 0x504d44 (column) and 0x504d40 (row).")
label(0x000227b0, "status_grid_initializer",
      "Selects on phase modulo 192, uses source 0x2fe8fc4 and helpers 0x1de80/0x1de00, and builds 32 cells in a 16 by 8 region.")
label(0x00022840, "status_patterned_fill",
      "Writes destination 0x100d000 plus 2 times the start row, repeats 192 times, uses four fill and four solid repetitions, and masks generator/state values to 0x1ff.")
label(0x0007e390, "geometry_object_record_transform",
      "Uses object offset 0x200 with 0x20-byte stride and records at 0x562cb0 with 0x30-byte stride; observed literals include 0x40c00000, 0x42f00000, 0x3ff80000, 0xffff, and 0xffffa000, with selectors 29 and 30.")
label(0x0007ea10, "geometry_object_state_commit",
      "Observed state gate requires 0x509b30 > 0x1f3, object halfword 0x172 == 31, object fields 0x64 == 6, and 0x504e48 == 3 before writing state values.")
label(0x0000c57a0, "result_node_id_format_string")

print("Virtual-On i960 annotations applied")
