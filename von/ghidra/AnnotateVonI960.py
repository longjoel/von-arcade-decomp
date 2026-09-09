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
      "First post-register-stack startup call reached from reset continuation at 0xa28. Seeds startup globals and timeout, drains the one-count frame guard, then calls 0x186c0, 0x18960, and 0x18a10 before entering the mode loop.")
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
label(0x000186c0, "startup_pre_dispatch_helper",
      "Publishes startup command 3, clears the command byte, and invokes the 16-byte clear helper on the device command buffer at 0x5770c0.")
label(0x00018a10, "startup_status_helper_18a10",
      "Classifies 0x1d00028 into mode 1/2/3, publishes 0x503a08, then opens the 120-call 0x18ab0 service loop only when 0xc5870 returns zero and startup mode is 5.")
label(0x00018ab0, "startup_state_service",
      "Calls the 0x28de8 frame poll, updates the latest/profile-4 extrema state, and always continues through the 0x2d60 post-service helper.")
label(0x00018538, "startup_status_service")
label(0x000294b0, "startup_warning_or_text_service")
label(0x000f50a8, "startup_input_formatter")
label(0x000188a0, "startup_device_write_loop")
label(0x00018918, "startup_return_thunk_18918",
      "Moves the private continuation through g1, clears g14, returns zero through bx (g1), and rejoins at 0x18928.")
label(0x00018960, "startup_system_setup_18960",
      "Runs the ordered I/O, video, asset, audio, text, geometry, stage-table, and queue services before the 0x2440 validation wrapper.")

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
label(0x00002440, "io_self_test_wrapper",
      "Runs the input initializer, validates the two startup records through the 0x2080/0x2040 helpers, conditionally clears 0x50240c, and performs the second CRC/device-ready phase.")
label(0x00002850, "controller_command_upload")
label(0x00002990, "controller_indexed_command_upload")
label(0x00002c70, "input_initializer_select")
label(0x00002cb0, "failure_input_sampler_select")
label(0x00002d60, "input_sampler_select")
label(0x00002da0, "input_controller_sample_and_pack",
      "Per-frame 315-5649 sample: averages the eight-byte history at 0x502490, reads controller ports, and packs the active-low state into 0x502498-0x5024bc.")
label(0x000034c0, "input_state_reset_fields")
label(0x00003540, "input_state_step_3540",
      "Clears the transient input byte, then increments the packed state while bit 3 of 0x502482 is set, otherwise resets it to zero.")
label(0x00003a38, "input_byte_state_parser")
label(0x00003ae0, "input_dual_byte_parser")
label(0x00003ba0, "controller_timing_status_check")
label(0x000183b8, "device_address_classify")
label(0x00018438, "device_mode_pair_validate")
label(0x00018488, "host_byte_queue_initialize")
label(0x0001c2c0, "text_video_transfer_wrapper",
      "Snapshots argument/context and four FP registers, then builds the 512-halfword 0x01008000 workspace and 0x0100a000 metadata block.")
label(0x0001cbb8, "text_control_character_handler",
      "Handles TAB (column rounded to the next eight-cell boundary with wrap at 61) and LF (return to origin column), incrementing row only through 46; other controls are inert.")
label(0x000226b0, "startup_state_service_gate_226b0",
      "Subtracts 10 from the service counter, selects sentinel/transfer/clear/no-op routes, and increments 0x504d10 on return.")
label(0x00025040, "state_dispatch_25040",
      "Initializes record fields from 0x50249c/0x5024a4, dispatches explicit service/state cases, and enters the common record-tail update.")
label(0x00027550, "geometry_record_transform_service",
      "Seeds a geometry record, selects a profile asset from mode/record kind, and connects the profile helper, stage selector, and 0x6f600 producer.")
label(0x0001d090, "text_special_glyph_writer")
label(0x0001d1d0, "text_alternate_string_walker")
label(0x0001d210, "text_special_glyph_string_walker")
label(0x0001d7d0, "text_attributed_glyph_string_walker",
      "Scans after the first byte for lowercase ASCII, selects glyph mode 2 or 3, and emits each byte through 0x1d310 with attribute bit 14 set.")
label(0x0001d570, "text_glyph_block_writer",
      "Normalizes the character, selects special or descriptor-backed glyph data, and writes a two-row plane-0 tile block with bit 15 forced before updating the text column.")
label(0x0001d6a0, "text_glyph_writer_1d6a0",
      "Treats byte 0x21 as an origin-column/new-row control; otherwise selects the 0x2ea11d0 glyph descriptor, writes two plane-0 rows, and applies the glyph-index 0x5c cursor adjustment.")
label(0x0001d880, "text_glyph_table_match_writer")
label(0x0001d930, "text_attributed_glyph_table_match_writer",
      "Scans after the first byte for lowercase ASCII, selects glyph mode 0 or 1, and emits each byte through 0x1d310 with attribute bit 14 set.")
label(0x0001dbf0, "text_glyph_string_walk_1dbf0",
      "Walks a NUL-terminated string one byte at a time and dispatches each nonzero byte to the 0x1d6a0 glyph writer.")
label(0x0001dc10, "text_tile_plane_writer")
label(0x0001dc90, "text_attributed_tile_plane_writer")
label(0x0001dd10, "text_patterned_tile_plane_writer")
label(0x0001df00, "text_tile_region_clear")
label(0x0001df70, "text_plane_region_clear")
label(0x0001dfd0, "text_plane1_region_clear",
      "Fills an explicit width-by-height rectangle in plane 0x01002000 with unchanged g14 values; signed-positive dimensions gate both loops.")
label(0x0001efc0, "text_home_dispatch_variant_1efc0",
      "Homes columns 16/16 and row 2, then selects the same 32x6 0x1df00 clear or 0x1dc90 emit path as 0x1ef70.")
label(0x0001f080, "text_panel_setup_1f080",
      "Homes columns 19/19 and row g9+31, then selects source 0x2fe077e as 23x5 through 0x1dc90 or a 23x5 clear through 0x1df00.")
label(0x0001e030, "text_status_render_context",
      "Saves the 0x50-byte register/FP frame; nonzero 0x1d00034 renders 0x2fd81ec as 19x2, while secondary value 1 selects 0x2fd8170/14x2 plus 15x2 clear and other values select 0x2fd81a8/16x2 plus 17x2 clear.")
label(0x00029a80, "audio_device_table_clear")
label(0x00029ae8, "audio_service_table_reset")
label(0x00029b20, "audio_device_table_upload",
      "Loops over 23 records, masks selector/exponent-derived indices, reads ROM halfwords, stores them at 0x1802010 + 2*record, conditionally selects the 0x180203e status halfword (zero skips, negative clamps to 0x7fff), then commits nonzero 0x51a0c0 pointer/value pairs.")
label(0x00029c08, "audio_command_value_clamp")
label(0x00029ca0, "audio_device_buffer_copy")
label(0x00029dc0, "upload_masked_blend_planes",
      "Runs three 32-word plane kernels for eight outer passes; mode bits 0-2 select fade versus scale forms, with pair-2 receiving the extra 0x180 stride at each plane transition.")
label(0x00029f60, "upload_direct_planes",
      "Mode-zero upload path: applies one fade/scale factor to all three planes over eight 32-word passes with uniform 0x200-byte-per-pass pointer cadence.")
label(0x0002a00c, "upload_direct_fade_kernel")
label(0x0002a430, "audio_scsp_settle_delay",
      "Short volatile delay between SCSP control writes; recovered as four countdown iterations.")
label(0x0002a458, "audio_scsp_fifo_send_u16",
      "Host-side SCSP command producer. Queues 0xae, high byte, low byte; 0xff is a one-byte special command.")
label(0x0002a4e0, "audio_scsp_fifo_enqueue",
      "Special-cases low-halfword 0xff as a one-byte command; otherwise applies the mode-1/status-2 suppression gate, reserves one or three ring bytes through 0x2a458, enqueues them via 0x2a4a8, and requests service through 0x1348.")
label(0x0002a5f0, "audio_scsp_fifo_send_u16_idle_gate",
      "Sibling command producer with the mode-1/board-status-zero suppression gate.")
label(0x0002a690, "audio_scsp_send_level",
      "Clamps signed level to 1..127 and emits the 0xa0, selector-1, level frame.")
label(0x0002a870, "audio_scsp_send_selector_zero",
      "Emits the 0xa0, selector-0, low-byte frame.")
label(0x0002a8a0, "audio_scsp_initialize",
      "Initializes the 64-byte host FIFO and writes the recovered SCSP control sequence 0,0,0,0x40,0x4e,0x37 before queuing 0xff.")
label(0x00001348, "audio_scsp_service_request",
      "Loads fixed continuation 0x1370 into g14/g0, clears g14, raises interrupt-control bit 10 in the host mirror and MMIO register, then tail-jumps through g0 to request SCSP FIFO service.")
label(0x000016dc, "audio_scsp_fifo_consumer",
      "Interrupt route 0x400: consumes one queued byte only when the FIFO is nonempty and SCSP status bit 0 is set, then writes it to SCSP command port 0x009c0000.")
label(0x00501cd0, "audio_interrupt_control_mirror")
label(0x0051aa70, "audio_fifo_read_index")
label(0x0051aa74, "audio_fifo_write_index")
label(0x0051aa80, "audio_fifo_bytes_64")
label(0x009c0000, "scsp_command_port")
label(0x009c0004, "scsp_status_control_port")
label(0x000292d8, "geometry_command_stream_upload")
label(0x000294b0, "geometry_profile_upload_setup",
      "Fixed profile-3 setup prefix: programs 0x800160/0x800070/0x800080/0x800030, calls 0x292d8 with headers 0/32 from 0x293b0, then emits the 0x800090/0x804000/0x8000a0 handshake and finishes through 0x28d30.")
label(0x000295d0, "geometry_profile_upload_variant",
      "Alternate fixed profile stream: uses 0x46000000, calls 0x292d8 with headers 0/32 from 0x293b0, programs 0x800030, emits 0x3f333333/0xbf000000 and 0x3f000000 through 0x804000, then finishes through 0x28d30.")
label(0x000296d0, "geometry_service_state_initialize",
      "Initializes service slots at 0x515098-0x5150b4, then calls 0x29778 with head 0x5150c0/stride 0x100 and 0x29738 with head 0x5190c0/stride 0x40.")
label(0x00029738, "geometry_pointer_table_initialize")
label(0x00029778, "geometry_pointer_table_initialize_alt")
label(0x00029d50, "geometry_tile_buffer_transform")
label(0x0002b430, "geometry_object_record_dispatch",
      "Indexes 0x51c5b0 records with 0x54-byte stride, repeats for the record +0x08 count, routes slot-left < slot-right through the 0x2b420 table or otherwise calls 0x6fd50, and increments the 0x51bb30 slot count. Match capture confirms the surrounding polygon-ROM submission path.")
label(0x0002be30, "geometry_frame_service_initialize",
      "Calls the alternate profile upload 0x295d0, emits FIFO selectors 8/16, clears 0x50427a and 0x503c7a, calls 0x2a990(0xd000,0), advances/reset counters, and dispatches phase % 12 through 0x2bee4.")
label(0x0002d9a0, "geometry_transform_dispatch",
      "Calls the alternate profile upload and 0x2a990, emits FIFO selectors 8/16/10/31/29/30/10/20/21/18, and stores response-derived fields at 0x51aad0–0x51aae4.")
label(0x0002db0c, "geometry_transform_zero_halfword_state",
      "Stores the zeroed g14 halfword at 0x51aad2 and 0x51aad4 after the first response-derived real calculations; the adjacent 0x51aad0 slot receives r4.")
label(0x0002db20, "geometry_transform_first_state_store",
      "Stores r4 to 0x51aad0, then converts r6/g13 and writes the full-word response-derived fields at 0x51aad8, 0x51aadc, and 0x51aae0.")
label(0x0002db48, "geometry_transform_final_state_store",
      "Stores the final g2-derived value to 0x51aae0 before the selector-30 response request; the later 0x51aae4 store completes the seven-slot state output.")
label(0x0002e1c8, "geometry_status_continuation_trampoline",
      "Loads return stub 0x2e1d4 into g14, moves it to g0, clears g14, and returns through bx(g0).")
label(0x0002e1e8, "geometry_status_continuation_trampoline_alt",
      "Loads return stub 0x2e1f4 into g14, moves it to g0, clears g14, and returns through bx(g0).")
label(0x0002e320, "geometry_frame_packet_emit",
      "Normalizes a geometry selector, loads its packet tuple, and emits the 0x804000 command record.")
label(0x0002e450, "geometry_object_update_variant_a",
      "Updates one object-state variant, emits its geometry record, and invokes the selected device callback.")
label(0x0002e590, "geometry_object_update_variant_b",
      "Updates a second object-state variant using the shared geometry record skeleton.")
label(0x0002e6f0, "geometry_object_update_variant_c",
      "Updates a third object-state variant using the shared geometry record skeleton.")
label(0x0002e860, "geometry_object_update_variant_d",
      "Updates a fourth object-state variant using the shared geometry record skeleton.")
label(0x0002e990, "geometry_object_update_variant_e",
      "Updates a fifth object-state variant using the shared geometry record skeleton.")
label(0x0002eaa0, "geometry_object_update_variant_f",
      "Updates a sixth object-state variant using the shared geometry record skeleton.")
label(0x0002ebb0, "geometry_object_update_variant_g",
      "Updates a seventh object-state variant using the shared geometry record skeleton.")
label(0x0002ece0, "geometry_object_update_variant_h",
      "Updates an eighth object-state variant and joins the shared object callback path.")
label(0x0002ef90, "geometry_object_callback_state_dispatch",
      "Selects one of four object callbacks from the object state field at offset 0x174.")
label(0x0002f010, "geometry_object_motion_variant_a",
      "Advances an object motion state, updates frame fields, and returns through a supplied continuation.")
label(0x0002f260, "geometry_object_motion_variant_b",
      "Parallel object motion/update variant using the shared geometry callback skeleton.")
label(0x0002f360, "geometry_object_motion_variant_c",
      "Advances the shared object timer/state and emits the common geometry callback result.")
label(0x0002f460, "geometry_object_motion_variant_d",
      "Updates object position/state and selects the next device callback by motion phase.")
label(0x0002f580, "geometry_object_motion_variant_e",
      "Updates motion phase, interpolated geometry coordinates, and the shared callback state.")
label(0x0002f930, "geometry_object_motion_variant_f",
      "Runs the motion completion callback and derives the next object phase/geometry mode.")
label(0x0002fa20, "geometry_object_motion_continuation_a",
      "Continuation trampoline for motion geometry output; returns through the supplied callback address.")
label(0x0002fb20, "geometry_object_motion_variant_g",
      "Dispatches phase-specific motion callbacks and selects the corresponding geometry result.")
label(0x0002fd50, "geometry_object_motion_continuation_b",
      "Continuation trampoline for the second motion geometry output path.")
label(0x0002fe30, "geometry_object_motion_variant_h",
      "Updates object phase and geometry coordinates, then selects the active callback result.")
label(0x0002ff80, "geometry_object_motion_variant_i",
      "Advances object motion and phase fields while updating the shared geometry output window.")
label(0x000300c0, "geometry_object_motion_variant_j",
      "Dispatches the next motion phase and publishes the resulting geometry callback state.")
label(0x00030230, "geometry_object_motion_continuation_c",
      "Continuation trampoline that resets motion state and returns through a supplied callback address.")
label(0x000303e0, "geometry_object_motion_phase_reset_a",
      "Invokes the phase callback and resets the object motion fields when the phase is complete.")
label(0x00030420, "geometry_object_motion_phase_reset_b",
      "Parallel phase-reset helper using the shared callback and motion-field initialization sequence.")
label(0x00030460, "geometry_object_motion_variant_k",
      "Advances motion coordinates and phase state through the selected geometry continuation.")
label(0x00030590, "geometry_object_motion_variant_l",
      "Parallel motion-coordinate update using the neighboring geometry profile tables.")
label(0x00030660, "geometry_object_motion_variant_m",
      "Dispatches motion phases, selects geometry profiles, and updates the object callback result.")
label(0x00030c20, "geometry_object_motion_continuation_d",
      "Continuation trampoline selecting a geometry profile and returning through the caller continuation.")
label(0x00030d40, "geometry_object_motion_continuation_e",
      "Continuation trampoline for the alternate geometry profile table and phase update path.")
label(0x00030e40, "geometry_object_motion_variant_n",
      "Initializes a motion phase from the selected geometry profile and publishes callback state.")
label(0x00030ff0, "geometry_object_motion_variant_o",
      "Advances motion state, selects a profile by phase, and updates the object's callback result.")
label(0x00031210, "geometry_object_motion_variant_p",
      "Initializes motion from a combined profile/phase table and publishes the next callback state.")
label(0x000313e0, "geometry_object_motion_variant_q",
      "Selects an indexed geometry profile and advances the object through its callback phase.")
label(0x000315a0, "geometry_object_motion_variant_r",
      "Emits the shared geometry packet and advances the startup/motion phase state.")
label(0x000316d0, "geometry_object_motion_variant_s",
      "Parallel geometry packet emitter using the alternate callback table entry.")
label(0x000317f0, "geometry_object_motion_variant_t",
      "Parallel geometry packet emitter using the shared phase and callback state path.")
label(0x00031910, "geometry_object_motion_variant_u",
      "Selects indexed geometry profiles and updates the object frame/result state.")
label(0x00031ab0, "geometry_object_motion_variant_v",
      "Selects a four-way geometry profile, updates motion timing, and advances the object phase.")
label(0x00031d20, "geometry_object_motion_variant_w",
      "Runs the paired geometry-profile timing path and transitions the object to the next phase.")
label(0x00032120, "geometry_object_motion_variant_x",
      "Updates profile-dependent motion state and performs the associated phase reset/transition.")
label(0x00032330, "geometry_object_motion_variant_y",
      "Selects the next geometry profile, updates frame timing, and publishes the object result state.")
label(0x000324e0, "geometry_object_motion_phase_helper_a",
      "Invokes the phase callback and derives the per-object animation timing value.")
label(0x00032540, "geometry_object_motion_phase_helper_b",
      "Invokes the alternate phase callback and clears the transient geometry result state.")
label(0x00032810, "geometry_object_state_machine",
      "Copies source-record fields, emits the bounded packet-31/packet-10 prefix, publishes response fields, then dispatches the 0x1b2 state through fourteen arms at 0x32968.")
label(0x000371e0, "geometry_frame_step",
      "Decrements object timers, updates fixed-point fields, and dispatches the phase at 0x172 through the table at 0x37130 after the 0x25040/0x24f98 gate.")
label(0x00032968, "geometry_object_state_dispatch_table",
      "Fourteen internal object-state arms selected from the state field at offset 0x1b2.")
label(0x00036460, "geometry_object_profile_state_variant_a",
      "Selects a profile-dependent object state, initializes geometry fields, and returns through a continuation.")
label(0x00036690, "geometry_object_profile_state_variant_b",
      "Parallel profile/state initializer using the alternate transition conditions.")
label(0x000367f0, "geometry_object_profile_state_variant_c",
      "Initializes the next profile/state combination and returns through the shared continuation.")
label(0x00036980, "geometry_object_profile_state_variant_d",
      "Initializes the fourth profile/state combination and updates the object transition fields.")
label(0x00036af0, "geometry_object_profile_state_variant_e",
      "Adjusts object motion timing and selects the next state through a supplied continuation.")
label(0x00036bb0, "geometry_object_transform_variant_a",
      "Transforms object coordinates and applies the shared position/state completion rules.")
label(0x00036c40, "geometry_object_transform_variant_b",
      "Updates position bounds and transforms the object through the alternate completion path.")
label(0x00036cc0, "geometry_object_transform_variant_c",
      "Transforms object coordinates with the neighboring timing limits and state reset rules.")
label(0x00036d50, "geometry_object_transform_variant_d",
      "Parallel coordinate transform/update path using the adjacent motion timing profile.")
label(0x00036de0, "geometry_object_transform_variant_e",
      "Transforms coordinates and selects the terminal or reset state based on object flags.")
label(0x00036e70, "geometry_object_profile_transition_variant_a",
      "Tests the active profile and advances the object state when the transition predicate succeeds.")
label(0x00036ef0, "geometry_object_profile_transition_variant_b",
      "Initializes a profile transition from object flags and returns through its continuation.")
label(0x00036f90, "geometry_object_profile_transition_variant_c",
      "Parallel profile transition handler with the shared motion/timing update sequence.")
label(0x00037060, "geometry_object_profile_transition_variant_d",
      "Final profile transition handler before the table-backed object callback family ends.")
label(0x00037130, "geometry_object_profile_state_dispatch_table",
      "Fourteen-entry continuation table used by the runtime object phase/state updater.")
label(0x000371e0, "geometry_object_runtime_update",
      "Advances one runtime object through fixed-point motion, phase predicates, and callback/state transitions.")
label(0x00037f50, "geometry_object_runtime_motion_continuation",
      "Continuation-style motion handler; clamps the signed fixed-point coordinate and publishes the selected geometry result.")
label(0x00038340, "geometry_object_resource_motion_variant_a",
      "Consumes the first resource-profile table entry and publishes the object result/phase update.")
label(0x00038490, "geometry_object_resource_motion_variant_b",
      "Parallel resource-profile motion path using the second table entry and timing window.")
label(0x000385f0, "geometry_object_resource_motion_variant_c",
      "Resource-profile motion path that resets the object phase on completion and returns through a continuation.")
label(0x000386c0, "geometry_object_resource_motion_variant_d",
      "Advances the secondary object motion coordinate and applies the corresponding result resource.")
label(0x000388f0, "geometry_object_resource_motion_variant_e",
      "Advances the primary resource phase, applies the profile timing envelope, and clears the transient result on completion.")
label(0x000389f0, "geometry_object_resource_motion_variant_f",
      "Updates the secondary fixed-point coordinate with bounded motion deltas and advances the object phase.")
label(0x00038b30, "geometry_object_pair_packet_update",
      "Emits a paired 0x884000 geometry packet and advances the object coordinate fields at offsets 0x36 and 0x38.")
label(0x00038db0, "geometry_object_service_counter_loop",
      "Processes the object service counter table, dispatches geometry payloads, and advances the service state.")
label(0x00038ef0, "geometry_object_profile_packet_builder",
      "Selects profile records from 0x51ab60, emits coordinate packets through 0x884000, clamps both axes, and advances phase state.")
label(0x000392b0, "geometry_object_displacement_classifier",
      "Classifies the object displacement against fixed-point thresholds and selects the corresponding object phase state.")
label(0x00039410, "geometry_object_service_state_continuation",
      "Checks the four-word service state, updates the active counter slots, and returns through the caller continuation.")
label(0x00039490, "geometry_object_service_motion_update",
      "Handles the three service-motion states, emits paired 0x884000 records, clamps fixed-point deltas, and updates the active counters.")
label(0x00039740, "geometry_object_service_motion_state3_arm",
      "Fall-through state arm of geometry_object_service_motion_update; emits the state-3 paired packet and updates its counter.")
label(0x00039850, "geometry_object_service_motion_variant_g",
      "Dispatches alternating resource records through the geometry producer and advances the object phase.")
label(0x00039910, "geometry_object_resource_remainder_continuation",
      "Publishes the remainder-based resource result and returns through the caller continuation.")
label(0x00039980, "geometry_object_resource_phase_dispatch",
      "Selects phase-specific resource state, publishes the result, and returns through the caller continuation.")
label(0x00039a90, "geometry_geometry_batch_initializer",
      "Initializes a framed 0x884000 batch, programs 0x800010/0x804000, and submits the related geometry records.")
label(0x00039da0, "geometry_selector_packet_builder",
      "Converts the selector with i960 floating-point arithmetic and emits selector-dependent 5/18 geometry packet layouts.")
label(0x0003a140, "geometry_selector_geometry_emitter",
      "Computes the selector-dependent floating-point geometry value and emits the corresponding 5/18 packet records.")
label(0x0003a510, "geometry_scene_update_dispatch",
      "Framed scene/object update that emits profile geometry packets, advances scene counters, and dispatches object effects.")
label(0x0003d520, "geometry_scene_update_dispatch_table",
      "Eight-entry table routing scene update phases to the recovered geometry resource handlers.")
label(0x0003d540, "geometry_fixed_point_clamp_helper",
      "Clamps a floating-point input and writes the corresponding fixed-point limit through the supplied object pointer.")
label(0x0003d5d0, "geometry_service_state_initialize",
      "Clears and initializes the shared 0x51abxx geometry service state and selects the active profile tables.")
label(0x0003d730, "geometry_object_record_update",
      "Updates one active object record: emits the 0x884000 geometry setup, advances profile/service state, applies fixed-point motion and clamp paths, and publishes the resulting coordinate fields.")
label(0x0003e5e0, "geometry_object_profile_state_initialize",
      "Initializes the selected object profile from the shared service cursor, applies profile-specific fixed-point timing/state transitions, and publishes the object phase/result fields.")
label(0x0003eca0, "geometry_record_profile_value_table",
      "Packed halfword profile values indexed by the low 16 bits of a runtime record selector.")
label(0x0003ecd0, "geometry_runtime_record_allocate",
      "Scans the 23-entry runtime record pool for a free slot, initializes its fields, and derives its profile value from the packed selector table.")
label(0x0003ed60, "geometry_runtime_record_allocate_alt",
      "Alternate runtime record allocator using the same 23-entry pool and selector-value table with a different register arrangement.")
label(0x0003edd0, "geometry_runtime_record_update",
      "Finds a free runtime record and writes the caller geometry fields, normalized coordinates, and selector-derived profile value.")
label(0x0003eeb0, "geometry_runtime_record_reset",
      "Finds a free runtime record, emits the reset packet prefix, and clears its payload and profile fields.")
label(0x0003ef50, "geometry_runtime_record_motion_emit",
      "Scans active runtime records, converts packed input components into fixed-point motion values, and emits selectors 8, 13, 29, and 30.")
label(0x0003f120, "geometry_runtime_record_motion_emit_alt",
      "Parallel runtime-record motion emitter using caller-supplied offsets and the same fixed-point conversion and packet format.")
label(0x0003f2b0, "geometry_runtime_record_packet_initialize",
      "Initializes the first available runtime record with the caller geometry tuple and fixed profile constants.")
label(0x0003f380, "geometry_runtime_record_packet_initialize_alt",
      "Initializes the first available runtime record with the alternate profile constants and fixed-point scale.")
label(0x0003f470, "geometry_runtime_record_table_clear",
      "Clears the bounded 0x33c-byte runtime record table and returns through its caller continuation.")
label(0x0003f4e0, "geometry_runtime_record_seed_selector10",
      "Clears the bounded runtime record table, seeds the first slot with selector 10, and returns through its caller continuation.")
label(0x0003f550, "geometry_runtime_record_table_seed_pair",
      "Walks the runtime record table, fills available slots with the requested selector pair, and returns after the bounded scan.")
label(0x0003f5f0, "geometry_runtime_record_seed_command17",
      "Finds a free 0x24-byte runtime record, stores the caller fields, and fills its twelve-word payload from command 17 readbacks.")
label(0x0003f6e0, "geometry_runtime_record_seed_command17_alt",
      "Alternate free-record initializer using command 17 and an explicit selector word at record offset zero.")
label(0x0003f7d0, "geometry_runtime_record_seed_command17_bounded",
      "Finds a free record in the 0x508-byte pool, marks it active, and copies the command 17 payload into its 0x30-byte record area.")
label(0x0003f8d0, "geometry_profile_command5_emit_a",
      "Updates the object coordinates, checks the selector-derived profile value, and submits the first command-5 profile payload through 0x804000.")
label(0x0003fa90, "geometry_profile_command5_emit_b",
      "Parallel command-5 geometry emitter using the second profile payload table at 0x2be02b8.")
label(0x0003fc50, "geometry_profile_command5_emit_c",
      "Parallel command-5 geometry emitter using the third profile payload table at 0x2be04f8.")
label(0x0003fdc0, "geometry_profile_command5_emit_d",
      "Command-5 geometry emitter using the compact three-word profile table at 0x2be04ec and the alternate object register layout.")
label(0x0003ff80, "geometry_profile_command5_emit_e",
      "Parallel command-5 geometry emitter using the profile payload table at 0x2be0738.")
label(0x000400f0, "geometry_profile_command5_emit_f",
      "Parallel command-5 geometry emitter for the next profile payload table and object variant.")
label(0x00040310, "geometry_profile_command5_emit_g",
      "Command-5 geometry emitter with a stack frame, shared profile comparison, and the payload table at 0x2be41d8.")
label(0x000406d0, "geometry_profile_command5_emit_h",
      "Command-5 geometry emitter that submits two successive profile payloads from the 0x2be3eb4 and 0x2be4034 tables while advancing the record selector.")
label(0x000408b0, "geometry_object_packet_variant_a",
      "Emits the command-5 object packet, selects payload words from 0x2be0ef4, and applies the profile-dependent object coordinate increment.")
label(0x00040a80, "geometry_object_packet_variant_b",
      "Emits the command-5/18/21 object packet sequence using the selector table at 0x2be129c and advances the record state.")
label(0x00040bc0, "geometry_object_packet_variant_c",
      "Parallel command-5/18/21 object packet path using the selector table at 0x2be0f9c and its alternate payload constants.")
label(0x00040d00, "geometry_object_packet_variant_d",
      "Emits the command-5/18/19 object packet sequence and submits profile payloads from 0x2be105c.")
label(0x00040e10, "geometry_object_packet_variant_e",
      "Parallel command-5/18/19 object packet path using payloads from 0x2be135c.")
label(0x00040f50, "geometry_object_packet_variant_f",
      "Emits the command-5/18/19/30/21 object packet sequence and selects the payload table at 0x2be17dc.")
label(0x00041090, "geometry_object_motion_packet_variant_a",
      "Updates the active object motion fields with fixed-point interpolation, then emits the command-5/18/19/21 packet sequence from 0x2be14dc.")
label(0x00041340, "geometry_object_motion_packet_variant_b",
      "Emits the standard command-5 geometry packet after coordinate accumulation, using the profile payload table at 0x2be159c.")
label(0x000414b0, "geometry_object_motion_packet_variant_c",
      "Parallel command-5 geometry packet path using the payload table at 0x2be171c and the shared selector comparison.")
label(0x00041620, "geometry_object_motion_packet_variant_d",
      "State-sensitive command-5/18/19/21 emitter that adjusts object motion fields, selects payloads from the 0x2be2xxx tables, and returns after the shared packet tail.")
label(0x00041800, "geometry_object_motion_packet_variant_e",
      "Parallel command-5 emitter using the alternate selector comparison and the payload table at 0x2be04f8.")
label(0x000419c0, "geometry_object_motion_packet_variant_f",
      "Framed command-5/18/19/21 emitter with fixed-point interpolation and the shared 0x804000 submission sequence.")
label(0x00041c50, "geometry_object_packet_dispatch_table",
      "Indirect dispatch table selecting the recovered object packet and motion variants for the active record state.")
label(0x00041cb0, "geometry_object_packet_batch_emit",
      "Walks the active object packet inputs, applies fixed-point interpolation, emits command 0x202/0x804000 geometry records, and copies the final transformed fields.")
label(0x00041f20, "geometry_runtime_packet_dispatch",
      "Dispatches the 23-entry runtime record pool through the 0x41c50 handler table, then scans the larger pool and emits active command-5/7/9 records.")
label(0x00042320, "geometry_runtime_buffer_record_store",
      "Selects one of the two runtime output buffers, computes its 16-byte record index, and stores the seven caller words.")
label(0x00042460, "geometry_profile_state_table_a",
      "Seven-word profile-state descriptor table consumed by the first state-transition handler family.")
label(0x00042480, "geometry_object_profile_state_variant_a",
      "Updates profile cursor and phase state from the 0x42460 descriptor table, clamps the derived state window, and publishes offsets 0xc2/0xc8.")
label(0x00042670, "geometry_object_profile_state_variant_b",
      "Continuation-style profile state update using the alternate descriptor entry and shared cursor/phase fields.")
label(0x00042760, "geometry_profile_state_table_b",
      "Alternate seven-word profile-state descriptor table for the second transition family.")
label(0x00042780, "geometry_object_profile_state_variant_c",
      "Updates the object profile cursor and phase from the 0x42760 descriptor table and publishes the bounded state window.")
label(0x000428e0, "geometry_object_profile_state_variant_d",
      "Continuation-style alternate profile state update using the 0x42760 descriptor table and phase thresholds.")
label(0x000429d0, "geometry_profile_state_table_c",
      "Six-word profile-state descriptor table consumed by the full profile transition handler.")
label(0x000429f0, "geometry_object_profile_state_transition",
      "Full framed profile transition handler: advances object phase, emits paired command-5/18/19/21 state packets, updates timing fields, and publishes bounded state at offsets 0xc2/c8.")
label(0x000430d0, "geometry_object_profile_state_transition_alt",
      "Continuation-style alternate profile transition using the 0x429e0 descriptor values and the shared phase/timing state.")
label(0x000431a0, "geometry_profile_state_table_d",
      "Six-word profile-state descriptor table for the next transition sibling family.")
label(0x000431c0, "geometry_object_profile_state_variant_e",
      "Profile-state transition variant using the 0x431a0 descriptor table; advances shared cursor timing and clamps object offsets 0xd2/0xd4.")
label(0x00043420, "geometry_object_profile_state_variant_f",
      "Alternate framed profile-state transition using the 0x431b0 descriptor pair and the shared cursor/timing state.")
label(0x00043510, "geometry_profile_state_table_e",
      "Six-word profile-state descriptor table consumed by the next object transition variant.")
label(0x00043530, "geometry_object_profile_state_variant_g",
      "Profile-state transition variant using the 0x43510 descriptor table; initializes phase-dependent object fields and publishes bounded offsets 0xc2/c8.")
label(0x00043680, "geometry_object_profile_state_variant_h",
      "Alternate profile-state transition using the 0x43520 descriptor pair and the shared cursor/timing state.")
label(0x00043780, "geometry_profile_state_table_f",
      "Six-word profile-state descriptor table for the next transition sibling family.")
label(0x000437ac, "geometry_object_profile_state_variant_i",
      "Profile-state transition variant using the 0x43780 descriptor table; clamps and publishes object phase fields at offsets 0xbc/0xc0/0xc4.")
label(0x000438e0, "geometry_object_profile_state_variant_j",
      "Alternate framed profile-state transition using the 0x43790 descriptor pair and the shared cursor/timing state.")
label(0x000439c0, "geometry_profile_state_table_g",
      "Six-word profile-state descriptor table consumed by the next transition variant.")
label(0x000439e0, "geometry_object_profile_state_variant_k",
      "Profile-state transition variant using the 0x439c0 descriptor table; advances shared cursor state and conditionally updates the object phase latch.")
label(0x00043b90, "geometry_profile_state_table_h",
      "Six-word profile-state descriptor table shared by the next transition and cursor-update handlers.")
label(0x00043b00, "geometry_object_profile_state_variant_l",
      "Continuation-style profile cursor transition using the 0x439d0 descriptor pair and returning through a caller-supplied link.")
label(0x00043bb0, "geometry_object_profile_state_variant_m",
      "Profile-state transition using the 0x43b90 descriptor table; handles initial-state setup, phase thresholds, and shared cursor publication.")
label(0x00043cb0, "geometry_object_profile_state_variant_n",
      "Compact profile cursor advance using the 0x43ba0 descriptor pair and shared timing globals.")
label(0x00043d20, "geometry_profile_state_table_i",
      "Twelve-word profile-state descriptor table used by the floating-point phase variants.")
label(0x00043d50, "geometry_object_profile_state_variant_o",
      "Floating-point profile transition variant using the 0x43d20 descriptor table and updating object field 0xac.")
label(0x00043e00, "geometry_object_profile_state_variant_p",
      "Alternate floating-point profile transition using the 0x43d40 descriptor pair, bounded scaling, and object field 0xac.")
label(0x00043ee0, "geometry_profile_runtime_pool_clear",
      "Clears the per-mode runtime profile pools and associated phase latch fields for both configured runtime contexts.")
label(0x00043fc8, "geometry_profile_phase_dispatch_table",
      "Eight-entry phase/geometry dispatch table selected by the object state field at offset 0x64.")
label(0x00043fa0, "geometry_profile_phase_dispatch",
      "Selects a phase-specific geometry state arm from the 0x43fc8 table and computes bounded object offsets 0xc2/0xc8.")
label(0x00044390, "geometry_profile_timing_state_update",
      "Updates the active profile timing fields at offsets 0x172/0x17a, handles mode-specific transition thresholds, and routes affected objects through the phase dispatcher.")
label(0x000445a0, "geometry_profile_runtime_mode_update",
      "Selects the active runtime profile mode, dispatches its geometry/state update, and publishes the resulting profile cursor and hardware timing fields.")
label(0x00044ad0, "geometry_profile_timing_hardware_emit",
      "Converts the selected profile timing state into hardware-scaled values and emits the associated command sequence through 0x884000.")
label(0x00045080, "geometry_profile_timing_hardware_emit_variant_a",
      "Alternate hardware timing emitter for the first runtime profile geometry mode; publishes scaled cursor values and command words.")
label(0x00045380, "geometry_profile_timing_hardware_emit_variant_b",
      "Second hardware timing emitter variant using the shared profile timing fields and 0x884000 command stream.")
label(0x00045680, "geometry_profile_timing_hardware_emit_variant_c",
      "Third hardware timing emitter variant with mode-specific fixed-point scaling and shared profile-state publication.")
label(0x00045c30, "geometry_profile_timing_hardware_emit_variant_d",
      "Fourth hardware timing emitter variant for an alternate profile range, retaining the shared 0x884000 output protocol.")
label(0x00045f50, "geometry_profile_timing_hardware_emit_variant_e",
      "Fifth hardware timing emitter variant with its own profile scaling constants and shared cursor output fields.")
label(0x00046480, "geometry_profile_timing_hardware_emit_variant_f",
      "Sixth timing emitter variant combining profile cursor fields with object-local timing inputs before emitting the 0x884000 command sequence.")
label(0x000466b0, "geometry_profile_timing_dual_buffer_emit",
      "Final profile timing emitter variant; derives scaled timing from the active object and writes paired values through the 0x804000 geometry buffer path.")
label(0x0004a420, "geometry_object_profile_threshold_update",
      "Updates object profile threshold flags and derives the normalized 0x1e2/0x1e4/0x1e6 fields from the active profile record.")
label(0x0004a780, "geometry_object_profile_phase_advance",
      "Advances the object profile phase through the descriptor data at 0x46930, resets phase state when bounded, and publishes shared cursor globals.")
label(0x0004a990, "geometry_object_profile_phase_advance_alt",
      "Alternate profile phase advance using the adjacent descriptor records and the shared cursor/phase state.")
label(0x0004abc0, "geometry_object_profile_phase_transition_variant_a",
      "Profile phase transition using descriptor pairs at 0x469d0/0x469d8; advances object phase and resets bounded state when a range completes.")
label(0x0004ad50, "geometry_object_profile_phase_transition_variant_b",
      "Alternate profile phase transition using descriptor pairs at 0x469b0/0x469b4 and the shared cursor/phase globals.")
label(0x0004ae70, "geometry_object_profile_phase_transition_variant_c",
      "Profile phase transition using the next descriptor pair, with a mode-specific phase threshold and reset path.")
label(0x0004af20, "geometry_object_profile_phase_transition_variant_d",
      "Alternate profile phase transition using descriptor pairs at 0x469f0/0x469f4 and the shared cursor state.")
label(0x0004aff0, "geometry_object_profile_phase_transition_variant_e",
      "Profile phase transition using the next descriptor pair and bounded object phase reset behavior.")
label(0x0004b090, "geometry_object_profile_phase_transition_variant_f",
      "Profile phase transition using descriptor data at 0x46a20 and the shared cursor globals, with bounded phase reset behavior.")
label(0x0004b150, "geometry_object_profile_state_event_update",
      "Updates profile event state, derives shared cursor values from the active object, and routes phase-triggered status changes.")
label(0x0004b600, "geometry_object_profile_event_progress_update",
      "Advances profile event progress, selects the relevant descriptor range, updates cursor state, and emits phase-triggered status events.")
label(0x0004b940, "geometry_object_profile_cursor_transition_variant_a",
      "Cursor transition variant using the 0x46a90 descriptor records and returning through a caller-supplied link.")
label(0x0004bb10, "geometry_object_profile_cursor_transition_variant_b",
      "Alternate cursor transition variant using the adjacent 0x46af0 descriptor records and returning through a caller-supplied link.")
label(0x0004bce0, "geometry_object_profile_state_finalize",
      "Finalizes an object profile transition: resets phase fields, emits the associated 0x884000 state packet, and applies the mapped status event.")
label(0x0004c050, "geometry_object_profile_runtime_update_variant_a",
      "Runtime profile update variant: advances object timing, derives scaled profile state, emits status events, and refreshes profile record fields.")
label(0x0004c610, "geometry_object_profile_runtime_update_variant_b",
      "Alternate runtime profile update variant using the next descriptor range and the shared cursor/event protocol.")
label(0x0004c8f0, "geometry_object_profile_runtime_update_variant_c",
      "Third runtime profile update variant using the adjacent descriptor range and the shared phase/event state.")
label(0x0004ca40, "geometry_object_profile_runtime_update_variant_d",
      "Fourth runtime profile update variant; advances phase state from the shared descriptor records and applies reset/event handling.")
label(0x0004cb70, "geometry_object_profile_runtime_update_variant_e",
      "Fifth runtime profile update variant using the 0x46d90 descriptor range and shared cursor/event state.")
label(0x0004cc20, "geometry_object_profile_runtime_update_variant_f",
      "Sixth runtime profile update variant with bounded cursor advance and profile reset paths.")
label(0x0004cd00, "geometry_object_profile_runtime_update_variant_g",
      "Seventh runtime profile update variant using the 0x46bb0 descriptor range and the shared status/event protocol.")
label(0x0004d540, "geometry_object_profile_cursor_transition_variant_c",
      "Cursor transition variant using mode-specific descriptor/scalar ranges, publishing shared cursor state and advancing the active object phase.")
label(0x0004d720, "geometry_object_profile_cursor_transition_variant_d",
      "Alternate cursor transition variant using the 0x46c40/0x46c48/0x46c50 descriptor ranges and the shared cursor/event protocol.")
label(0x0004d880, "geometry_object_profile_cursor_transition_variant_e",
      "Profile cursor transition variant using the 0x46c60-series descriptor ranges, status messages, and the shared timing/phase protocol.")
label(0x0004da80, "geometry_object_profile_cursor_transition_variant_f",
      "Cursor transition variant using indexed records at 0x46c80, advancing profile phase and entering the shared status-reset path at range completion.")
label(0x0004dce0, "geometry_object_profile_cursor_transition_variant_g",
      "Alternate cursor transition variant using indexed records at 0x46ce0 and the shared cursor/status reset protocol.")
label(0x0004def0, "geometry_object_profile_cursor_transition_variant_h",
      "Cursor transition variant using the compact 0x46d40 record range, publishing shared cursor values and mode-specific status transitions.")
label(0x0004e080, "geometry_object_profile_threshold_update_variant_b",
      "Alternate profile threshold update that clamps three timing fields, sets threshold flags, and recomputes normalized 0x1e2/0x1e4/0x1e6 values.")
label(0x0004e3e0, "geometry_object_profile_phase_dispatch_variant_b",
      "Alternate profile phase dispatcher using the object phase field and returning through a caller-supplied link after the selected transition path.")
label(0x0004e5f0, "geometry_object_profile_phase_dispatch_variant_c",
      "Profile phase dispatcher sibling using the 0x46dc0 records, updating phase/cursor state and resetting the object profile at range completion.")
label(0x0004e820, "geometry_object_profile_phase_dispatch_variant_d",
      "Profile phase dispatcher sibling using the 0x2572744-backed descriptor range and the shared cursor/status transition protocol.")
label(0x0004e920, "geometry_object_profile_phase_dispatch_variant_e",
      "Profile phase dispatcher sibling using paired 0x46e20/0x46e24 records and publishing the resulting cursor transition through the caller link.")
label(0x0004ea40, "geometry_object_profile_phase_dispatch_variant_f",
      "Compact profile phase transition using the 0x46e40 descriptor range and the shared cursor publication protocol.")
label(0x0004eaf0, "geometry_object_profile_phase_dispatch_variant_g",
      "Profile phase transition sibling using paired 0x46e50/0x46e54 records and the shared cursor/status state.")
label(0x0004ebc0, "geometry_object_profile_phase_dispatch_variant_h",
      "Compact profile phase transition using the 0x46e70 descriptor range and resetting the object phase state on completion.")
label(0x0004ec60, "geometry_object_profile_phase_dispatch_variant_i",
      "Profile phase transition sibling using the 0x46e80/0x46e84 records and the shared cursor/status state.")
label(0x0004ed20, "geometry_object_profile_phase_state_dispatch",
      "Dispatches profile phase-state arms after updating the derived object coordinate, selecting mode-specific record ranges and status transitions.")
label(0x0004f020, "geometry_object_profile_phase_transition_variant_g",
      "Profile phase transition using the 0x46ea0/0x46ea4 descriptor records, publishing paired cursor values and resetting bounded state.")
label(0x0004f1f0, "geometry_object_profile_phase_transition_variant_h",
      "Alternate profile phase transition using the 0x46f00/0x46f04 descriptor records and the shared cursor/status protocol.")
label(0x00051440, "geometry_object_profile_runtime_state_update_variant_a",
      "Extended profile runtime-state update using mode-indexed records at 0x470b0/0x470b4, status transitions, and shared cursor publication.")
label(0x000517f0, "geometry_object_profile_runtime_state_update_variant_b",
      "Alternate extended profile runtime-state update using the 0x47110/0x47114 records and the shared phase/status reset protocol.")
label(0x00051a80, "geometry_object_profile_threshold_update_variant_c",
      "Object-pair threshold update sibling that clamps timing fields, invokes the profile service at 0xbf120, and recomputes normalized threshold values.")
label(0x000520e0, "geometry_object_profile_phase_state_dispatch_variant_b",
      "Profile phase-state dispatcher sibling using descriptor bases at 0x47200/0x47208/0x47210/0x47218 and mode-specific reset transitions.")
label(0x00052360, "geometry_object_profile_phase_state_dispatch_variant_c",
      "Profile phase-state dispatcher sibling using the 0x47220-series records and the shared cursor/status transition protocol.")
label(0x00052650, "geometry_object_profile_threshold_event_update",
      "Threshold-event handler that emits the mapped status message, updates object flag 0x1a6, and advances through the 0x47260-series profile records.")
label(0x00052880, "geometry_object_profile_threshold_event_update_variant_b",
      "Threshold-event handler sibling using the 0x47280/0x47284 profile records, the shared status message path, and object flag 0x1a6.")
label(0x00052b00, "geometry_object_profile_phase_transition_variant_i",
      "Compact profile phase transition using the 0x472b0 descriptor range and the shared cursor publication/reset protocol.")
label(0x00052ba0, "geometry_object_profile_phase_transition_variant_j",
      "Profile phase transition sibling using the 0x472c0 indexed records and the shared cursor/status state.")
label(0x00052ca0, "geometry_object_profile_phase_transition_variant_k",
      "Profile phase transition sibling using the 0x472d0 records, publishing cursor state and raising the phase completion flag.")
label(0x00052e30, "geometry_object_profile_phase_state_dispatch_variant_d",
      "Profile phase-state dispatcher using the large 0x22749d8/0x22770e8/0x22749e0 data ranges and mode-specific status transitions.")
label(0x00053050, "geometry_object_profile_phase_transition_variant_l",
      "Profile phase transition using the 0x472f0/0x472f4 descriptor records, publishing paired cursor values and status completion state.")
label(0x00053280, "geometry_object_profile_phase_dispatch_variant_f",
      "Profile phase dispatcher sibling using the 0x47350/0x47354 records, shared cursor state, and caller-link completion paths.")
label(0x000534d0, "geometry_object_profile_phase_state_dispatch_variant_g",
      "Profile phase-state dispatcher using the large profile data ranges, shared cursor publication, and mode-specific status completion paths.")
label(0x00053680, "geometry_profile_runtime_geometry_math_update",
      "Runtime profile geometry update that derives floating-point/fixed-point correction values, updates object timing fields, and publishes status state.")
label(0x00053a20, "geometry_object_profile_status_transition_variant_a",
      "Profile status transition using the 0x473c0/0x473c8/0x473d0 descriptor ranges, shared cursor publication, and mode-specific status resets.")
label(0x00053d00, "geometry_object_profile_status_transition_variant_b",
      "Alternate profile status transition using the 0x473e0/0x473e8/0x473f0 descriptor ranges and the shared cursor/status protocol.")
label(0x00053fe0, "geometry_object_profile_status_transition_variant_c",
      "Compact profile transition using the 0x473f8 descriptor range, shared cursor publication, and an indirect completion return.")
label(0x000540a0, "geometry_object_profile_status_transition_variant_d",
      "Alternate compact profile transition using the 0x47400 descriptor range, shared cursor publication, and an indirect completion return.")
label(0x00054160, "geometry_object_profile_phase_state_dispatch_variant_h",
      "Profile phase-state dispatcher using the 0x47410/0x47418/0x47428 records, shared cursor publication, and geometry/status completion paths.")
label(0x00054340, "geometry_object_profile_compact_transition_variant_a",
      "Compact profile transition using the 0x475d0 descriptor and an indirect completion return, with phase reset at the range boundary.")
label(0x000543f0, "geometry_object_profile_compact_transition_variant_b",
      "Compact profile transition sibling using the 0x475d8 descriptor and an indirect completion return, with phase reset at the range boundary.")
label(0x000544a0, "geometry_object_profile_threshold_event_update_variant_c",
      "Threshold-event handler using the 0x475c0 descriptor, status message path, object flag 0x1a6, and paired terminal state arms.")
label(0x000545f0, "geometry_object_profile_threshold_event_update_variant_d",
      "Threshold-event handler sibling using the 0x475c8 descriptor, status message path, object flag 0x1a6, and paired terminal state arms.")
label(0x00054760, "geometry_object_profile_indexed_geometry_update_variant_a",
      "Indexed profile geometry update using the paired 0x47440 records, shared cursor publication, phase progression, and status completion.")
label(0x00054a60, "geometry_object_profile_indexed_geometry_update_variant_b",
      "Indexed profile geometry update sibling using the 0x47470 records, shared cursor publication, phase progression, and status completion.")
label(0x00054e00, "geometry_object_profile_runtime_geometry_math_update_variant_b",
      "Runtime profile geometry/status update using the 0x22740d0-derived records, phase cursor publication, and correction of object field 0x150.")
label(0x00054f50, "geometry_object_profile_compact_transition_variant_c",
      "Compact profile transition using the 0x22740d0-derived descriptor path, shared cursor publication, and an indirect completion return.")
label(0x000550c0, "geometry_object_profile_indexed_geometry_update_variant_c",
      "Indexed profile geometry update using the paired 0x474a0 records, shared cursor publication, phase progression, and status reset publication.")
label(0x00055300, "geometry_object_profile_indexed_geometry_update_variant_d",
      "Multi-arm indexed profile geometry update using the paired 0x47500 records, shared cursor publication, phase progression, and status/message completion paths.")
label(0x00055550, "geometry_object_profile_indexed_geometry_update_variant_e",
      "Indexed profile geometry update sibling using the paired 0x47560 records, shared cursor publication, phase progression, and threshold-event completion paths.")
label(0x00055930, "geometry_object_profile_kinematics_collision_update",
      "Per-frame object kinematics update that clamps three position fields, derives collision flags 0x1dd/0x1de/0x1df, and computes normalized extents 0x1e2/0x1e4/0x1e6.")
label(0x00055c90, "geometry_object_profile_phase_transition_controller",
      "Profile phase transition controller that selects 0x475e0/0x475e8/0x475f0 records, advances or resets phase 0x178, and manages transition state 0x17c/0x180.")
label(0x00055ea0, "geometry_object_profile_phase_transition_variant_e",
      "Alternate profile phase transition using 0x47600 indexed records and the shared cursor protocol, with multi-arm phase reset and progression paths.")
label(0x000560d0, "geometry_object_profile_phase_transition_variant_f",
      "Profile phase transition using the 0x2572744-derived record family, status message selection, and shared cursor publication.")
label(0x000561f0, "geometry_object_profile_indexed_transition_variant_a",
      "Indexed profile transition using paired records at 0x47660/0x47664, with phase advancement and reset-state completion.")
label(0x00056320, "geometry_object_profile_indexed_transition_variant_b",
      "Indexed profile transition using the 0x47680 descriptor family, with phase advancement and reset-state completion.")
label(0x000563f0, "geometry_object_profile_indexed_transition_variant_c",
      "Indexed profile transition using paired records at 0x47690/0x47694, with phase advancement and reset-state completion.")
label(0x000564e0, "geometry_object_profile_compact_transition_variant_d",
      "Compact profile transition using the 0x476b0 descriptor and shared cursor publication, with phase/state reset completion.")
label(0x00056580, "geometry_object_profile_compact_transition_variant_e",
      "Compact profile transition using the 0x476c0 indexed descriptor and shared cursor publication, with phase/state reset completion.")
label(0x00056640, "geometry_object_profile_phase_state_dispatch_variant_i",
      "Parent profile phase-state dispatcher that recomputes derived field 0x2e and selects the 0x2563700/0x2564a28/0x2566a30 record families.")
label(0x00056930, "geometry_object_profile_indexed_transition_variant_d",
      "Indexed profile transition using paired records at 0x476e0/0x476e4, with phase advancement, cursor publication, and status completion.")
label(0x00056b30, "geometry_object_profile_indexed_transition_variant_e",
      "Indexed profile transition using paired records at 0x47740/0x47744, with phase advancement, cursor publication, and indirect completion return.")
label(0x00056d10, "geometry_object_profile_phase_state_dispatch_variant_j",
      "Profile phase-state dispatcher that resets object fields 0x186/0x188, recomputes 0x2e, and selects the 0x477a0/0x477a8/0x477b0 records.")
label(0x00056f40, "geometry_object_profile_phase_state_dispatch_variant_k",
      "Extended profile phase-state dispatcher using the 0x477c0/0x477c8/0x477d0 records, collision flags, status messages, and shared cursor publication.")
label(0x00057270, "geometry_object_profile_phase_state_dispatch_variant_l",
      "Profile phase-state dispatcher using the 0x477e0/0x477e8/0x477f0 records, collision/status gating, shared cursor publication, and geometry completion.")
label(0x00057530, "geometry_object_profile_indexed_geometry_update_variant_f",
      "Indexed profile geometry update using the 0x47800 record pair, shared cursor publication, phase progression, and status reset paths.")
label(0x000576d0, "geometry_object_profile_indexed_geometry_update_variant_g",
      "Indexed profile geometry update sibling using the 0x47810 record pair, shared cursor publication, phase progression, and status reset paths.")
label(0x00057870, "geometry_object_profile_video_command_producer_variant_a",
      "Video/geometry command producer that emits the object packet to 0x884000, polls the result threshold, and publishes fields 0x1c4/0x19c/0x1af.")
label(0x00057ad0, "geometry_object_profile_video_command_producer_variant_b",
      "Video/geometry command producer sibling using the 0x47830 record pair, command-port polling, phase progression, and status completion.")
label(0x00057d70, "geometry_object_profile_compact_transition_variant_f",
      "Compact profile transition using the 0x47840 descriptor and shared cursor publication, with an indirect completion return.")
label(0x00057e30, "geometry_object_profile_video_command_producer_variant_c",
      "Video/geometry command producer sibling using the 0x47848 descriptor, command-port polling, phase progression, and status completion.")
label(0x00057fc0, "geometry_object_profile_compact_transition_variant_g",
      "Compact profile transition using the 0x47a30 descriptor, shared cursor publication, phase advancement, and an indirect completion return.")
label(0x00058070, "geometry_object_profile_compact_transition_variant_h",
      "Compact profile transition sibling using the 0x47a38 descriptor, shared cursor publication, phase advancement, and an indirect completion return.")
label(0x00058120, "geometry_object_profile_indexed_transition_variant_f",
      "Indexed profile transition using qword record data at 0x47a10, shared cursor publication, and status-message completion.")
label(0x00058230, "geometry_object_profile_indexed_transition_variant_g",
      "Indexed profile transition sibling using qword record data at 0x47a20, shared cursor publication, and status-message completion.")
label(0x00058340, "geometry_object_profile_indexed_geometry_update_variant_h",
      "Large indexed profile geometry update using the paired 0x47850/0x47854 records, shared cursor publication, phase progression, and status completion.")
label(0x00058690, "geometry_object_profile_indexed_geometry_update_variant_i",
      "Indexed profile geometry update sibling using the paired 0x47880/0x47884 records, shared cursor publication, phase progression, and status completion.")
label(0x00058930, "geometry_object_profile_indexed_transition_variant_h",
      "Compact indexed profile transition using the 0x478b0/0x478b8/0x478c0 records, shared cursor publication, phase advancement, and reset completion.")
label(0x00058af0, "geometry_object_profile_runtime_geometry_status_update_variant_c",
      "Runtime profile geometry/status update using the 0x2560bc8-derived records, object-field correction, phase progression, and status completion.")
label(0x00058c40, "geometry_object_profile_indexed_transition_variant_i",
      "Indexed profile transition using the 0x478d0/0x478d8 records, collision/status gating, shared cursor publication, and multi-arm completion.")
label(0x00058eb0, "geometry_object_profile_indexed_transition_variant_j",
      "Indexed profile transition using the 0x478f0 records, shared cursor publication, phase advancement, and multi-arm completion.")
label(0x000590c0, "geometry_object_profile_indexed_transition_variant_k",
      "Indexed profile transition using the 0x47950/0x47954 records, shared cursor publication, phase advancement, and terminal status updates.")
label(0x00059370, "geometry_object_profile_transition_driver_variant_a",
      "Larger multi-arm transition driver using the 0x479b0 records, shared cursor publication, phase/status progression, and reset completion.")
label(0x00059640, "geometry_object_profile_geometry_bounds_flags_update",
      "Geometry bounds and collision-flag evaluator that clamps profile coordinates, tests three axis bounds, and publishes derived geometry ratios.")
label(0x000599a0, "geometry_object_profile_phase_controller_variant_a",
      "Profile phase controller dispatching states 0 through 3, selecting 0x47e20/0x47e28/0x47e30/0x47e38 records, and advancing phase state.")
label(0x00059c40, "geometry_object_profile_phase_controller_variant_b",
      "Profile phase controller sibling dispatching states 0 through 3, selecting 0x47e40/0x47e44/0x47e48/0x47e4c records, and advancing phase state.")
label(0x00059f40, "geometry_object_profile_phase_transition_variant_g",
      "Profile phase transition handler using the 0x47e80/0x47e88 records, advancing frame counters, and resetting phase status at terminal thresholds.")
label(0x0005a1a0, "geometry_object_profile_phase_controller_variant_c",
      "Profile phase controller sibling selecting 0x47ea0/0x47ea4/0x47ea8 records, updating the per-object phase counter, and publishing completion state.")
label(0x0005a440, "geometry_object_profile_phase_transition_variant_h",
      "Compact profile phase transition using the 0x47ed0 record, advancing or resetting the shared phase counter, and returning through the controller link.")
label(0x0005a4e0, "geometry_object_profile_phase_transition_variant_i",
      "Profile phase transition sibling using the 0x47ee0 record, advancing or resetting phase state at its terminal threshold.")
label(0x0005a5e0, "geometry_object_profile_phase_transition_variant_j",
      "Compact profile phase transition using the 0x47ef0 record, advancing or resetting phase state and publishing the shared cursor values.")
label(0x0005a680, "geometry_object_profile_phase_transition_variant_k",
      "Compact profile phase transition using the 0x47f00 record, advancing or resetting phase state and publishing the shared cursor values.")
label(0x0005a780, "geometry_object_profile_phase_transition_variant_l",
      "Multi-state profile transition using geometry-derived timing, phase counters, status flags, and terminal record selection.")
label(0x0005aac0, "geometry_object_profile_indexed_transition_variant_l",
      "Indexed profile transition using the paired 0x47f10/0x47f14 records, shared cursor publication, and phase completion updates.")
label(0x0005acc0, "geometry_object_profile_indexed_transition_variant_m",
      "Indexed profile transition using the paired 0x47f70/0x47f74 records, shared cursor publication, phase/status updates, and reset completion.")
label(0x0005af10, "geometry_object_profile_phase_transition_variant_m",
      "Large profile phase transition using the 0x47fd0/0x47fd8/0x47fe0 records, status-gated frame progression, and terminal reset handling.")
label(0x0005b1e0, "geometry_object_profile_phase_transition_variant_n",
      "Parallel large profile phase transition using the 0x47ff0/0x47ff8/0x48000 records, status-gated frame progression, and terminal reset handling.")
label(0x0005b4b0, "geometry_object_profile_phase_transition_variant_o",
      "Profile phase transition using the 0x48008 record, shared cursor progression, terminal state reset, and fixed-point object geometry setup.")
label(0x0005b610, "geometry_object_profile_phase_transition_variant_p",
      "Parallel profile phase transition using the 0x48010 record, shared cursor progression, terminal state reset, and fixed-point object geometry setup.")
label(0x0005b770, "geometry_object_profile_phase_transition_variant_q",
      "Compact profile phase transition using the 0x48020 record, advancing the phase counter and resetting terminal object state.")
label(0x0005b830, "geometry_object_profile_phase_transition_variant_r",
      "Compact profile phase transition using the 0x48018 record, advancing the phase counter and resetting terminal object state.")
label(0x0005b8f0, "geometry_object_profile_phase_transition_variant_s",
      "Compact profile phase transition using the 0x48230 record, advancing a short frame counter and setting the next phase state.")
label(0x0005b9a0, "geometry_object_profile_phase_transition_variant_t",
      "Compact profile phase transition using the 0x48238 record, advancing a short frame counter and setting the next phase state.")
label(0x0005ba50, "geometry_object_profile_phase_transition_variant_u",
      "Profile frame transition using the 0x48210 record, advancing the shared counter and entering terminal status progression.")
label(0x0005bb60, "geometry_object_profile_phase_transition_variant_v",
      "Parallel profile frame transition using the 0x48220 record, advancing the shared counter and entering terminal status progression.")
label(0x0005bc70, "geometry_object_profile_indexed_transition_variant_n",
      "Large indexed profile transition using the paired 0x48030/0x48034 records, status gating, shared cursor publication, and object-state setup.")
label(0x0005bff0, "geometry_object_profile_indexed_transition_variant_o",
      "Large indexed profile transition using the paired 0x48060/0x48064 records, status gating, shared cursor publication, and object-state setup.")
label(0x0005c370, "geometry_object_profile_indexed_transition_variant_p",
      "Multi-arm indexed profile transition using the 0xfc/0xf8 object arrays and paired 0x48090/0x48094 records, with terminal status progression.")
label(0x0005c650, "geometry_object_profile_transition_reset_helper",
      "Profile transition reset helper that selects the mode-specific reset record, clears object phase fields, and initializes the next state.")
label(0x0005c6c0, "geometry_object_profile_indexed_transition_variant_q",
      "Multi-arm indexed profile transition using the paired 0x480f0/0x480f4 records and object arrays, with terminal phase/status progression.")
label(0x0005c980, "geometry_object_profile_transition_reset_helper_variant_b",
      "Profile transition reset helper sibling that selects the mode-specific reset record, clears object phase fields, and initializes the next state.")
label(0x0005c9f0, "geometry_object_profile_indexed_transition_variant_r",
      "Multi-arm indexed profile transition using the paired 0x48150/0x48154 records and object arrays, with terminal phase/status progression.")
label(0x0005cd1c, "geometry_object_profile_transition_reset_helper_variant_c",
      "Profile transition reset helper that selects the mode-specific reset record, clears object phase fields, and initializes the next state.")
label(0x0005cd90, "geometry_object_profile_indexed_transition_variant_s",
      "Large profile transition using the 0x481b0/0x481b8 records, cursor progression, object-state setup, and geometry correction.")
label(0x0005cff0, "geometry_object_profile_phase_transition_variant_w",
      "Parallel profile phase transition using the 0x481d0/0x481d8 records, cursor progression, object-state setup, and geometry correction.")
label(0x0005d1c0, "geometry_object_profile_phase_transition_variant_x",
      "Large profile phase transition using the 0x481f0/0x481f8/0x48200 records, cursor progression, object-state setup, and geometry correction.")
label(0x0005d3d0, "geometry_object_profile_geometry_bounds_flags_update_variant_b",
      "Geometry bounds and collision-flag evaluator sibling that clamps profile coordinates, updates axis flags, and publishes derived geometry ratios.")
label(0x0005d730, "geometry_object_profile_phase_controller_variant_d",
      "Profile phase controller dispatching states through the 0x48240/0x48248/0x48250 records, advancing counters, and applying terminal resets.")
label(0x0005d970, "geometry_object_profile_indexed_phase_controller_variant_a",
      "Indexed profile phase controller using the 0x48260 records, object-state transitions, cursor publication, and terminal reset handling.")
label(0x0005dc90, "geometry_object_profile_phase_transition_variant_y",
      "Table-driven profile phase transition selecting the 0x482c0/0x482c8/0x482d0/0x482d8 records by threshold and publishing the next counter state.")
label(0x0005de50, "geometry_object_profile_phase_transition_variant_z",
      "Profile phase transition using the 0x482e0 records, cursor progression, terminal status changes, and object-state reset handling.")
label(0x0005e040, "geometry_object_profile_phase_transition_variant_aa",
      "Compact profile phase transition using the 0x48360 record, advancing the object phase counter and resetting terminal state.")
label(0x0005e110, "geometry_object_profile_indexed_transition_variant_t",
      "Indexed profile transition using the paired 0x48370/0x48374 records, cursor publication, and object phase reset handling.")
label(0x0005e200, "geometry_object_profile_phase_transition_variant_ab",
      "Compact profile phase transition using the 0x48390 record, advancing the shared counter and resetting terminal state.")
label(0x0005e2a0, "geometry_object_profile_indexed_transition_variant_u",
      "Indexed profile transition using the paired 0x483a0/0x483a4 records, threshold comparison, and terminal phase reset.")
label(0x0005e360, "geometry_object_profile_phase_controller_variant_e",
      "Multi-arm profile phase controller that derives the object coordinate, selects 0x79034-based assets, advances the phase counter, and applies terminal state resets.")
label(0x0005e530, "geometry_object_profile_indexed_transition_variant_v",
      "Indexed profile transition using the paired 0x483c0/0x483c4 records, publishing cursor values and switching to terminal object-state progression at its threshold.")
label(0x0005e730, "geometry_object_profile_indexed_transition_variant_w",
      "Callback-returning indexed profile transition using the paired 0x48420 records, phase threshold handling, and the shared cursor publication path.")
label(0x0005e910, "geometry_object_profile_phase_controller_variant_f",
      "Parallel multi-arm profile phase controller that derives the object coordinate, selects 0x79034-based assets, advances the phase counter, and applies terminal state resets.")
label(0x0005eaf0, "geometry_object_profile_phase_controller_variant_g",
      "Large profile phase controller using the 0x26d1f5c asset records, phase/status gates, object geometry setup, and terminal state transitions.")
label(0x0005ecc0, "geometry_object_profile_phase_transition_variant_ac",
      "Profile phase transition using the 0x48480/0x48488/0x48490 records, shared cursor publication, phase advancement, and terminal object-state reset.")
label(0x0005efa0, "geometry_object_profile_phase_transition_variant_ad",
      "Profile phase transition using the 0x484a0/0x484a8/0x484b0 records, shared cursor publication, phase advancement, and terminal object-state reset.")
label(0x0005f250, "geometry_object_profile_phase_transition_variant_ae",
      "Profile phase transition using the 0x484f0 record pair, shared cursor publication, object-state reset, and geometry setup at the terminal phase.")
label(0x0005f590, "geometry_object_profile_phase_transition_variant_af",
      "Profile phase transition using the 0x484c0 record pair, shared cursor publication, phase/status handling, and terminal geometry setup.")
label(0x0005f930, "geometry_object_profile_phase_controller_variant_h",
      "Callback-returning profile phase controller using the 0x48500 record pair, phase transition thresholds, and terminal object-state setup.")
label(0x0005f9f0, "geometry_object_profile_phase_controller_variant_i",
      "Callback-returning profile phase controller using the 0x48508 record pair and the short phase-to-state transition path.")
label(0x0005fad0, "geometry_object_profile_phase_controller_variant_j",
      "Callback-returning profile phase controller using the 0x486e0 record pair, advancing the phase and entering the next object state.")
label(0x0005fb80, "geometry_object_profile_phase_controller_variant_k",
      "Callback-returning profile phase controller using the 0x486e8 record pair, with the short threshold and next-state reset path.")
label(0x0005fc30, "geometry_object_profile_phase_transition_variant_ag",
      "Profile phase transition using the 0x486d0 record pair, advancing the phase and selecting the terminal state by mode.")
label(0x0005fcf0, "geometry_object_profile_phase_transition_variant_ah",
      "Profile phase transition using the 0x486d8 record pair, advancing the phase and selecting the terminal state by mode.")
label(0x0005fdb0, "geometry_object_profile_indexed_phase_controller_variant_b",
      "Large callback-returning indexed phase controller using the paired 0x48510/0x48514 records, object geometry correction, phase/status gates, and terminal reset handling.")
label(0x00060050, "geometry_object_profile_indexed_phase_controller_variant_c",
      "Large indexed phase controller using the paired 0x48540/0x48544 records, object geometry correction, phase/status gates, and terminal reset handling.")
label(0x00060370, "geometry_object_profile_phase_controller_variant_l",
      "Callback-returning profile phase controller using generated asset addresses, short phase thresholds, and terminal state progression.")
label(0x00060580, "geometry_object_profile_phase_controller_variant_m",
      "Callback-returning profile phase controller using generated asset addresses, phase thresholds, and terminal cursor progression.")
label(0x00060a30, "geometry_object_profile_indexed_transition_variant_x",
      "Indexed profile transition using the paired 0x48570/0x48574 records, advancing the phase and entering the next object state.")
label(0x00060c60, "geometry_object_profile_indexed_transition_variant_y",
      "Indexed profile transition using the 0x485d0/0x485d4 records, phase threshold handling, cursor publication, and terminal object-state reset.")
label(0x000611d0, "geometry_object_profile_geometry_bounds_flags_update_variant_c",
      "Geometry bounds and axis-flag evaluator that clamps the three object extents, tests collision-side conditions, computes derived ratios, and returns through a saved callback.")
label(0x000615f0, "geometry_object_profile_state_controller_variant_a",
      "Multi-state profile controller using the 0x47a40/0x47a48/0x47a50 records, phase and object-state transitions, and callback-based cursor publication.")
label(0x00061830, "geometry_object_profile_state_controller_variant_b",
      "Indexed profile state controller using the 0x47a60 records and object selector at 0x188, with phase progression and terminal state transitions.")
label(0x00061ab0, "geometry_object_profile_phase_transition_variant_ai",
      "Profile phase transition using the 0x47ab0/0x47ab8/0x47ac0 records, shared cursor publication, and terminal state reset handling.")
label(0x00061c40, "geometry_object_profile_indexed_transition_variant_z",
      "Indexed profile transition using the 0x47a90/0x47a94 records selected by object selector state, with phase progression and terminal reset handling.")
label(0x00061d60, "geometry_object_profile_phase_transition_variant_aj",
      "Profile phase transition using the 0x47ac8 record pair, advancing the cursor and entering the next object state at its threshold.")
label(0x00061e10, "geometry_object_profile_indexed_transition_late_variant_a",
      "Indexed profile transition using the 0x47ad0/0x47ad4 records selected by object state, with phase progression and terminal reset handling.")
label(0x00061ee0, "geometry_object_profile_phase_transition_variant_ak",
      "Profile phase transition using the 0x47af0 record pair, advancing the cursor and resetting the object phase at completion.")
label(0x00061f80, "geometry_object_profile_indexed_transition_late_variant_b",
      "Indexed profile transition using the 0x47b00/0x47b04 records selected by object state, with phase progression and terminal reset handling.")
label(0x00062040, "geometry_object_profile_object_state_controller_variant_a",
      "Object-state controller using the 0x2338078 asset base and 0xb3e98 offset, publishing the active pair and transitioning through object state 0x190.")
label(0x00062260, "geometry_object_profile_object_state_controller_variant_b",
      "Parallel object-state controller using the 0x2338078 asset base and 0xb3e98 offset, with visibility gating and phase progression.")
label(0x00062580, "geometry_object_profile_indexed_transition_variant_ac",
      "Indexed profile transition using the paired 0x47b20/0x47b24 records, shared cursor publication, threshold handling, and terminal state reset.")
label(0x00062920, "geometry_object_profile_geometry_setup_variant_a",
      "Geometry setup path that clears object selectors, derives the centered coordinate, emits object words to the 0x884000 FIFO, and computes the fixed-point 0x1c4 transform value.")
label(0x00062d30, "geometry_object_profile_phase_transition_variant_al",
      "Profile phase transition using the 0x47c00/0x47c08 records, shared cursor publication, phase advancement, and terminal object-state reset.")
label(0x00062fd0, "geometry_object_profile_phase_transition_variant_am",
      "Callback-returning profile phase transition using the 0x47c18 record pair, phase thresholds, and terminal object-state setup.")
label(0x00063120, "geometry_object_profile_phase_transition_variant_an",
      "Callback-returning profile phase transition using the 0x47c20 record pair and the short terminal-state reset path.")
label(0x000631e0, "geometry_object_profile_phase_controller_variant_n",
      "Callback-returning profile phase controller using the 0x47e10 record pair and short phase-to-state progression.")
label(0x00063290, "geometry_object_profile_phase_transition_variant_ao",
      "Profile phase transition using the 0x47e00 record pair, advancing the cursor and resetting the object state at completion.")
label(0x00063370, "geometry_object_profile_indexed_phase_controller_variant_d",
      "Large indexed profile phase controller using the paired 0x47c30/0x47c34 records, status gating, cursor publication, and terminal reset handling.")
label(0x000636c0, "geometry_object_profile_indexed_phase_controller_variant_e",
      "Large indexed profile phase controller using the paired 0x47c90/0x47c94 records, status gating, cursor publication, and terminal reset handling.")
label(0x00063a90, "geometry_object_profile_phase_transition_variant_ap",
      "Profile phase transition using the 0x47cc0/0x47cc8/0x47cd0 records, cursor progression, timing thresholds, and movement-state correction.")
label(0x00063c00, "geometry_object_profile_phase_transition_variant_aq",
      "Profile phase transition using the 0x47ce0/0x47ce8/0x47cf0 records, cursor progression, timing thresholds, and movement-state correction.")
label(0x00063d60, "geometry_object_profile_generated_asset_controller_variant_a",
      "Generated-asset profile controller using the 0x47d00/0x47d08/0x47d10 records, fixed-point cursor scaling, state flags, and terminal callback return.")
label(0x00063f30, "geometry_object_profile_indexed_transition_variant_ad",
      "Indexed profile transition using the paired 0x47d20/0x47d24 records, cursor publication, phase limits, and terminal object-state reset.")
label(0x000641a0, "geometry_object_profile_indexed_transition_late_variant_c",
      "Late indexed profile transition using the 0x47d80/0x47d84 records, threshold handling, cursor publication, and terminal object-state reset.")
label(0x00064310, "geometry_object_profile_phase_controller_variant_o",
      "Profile phase controller using the 0x47dc0/0x47dc4 records, paired phase counters at 0x1f8/0x1fa, and terminal state progression.")
label(0x000645a0, "geometry_object_profile_geometry_bounds_flags_update_variant_d",
      "Geometry bounds evaluator that clamps the three extents, updates axis collision flags, and computes derived fixed-point ratios.")
label(0x000648d0, "geometry_object_profile_object_state_controller_variant_c",
      "Object-state controller using the 0x486f0/0x486f8 callback records, movement flags, and state transitions through the saved callback.")
label(0x00064b00, "geometry_object_profile_object_state_controller_variant_d",
      "Object-state controller using the indexed 0x48710 record table and object selector at 0x188, with movement flags and callback return.")
label(0x00064d40, "geometry_object_profile_object_state_controller_variant_e",
      "Object-state controller using the 0x48770/0x48778 records, cursor progression, and terminal state changes for the selected object phase.")
label(0x00064f60, "geometry_object_profile_object_state_controller_variant_f",
      "Object-state controller using the indexed 0x48790 records, cursor progression, and terminal state changes for the selected object phase.")
label(0x000651a0, "geometry_object_profile_object_state_controller_variant_g",
      "Compact object-state controller using the 0x487f0 record and the phase-16 terminal transition.")
label(0x00065270, "geometry_object_profile_object_state_controller_variant_h",
      "Object-state controller using the object selector at 0x188 and paired records at 0x48800/0x48804, with phase-16 completion handling.")
label(0x00065360, "geometry_object_profile_object_state_controller_variant_i",
      "Compact object-state controller using the 0x48820 record, cursor advancement, and terminal state update through its saved callback.")
label(0x00065400, "geometry_object_profile_object_state_controller_variant_j",
      "Object-state controller using the selector-indexed 0x48830/0x48834 records, cursor progression, and terminal state update through its callback.")
label(0x000654c0, "geometry_object_profile_object_state_controller_variant_k",
      "Object-state controller that recenters the object coordinate, selects the 0x48850/0x48854 records, and applies the terminal phase reset.")
label(0x00065630, "geometry_object_profile_object_state_controller_variant_l",
      "Parallel recentering object-state controller using the 0x48850/0x48854 records, cursor progression, and terminal state reset.")
label(0x00065780, "geometry_object_profile_indexed_transition_variant_ae",
      "Indexed profile transition using the paired 0x48880/0x48884 records, dual cursor publication, and terminal phase handling.")
label(0x00065980, "geometry_object_profile_indexed_phase_controller_variant_f",
      "Indexed profile phase controller using the paired 0x488e0/0x488e4 records, callback-returning cursor progression, and phase-limit handling.")
label(0x00065bd0, "geometry_object_profile_object_state_controller_variant_m",
      "Object-state controller using the 0x48940/0x48948/0x48950 records, phase alignment, status gating, and terminal object initialization.")
label(0x00065f00, "geometry_object_profile_object_state_controller_variant_n",
      "Object-state controller using the 0x48960/0x48968 records, status-byte gating, cursor alignment, and terminal object initialization.")
label(0x00066220, "geometry_object_profile_object_state_controller_variant_o",
      "Object-state controller using the packed 0x489b0 record pair, status-byte gating, cursor advancement, and terminal object initialization.")
label(0x00066420, "geometry_object_profile_object_state_controller_variant_p",
      "Object-state controller using the packed 0x48990 record pair, status-byte gating, cursor advancement, and terminal object initialization.")
label(0x00066600, "geometry_object_profile_object_state_controller_variant_q",
      "Object-state controller using the packed 0x48980 record pair, phase threshold handling, and terminal object initialization.")
label(0x00066840, "geometry_object_profile_object_state_controller_variant_r",
      "Object-state controller using the packed 0x489a0 record pair, phase threshold handling, and terminal object initialization.")
label(0x00066a80, "geometry_object_profile_object_state_controller_variant_s",
      "Compact callback-returning object-state controller using the 0x489c0 record and terminal phase initialization.")
label(0x00066b50, "geometry_object_profile_object_state_controller_variant_t",
      "Compact callback-returning object-state controller using the 0x489c8 record and terminal phase initialization.")
label(0x00066c10, "geometry_object_profile_object_state_controller_variant_u",
      "Compact callback-returning object-state controller using the 0x48bd0 record, phase threshold handling, and terminal state update.")
label(0x00066cc0, "geometry_object_profile_object_state_controller_variant_v",
      "Compact callback-returning object-state controller using the 0x48bd8 record, phase threshold handling, and terminal state update.")
label(0x00066d70, "geometry_object_profile_phase_controller_variant_p",
      "Profile phase controller using the packed 0x48bb0 record pair, cursor progression, status gating, and terminal callback paths.")
label(0x00066f90, "geometry_object_profile_indexed_phase_controller_variant_g",
      "Indexed phase controller using the 0x489d0 record table, paired cursor publication, and terminal object-state transitions.")
label(0x000672c0, "geometry_object_profile_indexed_phase_controller_variant_h",
      "Indexed phase controller using the 0x48a00 record table, paired cursor publication, and terminal object-state transitions.")
label(0x00067600, "geometry_object_profile_indexed_phase_controller_variant_i",
      "Indexed phase controller using the 0x48a34 record table, paired cursor publication, and terminal object-state transitions.")
label(0x00067800, "geometry_object_profile_indexed_phase_controller_variant_j",
      "Indexed phase controller using the paired 0x48a90/0x48a94 record table, paired cursor publication, and terminal object-state transitions.")
label(0x00067a30, "geometry_object_profile_indexed_phase_controller_variant_k",
      "Indexed phase controller using the 0x48af4 record table, paired cursor publication, and terminal object-state transitions.")
label(0x00067c90, "geometry_object_profile_phase_controller_variant_q",
      "Profile phase controller using the packed 0x48b50 record pair and the phase-7 threshold transition.")
label(0x00067e40, "geometry_object_profile_phase_controller_variant_r",
      "Profile phase controller using the packed 0x48b70 record pair, cursor progression, and terminal phase handling.")
label(0x00068040, "geometry_object_profile_phase_controller_variant_s",
      "Profile phase controller using the packed 0x48b90 record pair, cursor progression, and terminal phase handling.")
label(0x00068230, "geometry_object_profile_geometry_bounds_flags_update_variant_e",
      "Parallel geometry bounds evaluator that clamps the three extents, applies object-record offsets, updates axis collision flags, and computes derived ratios.")
label(0x0006d130, "geometry_object_profile_phase_selection_controller",
      "Geometry phase/selection controller that updates the active object phase, cursor fields, and terminal state flags before returning through its callback.")
label(0x0006d390, "geometry_command_packet_writer_variant_a",
      "Geometry command packet writer that serializes object state and transform fields to the 0x884000 FIFO, with auxiliary setup calls.")
label(0x0006ddb0, "geometry_object_profile_phase_state_controller",
      "Geometry phase-state controller that advances object selectors and phase counters, applies mode-dependent transitions, and returns through its callback.")
label(0x0006e0b0, "geometry_command_packet_writer_variant_b",
      "Structured geometry command packet writer that emits object coordinates, dimensions, and mode words to the 0x884000 FIFO.")
label(0x0006e630, "geometry_motion_threshold_service",
      "Motion threshold service that gates phase states 10/11, selects fixed floating-point thresholds, updates motion state, and publishes the result through 0x804008/0x80400c.")
label(0x0006e6f0, "geometry_motion_math_dispatch_variant_a",
      "Floating-point motion math dispatcher that selects a phase-dependent constant and returns through the supplied callback.")
label(0x0006e7f0, "geometry_motion_math_dispatch_variant_b",
      "Floating-point motion math dispatcher variant that selects a phase-dependent constant and returns through the supplied callback.")
label(0x0006e8f0, "geometry_motion_math_dispatch_variant_c",
      "Compact floating-point motion math dispatcher for the phase-3 path, returning through the supplied callback.")
label(0x0006e940, "geometry_motion_math_dispatch_variant_d",
      "Floating-point motion math dispatcher variant that selects a phase-dependent constant and returns through the supplied callback.")
label(0x0006ea40, "geometry_motion_math_dispatch_variant_e",
      "Floating-point motion math dispatcher variant that selects a phase-dependent constant and returns through the supplied callback.")
label(0x0006eb40, "geometry_motion_math_callback_bridge",
      "Minimal callback bridge for the motion math dispatch cluster.")
label(0x0006ef70, "geometry_command_packet_emit_site_variant_a",
      "Instruction-site target inside the larger geometry renderer; emits the assembled vertex/attribute packet to the 0x884000 FIFO and is referenced by the late geometry callback table.")
label(0x0006efd0, "geometry_vertex_attribute_packet_renderer",
      "Geometry vertex/attribute renderer that combines two object vectors, converts them to fixed-point packet fields, and emits the resulting command sequence to the 0x884000 FIFO.")
label(0x00068550, "geometry_object_profile_geometry_bounds_flags_update_variant_f",
      "Third parallel geometry bounds evaluator that clamps extents, applies object-record offsets, updates axis collision flags, and computes derived ratios.")
label(0x00068770, "geometry_object_profile_phase_selection_controller_variant_b",
      "Phase/selection controller that dispatches on state byte 0x1ae, advances object phase fields, and returns through its saved callback.")
label(0x00068a40, "geometry_command_packet_writer_variant_c",
      "Geometry command packet writer that serializes object data and transform fields to the 0x884000 FIFO.")
label(0x00069050, "geometry_object_profile_phase_selection_controller_variant_c",
      "State-byte phase/selection controller that dispatches on 0x1ae and advances object phase fields through its callback tail.")
label(0x00069560, "geometry_command_packet_writer_variant_d",
      "Geometry command packet writer variant that emits object data and transform fields to the 0x884000 FIFO.")
label(0x00069c60, "geometry_object_profile_phase_selection_controller_variant_d",
      "State-byte phase/selection controller variant that dispatches on 0x1ae and advances object phase fields through its callback tail.")
label(0x00069f30, "geometry_object_profile_match_phase_controller",
      "Larger match-phase controller that gates phase 27, updates object status and transforms, and performs terminal state transitions.")
label(0x0006a6a0, "geometry_object_profile_phase_selection_controller_variant_e",
      "State-byte phase/selection controller variant that dispatches on 0x1ae and advances object phase fields through its callback tail.")
label(0x0006aa60, "geometry_command_packet_writer_variant_e",
      "Geometry command packet writer variant that emits object data and transform fields to the 0x884000 FIFO.")
label(0x0006ae80, "geometry_object_profile_phase_selection_controller_variant_f",
      "State-byte phase/selection controller variant that dispatches through the 0x1ae jump table and advances object phase fields.")
label(0x0006b3d0, "geometry_object_transform_motion_controller",
      "Transform/motion controller that computes fixed-point object coordinates and phase-dependent offsets, then emits geometry commands to the 0x884000 FIFO.")
label(0x0006c770, "geometry_object_profile_phase_selection_controller_variant_g",
      "State-byte phase/selection controller variant that dispatches through the 0x1ae jump table and advances object transform state.")
label(0x0006cc20, "geometry_command_packet_writer_variant_f",
      "Geometry command packet writer variant that serializes object transform data and mode words to the 0x884000 FIFO.")
label(0x00027550, "geometry_record_transform_service",
      "Runtime match geometry uses the associated object-record path; this service stores the record transform fields before calling the 0x6f600 geometry producer.")
ensure_function(0x00027550, "geometry_record_transform_service", 0x00027c50)
label(0x000281f0, "texture_profile_setup",
      "Loads a profile table word, stores it at 0x512bd0, decompresses into swapped 0x11200000/0x11000000 banks, and routes decoder statuses 1 and 2 to the observed state updates.")
label(0x00028270, "texture_profile_match",
      "Compares the selected 0x280c0 profile-table word with 0x512bd0 and returns one only when they match.")
label(0x000280c0, "texture_profile_source_table",
      "Five ROM source pointers consumed by the 0x281f0 profile setup index table.")
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
label(0x00003c40, "startup_mode_handler_0",
      "Publishes device command 8, initializes progress 0x503a04 to 0x234 on phase zero, walks records at 0x2ea2918 through 0x1cac8 and 0x1cc40, then decrements progress and completes by setting 0x5024d4, clearing phase, and advancing mode.")
label(0x00003c4c, "startup_mode0_device_command")
label(0x00003c60, "startup_mode0_record_walk_gate")
label(0x00003c88, "startup_mode0_record_table_walk")
label(0x00003d18, "startup_mode0_progress_tail")
label(0x00003d38, "startup_mode0_completion_transition")
label(0x0002b9e0, "startup_mode_handler_1_status_dispatch",
      "Checks hardware/status mode, emits command 16, masks phase through the 32-entry table at 0x2b960, suppresses null entries and mode-2 handler 0xe3ab0 by advancing phase to 1, and selects the mode-2 or normal tail.")
label(0x0002ba44, "startup_mode1_table_dispatch")
label(0x0002ba58, "startup_mode1_null_or_special_suppression")
label(0x0002ba88, "startup_mode1_mode2_tail_gate")
label(0x0002ba90, "startup_mode1_mode2_candidate_scan")
label(0x0002badc, "startup_mode1_mode2_candidate_acceptance")
label(0x0002bb04, "startup_mode1_mode2_candidate_publish")
label(0x0002bb2c, "startup_mode1_normal_tail")
label(0x00018b00, "startup_mode4_dispatch_table",
      "64-entry phase dispatch table used by slot-4 tail 0x19328: entries 0..34 target recovered startup/status handlers and entry 35 onward is zero padding.")
label(0x00018c00, "startup_mode4_phase_table_arm_0",
      "Initializes 0x504c98 via 0x2a870/0x31a8 when clear, checks 0x5024f4 against 16 and seven mapped offsets (six for device 0x52), publishes progress 0x293/ready, or falls back to command 35 and phase 3; clears 0x503a20 and returns at 0x18d9c.")
label(0x00018c0c, "startup_mode4_arm_0_initialize")
label(0x00018c34, "startup_mode4_arm_0_device_checks")
label(0x00018cc8, "startup_mode4_arm_0_success_publish")
label(0x00018d3c, "startup_mode4_arm_0_failure_or_fallback")
label(0x00018d80, "startup_mode4_arm_0_state_increment")
label(0x00018da0, "startup_mode4_phase_table_arm_1",
      "Runs the shared record/formatter setup, decrements progress 0x503a04, rechecks the device/status bytes, selects setup 0x1111 or 0x1100, and advances through the persistent counter 0x504c94 to phase/command fallbacks at 0x1900c or 0x19028.")
label(0x00018e78, "startup_mode4_arm_1_device_failure")
label(0x00018e98, "startup_mode4_arm_1_status_gate")
label(0x00018f28, "startup_mode4_arm_1_extended_status_gate")
label(0x00018fa8, "startup_mode4_arm_1_counter_path")
label(0x00019010, "startup_mode4_arm_1_ready_fallback")
label(0x00019030, "startup_mode4_phase_table_arm_2",
      "Increments progress 0x503a04, performs one-time reset/setup 0x1c618/0x2a4e0(0x100b) and probe 0x201a0(1), emits marker+31 and -1, then advances phase when the device word matches the marker-derived command.")
label(0x00019048, "startup_mode4_arm_2_initial_setup")
label(0x00019060, "startup_mode4_arm_2_device_command")
label(0x000190b0, "startup_mode4_arm_2_phase_advance")
label(0x00019660, "startup_mode4_phase_table_arm_5",
      "Resets through 0x1c618/0x1ccf8(0), publishes 0x503a98 to 0x5032fc, emits command 31+g6 plus the ready adjustment, clears progress, advances phase, and returns at 0x196b8.")
label(0x0001966c, "startup_mode4_arm_5_status_command")
label(0x000196a4, "startup_mode4_arm_5_phase_advance")
label(0x000196c0, "startup_mode4_phase_table_arm_6",
      "Matches the device word against primary marker+31, status+31, or 32; the primary path increments progress and performs setup 0x1325 or the zero-progress 0x201a0/3/0x100b sequence, while alternate paths publish ready/phase/workspace transitions through 0x19820.")
label(0x000196d0, "startup_mode4_arm_6_progress_gate")
label(0x00019720, "startup_mode4_arm_6_progress_26_setup")
label(0x00019744, "startup_mode4_arm_6_status_match")
label(0x000197a0, "startup_mode4_arm_6_command32_match")
label(0x000197ec, "startup_mode4_arm_6_ready_clear_fallback")
label(0x00019830, "startup_mode4_phase_table_arm_7",
      "Resets phase/workspace helpers, clears 0x503a70/74/6c and mirrors them to 0x50330a/0c/0e, runs 0x296d0, selects ready/non-ready profile sources, maps status 0xff to 0xf423f or through table 0x2250, publishes record/workspace state, and advances phase before 0x19b4c.")
label(0x0001985c, "startup_mode4_arm_7_workspace_snapshot")
label(0x000198a8, "startup_mode4_arm_7_nonready_profile")
label(0x00019960, "startup_mode4_arm_7_ready_profile")
label(0x00019b38, "startup_mode4_arm_7_phase_advance")
label(0x0001a280, "startup_mode4_phase_table_arm_9_prefix",
      "Decrements progress 0x503a04 against threshold 31, optionally requests setup 0x131b, then gates ready/hardware/device state to publish command 31+r18, mark 0x503a60, select record helper arguments (14,16) or (14,18), and continue at 0x1a3fc.")
label(0x0001a2a0, "startup_mode4_arm_9_progress_setup_gate")
label(0x0001a2b0, "startup_mode4_arm_9_ready_hardware_gate")
label(0x0001a320, "startup_mode4_arm_9_device_match")
label(0x0001a3dc, "startup_mode4_arm_9_record_helper_continuation")
label(0x0001a4a0, "startup_mode4_phase_table_arm_10",
      "Consumes the slot-9 result: gates ready/hardware state, signed-compares timing against 0xeff, updates timing words 0x503a14/0x503a20, publishes signed halfwords at 0x5032fe/0x503300 only on the 0x1a558 path, and returns after the 0x43ee8 completion helper.")
label(0x0001a4a0, "startup_mode4_phase_table_arm_10_timing_prefix")
label(0x0001a4f0, "startup_mode4_arm_10_hardware_pointer_path")
label(0x0001a514, "startup_mode4_arm_10_ready_timing_path")
label(0x0001a558, "startup_mode4_arm_10_result_publication")
label(0x0001a578, "startup_mode4_arm_10_progress_controller_gate",
      "For signed-negative progress 0x503a94, calls 0x19b50 with progress-1 when controller byte 0x5024e8 is zero, or with 0/16 when the byte exceeds 64 and the controller word low five bits match; rejoins slot-10 status processing at 0x1a5cc.")
label(0x0001a5cc, "startup_mode4_arm_10_status_gate")
label(0x0001a5cc, "startup_mode4_arm_10_status_split",
      "Compares status 0x503a18 with signed threshold 0xf423e; the high-status arm records 0x1cac8(6,3), selects text service 0x1d210 when controller bit 4 is set or 0x1d1f0 otherwise, and rejoins at 0x1a7c8, while the other arm continues at 0x1a620.")
label(0x0001a620, "startup_mode4_arm_10_status_zero_math",
      "For status zero, computes the 31+r17 remainder/quotient through phase divisor 0x503a14, derives the 35x stride and (r5,r6) arguments for 0x1e800, and requests setup 0x1148 when the original remainder is zero and r5 is at most 9; nonzero status bypasses to 0x1a7c8.")
label(0x0001a660, "startup_mode4_arm_10_record_and_arithmetic_helpers")
label(0x0001a690, "startup_mode4_arm_10_ready_row_phase_gate",
      "Requires ready 0x503a7c clear and row 0x503a80 equal to 9, then selects phase masks 7/15/31/63 from r5 ranges <=0/1..2/3..5/>=6, requests setup 0x1340 on a zero masked phase, and sets the phase latch for the bounded low-phase cases before continuing at 0x1a778.")
label(0x0001a778, "startup_mode4_arm_10_timing_gate",
      "Derives and stores the signed timing expression at 0x504ccc from status 0x503a18 and phase 0x503a14, then calls 0x29c58 with the negative expression divided by 5 and argument 1 only when the expression is negative and 8-aligned; continues at 0x1a7d0.")
label(0x0001a7d0, "startup_mode4_arm_10_grid_update",
      "When ready 0x503a7c is clear, increments phase/workspace 0x503a1c and computes 0xb40/(phase+1), the 35x scaled 31+r17 remainder, and the (31+r29) remainder before calling 0x1e9e0 with the three derived arguments; ready paths bypass to 0x1a820.")
label(0x0001a820, "startup_mode4_arm_10_ratio_latch_gate",
      "Compares ratios 0x503ca8/0x503ca2 and 0x5042a8/0x5042a2; a zero 0x504cc4 latch selects warning 0x97/0x9f for the less-than arm or 0x91/0x99 for the equal/greater arm based on hardware mode 0x503a08, then records the latch and continues at 0x1a8d0.")
label(0x0001a8d0, "startup_mode4_arm_10_ready_status_route",
      "Routes ready-clear to 0x1aad4, hardware mode to 0x1aa20, failed status/r5/r6 to 0x1a9e0, and the accepted ready-normal state to 0x1a904; the status threshold uses an unsigned object comparison, so equality with 0xf423e is accepted.")
label(0x0001a904, "startup_mode4_arm_10_accepted_ratio_arm",
      "Increments retry counter 0x504cc8, sends counts already at least 4 to 0x1a9e0, otherwise compares signed ratios 0x503ca2/0x503ca8 and 0x5042a2/0x5042a8 to publish state/command 1/0x41, callback/0x40, or 2/0x42, then advances through 0x1ac44 with phase 0x503a00.")
label(0x0001a9e0, "startup_mode4_arm_10_zero_halfword_selector",
      "Tests signed-halfword sources 0x503ca2 and 0x5042a2: a zero first source publishes state 1/command 0x41, otherwise a zero second source publishes callback state/command 0x40, and the nonzero/nonzero case enters common service at 0x1ac50.")
label(0x0001aa20, "startup_mode4_arm_10_ready_device_selector",
      "Selects ready-side device words 0x40/0x41/0x42/0x43 at 0x5024f4, publishes state/command pairs (1,0x41), (callback,0x40), (2,0x42), and (5,0x43), advances phase through 0x1ac44, and sends other words to 0x1ac50.")
label(0x0001aad4, "startup_mode4_arm_10_ready_clear_entry",
      "Admits the ready-clear path only for status at most 0xf423e with r5/r6 both zero; phase zero calls 0x1fb50, requests setup 0x1012, publishes state 5 and command 0x43, and rejoins 0x1ac50, while nonzero phase enters the ratio arm at 0x1ab40.")
label(0x0001ab40, "startup_mode4_arm_10_ratio_state_arm",
      "Compares the two signed-halfword ratios used by slot 10: less-than publishes state 1/command 0x41, equality publishes state 2/command 0x42, and greater-than publishes callback state/command 0x40 while incrementing 0x503a90; all selected paths continue at 0x1ac50.")
label(0x0001aee4, "startup_mode4_arm_10_completion_packet",
      "When the local phase latch r7 is set, emits the fixed 13-word completion packet to 0x884000, publishes [0,0x400128,0x8f31a0,0] at 0x804000, writes 0x101 to 0x800010, and stores the 0x802008 source plus 0x34 at 0x801008 before returning at 0x1afd0.")
label(0x0001ac44, "startup_mode4_arm_10_phase_advance",
      "Increments phase/state word 0x503a00 by one and enters the shared input/timer gate at 0x1ac50; this is the common handoff for selected state/command arms.")
label(0x0001ac8c, "startup_mode4_arm_10_common_state_dispatch",
      "Dispatches state 0x503ab0 values 0/1/2/5 to 0x1ad14/0x1ace0/0x1ad5c/0x1acac and sends all other states to generic service at 0x1ada0.")
label(0x0001aca8, "startup_mode4_arm_10_state_setup_warning_arms",
      "For recognized states 0/1/2/5, requests setup 0x1314/0x1315/0x1313/0x1312 unless ready is clear with row 9, then emits warning 0x93/0x9b for state 0 or 0x97/0x9f for the other states according to hardware mode, and rejoins 0x1ada0.")
label(0x0001ac50, "startup_mode4_arm_10_input_timer_gate",
      "Rejects timer 0x503ca0 when nonpositive or at least the logical 0x503ca8>>3 threshold, masks controller 0x5024e8 to six bits, requests setup 0x1110 only for a zero mask on the remaining path, and continues at 0x1ac8c.")
label(0x0001ada0, "startup_mode4_arm_10_common_service_plan",
      "Runs the fixed record/object/formatter service sequence through 0x1ae64, including indirect callbacks at 0x503ad4 and 0x5040d4 and a final 0xdf070 call only when ready 0x503a7c is clear.")
label(0x0001ae64, "startup_mode4_arm_10_completion_gate",
      "Runs the final record/service calls, selects 0x23d60 argument 0 only for ready set, unsigned status at most 0xf423e, and r5/r6 both zero (otherwise 1), calls 0x87f60 with 0x503ad0/0x5040d0, and enters the completion packet at 0x1aee4.")
label(0x0001afe0, "startup_mode4_phase_table_arm_11_prefix",
      "Clears marker 0x503a60, derives the 0x503a30 timing-table index from 0x503a1c using divisors r17+31 and 0xb40 plus the 3x/96x (99x total) remainder path and r29+31 remainder calculation, calls helper 0x1e9e0, stores the timing delta, and continues at 0x1b054.")
label(0x0001b000, "startup_mode4_arm_11_grid_index_arithmetic")
label(0x0001b02c, "startup_mode4_arm_11_grid_helper")
label(0x0001b038, "startup_mode4_arm_11_timing_table_publish")
label(0x0001b054, "startup_mode4_arm_11_service_bridge",
      "Runs the slot-11 record/buffer service sequence with indirect callbacks at 0x503ad4 and 0x5040d4, conditionally adds the ready-clear 0xdf070 call, copies signed halfwords 0x503ca2/0x5042a2 into timer words 0x503ca0/0x5042a0, calls 0x23d60 with zero, and dispatches the state through 0x8d0b8 before 0x1b160.")
label(0x0001b184, "startup_mode4_arm_11_state0_progress_arm",
      "For state 0, updates 0x504242/0x50424a from row 0x504134 and 31+r10 when ready is clear, publishes state 3, increments 0x503a6c, and on ready-set signed progress above 0x503a78 increments 0x503a94 and calls 0x20060 then 0x19b50 before 0x1b2fc.")
label(0x0001b244, "startup_mode4_arm_11_state45_latch_arm",
      "For state 1 or 5, compares latch halfword 0x503c42 against the mode-9/6 special case or shifted sentinel 0x290000, updates 0x503c42 and callback 0x503c4a when required, publishes state 4, increments 0x503a70, saves 0x504b94, and calls 0x20180 before 0x1b2fc.")
label(0x0001b2cc, "startup_mode4_arm_11_state2_counter_arm",
      "For state 2, saves the callback at 0x504b94, increments 0x503a6c and 0x503a70 with 32-bit wraparound, and rejoins the shared counter publication at 0x1b2fc.")
label(0x0001b2fc, "startup_mode4_arm_11_counter_publication",
      "Increments 0x503a74, snapshots low halfwords from 0x503a6c/0x503a70, publishes them at 0x50330a/0x50330c/0x50330e, and enters the command-20 trigger gate when ready is clear, the full signed 0x503a6c exceeds signed 0x503a78, and signed row 0x503a80 exceeds 8.")
label(0x0001b330, "startup_mode4_arm_11_counter_snapshot_publish")
label(0x0001b350, "startup_mode4_arm_11_command20_gate")
label(0x0001b400, "startup_mode4_arm_11_return_tail",
      "Publishes 31 or 31+g2 to 0x503a00, conditionally publishes command 20 when signed 0x503a70 <= 0x503a78 and ready is clear, sets progress 0x503a04 to 90, and returns at 0x1b460.")
label(0x0001b420, "startup_mode4_arm_11_state_publication")
label(0x0001b438, "startup_mode4_arm_11_final_command_gate")
label(0x0001b470, "startup_mode4_phase_table_arm_12",
      "Slot 12 repeats the grid-index/helper setup, then performs service initialization and a progress countdown: setup 3 is requested at progress 1, high progress above 0xaf diverts on control bit 4, and the ordinary path decrements 0x503a04 before ready/device gating.")
label(0x0001b470, "startup_mode4_arm_12_setup_prefix",
      "On ready-clear, repeats the 99x remainder grid arithmetic with divisor r17+31 and helper 0x1e9e0, then continues through 0x445a0 at 0x1b4b4; ready-set paths skip the grid helper.")
label(0x0001b598, "startup_mode4_arm_12_progress_setup_gate",
      "Requests setup 3 at progress 1, diverts signed-high progress above 0xaf on control bit 4 without decrementing, otherwise decrements 0x503a04; zero countdown or high diversion enters 0x1b614, while nonzero countdown enters 0x1b5d8.")
label(0x0001b5c8, "startup_mode4_arm_12_progress_countdown")
label(0x0001b5d8, "startup_mode4_arm_12_ready_device_gate",
      "Returns to 0x1b95c when ready is clear; otherwise compares the sign-extended low halfword loaded from 0x5024f4 with 31+r19, then applies the masked 0xffed fallback before 0x43ee8 or 0x1b95c.")
label(0x0001b5e4, "startup_mode4_arm_12_device_command_match")
label(0x0001b5f4, "startup_mode4_arm_12_device_status_fallback")
label(0x0001b614, "startup_mode4_arm_12_common_completion_gate",
      "Runs completion helpers 0x43ee8 and 0x423a8 in order, then enters the counter dispatcher at 0x1b61c.")
label(0x0001b61c, "startup_mode4_arm_12_counter_dispatch",
      "After completion, signed-compares 0x503a6c and 0x503a70 against 0x503a78; only when both counters are at or below the limit does it select state 8 at 0x1b800, while a secondary counter within the limit routes to 0x1b780 and the remaining cases take the 0x31c0 helper path at 0x1b650.")
label(0x0001b638, "startup_mode4_arm_12_secondary_counter_gate")
label(0x0001b650, "startup_mode4_arm_12_over_limit_record_path",
      "Calls 0x31c0, increments the 0xac or 0xb0 record lane selected by 0x503a7c, calls 0x2330, then checks only the diagnostic byte when ready is clear or both status word and byte when ready is set before publishing state 15/command 19 or running 0x29c08 for command 20/state increment; finally notifies 0x184e8 with 0xf0 or 0xf9 and continues at 0x1b950.")
label(0x0001b780, "startup_mode4_arm_12_ready_record_path",
      "For ready state, stores g14 at 0x503a84, increments 0x503a64 and the mapped 0xac record selected by 0x503a98, then selects state 15/command 19 when 0x503aa8 is zero or state 5 with the low halfword of 31+r19 otherwise, before 0x1b950.")
label(0x0001b7d4, "startup_mode4_arm_12_ready_status_split")
label(0x0001b818, "startup_mode4_arm_12_clear_ready_record_path",
      "For clear ready state, publishes state 7, increments 0x503a64 and the mapped 0xac record entry, increments row 0x503a80, and for a signed row value below 9 overwrites it with g14, calls 0x31c0, publishes command 19/state 17, and continues at 0x1b940.")
label(0x0001b864, "startup_mode4_arm_12_row_limit_gate")
label(0x0001b880, "startup_mode4_arm_12_row_retry_path")
label(0x0001b8a8, "startup_mode4_arm_12_row5_phase_gate",
      "When the incremented row is 5, signed-divides 0x503a1c by 0x503a8c and publishes the low halfword of 31+r19; signed quotient <= 0x690 selects state 6/row 6 at 0x1b924, while a larger quotient selects state 27, writes g14 to progress, sets bit 0 at 0x10000000, and continues at 0x1b940.")
label(0x0001b8bc, "startup_mode4_arm_12_row5_quotient_gate")
label(0x0001b8e8, "startup_mode4_arm_12_row5_high_quotient")
label(0x0001b914, "startup_mode4_arm_12_terminal_command_tail",
      "Publishes the low halfword of 31+r19, promotes state to 28 when row 0x503a80 equals 6, publishes the row low halfword at 0x5032f8, calls 0x1fe90, requests setup 3 through 0x2a4e0, and returns at 0x1b95c.")
label(0x0001b924, "startup_mode4_arm_12_row6_state28")
label(0x0001b940, "startup_mode4_arm_12_row_publication_return")
label(0x0001b960, "startup_mode4_phase_table_arm_15",
      "Runs setup/clear helper 0x29c08, stores the low byte of g14 at 0x5024c6, publishes state 25 to 0x503a00, and returns at 0x1b97c.")
label(0x0001b974, "startup_mode4_arm_15_state_return")
label(0x0001b9d0, "startup_mode4_phase_table_arm_16_counter_dispatch",
      "Masks 0x503a04 to bit 5 for helper 0x1fa30, bypasses decrement when flag bit 4 at 0x5024a4 is set, otherwise decrements the counter, and enters link publication at 0x1ba08 only from the flag path or an entry counter of 1.")
label(0x0001b9e0, "startup_mode4_arm_16_counter_helper_argument")
label(0x0001ba08, "startup_mode4_arm_16_link_publication",
      "Calls 0x2a4e0 with argument 2, stores flag 1 at 0x5039f4, publishes resume link 0x1ba10 at 0x503a00, and returns at 0x1ba24.")
label(0x0001ba10, "startup_mode4_arm_16_link_state")
label(0x0001ba30, "startup_mode4_phase_table_arm_17_service_head",
      "Runs 0x1c618, 0x1ccf8 with g0=0, 0x2a4e0 with argument 0x1013, and 0x1fa00; presets 0x503a04 to 0x12c, increments 0x503a00, and returns at 0x1ba6c.")
label(0x0001ba4c, "startup_mode4_arm_17_service_state_update")
label(0x0001ba70, "startup_mode4_phase_table_arm_18_threshold_dispatch",
      "Calls 0x2a4e0 with 0x1317 only when 0x503a04 equals 480, bypasses decrement on flag bit 4 at 0x5024a4, otherwise decrements and publishes state 22 only from counter 1, then returns at 0x1babc.")
label(0x0001ba80, "startup_mode4_arm_18_threshold_call")
label(0x0001bab0, "startup_mode4_arm_18_state22_publication")
label(0x0001bac0, "startup_mode4_phase_table_arm_19_flag_block",
      "Checks counter 0x503a04 against 0x118, runs 0x1c618 and clears the low 16 bits of 0x10000000 on equality, then advances the counter and returns at 0x1bb4c.")
label(0x0001bafc, "startup_mode4_arm_19_counter_mask_gate")
label(0x00086dc0, "startup_mode4_phase_table_arm_20_fifo_prelude",
      "Copies 0x600 bytes from 0x51c9e0 to 0x503ad0 and from 0x51cfe0 to 0x5040d0, loads 0x503ad8/0x5040d8/0x503ae0/0x5040e0 and emits their values in FIFO words [31, v503ad8, v5040d8, 0, 0, v503ae0, v5040e0] at 0x884000, loads the response from 0x51c9d0, then dispatches response 1 to 0x86eec and other responses to 0x873dc.")
label(0x00086e74, "startup_mode4_arm_20_fifo_packet")
label(0x00086edc, "startup_mode4_arm_20_response_dispatch")
label(0x00086eec, "startup_mode4_arm_20_response_selector",
      "Loads the selector response from 0x51c98c; treats value 10 as a special park value 8 at 0x51c97c; otherwise masks to 8 bits, rounds nonzero values down by (value-1)%6, routes values above 0xaf to 0x878e8, and indexes dispatch table 0x86f34.")
label(0x00086f08, "startup_mode4_arm_20_response_normalization")
label(0x00086f20, "startup_mode4_arm_20_response_table_dispatch")
label(0x00086f34, "startup_mode4_arm_20_response_dispatch_table")
label(0x000871f4, "startup_mode4_arm_20_response_handler_01")
label(0x00087210, "startup_mode4_arm_20_response_handler_1f",
      "Moves g6 into fp0, prepares extended-real compare pair r4=0/r5=0x40590000, and routes a less-than result to 0x878e8 or the non-less path to 0x87394.")
label(0x0008722c, "startup_mode4_arm_20_response_handler_25",
      "Sets r5=10, loads 0x51c98c, sets r4=1, passes 0x5040d0, and branches to 0x87738.")
label(0x00087738, "startup_mode4_arm_20_response_25_mode11_continuation",
      "Publishes mode 11 and flag 1 at 0x51c97c/0x51c9a0, stores 0x51c990 >> 8 at 0x51c994, calls 0x8c970 with buffer 0x503ad0, and continues at 0x878f8.")
label(0x000876e8, "startup_mode4_arm_20_secondary_response_handler_01",
      "Sets mode 15, loads 0x51c990, sets flag 1 with buffer 0x5040d0, and enters shared continuation 0x87864.")
label(0x00087704, "startup_mode4_arm_20_secondary_response_handler_1f",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087720, "startup_mode4_arm_20_secondary_response_handler_25",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x0008775c, "startup_mode4_arm_20_secondary_response_handler_31",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087778, "startup_mode4_arm_20_secondary_response_handler_37",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087794, "startup_mode4_arm_20_secondary_mode11_entry",
      "Sets mode 11 and jumps to shared setup 0x87850.")
label(0x0008779c, "startup_mode4_arm_20_secondary_response_handler_49",
      "Compares against 0x40590000 and 0x4072c000: below the first threshold branches to 0x878e8, the middle band enters mode-7 setup at 0x878a4, and the high band enters mode-5 setup at 0x878a0.")
label(0x000877d0, "startup_mode4_arm_20_secondary_response_handler_4f",
      "Publishes mode 5 and flag 1 at 0x51c97c/0x51c9a0, stores 0x51c990 >> 8 at 0x51c994, calls 0x88a10 with buffer 0x503ad0, and continues at 0x878d8.")
label(0x0008780c, "startup_mode4_arm_20_secondary_response_handler_7f",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087828, "startup_mode4_arm_20_secondary_response_handler_85",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087888, "startup_mode4_arm_20_secondary_response_handler_a9",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x878a0.")
label(0x00087248, "startup_mode4_arm_20_response_handler_31",
      "Moves g6 into fp0, prepares extended-real compare pair r4=0/r5=0x40590000, and routes a less-than result to 0x878e8 or the non-less path to 0x87394.")
label(0x00087264, "startup_mode4_arm_20_response_handler_37",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x87394.")
label(0x00087280, "startup_mode4_arm_20_response_handler_3d",
      "Moves g6 into fp0, compares against extended-real pair r4=0/r5=0x40590000, and branches less-than to 0x878e8 or otherwise to 0x87394.")
label(0x0008729c, "startup_mode4_arm_20_response_handler_49",
      "Compares fp0 against 0x40590000 and then 0x4072c000: below the first threshold branches to 0x878e8, the intermediate band sets r5=6 and branches to 0x87398, and the high band branches to 0x87394.")
label(0x00087398, "startup_mode4_arm_20_response_49_intermediate_continuation")
label(0x00087394, "startup_mode4_arm_20_shared_response_continuation",
      "Converged response paths set r5=4/r4=1, reload 0x51c98c, publish 4/1 and g4>>8 at 0x51c97c/0x51c9a0/0x51c994, call 0x888f0, pass 0x503ad0 to 0x88af0, and continue at 0x878f8.")
label(0x000873cc, "startup_mode4_arm_20_shared_response_buffer_call")
label(0x000873dc, "startup_mode4_arm_20_secondary_response_selector",
      "Rejects nonzero FIFO status from g0/0x51c9d0 to 0x878e8, then reloads the selector value from 0x51c990; parks value 10 as mode 9 at 0x51c97c before 0x878d8, otherwise masks/rounds the response, and dispatches through table 0x87428 with the same sparse normalized keys.")
label(0x00087428, "startup_mode4_arm_20_secondary_response_dispatch_table")
label(0x000878e8, "startup_mode4_arm_20_failure_to_shared_tail",
      "Calls 0xf5058, masks the helper result to bit 0, stores that result at 0x51c97c, and continues at 0x878f8.")
label(0x00087a10, "startup_mode4_arm_20_secondary_clear_gate",
      "Uses callback trampoline 0x87a98: bit 4 of 0x5024a4 immediately returns g0=1; otherwise zero 0x503a7c returns g0=0, while nonzero control with exception word 0x61/0x63 compares 0x503a70 <= 0x503a78 to store command 0x63 or 0x61 at 0x5032f4 before returning g0=1.")
label(0x00087b10, "startup_mode4_arm_20_secondary_fifo_tail",
      "Calls 0x294b0, writes literal FIFO words 8 and 16 to 0x884000, and continues at 0x87b2c where the 0x51c988 state is reloaded.")
label(0x00087ac0, "startup_mode4_arm_20_secondary_probe_loop",
      "Checks phase 0x503a00 against 20, probes through 0x8d0d8, gates through callback body 0x87a18, retries 0x18ab0 with r4=0..4 when needed, and calls 0x8d108 before entering the fixed FIFO tail at 0x87b10; phase-20 or non-one probe results continue directly at 0x87b2c.")
label(0x00087b2c, "startup_mode4_arm_20_secondary_state_prefix",
      "Advances 0x51c988 when nonzero or 0x51d5e4 when zero, clamps the timing candidate above 0x77 to zero, runs 0x88620/0xc8f10/0x6fec0/0x9b308/0x6fec0/0xc8f60, selects 0x503ad0 or 0x5040d0 from 0x51c9b4 for 0x9baa0, and calls 0xde990.")
label(0x00087bbc, "startup_mode4_arm_20_secondary_service_bridge",
      "Calls 0xde990, runs first-buffer services 0xbe1f0/0xbd730/0x503ad4/0x23980/0xdf070, then second-buffer services 0x26cb8/0xbd810/0x5040d4 through their indirect callback slots before entering the 0x503a7c gate at 0x87c2c.")
label(0x00087c2c, "startup_mode4_arm_20_secondary_indexed_upload_gate",
      "Runs optional 0xdf070 cleanup when 0x503a7c is zero; for negative 0x51c988, computes timing rounded up then masked by ~3 and uploads 0x400-byte table pairs only when the original timing differs from that aligned value, before common services 0xbece0/0x9b320/0x41f20/0xc5530/0x6fec0/0x71080.")
label(0x00087ce8, "startup_mode4_arm_20_secondary_timer_publication",
      "For nonnegative 0x51c988, copies signed halfwords from 0x51cbb0/0x51d1b0 to 0x503ca0/0x5042a0, then calls 0x23d60(1), 0x1cac8(21,14), and 0x1fe60 with 0x5024e8 masked to bit 2; negative state skips the halfword publication.")
label(0x00087d14, "startup_mode4_arm_20_secondary_command_setup",
      "Calls 0x23d60 with 1, formats through 0x1cac8 with arguments 21 and 14, masks 0x5024e8 to bit 2, and calls 0x1fe60 before the timing/upload branch at 0x87d38.")
label(0x00087d38, "startup_mode4_arm_20_secondary_timing_upload",
      "Rounds positive 0x51d5e4 upward by 3 and masks by ~3; when negative 0x51c988 and timing differs from the aligned value, indexes paired 0x600-byte blocks from 0x51d5f0/0x5289f0 and emits fixed 0x580-byte uploads from 0x560df0/0x561370 to 0x565320/0x5658a0 through 0xf5d40.")
label(0x00087de4, "startup_mode4_arm_20_secondary_state_seed_gate",
      "Compares 0x51d5e4 with 0x51d5e8 and then 0x51c988 with -1; only when both comparisons are equal stores g14 into 0x51c988, otherwise continues at 0x87e10.")
label(0x00087e10, "startup_mode4_arm_20_secondary_response_publication_gate",
      "Routes state above 31+r29 or flag bit 4 directly to response publication at 0x87e50; otherwise requires nonzero 0x503a7c and exception word 0x61/0x63 for publication, with all other cases returning at 0x87f50. Response 1 stores g14 at 0x503ca2 and response 0 stores g14 at 0x5042a2.")
label(0x00087e70, "startup_mode4_arm_20_secondary_response_buffer_setup",
      "For negative 0x51c988, uploads 0x600-byte blocks from 0x51c9e0/0x51cfe0 to 0x503ad0/0x5040d0, stores g14 at 0x503c4a/0x50424a, sets 0x503a00 to 12, formats with 0x1cac8(21,14), and renders source 0x87aa0 through 0x1da90.")
label(0x00087ee0, "startup_mode4_arm_20_secondary_terminal_publication",
      "Stores marker 1 at 0x503a60, maps 0x503aa4 values 0/1 to progress 1 and other values to 0xb4 at 0x503a04, selects command 0x61 or 0x63 from 0x503a70 <= 0x503a78, stores it at 0x5032f4, records g14 at 0x51d5e0, and returns at 0x87f50.")
label(0x00087f60, "startup_mode4_arm_20_secondary_counter_gate",
      "Initializes 0x51c9b0 from g14 and calls 0x8d170 when 0x503a14 is zero; otherwise increments 0x51c9b0, then admits the modulo-120 upload body at 0x87fac only when the resulting counter has low two bits clear.")
label(0x00087fac, "startup_mode4_arm_20_secondary_counter_upload_body",
      "Computes 0x51c9b0 % 120 and row index >> 2, uploads indexed 0x600-byte pairs from 0x51d5f0/0x5289f0 to caller destinations r5/r6, then emits fixed 0x580-byte copies from 0x560df0/0x561370 to 0x565320/0x5658a0 before 0x88030.")
label(0x00088030, "startup_mode4_arm_20_secondary_row_publication",
      "Publishes 0x108 halfwords from r5/r6 into 0x5618f0/0x561e90 at 12-byte slots indexed by 0x51c9b0 % 120; for nonzero counter low bits, computes (9*remainder) % 90 and uploads 0x400-byte pairs from 0x533df0/0x54a5f0 to r5+0x200/r6+0x200, then calls 0x880c0.")
label(0x000880c0, "startup_mode4_arm_20_secondary_flag_pair",
      "Decodes each caller mask independently: bit overlap with 0x5024a4 produces code 2, otherwise overlap with 0x50249c produces code 4, otherwise code 0; the first lane uses mask r5 and the second mask g1 before continuing at 0x88100.")
label(0x00088100, "startup_mode4_arm_20_secondary_flag_aggregate",
      "Adds bit 4 when 0x5024a4 overlaps r6/g2, otherwise bit 5 when 0x50249c overlaps r5/g1, preserving the two prior lane codes, then indexes 0x5618f0 by 0x51c9b0 % 120 and stores g7/g6 at row offsets +4/+8 before returning at 0x881a4.")
label(0x000881b0, "stage_slot_update_trampoline_881b0",
      "Loads return trampoline 0x881f4, preserves it in g2, indexes 0x561e90 by 0x51c9b0 % 120, stores caller words g0/g1 at offsets +4/+8, and returns through bx(g2) at 0x881f0.")
label(0x00088200, "stage_row_value_accessor_88200",
      "Loads return trampoline 0x88240, returns 0xffff when 0x51c988 is nonpositive, otherwise multiplies 0x51d5e4 by 12 and reads a halfword from 0x5618f0 before returning through bx(g1).")
label(0x00088250, "stage_published_row_value_accessor_88250",
      "Loads return trampoline 0x88290, returns 0xffff when 0x51c988 is nonpositive, otherwise multiplies 0x51d5e4 by 12 and reads a halfword from 0x561e90 before returning through bx(g1).")
label(0x000882a0, "stage_paired_row_accessor_882a0",
      "Loads return trampoline 0x88304, zeroes both caller outputs when 0x51c988 is nonpositive, otherwise multiplies 0x51d5e4 by 12 and reads 0x5618f0 row offsets +4/+8 into g0/g1 before returning through bx(g2).")
label(0x00088310, "stage_paired_published_row_accessor_88310",
      "Loads return trampoline 0x88374, zeroes both caller outputs when 0x51c988 is nonpositive, otherwise multiplies 0x51d5e4 by 12 and reads 0x561e90 row offsets +4/+8 into g0/g1 before returning through bx(g2).")
label(0x00088620, "startup_mode4_arm_20_secondary_frame_setup",
      "Calls 0x295d0, emits FIFO setup words 8 and 16, calls 0x2a990 with 0xd000 and zero seed, publishes the low byte of g14 at 0x503c7a, advances 0x51c984 with a 0xb4 clamp, and dispatches below mode 15 directly to 0x88780 or selects the sparse 0x88690 table entries with their buffer/helper pairs.")
label(0x0008878c, "startup_mode4_arm_20_secondary_frame_finalize",
      "After the mode handler returns, emits FIFO opcodes 20/21/18 with the 0x51c944 short field, negated 0x51c940 field, and bit-31-toggled 0x51c950/0x51c94c words; snapshots 0x51c950/0x51c94c/0x51c954 to 0x504b98/0x504b9c/0x504ba0, stores short fields at 0x504ba8/0x504baa, derives 0x504d28 and 0x5770f4, and returns at 0x88878.")
label(0x00088880, "secondary_record_state_loader_88880",
      "Requires phase 10 and record word +0x30 equal to zero; conditionally copies nonzero halfwords at record +0x48 and linked record +0x74/+0x48 into 0x51c98c/0x51c990, zero-extends record +0x1d6, and passes the values to 0x861e8 before returning at 0x888e8.")
label(0x00088948, "startup_mode4_arm_888f0_status_scan",
      "After the paired uploads, decrements timing by four with nonpositive wrap to 0x78, scans 29 indexed status bytes, arms on the first nonzero byte, stores the next zero's timing at 0x51c998, or publishes g14 at 0x51c9a0 when no zero-after-hit is found, then returns at 0x88a04.")
label(0x00088a64, "startup_mode4_arm_88a10_status_scan",
      "After the paired uploads, decrements timing by four with nonpositive wrap to 0x78, scans up to 29 indexed status bytes, stores the first zero's timing at 0x51c998, or publishes g14 at 0x51c9a0 when all 29 results are nonzero, then returns at 0x88ae8.")
label(0x00088b44, "startup_mode4_arm_88af0_status_gate",
      "After the paired uploads, scans the linked record +0x1d0 marker across up to 29 timing passes; a nonzero marker stores r5-6 with nonpositive wrap at 0x51c9b8, while 29 zero markers store -1, then returns at 0x88bc8.")
label(0x00088bd0, "startup_mode4_arm_88bd0_dispatch_gate",
      "Adjusts the stack, gates on 0x51d5e0/0x51c99c, seeds 0x51d5e0 when timing equals 0x51c9b8, conditionally promotes 0x51c9a0, evaluates the indexed status byte, selects 0x51c99c values 1/2 or the threshold-derived g14 value, and dispatches through table 0x88cec from 0x88cd4 via load at 0x88ce0.")
label(0x00088cec, "startup_mode4_arm_88cec_dispatch_table",
      "Six-entry table selected by 0x51c99c at load site 0x88ce0: selectors 0..5 target 0x88d04, 0x88ea0, 0x8903c, 0x8931c, 0x89930, and 0x89814 before bx(g4).")
label(0x00088d04, "startup_mode4_arm_88d04_packet_prefix",
      "Loads record +0x184, emits command 29 with (record +0x184 - 0x6000) masked to 16 bits and 0x42a00000, emits command 30 with the same transformed value and constant, then consumes the FIFO response before continuing at 0x88d70.")
label(0x00088d70, "startup_mode4_arm_88d70_response_state_bridge",
      "Combines the command-29 response with record +8 into 0x51c950, subtracts the command-30 response from record +0x10 into 0x51c954, stores record +0x184 at 0x51c940 and 0x42a00000 at 0x51c948, then branches at 0x88da8 into the floating/state tail.")
label(0x00088e4c, "startup_mode4_arm_88e4c_state_packet",
      "Emits command 10 with 0x51c948 and the computed state word, consumes the FIFO response, stores computed g7 at 0x51c94c and the response at 0x51c944, then branches on record +0x30 to 0x89ad8 or 0x89ac8.")
label(0x00088ea0, "startup_mode4_arm_88ea0_packet_prefix",
      "Loads record +0x184 from the linked record, emits command 29 with (record +0x184 + 0x6000) masked to 16 bits and 0x42a00000, emits command 30 with the same transformed value and constant, then consumes the FIFO response before 0x88f04.")
label(0x0008903c, "startup_mode4_arm_8903c_packet_prefix",
      "Builds command 29 and command 30 from record +0x184 minus 0x6000, then emits command 31 with the first response plus record +8, selector-table words at +0x10/+0x18, and record +0x10 minus the second response before the state/status tail.")
label(0x0008931c, "startup_mode4_arm_8931c_packet_state_prefix",
      "Selector-3 arm: builds command 29/30 from record +0x184 minus 0x6000, emits command 31 with response-derived record fields and selector-table words, retains the unmasked transform at 0x51c940, publishes 0x51c948/0x51c950/0x51c954, and continues at 0x89450.")
label(0x00089930, "startup_mode4_arm_89930_packet_state_prefix",
      "Selector-4 arm: builds command 29/30 from record +0x184 plus 0x6000, retains the unmasked transform at 0x51c940, publishes response-derived 0x51c950/0x51c954 and 0x42a00000 at 0x51c948, then branches at 0x899d8 into the floating tail.")
label(0x000899d8, "startup_mode4_arm_899d8_float_tail",
      "Consumes the 0x6ece0 result, selects it when nonpositive or substitutes 30.0f, subtracts record +0x0c in single precision, emits command 10 with 0x51c948, preserves 0x51c940, publishes 0x51c94c/0x51c944, and branches on record +0x30 at 0x89ac4.")
label(0x00089ac8, "startup_mode4_arm_common_state_commit_89ac8",
      "Commits selector-tail state: chooses 1 or g14 for 0x51c9b4 from record +0x30, conditionally writes g14 to 0x51d5e0 when record +0x64 is 7, rolls 0x51c950/0x51c94c/0x51c954 into 0x51c958/0x51c95c/0x51c960, and returns at 0x89b20.")
label(0x00089b30, "startup_mode4_arm_common_dispatch_89b30",
      "Maps 0x51c984 thresholds to selector 0/g14/1/2/3, emits command 10 from current and linked record deltas, stores the FIFO response at 0x51c940, and dispatches selectors 0..3 to 0x89c04/0x89e44/0x8a178/0x8a4bc.")
label(0x00089c04, "startup_mode4_arm_89c04_packet_state_prefix",
      "Selector-0 downstream arm: derives 0xb4-0x51c984, forms a prior-response-plus-0x1000 base minus the timing delta, emits command 29/30 with its low 16 bits and computed packet word, publishes 0x51c940/0x51c942/0x51c948/0x51c950/0x51c954, and branches at 0x89cf4.")
label(0x00089cf4, "startup_mode4_arm_89cf4_float_packet_tail",
      "Calls 0x6ece0 with the state-derived pair, selects a nonpositive result or 30.0f, builds the first command-10 delta packet and the second command-10 float packet, publishes 0x51c940/0x51c944/0x51c94c, and branches to 0x8a880 or 0x8a16c from record +0x30.")
label(0x00089e44, "startup_mode4_arm_89e44_packet_state_prefix",
      "Selector-1 downstream arm: derives the 0xb4 timing delta and prior-response-plus-0x1000 transform, emits command 29/30 with the low 16-bit operand and computed packet word, publishes 0x51c940/0x51c942/0x51c948/0x51c950/0x51c954, and continues at 0x89f34.")
label(0x00089f34, "startup_mode4_arm_89f34_float_selection",
      "Calls 0x6ece0 with the selector-1 state-derived pair, selects a nonpositive result or 30.0f, records the 0x5770f0 timing predicate, and hands the selected float to the fixed-point continuation at 0x89f9c.")
label(0x0008a178, "startup_mode4_arm_8a178_packet_state_prefix",
      "Selector-2 downstream arm: loads 0x5770f0/0x51c984, derives the 0xb4 timing delta, transforms prior response plus 0x1000 by the byte-scaled delta, publishes 0x51c940/0x51c942, and continues at 0x8a1c0.")
label(0x0008a1c0, "startup_mode4_arm_8a1c0_float_selection",
      "Calls 0x6ece0 with 0x51c950/0x51c954, selects a nonpositive result or 30.0f, records the 0x5770f0 timing predicate, and hands the selected float to the scale continuation at 0x8a234.")
label(0x0008a350, "startup_mode4_arm_8a350_packet_sequence",
      "Selector-2 packet checkpoint: emits command 29/30 from 0x51c940 low16 and 0x51c948, derives command-10 current/linked deltas from both responses, then emits command 31 with the response/current/linked fields before continuing at 0x8a43c.")
label(0x0008a43c, "startup_mode4_arm_8a43c_response_tail",
      "Selector-2 response tail: subtracts linked record +0x0c from the selected float, emits command 10 with the command-31 response and float delta, preserves 0x51c950/0x51c954, publishes 0x51c940/0x51c944, and branches on record +0x30 to 0x8a880 or 0x8a16c.")
label(0x0008a4bc, "startup_mode4_arm_8a4bc_float_prefix",
      "Selector-3 arm: derives the 0xb4 timing delta and prior-response-plus-0x1000 transform, publishes 0x51c940/0x51c942, calls 0x6ece0 with 0x51c950/0x51c954, selects a nonpositive result or 30.0f, and continues at 0x8a584.")
label(0x0008a670, "startup_mode4_arm_8a670_packet_state",
      "Selector-3 packet/state sequence: emits command 29/30 from 0x51c940 low16 and 0x51c948, derives response-relative rolling values, publishes 0x51c950/0x51c954 and 0x51c958/0x51c95c/0x51c960, then emits command 31 and stores its response at 0x51c940.")
label(0x0008a7e4, "startup_mode4_arm_8a7e4_response_tail",
      "Selector-3 response tail: completes the command-31 FIFO payload, emits command 10 with the first response and computed packet word, stores the final response at 0x51c944, and branches on record +0x30 to 0x8a16c or 0x8a880.")
label(0x0008a880, "startup_mode4_arm_8a880_force_state",
      "Selector-tail success epilogue: writes 1 to 0x51c9b4 and returns at 0x8a88c.")
label(0x0008a890, "startup_mode4_arm_8a890_post_dispatch",
      "Post-selector dispatch: selects 0x51c99c from the 0x51c984 threshold bands, emits command 10 from current/linked record deltas, stores the response at 0x51c940, and routes selectors 0..3 to 0x8a964/0x8aba4/0x8aed8/0x8b21c.")
label(0x0008a964, "startup_mode4_arm_8a964_packet_state_prefix",
      "Selector-0 arm: derives the 0xb4 timing delta and prior-response transform, emits command 29/30 from the computed operand and float word, publishes 0x51c940/0x51c942/0x51c948 and response-relative 0x51c950/0x51c954, then continues at 0x8aa54.")
label(0x0008aa54, "startup_mode4_arm_8aa54_float_packet_tail",
      "Selector-0 floating tail: calls 0x6ece0, selects a nonpositive result or 30.0f, adds 2.5f when 0x5770f0 is zero, emits two command-10 packets, publishes 0x51c940/0x51c944/0x51c94c, and branches on record +0x30 to 0x8b604 or 0x8aecc.")
label(0x0008ac94, "startup_mode4_arm_8ac94_float_selection",
      "Selector-1 helper selection: calls 0x6ece0, selects a nonpositive result or 30.0f, adds 2.5f when 0x5770f0 is zero, and continues at 0x8ad00.")
label(0x0008ad00, "startup_mode4_arm_8ad00_packet_state_tail",
      "Selector-1 packet/state tail: publishes rolling 0x51c958/0x51c95c/0x51c960 values, completes command 31, emits two command-10 packets, stores responses at 0x51c940/0x51c944, and routes to 0x8aecc or 0x8b604 from record +0x30.")
label(0x0008aed8, "startup_mode4_arm_8aed8_packet_state_prefix",
      "Selector-2 arm: derives the timing delta and prior-response-plus-0x1000 transform, publishes 0x51c940/0x51c942, and calls 0x6ece0 with the existing 0x51c950/0x51c954 pair before continuing at 0x8af20.")
label(0x0008af20, "startup_mode4_arm_8af20_float_selection",
      "Selector-2 helper selection: calls 0x6ece0 with 0x51c950/0x51c954, selects a nonpositive result or 30.0f, adds 2.5f when 0x5770f0 is zero, and continues at 0x8af94.")
label(0x0008af94, "startup_mode4_arm_8af94_scale_state",
      "Selector-2 scale/state block: bounds the computed scale against 0x51c948, chooses positive versus nonpositive packet arithmetic, publishes 0x51c94c/0x51c948, and reconverges at 0x8b0b0.")
label(0x0008b21c, "startup_mode4_arm_8b21c_packet_state_prefix",
      "Selector-3 post-dispatch prefix: derives the timing delta and prior-response-plus-0x1000 transform, publishes 0x51c940/0x51c942/0x51c948, and enters the 0x6ece0 helper continuation at 0x8b298.")
label(0x0008b298, "startup_mode4_arm_8b298_float_selection",
      "Selector-3 helper selection: calls 0x6ece0 with 0x51c950/0x51c954, selects a nonpositive result or 30.0f, adds 2.5f when 0x5770f0 is zero, and continues at 0x8b30c.")
label(0x0008b30c, "startup_mode4_arm_8b30c_scale_state",
      "Selector-3 scale/state block: bounds the computed scale against 0x51c948, chooses positive versus nonpositive packet arithmetic, publishes 0x51c94c/0x51c948, and reconverges at 0x8b3f4.")
label(0x0008b3f4, "startup_mode4_arm_8b3f4_packet_state",
      "Selector-3 packet/state builder: emits command 29/30 from 0x51c940 low16 and 0x51c948, publishes response-relative rolling values and 0x51c94c, then enters the command-10 boundary at 0x8b4e8.")
label(0x0008b554, "startup_mode4_arm_8b554_response_tail",
      "Selector-3 response tail: completes command 31, emits a final command 10 with the first response and computed word, stores 0x51c940/0x51c944, and routes zero record +0x30 to 0x8aecc or nonzero to 0x8b604.")
label(0x0008b604, "startup_mode4_arm_8b604_force_state",
      "Selector-3 success epilogue: writes 1 to 0x51c9b4 and returns at 0x8b610.")
label(0x0008b620, "startup_mode4_arm_8b620_dispatch_gate",
      "Post-selector dispatch gate: compares 0x51c984 against 61 and 0x77, publishes g14/1/2 to 0x51c99c, and continues at 0x8b678 before timing/state updates.")
label(0x0008b678, "startup_mode4_arm_8b678_state_packet_bridge",
      "Shared state/packet bridge: reconciles 0x51d5e0/0x51d5e4 with 0x51c9b8, advances the retry counter below 26, emits command 10 from record deltas, publishes 0x51c940, and returns through selector-specific branches.")
label(0x0008b754, "startup_mode4_arm_8b754_packet_state_prefix",
      "Selector-0 packet/state prefix: adds 0x1000 to the command-10 response, emits command 29/30 with 0x42200000, publishes 0x51c940/0x51c948/0x51c950/0x51c954, and continues at 0x8b7e0.")
label(0x0008b7e0, "startup_mode4_arm_8b7e0_float_selection",
      "Selector-0 setup/helper selection: subtracts 3 from the masked operand, takes the low path at 0x8b830 when ordered-below 1, otherwise calls 0x6ece0, selects a nonpositive result or 30.0f, applies the timing-zero 2.5f adjustment, and continues at 0x8b85c.")
label(0x0008b85c, "startup_mode4_arm_8b85c_response_tail",
      "Selector-0 response tail: derives two command-10 packet words from record/state deltas, emits both packets, stores their responses at 0x51c940/0x51c944, clears 0x51c94c, and routes record +0x30 zero/nonzero to 0x8bfac or 0x8bd60.")
label(0x0008b944, "startup_mode4_arm_8b944_packet_prefix",
      "Selector-1 packet prefix: adds 0x1000 to the prior command-10 response, emits command 29/30 with 0x42200000, prepares the +0x5000 masked follow-up word, and continues at 0x8b9e4.")
label(0x0008baf0, "startup_mode4_arm_8baf0_float_selection",
      "Selector-1 helper selection: subtracts 3 from 0x5770f0, takes the unsigned-below-1 path at 0x8bb34, otherwise calls 0x6ece0, selects a nonpositive result or 30.0f, applies the timing-zero 2.5f adjustment, and continues at 0x8bb60.")
label(0x0008bb60, "startup_mode4_arm_8bb60_packet_state_tail",
      "Selector-1 packet/state tail: derives record-delta fixed-point inputs, emits a command-31 prefix and two command-10 packets, publishes rolling/shared state and responses, and routes record +0x30 zero/nonzero to 0x8bd60 or 0x8bfac.")
label(0x0008bd60, "startup_mode4_arm_8bd60_force_state",
      "Selector-1 success epilogue: writes g14 to 0x51c9b4 and returns at 0x8bd70.")
label(0x0008bd74, "startup_mode4_arm_8bd74_packet_state_prefix",
      "Selector-2 packet/state prefix: adds 0x5000 to the prior command-10 response, emits command 29/30 with 0x42200000, publishes 0x51c940/0x51c948 and response-relative state, and continues at 0x8be00.")
label(0x0008bfac, "startup_mode4_arm_8bfac_force_state",
      "Selector-1 success epilogue: forces 0x51c9b4 to 1 and returns at 0x8bfc0.")
label(0x0008bfd0, "startup_mode4_common_dispatch_8bfd0",
      "Shared post-epilogue dispatch: conditionally promotes 0x51c9a0, rewrites 0x51c99c from scan state, increments 0x51c9a8 below 9, emits command 10 from record deltas, and continues at 0x8c0c8.")
label(0x0008c0c8, "startup_mode4_common_dispatch_8c0c8_selector_routes",
      "Selector routing bridge: honors the prior equal gate to 0x8c2cc, then routes selector 0 to 0x8c0e0, selector 2 to 0x8c660, and selector 1/default to 0x8c760.")
label(0x0008c0e0, "startup_mode4_arm_8c0e0_packet_state_prefix",
      "Selector-0 packet/state prefix: subtracts 0x6000 from the command-10 response, emits command 29/30 with 0x42200000, publishes 0x51c940/0x51c948 and response-relative state, and continues at 0x8c16c.")
label(0x0008c16c, "startup_mode4_arm_8c16c_response_tail",
      "Selector-0 response tail: applies the helper/timing selection, emits two command-10 packets, publishes 0x51c940/0x51c944/0x51c94c, and routes record +0x30 zero/nonzero to 0x8c904 or 0x8c8f4.")
label(0x0008c2cc, "startup_mode4_arm_8c2cc_packet_state_prefix",
      "Selector-1 packet/state prefix: subtracts 0x6000 from the command-10 response, emits command 29/30 with 0x42200000, publishes 0x51c940/0x51c948 and response-relative state, and continues at 0x8c358.")
label(0x0008c358, "startup_mode4_arm_8c358_float_selection",
      "Selector-1 helper selection: subtracts 3 from timing, takes the ordered-below-1 path at 0x8c3a4, otherwise calls 0x6ece0, selects a nonpositive result or 30.0f, applies the timing-zero 2.5f adjustment, and continues at 0x8c3d0.")
label(0x0008c3d0, "startup_mode4_arm_8c3d0_scale_state",
      "Selector-1 scale/state checkpoint: derives the scale from 0x51c984, publishes 0x51c94c, selects the <=120 short path, updates rolling 0x51c958/0x51c95c/0x51c960, clamps negative 0x51c95c to 10.0f, and continues at 0x8c510.")
label(0x0008c510, "startup_mode4_arm_8c510_packet_state_tail",
      "Selector-1 command/response tail: clamps negative 0x51c95c to 10.0f, emits command 31 and two command-10 packets from shared state, publishes 0x51c940/0x51c944, promotes selector 2 on a zero 0x1d0 marker, and routes record +0x30 to 0x8c904 or 0x8c90c.")
label(0x0008c660, "startup_mode4_arm_8c660_packet_state_tail",
      "Selector-2 command/response tail: emits command 31 and two command-10 packets from shared rolling state, publishes 0x51c940/0x51c944, and routes record +0x30 zero/nonzero to 0x8c8f4 or 0x8c904.")
label(0x0008c760, "startup_mode4_arm_8c760_packet_state_prefix",
      "Selector-3 packet/state prefix: derives record +0x184, adds 0x6000, emits command 29/30 with 0x42a00000, publishes 0x51c940/0x51c948 and response-relative state, and continues at 0x8c7f0.")
label(0x0008c7f0, "startup_mode4_arm_8c7f0_float_selection",
      "Selector-3 helper selection: subtracts 3 from timing, calls 0x6ece0 unless the signed-below-1 gate takes the zero path, selects helper/nonpositive or 30.0f, applies two 2.5f additions when timing is zero, and continues at 0x8c840.")
label(0x0008c840, "startup_mode4_arm_8c840_scale_packet_tail",
      "Selector-3 scale/packet tail: applies the remaining float adjustments, emits command 10 with 0x51c948 and the computed payload, publishes 0x51c94c/0x51c944, routes record +0x30 to 0x8c8f4/0x8c904, and snapshots shared state at 0x51c964-0x51c978.")
label(0x0008b0b0, "startup_mode4_arm_8b0b0_packet_state",
      "Selector-2 packet/state sequence: emits command 29/30, derives the command-10 and command-31 payloads from response-relative fields, publishes 0x51c950/0x51c954 and rolling state, and continues at 0x8b1a4.")
label(0x0008b1a4, "startup_mode4_arm_8b1a4_response_tail",
      "Selector-2 response tail: commits 0x51c950/0x51c954 and 0x51c940, emits the final command-10 response at 0x51c944, and branches on record +0x30 to 0x8aecc or 0x8b604.")
label(0x0008aecc, "startup_mode4_arm_8aecc_force_state",
      "Selector-1 success epilogue: writes g14 to 0x51c9b4 and returns at 0x8aed4.")
label(0x00089814, "startup_mode4_arm_89814_state_packet_sequence",
      "Selector-5 arm: derives deltas from prior 0x51c958/0x51c960 state, emits command 10 and command 31, emits a second command 10 with 0x51c948 and the computed word, republishes 0x51c940/0x51c944/0x51c94c/0x51c950/0x51c954, and continues at 0x89930.")
label(0x000878a0, "startup_mode4_arm_20_mode5_common_continuation",
      "Publishes mode 5 and flag 1 at 0x51c97c/0x51c9a0, stores 0x51c990 >> 8 at 0x51c994, calls 0x888f0, sends 0x5040d0 to 0x88af0, and continues at 0x878f8.")
label(0x000878a4, "startup_mode4_arm_20_mode7_common_continuation",
      "Publishes mode 7 and flag 1 at 0x51c97c/0x51c9a0, stores 0x51c990 >> 8 at 0x51c994, calls 0x888f0, sends 0x5040d0 to 0x88af0, and continues at 0x878f8.")
label(0x00087850, "startup_mode4_arm_20_secondary_mode_setup",
      "Loads 0x51c990, sets buffer 0x503ad0 and flag 1, and enters shared continuation 0x87864 with the mode prepared by the caller.")
label(0x00087844, "startup_mode4_arm_20_secondary_mode11_entry_alt",
      "Sets mode 11 and jumps to shared setup 0x87850.")
label(0x0008784c, "startup_mode4_arm_20_secondary_mode5_entry",
      "Sets mode 5 and jumps to shared setup 0x87850.")
label(0x00087864, "startup_mode4_arm_20_shared_mode_continuation",
      "Publishes the caller-supplied mode and flag 1 at 0x51c97c/0x51c9a0, stores 0x51c990 >> 8 at 0x51c994, calls 0x88a10 with buffer 0x503ad0, and continues at 0x878f8.")
label(0x000878d8, "startup_mode4_arm_20_shared_buffer_continuation",
      "Passes buffer 0x5040d0 to helper 0x88af0 and continues at 0x878f8.")
label(0x000878f8, "startup_mode4_arm_20_shared_upload_state_tail",
      "Publishes mode 1 when either status 0x503b34/0x504134 is below 7, uploads two 0x600-byte indexed blocks from 0x51d5f0/0x5289f0, calls 0x88380, sets marker 0x503a60, keeps timing+1 at or below 0x77 and otherwise substitutes the seed in 0x51d5e4, seeds six workspace cells with g14, increments 0x503a00, and returns at 0x87a00.")
label(0x00087928, "startup_mode4_arm_20_indexed_uploads")
label(0x00087980, "startup_mode4_arm_20_seed_and_timing_publication")
label(0x000872d0, "startup_mode4_arm_20_response_handler_4f",
      "Sets r5=4, loads 0x51c98c, sets r4=1, passes 0x5040d0, stores 4/1 at 0x51c97c/0x51c9a0, stores g4>>8 at 0x51c994, calls 0x88a10, and continues at 0x873cc.")
label(0x00088a10, "startup_mode4_arm_20_indexed_dual_upload_helper_mode_scan",
      "Uploads timing-indexed 0x600-byte paired blocks through 0xf5d40 (positive timing bias 0x78), scans 29 status entries using 0x51c994, and updates 0x51c9a0 or 0x51c998; callers supply mode-specific state before entering this shared helper.")
label(0x000888f0, "startup_mode4_arm_20_indexed_dual_upload_helper",
      "Indexes the timing table from 0x51d5e4 (biasing positive values by 0x78), uploads paired 0x600-byte blocks from 0x51d5f0/0x5289f0 to 0x503ad0/0x5040d0, then scans the 29-entry status table before updating 0x51c9a0 or 0x51c998.")
label(0x00088af0, "startup_mode4_arm_20_indexed_dual_upload_helper_alt",
      "Uploads the current and prior timing-table blocks through 0xf5d40, scans the 29-entry status table using 0x51c994, and updates 0x51c9a0 or 0x51c998.")
label(0x00088380, "startup_mode4_arm_20_fifo_response_builder",
      "Builds the response-10 FIFO packet from 0x503ad8/0x503ae0 and 0x5040d8/0x5040e0, calls 0x2a990, then emits the command-31 follow-up fields.")
label(0x0008c970, "startup_mode4_arm_20_response25_upload_helper",
      "Uploads the current timing-indexed pair, scans 32 status slots, and retries from 0x8c9cc for up to 26 additional passes; each pair uses ((timing >> 2) * 3) << 9 from 0x51d5f0/0x5289f0, timing advances by 4 and wraps by subtracting 0x78 when above 0x78, destinations are 0x503ad0/0x5040d0 with 0x600 bytes, and the scan begins at 0x8ca1c.")
label(0x0008ca1c, "startup_mode4_arm_8ca1c_status_scan",
      "Response-25 status scan: checks 32 entries at 0x20-byte stride, accepts a masked status in (lower, upper] with a zero following byte, stores the matching entry pointer/count at 0x51c998/0x51c994, or stores zero at 0x51c9a0 on exhaustion, then returns to 0x8ca80.")
label(0x0008ca80, "startup_mode4_arm_20_response_helper_gate",
      "Derives gate 0x51c99c as (0x51c984 > 0x77), returns immediately for gate zero, and enters the packet path at 0x8ccfc for gate one; dispatch-table callers at 0x88760/0x88770 supply buffers 0x5040d0/0x503ad0.")
label(0x0008cac8, "startup_mode4_arm_20_response_helper_packet_prefix_a",
      "Emits the shared response packet prefix: command 10 with endpoint deltas, then command 29 and command 30 using (FIFO response + 0x3000) & 0xffff and constant 0x42200000 before continuing at 0x8cb00.")
label(0x0008ccfc, "startup_mode4_arm_20_response_helper_packet_prefix_b",
      "Repeats the response packet prefix of 0x8cac8—command 10 endpoint deltas followed by command 29/30 lane packets—and continues at 0x8cd30 for the alternate gate arm.")
label(0x0008cb00, "startup_mode4_arm_8cb00_response_state_bridge",
      "Response-helper state bridge: consumes the command-29 FIFO response, emits command 29/30 with the masked +0x3000 lane and 0x42200000, publishes 0x51c940/0x51c948/0x51c950/0x51c954, selects helper/nonpositive or 30.0f, and continues at 0x8cc0c.")
label(0x0008cc0c, "startup_mode4_arm_8cc0c_command10_tail",
      "Selector-0 command-10 tail: derives explicit response-relative payload words, emits two command-10 packets, publishes 0x51c940/0x51c944/0x51c94c, and routes the record-30 completion to 0x8ccf0 or 0x8d094.")
label(0x0008cd30, "startup_mode4_arm_8cd30_response_state_bridge",
      "Response-helper gate-1 state bridge: consumes the command-29 FIFO response, emits command 29/30 with the masked +0x3000 lane and 0x42200000, publishes 0x51c940/0x51c948/0x51c950/0x51c954, selects helper/nonpositive or 30.0f, and continues at 0x8ce14.")
label(0x0008ce14, "startup_mode4_arm_8ce14_packet_state_tail",
      "Gate-1 packet/state tail: emits command 31, command 29/30, and two command-10 packets from explicit arithmetic words, publishes 0x51c940/0x51c944/0x51c948/0x51c958/0x51c960/0x51c94c/0x51c95c, and enters the 0x8d090 completion gate.")
label(0x0008d090, "startup_mode4_arm_20_response_helper_completion_gate",
      "Tests the record word at offset 0x30: zero publishes 1 to 0x51c9b4 and returns at 0x8d0a0; nonzero leaves the completion value clear and loops back to 0x8ccf0.")
label(0x0008d0a4, "startup_mode4_arm_8d0a4_retry_bridge",
      "Completion retry bridge: branches unconditionally back to the response-helper retry entry at 0x8ccf0 before the callback trampoline cluster at 0x8d0b0.")
label(0x0008d0b0, "startup_mode4_arm_20_callback_state_store",
      "Stores the incoming g0 value at 0x51c9d0, clears the callback register, and indirect-branches through the callback with local return stub 0x8d0cc.")
label(0x0008d0d0, "startup_mode4_arm_20_callback_state_query",
      "Indirect-calls through a callback after returning g0=1 only when 0x51d5e0 equals 1, otherwise g0=0; local return stub is 0x8d0fc.")
label(0x0008d100, "startup_mode4_arm_20_callback_state_initialize",
      "Publishes timing/state initialization 0x51d5e0=2, 0x503a04=1, and 0x51c9c0=1 before indirect-branching through the callback with local return stub 0x8d134.")
label(0x0008d140, "startup_mode4_arm_20_callback_latch_query",
      "Indirect-calls through a callback after returning g0=1 only when 0x51c9c0 equals 1, otherwise g0=0; local return stub is 0x8d16c.")
label(0x0008d170, "startup_mode4_arm_20_first_call_asset_table_initializer",
      "On the first-call path from 0x87f80, uploads 30 paired 0x600-byte timing blocks, two fixed 0x580-byte tables, then 90 indexed 0x400-byte asset pairs; initializes 90 rows of 0x5618f0/0x561e90 at 12-byte strides with 0xffff at offsets +4/+8.")
label(0x0008d2a0, "scheduler_response_selector_8d2a0",
      "Computes (0x51c9b0 % 120) >> 2 with a maximum of 29; response 10 returns result 10 at 0x8d3ec, while other responses continue through normalization at 0x8d2d0. The result feeds caller arithmetic at 0x849dc.")
label(0x0008d2d0, "scheduler_response_search_8d2d0",
      "Normalizes the non-special response by subtracting 0x25, advances the modulo-120-derived row before probing up to 30 cyclic rows, scans 32 status entries at 0x20-byte stride per row, accepts masked status values > (lower+31) and <= (upper+31) only when the following byte is zero, returns 30-attempt on the first match, and returns -1 after exhaustion; low normalized values branch separately to 0x8d390, which starts on the unadvanced row.")
label(0x0008d390, "scheduler_response_low_search_8d390",
      "For low normalized responses, selects the caller-supplied upper-byte column at high_byte<<5, probes 30 table rows in reverse cyclic order from the modulo-120-derived index, returns the probe count at the first zero byte, and returns -1 after exhaustion.")
label(0x0008730c, "startup_mode4_arm_20_response_handler_7f",
      "Compares fp0 against extended-real pair r4=0/r5=0x40590000, branching less-than to 0x878e8 or otherwise to 0x87394.")
label(0x00087328, "startup_mode4_arm_20_response_handler_85",
      "Compares fp0 against extended-real pair r4=0/r5=0x40590000, branching less-than to 0x878e8 or otherwise to 0x87394.")
label(0x00087344, "startup_mode4_arm_20_response_handler_8b",
      "Sets mode 10, loads 0x51c98c, sets flag 1 with buffer 0x5040d0, and enters shared continuation 0x87864.")
label(0x00087360, "startup_mode4_arm_20_response_handler_9d",
      "Sets mode 4, loads 0x51c98c, sets flag 1 with buffer 0x5040d0, and enters shared continuation 0x87864.")
label(0x0008737c, "startup_mode4_arm_20_response_handler_a9",
      "Compares fp0 against extended-real pair r4=0/r5=0x40590000, branching less-than to 0x878e8 or otherwise to 0x87394.")
label(0x00019c30, "startup_mode4_phase_table_arm_8_prefix",
      "Initializes the slot-8 status/profile path: marks 0x503ab0 with 0xff, clears 0x503a60, calls setup 2 and optional 0xc8fa0, maps phase flag 0/1/other to 100/105/110, publishes status through 0x2250 with 0xf423f sentinel handling, and uses the 99x remainder arithmetic before entering the ready/hardware continuation at 0x19d20.")
label(0x00019c50, "startup_mode4_arm_8_phase_code")
label(0x00019c9c, "startup_mode4_arm_8_status_threshold")
label(0x00019ccc, "startup_mode4_arm_8_ready_split")
label(0x000ce670, "startup_mode4_phase_table_arm_3",
      "Initializes the indexed startup workspace: resets 0x577590, calls 0x29c08/0x1ccf8(0x7cc1), advances phase, copies 21 words from 0xc9220 into a 0x154-byte record at 0x51c5b0, seeds workspace fields, and runs setup/probe calls before returning at 0xce8ec.")
label(0x000ce680, "startup_mode4_arm_3_phase_setup")
label(0x000ce6dc, "startup_mode4_arm_3_record_template_copy")
label(0x000ce754, "startup_mode4_arm_3_workspace_seed")
label(0x000ce8cc, "startup_mode4_arm_3_workspace_finalize")
label(0x000ce8f0, "startup_mode4_phase_table_arm_4",
      "Consumes the indexed workspace record: normalizes countdown 0x51c858, runs 0xcd5b0/0xcd4f0/0xce100, conditionally initializes nine 0x54-byte entries from 0x51bb30, links record fields, increments the selected record count, and returns at 0xceab4.")
label(0x000ce900, "startup_mode4_arm_4_countdown_gate")
label(0x000ce964, "startup_mode4_arm_4_record_status_gate")
label(0x000ce998, "startup_mode4_arm_4_entry_initialization")
label(0x000ce9e4, "startup_mode4_arm_4_record_link")
label(0x00018650, "startup_mode_handler_2",
      "Invokes helper 0x1ccf8, clears phase 0x503a00, increments startup mode 0x5039f4, and returns at 0x18678.")
label(0x00018658, "startup_mode2_phase_clear")
label(0x00018668, "startup_mode2_mode_increment")
label(0x000190d0, "startup_mode_handler_3",
      "Runs setup 0x2a4e0 with 0x1111, clears phase state through 0x1c618/0x1bda0, seeds 0x504b96 and video/upload bases, clears seven phase fields, increments 0x5039f4, and returns at 0x19170.")
label(0x000190e8, "startup_mode3_seed_phase_state")
label(0x00019114, "startup_mode3_clear_phase_fields")
label(0x00019164, "startup_mode3_mode_increment")
label(0x00019180, "startup_mode_handler_4",
      "Writes device words 8/16 to 0x884000, gates on 0x503a7c/0x5024f4 and phase window 8..12 or special phase 27, masks 0x10000000 with 0xfffe, performs setup 0x2a870/0x2a4e0, publishes marker 32, and enters the shared tail at 0x1922c.")
label(0x00019180, "startup_mode4_device_setup_prefix")
label(0x000191a8, "startup_mode4_ready_and_phase_gate")
label(0x000191d0, "startup_mode4_hardware_mask_and_setup")
label(0x0001922c, "startup_mode4_status_tail")
label(0x0001922c, "startup_mode4_status_maintenance_gate")
label(0x00019254, "startup_mode4_fixed_copy")
label(0x00019274, "startup_mode4_configuration_bank_gate")
label(0x0001930c, "startup_mode4_handler_table_dispatch")
label(0x000f3f00, "startup_mode_handler_5",
      "Masks 0x10000000 with 0xfffe, seeds 0x5039f0/0x5039f4, resets diagnostic state 0x5784f8/04/00/08/0c/10/14/b4/b8, builds the geometry table through 0xec820, and writes startup marker 0x50 before returning at 0xf3fb8.")
label(0x000f3fe0, "startup_mode_handler_6",
      "Writes marker 0x50, advances 0x5784fc modulo 11 after a successful 0xeada8 probe in mode zero, selects from 0xf3ec0 with mask 0xf, dispatches 0xeb060 or the selected service, copies 0x5024e8 for 0x1a7 bytes, and applies mode-2 checks at 0x502482/0x5024ac before returning at 0xf4138.")
label(0x000f3d30, "startup_mode_handler_7",
      "Runs the phase-0 timing/text setup, the gated phase-1 advance, and the later device/status transition; clears 0x5024c4/0x5024c6/0x5024c8 and returns before the 0xf3ec0 table.")
label(0x000f3d3c, "startup_mode7_phase0_reset_and_timing")
label(0x000f3d70, "startup_mode7_timing_limit_check")
label(0x000f3d9c, "startup_mode7_message_sequence")
label(0x000f3e10, "startup_mode7_phase1_gate")
label(0x000f3e3c, "startup_mode7_device_status_transition")
label(0x000f3ec0, "diagnostic_service_handler_table",
      "Eleven-entry diagnostic service dispatch table: 0xed220, 0xed320, 0xed5c0, 0xeda30, 0xf04d0, 0xf0980, 0xf1c90, 0xf2e20, 0xf33a0, 0xf3ab0, and 0xf3c50.")
label(0x00018620, "startup_mode_handler_8_and_15",
      "Clears startup mode 0x5039f4 and phase 0x503a00, then branches through the local return thunk at 0x18644; shared by table slots 8 and 15.")
label(0x00018644, "startup_mode_handler_8_return_thunk")
ensure_function(0x00003c40, "startup_mode_handler_0", 0x00003d64)
ensure_function(0x0002b9e0, "startup_mode_handler_1_status_dispatch", 0x0002bb5c)
ensure_function(0x00018c00, "startup_mode4_phase_table_arm_0", 0x00018da0)
ensure_function(0x00018da0, "startup_mode4_phase_table_arm_1", 0x00019030)
ensure_function(0x00019030, "startup_mode4_phase_table_arm_2", 0x000190d0)
ensure_function(0x00019660, "startup_mode4_phase_table_arm_5", 0x000196c0)
ensure_function(0x000196c0, "startup_mode4_phase_table_arm_6", 0x00019830)
ensure_function(0x00019830, "startup_mode4_phase_table_arm_7", 0x00019b50)
ensure_function(0x0001a280, "startup_mode4_phase_table_arm_9_prefix", 0x0001a3fc)
ensure_function(0x0001a4a0, "startup_mode4_phase_table_arm_10", 0x0001afe0)
ensure_function(0x00019c30, "startup_mode4_phase_table_arm_8_prefix", 0x00019d20)
ensure_function(0x000ce670, "startup_mode4_phase_table_arm_3", 0x000ce8f0)
ensure_function(0x000ce8f0, "startup_mode4_phase_table_arm_4", 0x000ceac0)
ensure_function(0x00018620, "startup_mode_handler_8_and_15", 0x00018648)
ensure_function(0x00018650, "startup_mode_handler_2", 0x00018678)
ensure_function(0x000f3f00, "startup_mode_handler_5", 0x000f3fbc)
ensure_function(0x000f3fe0, "startup_mode_handler_6", 0x000f4140)
ensure_function(0x000f3d30, "startup_mode_handler_7", 0x000f3ec0)

# Second-level status/service dispatch table selected by the low five bits of
# 0x503a00 from startup_mode_handler_1_status_dispatch.
label(0x0002b960, "startup_status_dispatch_table",
      "32-entry status/service target table selected by the low five bits of 0x503a00.")
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
label(0x0002b700, "startup_status_arm_post_test_transition",
      "Performs the post-test command/video transition and advances the startup mode.")
label(0x0002b770, "startup_status_arm_subcounter_decrement",
      "Decrements the status subcounter and resets the startup mode when it expires.")
label(0x0002b940, "startup_status_arm_continuation_trampoline",
      "Indirect continuation trampoline used by the status dispatcher tail.")
label(0x0002bdc0, "startup_geometry_status_dispatch_table",
      "Three-entry geometry/status arm table selected by the low two bits of 0x503a00.")
label(0x0002bdd0, "startup_geometry_status_dispatch",
      "Dispatches the selected geometry/status arm and advances the startup counter on fallback.")
label(0x0002bee4, "geometry_frame_service_arm_table",
      "Twelve-entry frame-service target table whose geometry arms share downstream code and returns.")
label(0x0002dc50, "startup_status_arm_geometry_init")
label(0x0002de5c, "startup_status_arm_geometry_transform_call",
      "Calls the shared geometry transform route at 0x2d9a0 after preparing the 0x503ad0/0x5040d0 workspace pair and submitting the preceding geometry records; the continuation clears 0x503a60, 0x503a14, and 0x503a04 before the 0x101b service request.")
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
      "Returns when board byte 0x1d00026 is zero; otherwise routes state 1 to 0xe61c0, state 2 to 0xe6660, and states 0 or >=3 to the common gateway at 0xe5da0.")
label(0x000e5da0, "status_transition_render_gateway",
      "Reduces the caller timer modulo 0x870; remainders through 0x437 return, exactly 0x438 enters the special packet arm, and larger remainders continue at 0xe5de8.")
label(0x000e5dac, "status_transition_render_gateway_window",
      "Applies the literal-first 0x437 lower bound and exact 0x438 special-window comparison before the downstream status packet path.")
label(0x000e5dbc, "status_transition_gateway_special_438",
      "Exact remainder 0x438 arm: calls 0x1c618, stores 0xc000/0x8000 to 0x504d2c/0x504d2e, sets bit 9 at 0x100a000, and joins 0xe60d0.")
label(0x000e5de8, "status_transition_gateway_439_gate",
      "Routes only exact remainder 0x439 into the status-render setup at 0xe5df0; all other general-window remainders continue at 0xe5f48.")
label(0x000e5e40, "status_render_record_sentinel_gate",
      "Tests status record +4 at 0x578410 against 0xffffffff, selecting fallback asset 0xe3b50 through 0xe3a00 or numeric formatter 0xe3a10.")
label(0x000e5e60, "status_render_numeric_values",
      "Computes the three numeric display values record/0xb40, (record/48)%60, and ((record%48)*33)/48 before calling the shared decimal formatter 0xe3a10 with separator assets 0xe3b5a/0xe3b5c.")
label(0x000e5ebc, "status_render_row_advance",
      "Advances the status record pointer by 8 and text column by 3, increments the row counter, loops through row 4 via 0xe5e20, and joins 0xe60d0 after the fifth row.")
label(0x000e5f48, "status_transition_gateway_special_654",
      "Exact remainder 0x654 arm: publishes 0xc000/0x8000 to 0x504d2c/0x504d2e, stores 0x200 to 0x504d24, sets device bit 9, and enters status setup through 0x1cac8.")
label(0x000e61c0, "status_transition_render_variant",
      "State-1 variant reduces the caller timer modulo 0x870; remainders through 0x437 return, exact 0x438 enters the special arm joining 0xe6410, and larger remainders continue at 0xe6208.")
label(0x000e61c8, "status_transition_render_variant_window",
      "Mirrors the 0x437 lower bound and exact 0x438 special-window comparison for the state-1 transition renderer.")
label(0x000e61dc, "status_transition_render_variant_special_438",
      "State-1 exact-0x438 arm: calls 0x1c618, publishes 0xc000/0x8000 at 0x504d2c/0x504d2e, sets device bit 9 at 0x100a000, and joins at 0xe6410.")
label(0x000e6208, "status_transition_render_variant_439_prefix",
      "State-1 remainder-0x439 renderer prefix: emits the fixed setup, scans five 12-byte records from 0x578460, advances text columns by 3 from 19, and joins at 0xe6410; other remainders continue at 0xe62f8.")
label(0x000e62f8, "status_transition_render_variant_654_prefix",
      "State-1 remainder-0x654 renderer prefix: publishes 0xc000/0x8000 and 0x200, sets device bit 9, then scans five 12-byte records from 0x578460+0x3c with index offset 31 before joining at 0xe6410.")
label(0x000e6410, "status_transition_render_variant_common_tail",
      "Shared state-1 transition tail: compares signed remainder windows anchored at 0x438 and 0x654, programs status fields and initializes 0x200 halfwords at 0x577bb0 for accepted windows, otherwise clears transient status fields before returning at 0xe64fc.")
label(0x000e6500, "status_profile_selector_dispatch",
      "Maps a bounded selector through the local table at 0xe651c before the profile renderer loop.")
label(0x000e651c, "status_profile_selector_table",
      "Eight-entry local dispatch table for the status profile renderer; effective profiles are 0,4,3,7,1,2,6,5 and all arms join at 0xe6578.")
label(0x000e6648, "status_blank_dot_strings",
      "Fallback dot strings used by the status profile renderer for empty entries.")
label(0x000e6660, "status_service_state2_prefix",
      "State-2 status service prefix: signed timer modulo 0x870 returns through 0xe6678 through remainder 0x437, exact 0x438 publishes 0xc000/0x200/0x8000 and device bit 9 before 0xe6c50, and larger values continue at 0xe66b4.")
label(0x000e66b4, "status_service_state2_grid_seed",
      "State-2 exact-0x439 grid seed: initializes ten 12-byte frame records at 0x40/0x44 with -1/0, sums ten 16-byte-spaced words from 0x1d0000a4, clamps nonpositive totals to 1, and continues at 0xe6708.")
label(0x000e6708, "status_service_state2_grid_match",
      "State-2 grid matching pass: scans eight rows and eight frame columns, writes matched source values at +0x44, computes +0x48 as source*100/normalized sum, and continues through 0xe6714 to 0xe67f4.")
label(0x000e6818, "status_service_state2_grid_row_render",
      "State-2 row renderer: visits four 12-byte frame rows, alternates formatter/helper pairs (8,13) and (16,21), reads +0x40/+0x48, advances columns 19,22,25,28, and hands off at 0xe6930.")
label(0x000e67f4, "status_service_state2_grid_render_handoff",
      "State-2 grid render handoff: renders four 12-byte frame rows from text column 19 with stride 3 through 0x1d880, then calls 0xe6500 four times at frame offsets 0x40/0x4c/0x58/0x64 with argument pairs (2,13),(31,16),(2,25),(31,28) before 0xe6c50.")
label(0x000e6968, "status_service_state2_second_half",
      "State-2 exact-0x674 second-half path: publishes 0xc000/0x200/0x8000 and device bit 9, renders rows 4..7 from frame offset 0x30, then calls 0xe6500 at offsets 0x70/0x7c/0x88/0x94 before 0xe6c50.")
label(0x000e6c50, "status_service_state2_common_tail",
      "Shared state-2 status tail: uses signed 0x438 and 0x654 windows, programs 0x4000/0x8000 status fields and a 0x200-halfword table at 0x577fb0, clears out-of-window fields, and returns at 0xe6d3c after the exact-0x86f helper gate.")
label(0x000e6d40, "status_record_word_copy_continuation",
      "Copies 0x200 signed halfwords from the source pointer to the destination pointer with 2-byte strides, branches through 0xe6d78, and returns.")
label(0x000e6d80, "geometry_status_emit_variant_a",
      "Clamps phase 0x5783d8 to 0..40, quantizes with shift 10/mask 0xfc00, emits opcodes 29/29/30/18 through 0x884000, and stores phase-1 before returning at 0xe6ee8.")
label(0x000e6ef0, "geometry_status_emit_variant_b",
      "Alternate fixed-point status-to-geometry packet emitter with the same phase source.")
label(0x000e7060, "geometry_status_emit_variant_c",
      "Third fixed-point status-to-geometry packet emitter for the adjacent profile path.")
label(0x000e71d0, "geometry_status_emit_variant_d",
      "Fourth fixed-point status-to-geometry packet emitter used by the status-state dispatcher.")
label(0x000e7340, "geometry_status_emit_dispatch",
      "Selects variant A/B/C/D from mode word 0x5783dc: modes 0 or above 3 default to 0xe6d80, while modes 1,2,3 target 0xe6ef0, 0xe7060, and 0xe71d0.")
label(0x000e7390, "geometry_object_packet_dispatch",
      "Compares object byte -3 with the caller tag byte; mismatches route to 0xe7560, matching queue flag 0 routes through emitter dispatcher 0xe7340, and other matches use direct packet path 0xe7420.")
label(0x000e7420, "geometry_object_direct_packet_prefix",
      "Direct object packet prefix: writes opcode 18, saved base plus computed offset, and the two preserved coordinate words to 0x884000 before joining at 0xe7454.")
label(0x000e7454, "geometry_object_packet_common_tail_prefix",
      "Object packet common tail: the saved incoming control flag at fp+0xc0 selects whether suffix 19/1.0/1.0/10.0/computed-offset+27 is emitted through 0x884000; the same flag is consumed by the response split at 0xe7490.")
label(0x000e7490, "geometry_object_packet_response_split",
      "Object packet response split: emits computed-offset+27 and the 0x802008 control word, writes control+0x34 to 0x801008, then uses the saved incoming control flag (fp+0xc0) for the fallback/queued split; the later 0x884000 readback is transport data, not the selector.")
label(0x000e7560, "geometry_object_alternate_admission",
      "Alternate object admission: after helper 0xf50c8, accepts object byte -2 when it matches the caller tag or when the caller tag is literal 60, targeting 0xe758c; other values route to 0xe76d0.")
label(0x000e758c, "geometry_object_alternate_packet",
      "Alternate accepted packet path: emits opcode 18 and the same optional 19/1.0/1.0/10.0 suffix, then uses the saved incoming control flag (fp+0xc0) for fallback assets 0x4934b0/0x493534/0x900905 or queued descriptor 0x8fe625; the 0x884000 readback is separate transport data.")
label(0x000e76d0, "geometry_object_fallback_admission",
      "Fallback object admission: after helper 0xf50c8, accepts object byte -1 when it matches the caller tag or when the caller tag is literal 62, then splits at 0xe7850 to emitter dispatch 0xe7340 or direct packet 0xe7874.")
label(0x000e7874, "geometry_object_fallback_packet",
      "Fallback direct packet path: emits opcode 18 and the optional 19/1.0/1.0/10.0 suffix, then uses the saved incoming control flag (fp+0xc0) for fallback assets 0x49353c/0x493744/0x9009b6 or queued descriptor 0x8fe654; the 0x884000 readback is separate transport data.")
label(0x000e79f0, "geometry_status_scene_dispatch",
      "Initializes scene registers 0x800070/0x800030/0x800090/0x8000a0/0x800160, emits the fixed 8/16/18 geometry prefix, loops object records through 0xe7390 starting at index -5, and dispatches the final mode through the arm table.")
label(0x000e8920, "geometry_status_scene_arm_table",
      "Six-entry local dispatch table for the status scene's final geometry arms: 0xe8938, 0xe89d4, 0xe8ae0, 0xe8c5c, 0xe8e44, and 0xe8fe4; unsigned modes above 5 return at 0xe9138.")
label(0x000e8938, "geometry_status_scene_arm0",
      "If bit 3 of 0x5024e8 is set, emits 5/19/0x41400000/0x41400000/1.0, loads the scene-count-indexed object byte, calls 0xe7390 with fixed transform words 0x49c980/0xc0c00000/0xc0900000, and completes with opcode 6; a clear bit returns at 0xe89d0.")
label(0x000e89d4, "geometry_status_scene_arm1",
      "Always emits the 5/19/0x41400000/0x41400000/1.0 packet for the byte at 0x5784e8, then if bit 3 of 0x5024e8 is set emits the same packet for the scene-count-indexed byte at 0x5784e4, using 0x49c980/0/c0900000 for the second call; completes with 6 and returns at 0xe8adc.")
label(0x000e8ae0, "geometry_status_scene_arm2",
      "Emits the fixed packet for bytes at 0x5784e8 and 0x5784e9, then gates a third scene-count-indexed packet on bit 3 of 0x5024e8; the third call uses 0x49c980/0x40c00000/0xc0900000 and returns at 0xe8c58 after completion 6.")
label(0x000e8c5c, "geometry_status_scene_arm3",
      "Emits packets for bytes 0x5784e8/0x5784e9/0x5784ea, gates a fourth scene-count-indexed packet on bit 3 of 0x5024e8, then decrements 0x503a04 and on zero calls 0xe54a0/0xe37b0 and increments 0x503a00; returns at 0xe8e40.")
label(0x000e8e44, "geometry_status_scene_arm4",
      "Gates three fixed-object packets (bytes 0x5784e8/0x5784e9/0x5784ea) on bit 3 of 0x5024e8, then converges at shared cleanup 0xe8fac; transform middle words are 0xc0c00000/0/0x40c00000 and the final return is 0xe8fe0.")
label(0x000e8fe4, "geometry_status_scene_arm5",
      "Emits three unconditional fixed-object packets for bytes 0x5784e8/0x5784e9/0x5784ea with middle transforms 0xc0c00000/0/0x40c00000, then branches to shared completion 0xe8e34 and returns at 0xe9138.")
label(0x000e9140, "geometry_runtime_event_dispatch",
      "Updates the rolling geometry-event fields, computes pair deltas, and dispatches the next event arm.")
label(0x000e91f0, "geometry_runtime_event_arm_table",
      "Twelve-entry event-arm table selected from 0x5783fc modulo 12: 0xe9470, 0xe95a4, 0xe9da8, 0xea1a0, 0xe9da8, 0xea1a0, 0xea598, 0xea610, 0xe96b8, 0xe99fc, 0xe9bcc, and 0xe9220; the out-of-range guard targets 0xea744.")
label(0x000e9470, "geometry_runtime_event_arm0",
      "Builds the arm-0 fixed-point word from prior phase 0x5783e6 plus record word 0x184 and 0x3000, emits 29/30 with 0x43020000 through the geometry FIFO, updates 0x5783e4/0x5783e6/0x5783ec/0x5783f4/0x5783f8/0x5783e8, and continues at 0xea720.")
label(0x000e95a4, "geometry_runtime_event_arm1",
      "Builds the mirrored arm-1 fixed-point word from record word 0x184 minus 0x3000 and prior phase 0x5783e6 minus 0x100, emits 29/30 with 0x43020000, publishes 0x41c80000 at 0x5783f0, updates shared event fields, and continues at 0xea6fc.")
label(0x000e96b8, "geometry_runtime_event_arm2_prefix",
      "Loads paired word-8/word-10 values from record bases 0x5040d0 and 0x503ad0, emits opcode 10 with their deltas and opcode 31 with the paired word-8 values, increments phase 0x5783e6, and continues at 0xe974c.")
label(0x000e9da8, "geometry_runtime_event_arm3_prefix",
      "Computes paired word-10/word-8 deltas, emits opcode 10, stores the FIFO response to 0x5783e4, then compares event count 0x578400 against threshold 44 to choose 0xe9e00 or 0xe9ec0.")
label(0x000e9e00, "geometry_runtime_event_arm3_short_path",
      "Scales event count by 2^14/45, uses the FIFO response as a lookup base, masks the looked-up word to 16 bits, emits 29/30 with 0x43020000, reads a second FIFO response, and continues at 0xe9e50.")
label(0x000ea0b0, "geometry_runtime_event_common_finalize",
      "Shared finalizer: emits opcode 10 with record-word deltas, then opcode 31 with state 0x5783f4 and record word-8/word-10 values, publishes the first FIFO response to 0x5783e4, and continues at 0xea6fc.")
label(0x000ea6fc, "geometry_runtime_event_prepare",
      "Stores the derived value at 0x5783e8, emits setup words 20/0x5783e8/21/-0x5783e4 through the FIFO, and branches to shared event finalizer 0xea9a0; arm 0 reaches the equivalent sequence at 0xea720.")
label(0x000ea9a0, "geometry_runtime_event_finalize",
      "Snapshots state 0x5783f4/0x5783f0/0x5783f8/0x5783e8/0x5783e4 to 0x504b98/0x504b9c/0x504ba0/0x504ba8/0x504baa, emits 18 plus bit-31-toggled state words, derives 0x504d28 and 0x5770f4, and returns at 0xeaa50.")
label(0x000eaa60, "geometry_event_setup_prefix",
      "Calls 0x295d0, emits setup words 8/16, calls 0x2a990 with 0xd000, then emits opcode 10 with deltas from 0x503ad8/0x5040d8 and continues at 0xeaaf0.")
label(0x000eaaf0, "geometry_event_setup_packet",
      "Reads the setup FIFO response, emits opcode 31 with workspace addresses 0x503ad8/0x5040d8/0/0/0x503ae0/0x5040e0, and continues at 0xeab48.")
label(0x000ea598, "geometry_runtime_event_arms6_7_prefix",
      "Arms 6 and 7 load record word 0x184, add 0x6000 or 0xffffa000 respectively, mask to 16 bits, emit opcode 29 and opcode 30 with constant 0x430c0000, consume both FIFO responses, load words 8/0x10/0xc, and share continuation 0xea684.")
label(0x000eab48, "geometry_event_setup_state_prefix",
      "Builds the setup-helper phase word by adding 0x4000, masks it for the opcode-29/30 packets, publishes the visible 0x5783e4/0x5783e6/0x5783e8/0x5783ec/0x5783f0/0x5783f4 state fields, carries preserved g14 into 0x5783e6/0x5783e8, and continues at 0xeac1c; extended-real results remain explicit inputs until their semantics are proven.")
label(0x000eac1c, "geometry_event_setup_handoff",
      "Replays opcode 30 with the masked phase and extended-real word, publishes preserved g14 to 0x578400 and 0x5783fc, reads the FIFO response, emits opcode 10 with the extended-real word and 0x430c0000, and continues at 0xeac84.")
label(0x000eac84, "geometry_event_setup_finalize",
      "Emits opcode 20 with the low halfword of the opcode-10 FIFO response, opcode 21 with -0x5783e4, then opcode 18 with bit-31-toggled state words; publishes the computed division result g6 at 0x5783f8 and reuses it for the final toggled word before returning at 0xead1c.")
label(0x000ea1a0, "geometry_runtime_event_arm4_prefix",
      "Computes paired word-10 and reversed word-8 deltas, emits opcode 10, stores the FIFO response to 0x5783e4, then compares event count 0x578400 against threshold 44 to choose 0xea1f8 or 0xea2b8.")
label(0x000eaa60, "geometry_event_setup_helper",
      "Emits the event setup packet, derives shared geometry fields, and updates the event workspace.")
label(0x000ead20, "geometry_event_lookup_data",
      "Literal geometry-event lookup records following the setup helper.")
label(0x000eada0, "runtime_flag_gate_a",
      "Tests bit 3 of byte 0x5023f0, otherwise bit 1 of 0x5024b4, and returns boolean 1/0 through the supplied continuation.")
label(0x000eade0, "runtime_flag_gate_b",
      "Tests bit 2 of byte 0x5023f0, otherwise bit 0 of 0x5024b4, and returns boolean 1/0 through the supplied continuation.")
label(0x000eae20, "runtime_flag_gate_c",
      "Tests bit 2 of byte 0x502480, otherwise bit 0 of 0x5024b8, and returns boolean 1/0 through the supplied continuation.")
label(0x000eae60, "runtime_byte_copy_continuation",
      "Copies g2 >> 1 source bytes from g1 to g0, writes a zero byte after each copied byte, and returns through the caller-supplied continuation.")
label(0x000eaeb0, "runtime_format_value",
      "Moves g2 to r4, calls numeric helper 0x1cac8, moves its result to g0, calls renderer 0xf5100, and returns at 0xeaec0.")
label(0x000eaed0, "runtime_format_value_adjusted",
      "Moves g2 to r4, decrements g0, selects 32 or 42 for helper 0x1cc40 from byte 0x1d00028 (values 1/2 versus other), then calls renderer 0xf5100 and returns at 0xeaf1c.")
label(0x000eaf20, "runtime_render_value_string",
      "Moves g2 to r4, calls numeric helper 0x1cac8, moves its result to g0, calls alternate renderer 0x1da90, and returns at 0xeaf30.")
label(0x000eaf40, "diagnostic_menu_strings",
      "Literal diagnostic-menu strings used by the runtime test/status screen.")
label(0x000eb060, "diagnostic_menu_render",
      "Renders fourteen diagnostic menu strings at fixed tile coordinates from 0xeaf40-0xeb040, then updates the selected test-menu marker from 0x5784fc and returns at 0xeb19c or 0xeb1b4.")
label(0x000eb1c0, "runtime_packed_record_scan",
      "Fills g0 >> 1 halfwords at 0x5785a4 with the target, scans g0 >> 2 two-halfword records after that region, and stores low/high-byte match pointers at 0x578548, 0x57854c, and 0x578550.")
label(0x000eb2c0, "runtime_record_table_init",
      "Sets the packed workspace base to 0x200000 and byte count to 0x220000, scans 0xffff followed by all 16 powers of two 1..0x8000 and the caller target through 0xeb1c0, normalizes zero match slots to 1, and advances the status counter.")
label(0x000eb3b0, "runtime_record_base_select",
      "Selects 0x200000 when primary markers 0x578548/0x57854c/0x578550/0x578554 are all 1, else 0x1080000 when alternate markers 0x578578/0x57857c/0x578580/0x578584 are all 1, else 0x5e0000, publishes at 0x501cc4, and returns through the supplied continuation.")
label(0x000eb450, "runtime_record_match_scan_alt",
      "Fills g0 >> 1 halfwords at 0x501cc0 with the target, scans g0 >> 2 two-halfword records after that region, and records post-increment pointers for full-word mismatches at 0x578558 and 0x57855c.")
label(0x000eb510, "runtime_record_table_reset_copy",
      "Sets packed byte count 0x20000 and target 0xffff, reruns the alternate scanner at 0xeb458 for 0xffff, all 16 powers of two 1..0x8000, and the caller target, then copies 0x10000 halfwords from 0x501cc4 into 0x501cc0 before returning at 0xeb5a8.")
label(0x000eb5b0, "runtime_rom_bank_loader_5e",
      "Copies 0x10000 halfwords from ROM bank 0x5e0000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb600, "runtime_rom_bank_loader_5c",
      "Copies 0x10000 halfwords from ROM bank 0x5c0000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb650, "runtime_rom_bank_loader_5a",
      "Copies 0x10000 halfwords from ROM bank 0x5a0000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb6a0, "runtime_rom_bank_loader_58",
      "Copies 0x10000 halfwords from ROM bank 0x580000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb6f0, "runtime_rom_bank_loader_56",
      "Copies 0x10000 halfwords from ROM bank 0x560000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb740, "runtime_rom_bank_loader_54",
      "Copies 0x10000 halfwords from ROM bank 0x540000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb790, "runtime_rom_bank_loader_52",
      "Copies 0x10000 halfwords from ROM bank 0x520000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb7e0, "runtime_rom_bank_loader_50",
      "Copies 0xf000 halfwords from ROM bank 0x502000 to 0x501cc4, then calls reset/copy helper 0xeb510.")
label(0x000eb830, "runtime_rom_bank_load_all",
      "Calls the record-base selector continuation at 0xeb3b8, runs all eight ROM-bank loaders in order, normalizes zero mismatch slots 0x578558/0x57855c to 1, advances 0x578510, and returns at 0xeb898.")
label(0x000eb8a0, "runtime_packed_record_match_scan",
      "Copies g0 >> 2 dwords into the active workspace at 0x5785b0, scans the following g0 >> 2 dwords, compares byte masks 0xff/0xff00/0xff0000/0xff000000, and records matching pointers at 0x578560-0x57856c.")
label(0x000eb9a4, "runtime_packed_record_match_scan_b",
      "Repeats the four byte-mask packed-record scan against workspace base 0x910004, publishing matches at 0x578560-0x57856c and returning at 0xebaa4.")
label(0x000ebab0, "runtime_alt_record_table_init_a",
      "Sets workspace base 0x900004 and packed count 0xfffc, scans 0xffffffff followed by all 16 doubled-byte targets from 0x01010101 through 0x80808080 and the caller target through 0xeb8a0, normalizes zero match slots, and advances the status counter.")
label(0x000ebba0, "runtime_alt_packed_record_scan",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans the following single-halfword records, compares low/high bytes with masks 0xff/0xff00, and publishes the last matching record addresses at 0x578570/0x578574 before returning at 0xebc5c.")
label(0x000ebc60, "runtime_alt_record_table_init",
      "Initializes workspace base 0x1000000 with packed count 0x10000, invokes 0xebba0 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slots 0x578570/0x578574, increments 0x578510, and returns at 0xebd14.")
label(0x000ebd20, "runtime_alt_packed_record_scan_b",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans packed_byte_count >> 2 two-halfword records, compares low/high bytes with masks 0xff/0xff00, publishes first-pair matches at 0x578578/0x57857c and second-pair matches at 0x578580/0x578584, and returns at 0xebe1c.")
label(0x000ebe20, "runtime_alt_record_table_init_b",
      "Initializes workspace base 0x1080000 with packed count 0x80000, invokes 0xebd20 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slots 0x578578-0x578584, increments 0x578510, and returns at 0xebf04.")
label(0x000ebf10, "runtime_alt_packed_record_scan_c",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans the following halfwords, compares low/high bytes with masks 0xff/0xff00, publishes matches at 0x578588/0x57858c, and returns at 0xebfcc.")
label(0x000ebfd0, "runtime_alt_record_table_init_c",
      "Initializes workspace base 0x1800000 with packed count 0x4000, invokes 0xebf10 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slots 0x578588/0x57858c, increments 0x578510, and returns at 0xec084.")
label(0x000ec090, "runtime_alt_packed_record_scan_d",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, then scans 32 groups of 128 halfwords with 0x200-byte group strides, compares each low byte against the byte at 0x57852c masked by 0x7f, publishes the last match at 0x578590, and returns at 0xec130.")
label(0x000ec140, "runtime_alt_record_table_init_d",
      "Initializes workspace base 0x1810000 with packed count 0x4000, invokes 0xec090 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slot 0x578590, increments 0x578510, and returns at 0xec1dc.")
label(0x000ec1e0, "runtime_alt_packed_record_scan_e",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans 32 groups of 128 halfwords with 0x200-byte group strides, compares each low byte against the byte at 0x57852c masked by 0x7f, publishes the last match at 0x578594, and returns at 0xec280.")
label(0x000ec290, "runtime_alt_record_table_init_e",
      "Initializes workspace base 0x1814000 with packed count 0x4000, invokes 0xec1e0 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slot 0x578594, increments 0x578510, and returns at 0xec32c.")
label(0x000ec330, "runtime_alt_packed_record_scan_f",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans 32 groups of 128 halfwords with 0x200-byte group strides, compares each low byte against the byte at 0x57852c masked by 0x7f, publishes the last match at 0x578598, and returns at 0xec3d0.")
label(0x000ec3e0, "runtime_alt_record_table_init_f",
      "Initializes workspace base 0x1818000 with packed count 0x4000, invokes 0xec330 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slot 0x578598, increments 0x578510, and returns at 0xec47c.")
label(0x000ec480, "runtime_alt_record_base_select",
      "Selects alternate packed-record bases from marker groups: primary 0x578548-0x578554 -> 0x200000, 0x578570/0x578574 -> 0x1000000, 0x578578-0x578584 -> 0x1080000, 0x578588/0x57858c -> 0x1800000, then 0x578590/0x578594/0x578598 -> 0x1810000/0x1814000/0x1818000; fallback increments 0x578510 before continuation 0xec5b8 and indirect return 0xec61c.")
label(0x000ec630, "runtime_alt_record_table_copy",
      "Copies 0x2000 halfwords from the selected table pointer at 0x5785ac into destination base 0x1d00000, increments 0x578510, and returns through indirect continuation 0xec698.")
label(0x000ec6a0, "runtime_alt_packed_record_scan_g",
      "Initializes packed_byte_count >> 1 halfwords at 0x5785a4, scans packed_byte_count >> 1 paired records, compares low/high bytes independently, publishes first-halfword matches at 0x57859c and second-halfword matches at 0x5785a0, and returns at 0xec75c.")
label(0x000ec760, "runtime_alt_record_table_init_g",
      "Initializes workspace base 0x1d00000 with packed count 0x4000, invokes 0xec6a0 for 0xffff, all 16 power-of-two targets 1 through 0x8000, and the caller target, normalizes zero slots 0x57859c/0x5785a0, increments 0x578510, and returns at 0xec814.")
label(0x000ec820, "geometry_event_lookup_table_build",
      "Expands three 16-bit literals at 0xead20 into a 3x32x8 halfword command lookup table at 0x1800010, initializes eight 0x88888888 seed words at 0x1080000, and returns at 0xec8e4.")
label(0x000ec8f0, "runtime_alt_record_pipeline_dispatch",
      "Calls preparation routines 0x29a80, 0x1c220, 0x1bda0, and 0x28840 in order, clears g0 before the final preparation call, invokes lookup-table builder 0xec820, increments 0x578510, and returns at 0xec91c.")
label(0x000ec920, "runtime_event_counter_step",
      "Calls shared event service 0x28418, increments counter 0x578510, and returns at 0xec938.")
label(0x000ec940, "runtime_event_mode_flag_set",
      "Installs continuation 0xec960, sets event-mode flag 0x578514 to 1, and returns through that continuation.")
label(0x000ec970, "runtime_record_checksum_4stride",
      "Accumulates bytes at offsets 0 and 1 of each four-byte chunk, masks the sum to 16 bits, and returns through continuation 0xec9c0.")
label(0x000ec9d0, "runtime_record_checksum_3stride",
      "Accumulates bytes at offsets 2 and 3 of each four-byte chunk, masks the sum to 16 bits, and returns through continuation 0xeca28.")
label(0x000eca30, "runtime_event_result_publish_a",
      "Checksums source 0x2000000 with 0x800000 bytes via 0xec970, publishes to 0x578538, and advances 0x578510.")
label(0x000eca60, "runtime_event_result_publish_b",
      "Checksums source 0x2000000 with 0x800000 bytes via 0xec9d0, publishes to 0x57853c, and advances 0x578510.")
label(0x000eca90, "runtime_event_result_publish_c",
      "Checksums source 0x2800000 with 0x800000 bytes via 0xec970, publishes to 0x578530, and advances 0x578510.")
label(0x000ecac0, "runtime_event_result_publish_d",
      "Checksums source 0x2800000 with 0x800000 bytes via 0xec9d0, publishes to 0x578534, and advances 0x578510.")
label(0x000ecaf0, "runtime_event_result_publish_e",
      "Checksums source 0x1000000 with 0x1000000 bytes via 0xec970, publishes to 0x578540, and advances 0x578510.")
label(0x000ecb20, "runtime_event_result_publish_f",
      "Checksums source 0x1000000 with 0x1000000 bytes via 0xec9d0, publishes to 0x578544, and advances 0x578510.")
label(0x000ecb50, "runtime_event_handler_table",
      "Literal 25-entry event-handler table: publishers 0xeca30-0xecb20, primary/alternate initializers and scanners, pipeline/selector/copy entries, 0xeb830, and four repeated 0xec940 flag setters; terminator word at 0xecbb4 is zero.")
label(0x000ecbb8, "diagnostic_result_strings",
      "Literal result-format, GOOD/BAD, and IC-number strings used by diagnostics.")
label(0x000ecbe0, "diagnostic_result_format",
      "Calls value formatter 0x1cac8, renders format string at 0xecbb8 through 0xf5100, and selects GOOD 0xecbc0 for status 1, blank 0xecbc8 for status 0, or BAD 0xecbd0 otherwise.")
label(0x000ecc40, "diagnostic_result_format_compare",
      "Calls value formatter 0x1cac8 and renderer 0xf5100 with format 0xecbb8; selects blank 0xecbc8 for status -1, GOOD 0xecbc0 when status equals expected, or BAD 0xecc30 otherwise.")
label(0x000ecd80, "diagnostic_result_menu_render",
      "Renders the diagnostic IC result menu and its accumulated runtime results.")
label(0x000ed0d0, "runtime_record_workspace_reset",
      "Sets result slots 0x578530-0x578544 to 0xffffffff, clears marker slots 0x578548-0x5785a0, and returns through continuation 0xed1d0.")
label(0x000ed1e0, "diagnostic_wait_prompt_strings",
      "Literal diagnostic prompts for the test-button and wait states.")
label(0x000ed220, "diagnostic_result_service",
      "Initializes result state when 0x578500 is zero, resets the record workspace, clears 0x578510/0x578514, renders the test prompt and menu, then dispatches through 25-entry table 0xecb50 or falls back through 0xeade8 when event mode is active; returns at 0xed2e0 or 0xed300.")
label(0x000ed2e4, "diagnostic_result_service_fallback",
      "Handles the diagnostic result fallback and advances the service state.")
label(0x000ed320, "diagnostic_input_test_service",
      "Formats the input-test header at (23,6), advances state 1 to 2, advances states above 2 after calling 0x29330, combines 0x980010>>1 with 0x980014 for state 2, selects GOOD/BAD strings 0xed304/0xed308, then invokes wrapper 0xeaeb0 and fallback 0xeade8 for states 0/2; returns at 0xed438.")
label(0x000ed440, "diagnostic_input_status_strings",
      "Literal input-test status strings for directional, shot, dash, start, and coin inputs.")
label(0x000ed5c0, "diagnostic_input_status_render",
      "Renders header (21,6), 12 base status rows at x=19, a prompt at (20,39), and 12 conditional rows selected by bits 13,12,14,15,8,9,21,20,22,23,16,17 of 0x50249c; uses wrapper 0xeaeb0/renderer 0xf5100 and returns at 0xed968.")
label(0x000ed970, "diagnostic_billboard_test_strings",
      "Literal Versus City billboard, winner-lamp, 7-segment, and start-lamp test strings.")
label(0x000eda30, "diagnostic_billboard_test_render",
      "Renders header (21,6), emits pattern values 0x1f/0x3f/0x5f/0x7f/0x97/0x9f through 0x184e8, advances state 0x5785c4 using 0x503a08/0x5024e8, selects winner/7-segment/start-lamp labels, updates 0x502484, and invokes 0xeaeb0/0xeade8 before returning at 0xedcf8.")
label(0x000edd20, "diagnostic_sde_name_records",
      "Indexed SDE diagnostic event-name records used by the runtime trace/debug services.")
label(0x000eff60, "diagnostic_sdb_name_records",
      "Indexed SDB diagnostic event-name records used by the runtime trace/debug services.")
label(0x000f0674, "diagnostic_crt_pattern_handler_table",
      "Six-entry CRT pattern handler table at 0xf0674: 0xf068c, 0xf06ec, 0xf074c, 0xf07b8, 0xf0818, and 0xf0888.")
label(0x000f04d0, "diagnostic_crt_test_service",
      "Initializes 0x578500 to 1, sets pattern state 0x5784f4 to 6 and 0x1004e14 to 30, renders header at (12,6) with 0xeaf90 through 0xeaeb0, cycles the six-entry table at 0xf0674, and returns at 0xf08b4.")
label(0x000f08c0, "diagnostic_crt_pattern_buffer_fill",
      "Fills 4 planes x 6 rows x 32 halfwords at 0x100461e: destination = base + ((row + plane*6)<<7) + (halfword<<1), value = 0x2000 + ((plane*4 + (halfword>>3))<<7) + (halfword&7), and returns at 0xf0938.")
label(0x000f0980, "diagnostic_match_time_test_service",
      "Renders the match/time diagnostic, selects play-time versus match/death-match/network structures, and returns at 0xf0b38; external builder semantics remain unresolved.")
label(0x000f1c90, "diagnostic_coin_credit_service",
      "Initializes coin/credit diagnostic state, advances a modulo-20 index after 0xeada8 succeeds, writes the fixed pattern value 30, and dispatches through the table at 0xf1be0 before returning at 0xf1d40.")
label(0x000f1db0, "diagnostic_credit_math_formatter",
      "Runs five credit arithmetic columns using the recovered product/division/remainder branches, renders strings at 0xf1d50/0xf1d70/0xf1d90, and returns at 0xf1ebc.")
label(0x000f1f20, "diagnostic_coin_chute_status_render",
      "Reads the live status word at 0x1d0002a, handles zero and type-27 free-play cases, decodes normal packed bytes through 0xead30, calls the credit formatter twice, and returns at 0xf20a4.")
label(0x000f2de0, "diagnostic_bookkeeping_handler_table_a",
      "Primary bookkeeping diagnostic handler table selected by the service state.")
label(0x000f2e00, "diagnostic_bookkeeping_handler_table_b",
      "Alternate bookkeeping diagnostic handler table selected by the service state.")
label(0x000f2e20, "diagnostic_bookkeeping_service",
      "Initializes bookkeeping state, selects primary versus alternate counter/table flow from 0x578524, probes 0xeada8, advances modulo-5 state, and indirectly dispatches through 0xf2de0 or 0xf2e00 before returning at 0xf2ee4.")
label(0x000f33a0, "diagnostic_game_time_statistics_render",
      "Initializes 0x578500 when needed, branches on 0x57850c, renders header 0xf2ef0 at (18,6), emits fixed statistics rows from 0x1d00040/44/48/3c/4c/54, and returns at 0xf3a3c; alternate path begins at 0xf3668.")
label(0x000f3ab0, "diagnostic_eeprom_write_confirmation",
      "Gates on mode 1 and clear result state, renders the EEPROM clear/cancel confirmation, swaps pending pattern buffers, handles completion through 0x2350, and toggles 0x578508 after the final 0xeada8 probe before returning at 0xf3c0c.")
label(0x000f3c50, "diagnostic_test_mode_exit_reset",
      "Initializes 0x578500 if needed, writes exit marker 0x52 to 0x5032f4, clears 0x5770b0 and 0x503a00, increments 0x5039f4, and returns at 0xf3c9c.")
label(0x000f2940, "diagnostic_bookkeeping_arm_validate",
      "Selects 0xf2170 or 0xf2770 from 0x578524, probes 0xeade8, scans 25 records at 0xead30 from offset 4 using field order 0/3/2/1, writes the 1-based match selector to 0x1d0002a, and clears 0x578500 on exhaustion before returning at 0xf2a50.")
label(0x000f2a60, "diagnostic_bookkeeping_arm_credit_a",
      "Calls 0xf2170, writes pattern 30 at 0x1004622 and clears 0x10050a2, advances 0x1d0002c modulo 5 after 0xeade8, clamps 0x1d0002e when it exceeds coin-start, and returns at 0xf2ad8.")
label(0x000f2ae0, "diagnostic_bookkeeping_arm_credit_b",
      "Calls 0xf2170, writes pattern 30 at 0x1004722 and clears 0x1004622, advances 0x1d0002e modulo 5 after 0xeade8, clamps 0x1d0002c when it exceeds credit-start, and returns at 0xf2b58.")
label(0x000f2b60, "diagnostic_bookkeeping_arm_coin",
      "Calls 0xf2170, writes pattern 30 at 0x1004822 and clears 0x1004722, advances 0x1d0002a modulo 28 with zero replaced by 1, reconnects to 0xf19e8, and returns at 0xf2bbc.")
label(0x000f2bc0, "diagnostic_bookkeeping_arm_credit_reset",
      "Calls 0xf2170, writes pattern 30 at 0x1004fa2 and clears 0x1004822, resets selector 0x1d0002a from type 27 to 1 after 0xeade8, reconnects to 0xf19e8, and returns at 0xf2c14.")
label(0x000f2c20, "diagnostic_bookkeeping_arm_input_a",
      "Calls 0xf2770, writes pattern 30 at 0x1004514 and clears 0x1005094, advances 0x1d00035 modulo 10 with zero replaced by 1, and returns at 0xf2c84.")
label(0x000f2c90, "diagnostic_bookkeeping_arm_input_b",
      "Calls 0xf2770, writes pattern 30 at 0x1004614 and clears 0x1004514, advances 0x1d00036 modulo 10 with one replaced by 2, and returns at 0xf2cfc.")
label(0x000f2d00, "diagnostic_bookkeeping_arm_coin_chute_a",
      "Calls 0xf2770, writes pattern 30 at 0x1004714 and clears 0x1004614, advances 0x1d00030 modulo 10 with zero replaced by 1, and returns at 0xf2d64.")
label(0x000f2d70, "diagnostic_bookkeeping_arm_coin_chute_b",
      "Calls 0xf2770, writes pattern 30 at 0x1004c14 and clears 0x1004714, advances 0x1d00032 modulo 10 with zero replaced by 1, and returns at 0xf2dd4.")
label(0x000f2170, "diagnostic_coin_settings_render",
      "Renders the settings title at (18,6), formats 0x1d0002c/2e as coin and credit values, branches on 0x1d0002a between manual-setting text and the linked 0xf1f20 status renderer, and returns at 0xf22e0.")
label(0x000f2770, "diagnostic_coin_input_matrix_render",
      "Renders the coin/input matrix, selects zero/nonzero strings from 0x1d00035/36, calls the nine-entry builder at 0xf23e0 for rows rooted at x=17 and x=27, and returns at 0xf2930.")
label(0x000f19e8, "diagnostic_coin_config_decode",
      "Decodes the status word through 0xead30 offsets 0/2/1/3, writes 0x1d00035/30/32/36, normalizes 0x1d00034, sets 0x5785b4, and returns through 0xf1aa8.")
label(0x000f23e0, "diagnostic_coin_credit_matrix_builder",
      "Builds the nine-entry coin/credit arithmetic matrix from the live diagnostic input bytes.")
label(0x000f1ac0, "diagnostic_site_status_sync",
      "Gates on 0xeade8, validates hardware windows at 0x502408 and 0x502448, publishes status to 0x1d00028, and returns at 0xf1bb8.")
label(0x000f1bc0, "diagnostic_site_status_fallback",
      "On a successful 0xeade8 probe, sets 0x5784f8 to 2 and clears 0x578500 before returning at 0xf1bdc.")
label(0x000f1bc0, "diagnostic_site_status_fallback",
      "Handles the failed site/status probe and advances the diagnostic service state.")
label(0x000f1be0, "diagnostic_coin_display_dispatch_records",
      "Paired target/index records used to dispatch the coin diagnostic display handlers.")
label(0x000f14a0, "diagnostic_config_field_16_arm", "Updates configuration byte 0x1d00016.")
label(0x000f1520, "diagnostic_config_field_17_arm", "Updates configuration byte 0x1d00017.")
label(0x000f15a0, "diagnostic_config_field_18_arm", "Updates configuration byte 0x1d00018.")
label(0x000f1620, "diagnostic_config_field_19_arm", "Updates configuration byte 0x1d00019.")
label(0x000f16a0, "diagnostic_config_field_1a_arm", "Updates configuration byte 0x1d0001a.")
label(0x000f1720, "diagnostic_config_field_1b_arm", "Copies the diagnostic field at 0x1d0001b.")
label(0x000f1750, "diagnostic_config_field_1c_arm", "Copies the diagnostic field at 0x1d0001c.")
label(0x000f1780, "diagnostic_config_field_1d_arm", "Copies the diagnostic field at 0x1d0001d.")
label(0x000f17b0, "diagnostic_config_field_1f_arm", "Copies the diagnostic field at 0x1d0001f.")
label(0x000f17e0, "diagnostic_config_field_28_arm", "Copies the site/status field at 0x1d00028.")
label(0x000f1810, "diagnostic_config_field_20_arm", "Copies the diagnostic field at 0x1d00020.")
label(0x000f1840, "diagnostic_config_field_21_arm", "Normalizes and stores the diagnostic field at 0x1d00021.")
label(0x000f1890, "diagnostic_config_field_22_arm", "Cycles and stores the diagnostic field at 0x1d00022.")
label(0x000f18c0, "diagnostic_config_field_23_arm", "Normalizes and stores the diagnostic field at 0x1d00023.")
label(0x000f1900, "diagnostic_config_field_27_arm", "Cycles and stores the diagnostic field at 0x1d00027.")
label(0x000f1930, "diagnostic_config_field_24_arm", "Normalizes and stores the diagnostic field at 0x1d00024.")
label(0x000f1970, "diagnostic_config_field_25_arm", "Cycles and stores the diagnostic field at 0x1d00025.")
label(0x000f19a0, "diagnostic_config_field_26_arm", "Normalizes and stores the diagnostic field at 0x1d00026.")
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
label(0x000de990, "startup_status_workspace_reset",
      "Clears startup status fields 0x503c9c/0x503c98, conditionally clears 0x50429c/0x504298 for stage 4 and state 1, then routes mode 9 to 0xde9ec and other modes to 0xdead4.")
label(0x000de9ec, "startup_mode9_packet_prefix",
      "Emits the fixed mode-9 startup command-38/39 prefix using the 0x5040d8/0x5040e0 and 0x503ad8/0x503ae0 fields, constant 0x428c0000, and a zero field to 0x884000.")
label(0x000dea6c, "startup_mode9_response_gate",
      "Publishes the first two mode-9 FIFO responses at fp+0x40/fp+0x44, reads a third response, and routes zero to 0xdead0 or nonzero to the floating transform at 0xdea94.")
label(0x0006f600, "geometry_fixed_point_record_producer",
      "Sibling coordinate producer to 0x6ece0 and 0x6f6f0: validates cvtzri coordinates, submits the shared 0x41 half-coordinate lookup, emits the six-word 0x35 continuation, and returns the device response.")
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
ensure_function(0x0002b700, "startup_status_arm_post_test_transition", 0x0002b770)
ensure_function(0x0002b770, "startup_status_arm_subcounter_decrement", 0x0002b7b0)
ensure_function(0x0002b940, "startup_status_arm_continuation_trampoline", 0x0002b960)
ensure_function(0x0002bdd0, "startup_geometry_status_dispatch", 0x0002be30)
ensure_function(0x0002be30, "geometry_frame_service_initialize", 0x0002bee4)
ensure_function(0x0002d9a0, "geometry_transform_dispatch", 0x0002dc50)
ensure_function(0x0002e1c8, "geometry_status_continuation_trampoline", 0x0002e1e0)
ensure_function(0x0002e1e8, "geometry_status_continuation_trampoline_alt", 0x0002e200)
ensure_function(0x0002e320, "geometry_frame_packet_emit", 0x0002e3d0)
ensure_function(0x0002e450, "geometry_object_update_variant_a", 0x0002e590)
ensure_function(0x0002e590, "geometry_object_update_variant_b", 0x0002e6f0)
ensure_function(0x0002e6f0, "geometry_object_update_variant_c", 0x0002e860)
ensure_function(0x0002e860, "geometry_object_update_variant_d", 0x0002e990)
ensure_function(0x0002e990, "geometry_object_update_variant_e", 0x0002eaa0)
ensure_function(0x0002eaa0, "geometry_object_update_variant_f", 0x0002ebb0)
ensure_function(0x0002ebb0, "geometry_object_update_variant_g", 0x0002ece0)
ensure_function(0x0002ece0, "geometry_object_update_variant_h", 0x0002ef80)
ensure_function(0x0002ef90, "geometry_object_callback_state_dispatch", 0x0002f010)
ensure_function(0x0002f010, "geometry_object_motion_variant_a", 0x0002f260)
ensure_function(0x0002f260, "geometry_object_motion_variant_b", 0x0002f360)
ensure_function(0x0002f360, "geometry_object_motion_variant_c", 0x0002f460)
ensure_function(0x0002f460, "geometry_object_motion_variant_d", 0x0002f580)
ensure_function(0x0002f580, "geometry_object_motion_variant_e", 0x0002f930)
ensure_function(0x0002f930, "geometry_object_motion_variant_f", 0x0002fa20)
ensure_function(0x0002fa20, "geometry_object_motion_continuation_a", 0x0002fb20)
ensure_function(0x0002fb20, "geometry_object_motion_variant_g", 0x0002fd50)
ensure_function(0x0002fd50, "geometry_object_motion_continuation_b", 0x0002fe30)
ensure_function(0x0002fe30, "geometry_object_motion_variant_h", 0x0002ff80)
ensure_function(0x0002ff80, "geometry_object_motion_variant_i", 0x000300c0)
ensure_function(0x000300c0, "geometry_object_motion_variant_j", 0x00030230)
ensure_function(0x00030230, "geometry_object_motion_continuation_c", 0x000303e0)
ensure_function(0x000303e0, "geometry_object_motion_phase_reset_a", 0x00030420)
ensure_function(0x00030420, "geometry_object_motion_phase_reset_b", 0x00030460)
ensure_function(0x00030460, "geometry_object_motion_variant_k", 0x00030590)
ensure_function(0x00030590, "geometry_object_motion_variant_l", 0x00030660)
ensure_function(0x00030660, "geometry_object_motion_variant_m", 0x00030c20)
ensure_function(0x00030c20, "geometry_object_motion_continuation_d", 0x00030d40)
ensure_function(0x00030d40, "geometry_object_motion_continuation_e", 0x00030e40)
ensure_function(0x00030e40, "geometry_object_motion_variant_n", 0x00030ff0)
ensure_function(0x00030ff0, "geometry_object_motion_variant_o", 0x00031210)
ensure_function(0x00031210, "geometry_object_motion_variant_p", 0x000313e0)
ensure_function(0x000313e0, "geometry_object_motion_variant_q", 0x000315a0)
ensure_function(0x000315a0, "geometry_object_motion_variant_r", 0x000316d0)
ensure_function(0x000316d0, "geometry_object_motion_variant_s", 0x000317f0)
ensure_function(0x000317f0, "geometry_object_motion_variant_t", 0x00031910)
ensure_function(0x00031910, "geometry_object_motion_variant_u", 0x00031ab0)
ensure_function(0x00031ab0, "geometry_object_motion_variant_v", 0x00031d20)
ensure_function(0x00031d20, "geometry_object_motion_variant_w", 0x00032120)
ensure_function(0x00032120, "geometry_object_motion_variant_x", 0x00032330)
ensure_function(0x00032330, "geometry_object_motion_variant_y", 0x000324e0)
ensure_function(0x000324e0, "geometry_object_motion_phase_helper_a", 0x00032540)
ensure_function(0x00032540, "geometry_object_motion_phase_helper_b", 0x00032560)
ensure_function(0x00032810, "geometry_object_state_machine", 0x00036460)
ensure_function(0x000371e0, "geometry_frame_step", 0x00037460)
ensure_function(0x00036460, "geometry_object_profile_state_variant_a", 0x00036690)
ensure_function(0x00036690, "geometry_object_profile_state_variant_b", 0x000367f0)
ensure_function(0x000367f0, "geometry_object_profile_state_variant_c", 0x00036980)
ensure_function(0x00036980, "geometry_object_profile_state_variant_d", 0x00036af0)
ensure_function(0x00036af0, "geometry_object_profile_state_variant_e", 0x00036bb0)
ensure_function(0x00036bb0, "geometry_object_transform_variant_a", 0x00036c40)
ensure_function(0x00036c40, "geometry_object_transform_variant_b", 0x00036cc0)
ensure_function(0x00036cc0, "geometry_object_transform_variant_c", 0x00036d50)
ensure_function(0x00036d50, "geometry_object_transform_variant_d", 0x00036de0)
ensure_function(0x00036de0, "geometry_object_transform_variant_e", 0x00036e70)
ensure_function(0x00036e70, "geometry_object_profile_transition_variant_a", 0x00036ef0)
ensure_function(0x00036ef0, "geometry_object_profile_transition_variant_b", 0x00036f90)
ensure_function(0x00036f90, "geometry_object_profile_transition_variant_c", 0x00037060)
ensure_function(0x00037060, "geometry_object_profile_transition_variant_d", 0x00037130)
ensure_function(0x000371e0, "geometry_object_runtime_update", 0x00037f50)
ensure_function(0x00037f50, "geometry_object_runtime_motion_continuation", 0x000382e0)
ensure_function(0x00038340, "geometry_object_resource_motion_variant_a", 0x00038490)
ensure_function(0x00038490, "geometry_object_resource_motion_variant_b", 0x000385f0)
ensure_function(0x000385f0, "geometry_object_resource_motion_variant_c", 0x000386c0)
ensure_function(0x000386c0, "geometry_object_resource_motion_variant_d", 0x000388f0)
ensure_function(0x000388f0, "geometry_object_resource_motion_variant_e", 0x000389f0)
ensure_function(0x000389f0, "geometry_object_resource_motion_variant_f", 0x00038b30)
ensure_function(0x00038b30, "geometry_object_pair_packet_update", 0x00038db0)
ensure_function(0x00038db0, "geometry_object_service_counter_loop", 0x00038ef0)
ensure_function(0x00038ef0, "geometry_object_profile_packet_builder", 0x000392b0)
ensure_function(0x000392b0, "geometry_object_displacement_classifier", 0x00039410)
ensure_function(0x00039410, "geometry_object_service_state_continuation", 0x00039490)
ensure_function(0x00039490, "geometry_object_service_motion_update", 0x00039850)
ensure_function(0x00039850, "geometry_object_service_motion_variant_g", 0x00039910)
ensure_function(0x00039910, "geometry_object_resource_remainder_continuation", 0x00039980)
ensure_function(0x00039980, "geometry_object_resource_phase_dispatch", 0x00039a90)
ensure_function(0x00039a90, "geometry_geometry_batch_initializer", 0x00039da0)
ensure_function(0x00039da0, "geometry_selector_packet_builder", 0x0003a140)
ensure_function(0x0003a140, "geometry_selector_geometry_emitter", 0x0003a510)
ensure_function(0x0003a510, "geometry_scene_update_dispatch", 0x0003d520)
ensure_function(0x0003d540, "geometry_fixed_point_clamp_helper", 0x0003d5d0)
ensure_function(0x0003d5d0, "geometry_service_state_initialize", 0x0003d730)
ensure_function(0x0003d730, "geometry_object_record_update", 0x0003e5e0)
ensure_function(0x0003e5e0, "geometry_object_profile_state_initialize", 0x0003ec94)
ensure_function(0x0003ecd0, "geometry_runtime_record_allocate", 0x0003ed60)
ensure_function(0x0003ed60, "geometry_runtime_record_allocate_alt", 0x0003edd0)
ensure_function(0x0003edd0, "geometry_runtime_record_update", 0x0003eeb0)
ensure_function(0x0003eeb0, "geometry_runtime_record_reset", 0x0003ef50)
ensure_function(0x0003ef50, "geometry_runtime_record_motion_emit", 0x0003f120)
ensure_function(0x0003f120, "geometry_runtime_record_motion_emit_alt", 0x0003f2b0)
ensure_function(0x0003f2b0, "geometry_runtime_record_packet_initialize", 0x0003f380)
ensure_function(0x0003f380, "geometry_runtime_record_packet_initialize_alt", 0x0003f470)
ensure_function(0x0003f470, "geometry_runtime_record_table_clear", 0x0003f4e0)
ensure_function(0x0003f4e0, "geometry_runtime_record_seed_selector10", 0x0003f550)
ensure_function(0x0003f550, "geometry_runtime_record_table_seed_pair", 0x0003f5e8)
ensure_function(0x0003f5f0, "geometry_runtime_record_seed_command17", 0x0003f6e0)
ensure_function(0x0003f6e0, "geometry_runtime_record_seed_command17_alt", 0x0003f7d0)
ensure_function(0x0003f7d0, "geometry_runtime_record_seed_command17_bounded", 0x0003f8d0)
ensure_function(0x0003f8d0, "geometry_profile_command5_emit_a", 0x0003fa90)
ensure_function(0x0003fa90, "geometry_profile_command5_emit_b", 0x0003fc50)
ensure_function(0x0003fc50, "geometry_profile_command5_emit_c", 0x0003fdc0)
ensure_function(0x0003fdc0, "geometry_profile_command5_emit_d", 0x0003ff80)
ensure_function(0x0003ff80, "geometry_profile_command5_emit_e", 0x000400f0)
ensure_function(0x000400f0, "geometry_profile_command5_emit_f", 0x00040310)
ensure_function(0x00040310, "geometry_profile_command5_emit_g", 0x000406cc)
ensure_function(0x000406d0, "geometry_profile_command5_emit_h", 0x000408a8)
ensure_function(0x000408b0, "geometry_object_packet_variant_a", 0x00040a80)
ensure_function(0x00040a80, "geometry_object_packet_variant_b", 0x00040bc0)
ensure_function(0x00040bc0, "geometry_object_packet_variant_c", 0x00040d00)
ensure_function(0x00040d00, "geometry_object_packet_variant_d", 0x00040e10)
ensure_function(0x00040e10, "geometry_object_packet_variant_e", 0x00040f50)
ensure_function(0x00040f50, "geometry_object_packet_variant_f", 0x00041090)
ensure_function(0x00041090, "geometry_object_motion_packet_variant_a", 0x00041340)
ensure_function(0x00041340, "geometry_object_motion_packet_variant_b", 0x000414b0)
ensure_function(0x000414b0, "geometry_object_motion_packet_variant_c", 0x00041620)
ensure_function(0x00041620, "geometry_object_motion_packet_variant_d", 0x00041800)
ensure_function(0x00041800, "geometry_object_motion_packet_variant_e", 0x000419c0)
ensure_function(0x000419c0, "geometry_object_motion_packet_variant_f", 0x00041c50)
ensure_function(0x00041cb0, "geometry_object_packet_batch_emit", 0x00041f20)
ensure_function(0x00041f20, "geometry_runtime_packet_dispatch", 0x00042320)
ensure_function(0x00042320, "geometry_runtime_buffer_record_store", 0x000423a0)
ensure_function(0x00042480, "geometry_object_profile_state_variant_a", 0x00042670)
ensure_function(0x00042670, "geometry_object_profile_state_variant_b", 0x00042760)
ensure_function(0x00042780, "geometry_object_profile_state_variant_c", 0x000428e0)
ensure_function(0x000428e0, "geometry_object_profile_state_variant_d", 0x000429c0)
ensure_function(0x000429f0, "geometry_object_profile_state_transition", 0x000430d0)
ensure_function(0x000430d0, "geometry_object_profile_state_transition_alt", 0x00043198)
ensure_function(0x000431c0, "geometry_object_profile_state_variant_e", 0x00043420)
ensure_function(0x00043420, "geometry_object_profile_state_variant_f", 0x00043500)
ensure_function(0x00043530, "geometry_object_profile_state_variant_g", 0x00043680)
ensure_function(0x00043680, "geometry_object_profile_state_variant_h", 0x00043774)
ensure_function(0x000437ac, "geometry_object_profile_state_variant_i", 0x000438d0)
ensure_function(0x000438e0, "geometry_object_profile_state_variant_j", 0x000439bc)
ensure_function(0x000439e0, "geometry_object_profile_state_variant_k", 0x00043afc)
ensure_function(0x00043b00, "geometry_object_profile_state_variant_l", 0x00043b8c)
ensure_function(0x00043bb0, "geometry_object_profile_state_variant_m", 0x00043ca4)
ensure_function(0x00043cb0, "geometry_object_profile_state_variant_n", 0x00043d10)
ensure_function(0x00043d50, "geometry_object_profile_state_variant_o", 0x00043e00)
ensure_function(0x00043e00, "geometry_object_profile_state_variant_p", 0x00043edc)
ensure_function(0x00043ee0, "geometry_profile_runtime_pool_clear", 0x00043fa0)
ensure_function(0x00043fa0, "geometry_profile_phase_dispatch", 0x0004438c)
ensure_function(0x00044390, "geometry_profile_timing_state_update", 0x00044594)
ensure_function(0x000445a0, "geometry_profile_runtime_mode_update", 0x00044ac4)
ensure_function(0x00044ad0, "geometry_profile_timing_hardware_emit", 0x0004507c)
ensure_function(0x00045080, "geometry_profile_timing_hardware_emit_variant_a", 0x0004537c)
ensure_function(0x00045380, "geometry_profile_timing_hardware_emit_variant_b", 0x0004567c)
ensure_function(0x00045680, "geometry_profile_timing_hardware_emit_variant_c", 0x00045c2c)
ensure_function(0x00045c30, "geometry_profile_timing_hardware_emit_variant_d", 0x00045f4c)
ensure_function(0x00045f50, "geometry_profile_timing_hardware_emit_variant_e", 0x0004647c)
ensure_function(0x00046480, "geometry_profile_timing_hardware_emit_variant_f", 0x000466a4)
ensure_function(0x000466b0, "geometry_profile_timing_dual_buffer_emit", 0x00046930)
ensure_function(0x0004a420, "geometry_object_profile_threshold_update", 0x0004a774)
ensure_function(0x0004a780, "geometry_object_profile_phase_advance", 0x0004a990)
ensure_function(0x0004a990, "geometry_object_profile_phase_advance_alt", 0x0004abbc)
ensure_function(0x0004abc0, "geometry_object_profile_phase_transition_variant_a", 0x0004ad4c)
ensure_function(0x0004ad50, "geometry_object_profile_phase_transition_variant_b", 0x0004ae64)
ensure_function(0x0004ae70, "geometry_object_profile_phase_transition_variant_c", 0x0004af20)
ensure_function(0x0004af20, "geometry_object_profile_phase_transition_variant_d", 0x0004aff0)
ensure_function(0x0004aff0, "geometry_object_profile_phase_transition_variant_e", 0x0004b08c)
ensure_function(0x0004b090, "geometry_object_profile_phase_transition_variant_f", 0x0004b14c)
ensure_function(0x0004b150, "geometry_object_profile_state_event_update", 0x0004b5f4)
ensure_function(0x0004b600, "geometry_object_profile_event_progress_update", 0x0004b938)
ensure_function(0x0004b940, "geometry_object_profile_cursor_transition_variant_a", 0x0004bb00)
ensure_function(0x0004bb10, "geometry_object_profile_cursor_transition_variant_b", 0x0004bcdc)
ensure_function(0x0004bce0, "geometry_object_profile_state_finalize", 0x0004c048)
ensure_function(0x0004c050, "geometry_object_profile_runtime_update_variant_a", 0x0004c60c)
ensure_function(0x0004c610, "geometry_object_profile_runtime_update_variant_b", 0x0004c8ec)
ensure_function(0x0004c8f0, "geometry_object_profile_runtime_update_variant_c", 0x0004ca40)
ensure_function(0x0004ca40, "geometry_object_profile_runtime_update_variant_d", 0x0004cb6c)
ensure_function(0x0004cb70, "geometry_object_profile_runtime_update_variant_e", 0x0004cc1c)
ensure_function(0x0004cc20, "geometry_object_profile_runtime_update_variant_f", 0x0004cd00)
ensure_function(0x0004cd00, "geometry_object_profile_runtime_update_variant_g", 0x0004d044)
ensure_function(0x0004d540, "geometry_object_profile_cursor_transition_variant_c", 0x0004d714)
ensure_function(0x0004d720, "geometry_object_profile_cursor_transition_variant_d", 0x0004d874)
ensure_function(0x0004d880, "geometry_object_profile_cursor_transition_variant_e", 0x0004da7c)
ensure_function(0x0004da80, "geometry_object_profile_cursor_transition_variant_f", 0x0004dce0)
ensure_function(0x0004dce0, "geometry_object_profile_cursor_transition_variant_g", 0x0004def0)
ensure_function(0x0004def0, "geometry_object_profile_cursor_transition_variant_h", 0x0004e074)
ensure_function(0x0004e080, "geometry_object_profile_threshold_update_variant_b", 0x0004e3d4)
ensure_function(0x0004e3e0, "geometry_object_profile_phase_dispatch_variant_b", 0x0004e5f0)
ensure_function(0x0004e5f0, "geometry_object_profile_phase_dispatch_variant_c", 0x0004e81c)
ensure_function(0x0004e820, "geometry_object_profile_phase_dispatch_variant_d", 0x0004e920)
ensure_function(0x0004e920, "geometry_object_profile_phase_dispatch_variant_e", 0x0004ea34)
ensure_function(0x0004ea40, "geometry_object_profile_phase_dispatch_variant_f", 0x0004eaf0)
ensure_function(0x0004eaf0, "geometry_object_profile_phase_dispatch_variant_g", 0x0004ebc0)
ensure_function(0x0004ebc0, "geometry_object_profile_phase_dispatch_variant_h", 0x0004ec5c)
ensure_function(0x0004ec60, "geometry_object_profile_phase_dispatch_variant_i", 0x0004ed1c)
ensure_function(0x0004ed20, "geometry_object_profile_phase_state_dispatch", 0x0004f01c)
ensure_function(0x0004f020, "geometry_object_profile_phase_transition_variant_g", 0x0004f1e8)
ensure_function(0x0004f1f0, "geometry_object_profile_phase_transition_variant_h", 0x0004f3d4)
ensure_function(0x00051440, "geometry_object_profile_runtime_state_update_variant_a", 0x000517f0)
ensure_function(0x000517f0, "geometry_object_profile_runtime_state_update_variant_b", 0x00051a78)
ensure_function(0x00051a80, "geometry_object_profile_threshold_update_variant_c", 0x000520dc)
ensure_function(0x000520e0, "geometry_object_profile_phase_state_dispatch_variant_b", 0x00052360)
ensure_function(0x00052360, "geometry_object_profile_phase_state_dispatch_variant_c", 0x00052644)
ensure_function(0x00052650, "geometry_object_profile_threshold_event_update", 0x00052878)
ensure_function(0x00052880, "geometry_object_profile_threshold_event_update_variant_b", 0x00052af8)
ensure_function(0x00052b00, "geometry_object_profile_phase_transition_variant_i", 0x00052ba0)
ensure_function(0x00052ba0, "geometry_object_profile_phase_transition_variant_j", 0x00052ca0)
ensure_function(0x00052ca0, "geometry_object_profile_phase_transition_variant_k", 0x00052d30)
ensure_function(0x00052e30, "geometry_object_profile_phase_state_dispatch_variant_d", 0x00053044)
ensure_function(0x00053050, "geometry_object_profile_phase_transition_variant_l", 0x0005327c)
ensure_function(0x00053280, "geometry_object_profile_phase_dispatch_variant_f", 0x000534c4)
ensure_function(0x000534d0, "geometry_object_profile_phase_state_dispatch_variant_g", 0x00053680)
ensure_function(0x00053680, "geometry_profile_runtime_geometry_math_update", 0x00053a14)
ensure_function(0x00053a20, "geometry_object_profile_status_transition_variant_a", 0x00053cfc)
ensure_function(0x00053d00, "geometry_object_profile_status_transition_variant_b", 0x00053fe0)
ensure_function(0x00053fe0, "geometry_object_profile_status_transition_variant_c", 0x000540a0)
ensure_function(0x000540a0, "geometry_object_profile_status_transition_variant_d", 0x00054160)
ensure_function(0x00054160, "geometry_object_profile_phase_state_dispatch_variant_h", 0x00054340)
ensure_function(0x00054340, "geometry_object_profile_compact_transition_variant_a", 0x000543f0)
ensure_function(0x000543f0, "geometry_object_profile_compact_transition_variant_b", 0x000544a0)
ensure_function(0x000544a0, "geometry_object_profile_threshold_event_update_variant_c", 0x000545f0)
ensure_function(0x000545f0, "geometry_object_profile_threshold_event_update_variant_d", 0x00054760)
ensure_function(0x00054760, "geometry_object_profile_indexed_geometry_update_variant_a", 0x00054a60)
ensure_function(0x00054a60, "geometry_object_profile_indexed_geometry_update_variant_b", 0x00054db0)
ensure_function(0x00054e00, "geometry_object_profile_runtime_geometry_math_update_variant_b", 0x00054f4c)
ensure_function(0x00054f50, "geometry_object_profile_compact_transition_variant_c", 0x000550b4)
ensure_function(0x000550c0, "geometry_object_profile_indexed_geometry_update_variant_c", 0x00055300)
ensure_function(0x00055300, "geometry_object_profile_indexed_geometry_update_variant_d", 0x0005554c)
ensure_function(0x00055550, "geometry_object_profile_indexed_geometry_update_variant_e", 0x00055808)
ensure_function(0x00055930, "geometry_object_profile_kinematics_collision_update", 0x00055c90)
ensure_function(0x00055c90, "geometry_object_profile_phase_transition_controller", 0x00055ea0)
ensure_function(0x00055ea0, "geometry_object_profile_phase_transition_variant_e", 0x000560c8)
ensure_function(0x000560d0, "geometry_object_profile_phase_transition_variant_f", 0x000561e8)
ensure_function(0x000561f0, "geometry_object_profile_indexed_transition_variant_a", 0x0005631c)
ensure_function(0x00056320, "geometry_object_profile_indexed_transition_variant_b", 0x000563ec)
ensure_function(0x000563f0, "geometry_object_profile_indexed_transition_variant_c", 0x000564dc)
ensure_function(0x000564e0, "geometry_object_profile_compact_transition_variant_d", 0x0005657c)
ensure_function(0x00056580, "geometry_object_profile_compact_transition_variant_e", 0x0005663c)
ensure_function(0x00056640, "geometry_object_profile_phase_state_dispatch_variant_i", 0x0005692c)
ensure_function(0x00056930, "geometry_object_profile_indexed_transition_variant_d", 0x00056b28)
ensure_function(0x00056b30, "geometry_object_profile_indexed_transition_variant_e", 0x00056d08)
ensure_function(0x00056d10, "geometry_object_profile_phase_state_dispatch_variant_j", 0x00056f40)
ensure_function(0x00056f40, "geometry_object_profile_phase_state_dispatch_variant_k", 0x00057264)
ensure_function(0x00057270, "geometry_object_profile_phase_state_dispatch_variant_l", 0x00057530)
ensure_function(0x00057530, "geometry_object_profile_indexed_geometry_update_variant_f", 0x000576d0)
ensure_function(0x000576d0, "geometry_object_profile_indexed_geometry_update_variant_g", 0x00057870)
ensure_function(0x00057870, "geometry_object_profile_video_command_producer_variant_a", 0x00057ac8)
ensure_function(0x00057ad0, "geometry_object_profile_video_command_producer_variant_b", 0x00057d64)
ensure_function(0x00057d70, "geometry_object_profile_compact_transition_variant_f", 0x00057e30)
ensure_function(0x00057e30, "geometry_object_profile_video_command_producer_variant_c", 0x00057fb8)
ensure_function(0x00057fc0, "geometry_object_profile_compact_transition_variant_g", 0x00058068)
ensure_function(0x00058070, "geometry_object_profile_compact_transition_variant_h", 0x00058118)
ensure_function(0x00058120, "geometry_object_profile_indexed_transition_variant_f", 0x00058228)
ensure_function(0x00058230, "geometry_object_profile_indexed_transition_variant_g", 0x00058338)
ensure_function(0x00058340, "geometry_object_profile_indexed_geometry_update_variant_h", 0x00058688)
ensure_function(0x00058690, "geometry_object_profile_indexed_geometry_update_variant_i", 0x0005892c)
ensure_function(0x00058930, "geometry_object_profile_indexed_transition_variant_h", 0x00058ae4)
ensure_function(0x00058af0, "geometry_object_profile_runtime_geometry_status_update_variant_c", 0x00058c3c)
ensure_function(0x00058c40, "geometry_object_profile_indexed_transition_variant_i", 0x00058ea4)
ensure_function(0x00058eb0, "geometry_object_profile_indexed_transition_variant_j", 0x000590b8)
ensure_function(0x000590c0, "geometry_object_profile_indexed_transition_variant_k", 0x0005936c)
ensure_function(0x00059370, "geometry_object_profile_transition_driver_variant_a", 0x00059630)
ensure_function(0x00059640, "geometry_object_profile_geometry_bounds_flags_update", 0x00059990)
ensure_function(0x000599a0, "geometry_object_profile_phase_controller_variant_a", 0x00059c34)
ensure_function(0x00059c40, "geometry_object_profile_phase_controller_variant_b", 0x00059f3c)
ensure_function(0x00059f40, "geometry_object_profile_phase_transition_variant_g", 0x0005a194)
ensure_function(0x0005a1a0, "geometry_object_profile_phase_controller_variant_c", 0x0005a438)
ensure_function(0x0005a440, "geometry_object_profile_phase_transition_variant_h", 0x0005a4dc)
ensure_function(0x0005a4e0, "geometry_object_profile_phase_transition_variant_i", 0x0005a5dc)
ensure_function(0x0005a5e0, "geometry_object_profile_phase_transition_variant_j", 0x0005a67c)
ensure_function(0x0005a680, "geometry_object_profile_phase_transition_variant_k", 0x0005a77c)
ensure_function(0x0005a780, "geometry_object_profile_phase_transition_variant_l", 0x0005aabc)
ensure_function(0x0005aac0, "geometry_object_profile_indexed_transition_variant_l", 0x0005acb8)
ensure_function(0x0005acc0, "geometry_object_profile_indexed_transition_variant_m", 0x0005af00)
ensure_function(0x0005af10, "geometry_object_profile_phase_transition_variant_m", 0x0005b1dc)
ensure_function(0x0005b1e0, "geometry_object_profile_phase_transition_variant_n", 0x0005b4ac)
ensure_function(0x0005b4b0, "geometry_object_profile_phase_transition_variant_o", 0x0005b600)
ensure_function(0x0005b610, "geometry_object_profile_phase_transition_variant_p", 0x0005b764)
ensure_function(0x0005b770, "geometry_object_profile_phase_transition_variant_q", 0x0005b82c)
ensure_function(0x0005b830, "geometry_object_profile_phase_transition_variant_r", 0x0005b8ec)
ensure_function(0x0005b8f0, "geometry_object_profile_phase_transition_variant_s", 0x0005b994)
ensure_function(0x0005b9a0, "geometry_object_profile_phase_transition_variant_t", 0x0005ba44)
ensure_function(0x0005ba50, "geometry_object_profile_phase_transition_variant_u", 0x0005bb54)
ensure_function(0x0005bb60, "geometry_object_profile_phase_transition_variant_v", 0x0005bc64)
ensure_function(0x0005bc70, "geometry_object_profile_indexed_transition_variant_n", 0x0005bfe0)
ensure_function(0x0005bff0, "geometry_object_profile_indexed_transition_variant_o", 0x0005c360)
ensure_function(0x0005c370, "geometry_object_profile_indexed_transition_variant_p", 0x0005c648)
ensure_function(0x0005c650, "geometry_object_profile_transition_reset_helper", 0x0005c6b8)
ensure_function(0x0005c6c0, "geometry_object_profile_indexed_transition_variant_q", 0x0005c97c)
ensure_function(0x0005c980, "geometry_object_profile_transition_reset_helper_variant_b", 0x0005c9e8)
ensure_function(0x0005c9f0, "geometry_object_profile_indexed_transition_variant_r", 0x0005cd18)
ensure_function(0x0005cd1c, "geometry_object_profile_transition_reset_helper_variant_c", 0x0005cd88)
ensure_function(0x0005cd90, "geometry_object_profile_indexed_transition_variant_s", 0x0005cfe8)
ensure_function(0x0005cff0, "geometry_object_profile_phase_transition_variant_w", 0x0005d1b8)
ensure_function(0x0005d1c0, "geometry_object_profile_phase_transition_variant_x", 0x0005d3cc)
ensure_function(0x0005d3d0, "geometry_object_profile_geometry_bounds_flags_update_variant_b", 0x0005d72c)
ensure_function(0x0005d730, "geometry_object_profile_phase_controller_variant_d", 0x0005d964)
ensure_function(0x0005d970, "geometry_object_profile_indexed_phase_controller_variant_a", 0x0005dc80)
ensure_function(0x0005dc90, "geometry_object_profile_phase_transition_variant_y", 0x0005de4c)
ensure_function(0x0005de50, "geometry_object_profile_phase_transition_variant_z", 0x0005e034)
ensure_function(0x0005e040, "geometry_object_profile_phase_transition_variant_aa", 0x0005e104)
ensure_function(0x0005e110, "geometry_object_profile_indexed_transition_variant_t", 0x0005e1f4)
ensure_function(0x0005e200, "geometry_object_profile_phase_transition_variant_ab", 0x0005e298)
ensure_function(0x0005e2a0, "geometry_object_profile_indexed_transition_variant_u", 0x0005e358)
ensure_function(0x0005e360, "geometry_object_profile_phase_controller_variant_e", 0x0005e520)
ensure_function(0x0005e530, "geometry_object_profile_indexed_transition_variant_v", 0x0005e724)
ensure_function(0x0005e730, "geometry_object_profile_indexed_transition_variant_w", 0x0005e900)
ensure_function(0x0005e910, "geometry_object_profile_phase_controller_variant_f", 0x0005eae4)
ensure_function(0x0005eaf0, "geometry_object_profile_phase_controller_variant_g", 0x0005ecbc)
ensure_function(0x0005ecc0, "geometry_object_profile_phase_transition_variant_ac", 0x0005ef94)
ensure_function(0x0005efa0, "geometry_object_profile_phase_transition_variant_ad", 0x0005f24c)
ensure_function(0x0005f250, "geometry_object_profile_phase_transition_variant_ae", 0x0005f584)
ensure_function(0x0005f590, "geometry_object_profile_phase_transition_variant_af", 0x0005f750)
ensure_function(0x0005f930, "geometry_object_profile_phase_controller_variant_h", 0x0005f9ec)
ensure_function(0x0005f9f0, "geometry_object_profile_phase_controller_variant_i", 0x0005fac0)
ensure_function(0x0005fad0, "geometry_object_profile_phase_controller_variant_j", 0x0005fb78)
ensure_function(0x0005fb80, "geometry_object_profile_phase_controller_variant_k", 0x0005fc24)
ensure_function(0x0005fc30, "geometry_object_profile_phase_transition_variant_ag", 0x0005fcec)
ensure_function(0x0005fcf0, "geometry_object_profile_phase_transition_variant_ah", 0x0005fdac)
ensure_function(0x0005fdb0, "geometry_object_profile_indexed_phase_controller_variant_b", 0x0006004c)
ensure_function(0x00060050, "geometry_object_profile_indexed_phase_controller_variant_c", 0x0006036c)
ensure_function(0x00060370, "geometry_object_profile_phase_controller_variant_l", 0x0006057c)
ensure_function(0x00060580, "geometry_object_profile_phase_controller_variant_m", 0x000607fc)
ensure_function(0x00060a30, "geometry_object_profile_indexed_transition_variant_x", 0x00060ac0)
ensure_function(0x00060c60, "geometry_object_profile_indexed_transition_variant_y", 0x00060e78)
ensure_function(0x000611d0, "geometry_object_profile_geometry_bounds_flags_update_variant_c", 0x000615e8)
ensure_function(0x000615f0, "geometry_object_profile_state_controller_variant_a", 0x0006182c)
ensure_function(0x00061830, "geometry_object_profile_state_controller_variant_b", 0x00061aa4)
ensure_function(0x00061ab0, "geometry_object_profile_phase_transition_variant_ai", 0x00061c38)
ensure_function(0x00061c40, "geometry_object_profile_indexed_transition_variant_z", 0x00061d50)
ensure_function(0x00061d60, "geometry_object_profile_phase_transition_variant_aj", 0x00061e0c)
ensure_function(0x00061e10, "geometry_object_profile_indexed_transition_late_variant_a", 0x00061edc)
ensure_function(0x00061ee0, "geometry_object_profile_phase_transition_variant_ak", 0x00061f78)
ensure_function(0x00061f80, "geometry_object_profile_indexed_transition_late_variant_b", 0x00062038)
ensure_function(0x00062040, "geometry_object_profile_object_state_controller_variant_a", 0x00062258)
ensure_function(0x00062260, "geometry_object_profile_object_state_controller_variant_b", 0x00062570)
ensure_function(0x00062580, "geometry_object_profile_indexed_transition_variant_ac", 0x00062918)
ensure_function(0x00062920, "geometry_object_profile_geometry_setup_variant_a", 0x00062d28)
ensure_function(0x00062d30, "geometry_object_profile_phase_transition_variant_al", 0x00062fc8)
ensure_function(0x00062fd0, "geometry_object_profile_phase_transition_variant_am", 0x0006311c)
ensure_function(0x00063120, "geometry_object_profile_phase_transition_variant_an", 0x000631dc)
ensure_function(0x000631e0, "geometry_object_profile_phase_controller_variant_n", 0x00063284)
ensure_function(0x00063290, "geometry_object_profile_phase_transition_variant_ao", 0x0006336c)
ensure_function(0x00063370, "geometry_object_profile_indexed_phase_controller_variant_d", 0x000636b0)
ensure_function(0x000636c0, "geometry_object_profile_indexed_phase_controller_variant_e", 0x00063a88)
ensure_function(0x00063a90, "geometry_object_profile_phase_transition_variant_ap", 0x00063bf0)
ensure_function(0x00063c00, "geometry_object_profile_phase_transition_variant_aq", 0x00063d50)
ensure_function(0x00063d60, "geometry_object_profile_generated_asset_controller_variant_a", 0x00063f24)
ensure_function(0x00063f30, "geometry_object_profile_indexed_transition_variant_ad", 0x00064190)
ensure_function(0x000641a0, "geometry_object_profile_indexed_transition_late_variant_c", 0x00064300)
ensure_function(0x00064310, "geometry_object_profile_phase_controller_variant_o", 0x0006459c)
ensure_function(0x000645a0, "geometry_object_profile_geometry_bounds_flags_update_variant_d", 0x000648c4)
ensure_function(0x000648d0, "geometry_object_profile_object_state_controller_variant_c", 0x00064af0)
ensure_function(0x00064b00, "geometry_object_profile_object_state_controller_variant_d", 0x00064d3c)
ensure_function(0x00064d40, "geometry_object_profile_object_state_controller_variant_e", 0x00064f50)
ensure_function(0x00064f60, "geometry_object_profile_object_state_controller_variant_f", 0x00065190)
ensure_function(0x000651a0, "geometry_object_profile_object_state_controller_variant_g", 0x00065268)
ensure_function(0x00065270, "geometry_object_profile_object_state_controller_variant_h", 0x00065358)
ensure_function(0x00065360, "geometry_object_profile_object_state_controller_variant_i", 0x000653f8)
ensure_function(0x00065400, "geometry_object_profile_object_state_controller_variant_j", 0x000654b8)
ensure_function(0x000654c0, "geometry_object_profile_object_state_controller_variant_k", 0x0006562c)
ensure_function(0x00065630, "geometry_object_profile_object_state_controller_variant_l", 0x0006577c)
ensure_function(0x00065780, "geometry_object_profile_indexed_transition_variant_ae", 0x00065974)
ensure_function(0x00065980, "geometry_object_profile_indexed_phase_controller_variant_f", 0x00065bc0)
ensure_function(0x00065bd0, "geometry_object_profile_object_state_controller_variant_m", 0x00065ef4)
ensure_function(0x00065f00, "geometry_object_profile_object_state_controller_variant_n", 0x00066210)
ensure_function(0x00066220, "geometry_object_profile_object_state_controller_variant_o", 0x00066414)
ensure_function(0x00066420, "geometry_object_profile_object_state_controller_variant_p", 0x000665f8)
ensure_function(0x00066600, "geometry_object_profile_object_state_controller_variant_q", 0x00066830)
ensure_function(0x00066840, "geometry_object_profile_object_state_controller_variant_r", 0x00066a70)
ensure_function(0x00066a80, "geometry_object_profile_object_state_controller_variant_s", 0x00066b48)
ensure_function(0x00066b50, "geometry_object_profile_object_state_controller_variant_t", 0x00066c0c)
ensure_function(0x00066c10, "geometry_object_profile_object_state_controller_variant_u", 0x00066cb8)
ensure_function(0x00066cc0, "geometry_object_profile_object_state_controller_variant_v", 0x00066d68)
ensure_function(0x00066d70, "geometry_object_profile_phase_controller_variant_p", 0x00066f84)
ensure_function(0x00066f90, "geometry_object_profile_indexed_phase_controller_variant_g", 0x000672b8)
ensure_function(0x000672c0, "geometry_object_profile_indexed_phase_controller_variant_h", 0x000675f8)
ensure_function(0x00067600, "geometry_object_profile_indexed_phase_controller_variant_i", 0x000677f4)
ensure_function(0x00067800, "geometry_object_profile_indexed_phase_controller_variant_j", 0x00067950)
ensure_function(0x00067a30, "geometry_object_profile_indexed_phase_controller_variant_k", 0x00067ba4)
ensure_function(0x00067c90, "geometry_object_profile_phase_controller_variant_q", 0x00067e38)
ensure_function(0x00067e40, "geometry_object_profile_phase_controller_variant_r", 0x00068034)
ensure_function(0x00068040, "geometry_object_profile_phase_controller_variant_s", 0x00068228)
ensure_function(0x00068230, "geometry_object_profile_geometry_bounds_flags_update_variant_e", 0x00068548)
ensure_function(0x0006d130, "geometry_object_profile_phase_selection_controller", 0x0006d38c)
ensure_function(0x0006d390, "geometry_command_packet_writer_variant_a", 0x0006dce0)
ensure_function(0x0006ddb0, "geometry_object_profile_phase_state_controller", 0x0006e0a4)
ensure_function(0x0006e0b0, "geometry_command_packet_writer_variant_b", 0x0006e62c)
ensure_function(0x0006e630, "geometry_motion_threshold_service", 0x0006e6e0)
ensure_function(0x0006e6f0, "geometry_motion_math_dispatch_variant_a", 0x0006e7e4)
ensure_function(0x0006e7f0, "geometry_motion_math_dispatch_variant_b", 0x0006e8e4)
ensure_function(0x0006e8f0, "geometry_motion_math_dispatch_variant_c", 0x0006e93c)
ensure_function(0x0006e940, "geometry_motion_math_dispatch_variant_d", 0x0006ea34)
ensure_function(0x0006ea40, "geometry_motion_math_dispatch_variant_e", 0x0006eb34)
ensure_function(0x0006eb40, "geometry_motion_math_callback_bridge", 0x0006eb54)
ensure_function(0x0006efd0, "geometry_vertex_attribute_packet_renderer", 0x0006efcc)
ensure_function(0x00068550, "geometry_object_profile_geometry_bounds_flags_update_variant_f", 0x0006876c)
ensure_function(0x00068770, "geometry_object_profile_phase_selection_controller_variant_b", 0x00068a3c)
ensure_function(0x00068a40, "geometry_command_packet_writer_variant_c", 0x00069040)
ensure_function(0x00069050, "geometry_object_profile_phase_selection_controller_variant_c", 0x00069460)
ensure_function(0x00069560, "geometry_command_packet_writer_variant_d", 0x00069c54)
ensure_function(0x00069c60, "geometry_object_profile_phase_selection_controller_variant_d", 0x00069f20)
ensure_function(0x00069f30, "geometry_object_profile_match_phase_controller", 0x0006a694)
ensure_function(0x0006a6a0, "geometry_object_profile_phase_selection_controller_variant_e", 0x0006aa5c)
ensure_function(0x0006aa60, "geometry_command_packet_writer_variant_e", 0x0006ae78)
ensure_function(0x0006ae80, "geometry_object_profile_phase_selection_controller_variant_f", 0x0006b3c8)
ensure_function(0x0006b3d0, "geometry_object_transform_motion_controller", 0x0006c768)
ensure_function(0x0006c770, "geometry_object_profile_phase_selection_controller_variant_g", 0x0006cc1c)
ensure_function(0x0006cc20, "geometry_command_packet_writer_variant_f", 0x0006d07c)
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
ensure_function(0x000e9140, "geometry_runtime_event_dispatch", 0x000eaa54)
ensure_function(0x000eaa60, "geometry_event_setup_helper", 0x000ead20)
ensure_function(0x000eada0, "runtime_flag_gate_a", 0x000eaddc)
ensure_function(0x000eade0, "runtime_flag_gate_b", 0x000eae1c)
ensure_function(0x000eae20, "runtime_flag_gate_c", 0x000eae5c)
ensure_function(0x000eae60, "runtime_byte_copy_continuation", 0x000eaea8)
ensure_function(0x000eaeb0, "runtime_format_value", 0x000eaec4)
ensure_function(0x000eaed0, "runtime_format_value_adjusted", 0x000eaf20)
ensure_function(0x000eaf20, "runtime_render_value_string", 0x000eaf34)
ensure_function(0x000eb060, "diagnostic_menu_render", 0x000eb1b8)
ensure_function(0x000eb1c0, "runtime_packed_record_scan", 0x000eb2c0)
ensure_function(0x000eb2c0, "runtime_record_table_init", 0x000eb3a8)
ensure_function(0x000eb3b0, "runtime_record_base_select", 0x000eb450)
ensure_function(0x000eb450, "runtime_record_match_scan_alt", 0x000eb50c)
ensure_function(0x000eb510, "runtime_record_table_reset_copy", 0x000eb5ac)
ensure_function(0x000eb5b0, "runtime_rom_bank_loader_5e", 0x000eb600)
ensure_function(0x000eb600, "runtime_rom_bank_loader_5c", 0x000eb650)
ensure_function(0x000eb650, "runtime_rom_bank_loader_5a", 0x000eb6a0)
ensure_function(0x000eb6a0, "runtime_rom_bank_loader_58", 0x000eb6f0)
ensure_function(0x000eb6f0, "runtime_rom_bank_loader_56", 0x000eb740)
ensure_function(0x000eb740, "runtime_rom_bank_loader_54", 0x000eb790)
ensure_function(0x000eb790, "runtime_rom_bank_loader_52", 0x000eb7e0)
ensure_function(0x000eb7e0, "runtime_rom_bank_loader_50", 0x000eb830)
ensure_function(0x000eb830, "runtime_rom_bank_load_all", 0x000eb89c)
ensure_function(0x000eb8a0, "runtime_packed_record_match_scan", 0x000ebaa8)
ensure_function(0x000ebba0, "runtime_alt_packed_record_scan", 0x000ebc60)
ensure_function(0x000ebc60, "runtime_alt_record_table_init", 0x000ebd20)
ensure_function(0x000ebd20, "runtime_alt_packed_record_scan_b", 0x000ebe20)
ensure_function(0x000ebe20, "runtime_alt_record_table_init_b", 0x000ebf10)
ensure_function(0x000ebf10, "runtime_alt_packed_record_scan_c", 0x000ebfd0)
ensure_function(0x000ebfd0, "runtime_alt_record_table_init_c", 0x000ec090)
ensure_function(0x000ec090, "runtime_alt_packed_record_scan_d", 0x000ec140)
ensure_function(0x000ec140, "runtime_alt_record_table_init_d", 0x000ec1e0)
ensure_function(0x000ec1e0, "runtime_alt_packed_record_scan_e", 0x000ec290)
ensure_function(0x000ec290, "runtime_alt_record_table_init_e", 0x000ec330)
ensure_function(0x000ec330, "runtime_alt_packed_record_scan_f", 0x000ec3e0)
ensure_function(0x000ec3e0, "runtime_alt_record_table_init_f", 0x000ec480)
ensure_function(0x000ec480, "runtime_alt_record_base_select", 0x000ec624)
ensure_function(0x000ec630, "runtime_alt_record_table_copy", 0x000ec69c)
ensure_function(0x000ec6a0, "runtime_alt_packed_record_scan_g", 0x000ec760)
ensure_function(0x000ec760, "runtime_alt_record_table_init_g", 0x000ec820)
ensure_function(0x000ec820, "geometry_event_lookup_table_build", 0x000ec8e8)
ensure_function(0x000ec8f0, "runtime_alt_record_pipeline_dispatch", 0x000ec920)
ensure_function(0x000ec920, "runtime_event_counter_step", 0x000ec940)
ensure_function(0x000ec940, "runtime_event_mode_flag_set", 0x000ec970)
ensure_function(0x000ec970, "runtime_record_checksum_4stride", 0x000ec9c4)
ensure_function(0x000ec9d0, "runtime_record_checksum_3stride", 0x000eca2c)
ensure_function(0x000eca30, "runtime_event_result_publish_a", 0x000eca60)
ensure_function(0x000eca60, "runtime_event_result_publish_b", 0x000eca90)
ensure_function(0x000eca90, "runtime_event_result_publish_c", 0x000ecac0)
ensure_function(0x000ecac0, "runtime_event_result_publish_d", 0x000ecaf0)
ensure_function(0x000ecaf0, "runtime_event_result_publish_e", 0x000ecb20)
ensure_function(0x000ecb20, "runtime_event_result_publish_f", 0x000ecb50)
ensure_function(0x000ecbe0, "diagnostic_result_format", 0x000ecc38)
ensure_function(0x000ecc40, "diagnostic_result_format_compare", 0x000ecc98)
ensure_function(0x000ecd80, "diagnostic_result_menu_render", 0x000ed0c8)
ensure_function(0x000ed0d0, "runtime_record_workspace_reset", 0x000ed1d0)
ensure_function(0x000ed220, "diagnostic_result_service", 0x000ed2e0)
ensure_function(0x000ed2e4, "diagnostic_result_service_fallback", 0x000ed304)
ensure_function(0x000ed320, "diagnostic_input_test_service", 0x000ed43c)
ensure_function(0x000ed5c0, "diagnostic_input_status_render", 0x000ed970)
ensure_function(0x000eda30, "diagnostic_billboard_test_render", 0x000edcfc)
ensure_function(0x000f04d0, "diagnostic_crt_test_service", 0x000f08c0)
ensure_function(0x000f08c0, "diagnostic_crt_pattern_buffer_fill", 0x000f0940)
ensure_function(0x000f0980, "diagnostic_match_time_test_service", 0x000f0b3c)
ensure_function(0x000f1c90, "diagnostic_coin_credit_service", 0x000f1d50)
ensure_function(0x000f1db0, "diagnostic_credit_math_formatter", 0x000f1ec0)
ensure_function(0x000f1f20, "diagnostic_coin_chute_status_render", 0x000f20b0)
ensure_function(0x000f2e20, "diagnostic_bookkeeping_service", 0x000f2ef0)
ensure_function(0x000f33a0, "diagnostic_game_time_statistics_render", 0x000f3a80)
ensure_function(0x000f3ab0, "diagnostic_eeprom_write_confirmation", 0x000f3c10)
ensure_function(0x000f3c50, "diagnostic_test_mode_exit_reset", 0x000f3ca0)
ensure_function(0x000f2940, "diagnostic_bookkeeping_arm_validate", 0x000f2a60)
ensure_function(0x000f2a60, "diagnostic_bookkeeping_arm_credit_a", 0x000f2ae0)
ensure_function(0x000f2ae0, "diagnostic_bookkeeping_arm_credit_b", 0x000f2b60)
ensure_function(0x000f2b60, "diagnostic_bookkeeping_arm_coin", 0x000f2bc0)
ensure_function(0x000f2bc0, "diagnostic_bookkeeping_arm_credit_reset", 0x000f2c20)
ensure_function(0x000f2c20, "diagnostic_bookkeeping_arm_input_a", 0x000f2c90)
ensure_function(0x000f2c90, "diagnostic_bookkeeping_arm_input_b", 0x000f2d00)
ensure_function(0x000f2d00, "diagnostic_bookkeeping_arm_coin_chute_a", 0x000f2d70)
ensure_function(0x000f2d70, "diagnostic_bookkeeping_arm_coin_chute_b", 0x000f2de0)
ensure_function(0x000f2170, "diagnostic_coin_settings_render", 0x000f22f0)
ensure_function(0x000f2770, "diagnostic_coin_input_matrix_render", 0x000f2940)
ensure_function(0x000f19e8, "diagnostic_coin_config_decode", 0x000f1aac)
ensure_function(0x000f23e0, "diagnostic_coin_credit_matrix_builder", 0x000f2650)
ensure_function(0x000f1ac0, "diagnostic_site_status_sync", 0x000f1bc0)
ensure_function(0x000f1bc0, "diagnostic_site_status_fallback", 0x000f1be0)
ensure_function(0x000f14a0, "diagnostic_config_field_16_arm", 0x000f1520)
ensure_function(0x000f1520, "diagnostic_config_field_17_arm", 0x000f15a0)
ensure_function(0x000f15a0, "diagnostic_config_field_18_arm", 0x000f1620)
ensure_function(0x000f1620, "diagnostic_config_field_19_arm", 0x000f16a0)
ensure_function(0x000f16a0, "diagnostic_config_field_1a_arm", 0x000f1720)
ensure_function(0x000f1720, "diagnostic_config_field_1b_arm", 0x000f1750)
ensure_function(0x000f1750, "diagnostic_config_field_1c_arm", 0x000f1780)
ensure_function(0x000f1780, "diagnostic_config_field_1d_arm", 0x000f17b0)
ensure_function(0x000f17b0, "diagnostic_config_field_1f_arm", 0x000f17e0)
ensure_function(0x000f17e0, "diagnostic_config_field_28_arm", 0x000f1810)
ensure_function(0x000f1810, "diagnostic_config_field_20_arm", 0x000f1840)
ensure_function(0x000f1840, "diagnostic_config_field_21_arm", 0x000f1890)
ensure_function(0x000f1890, "diagnostic_config_field_22_arm", 0x000f18c0)
ensure_function(0x000f18c0, "diagnostic_config_field_23_arm", 0x000f1900)
ensure_function(0x000f1900, "diagnostic_config_field_27_arm", 0x000f1930)
ensure_function(0x000f1930, "diagnostic_config_field_24_arm", 0x000f1970)
ensure_function(0x000f1970, "diagnostic_config_field_25_arm", 0x000f19a0)
ensure_function(0x000f19a0, "diagnostic_config_field_26_arm", 0x000f19e0)
ensure_function(0x000d24b0, "startup_status_arm_text_status_init", 0x000d2560)
ensure_function(0x000d2560, "startup_status_arm_profile_dispatch", 0x000d25b0)
ensure_function(0x000d25b0, "startup_status_arm_profile_service", 0x000d25f0)
ensure_function(0x000d0820, "startup_profile_handler_0_geometry_setup", 0x000d0964)
ensure_function(0x000d0d10, "startup_profile_handler_1_geometry_setup", 0x000d0e5c)
ensure_function(0x000d1280, "startup_profile_handler_2_geometry_setup", 0x000d13ac)
ensure_function(0x000d1ab0, "startup_profile_handler_3_geometry_setup", 0x000d1bd8)
ensure_function(0x000de670, "startup_geometry_status_workspace_init", 0x000de988)
ensure_function(0x0006f600, "geometry_fixed_point_record_producer", 0x0006f6f0)
ensure_function(0x0006ece0, "geometry_float_to_fixed_helper", 0x0006ede0)
ensure_function(0x0006f6f0, "geometry_float_transform_helper", 0x0006f900)
ensure_function(0x0006fa40, "geometry_pool64_acquire", 0x0006fa84)
ensure_function(0x0006fa90, "geometry_pool64_release", 0x0006fac4)
ensure_function(0x0006f9e0, "geometry_pool64_reset", 0x0006fa30)
ensure_function(0x0006fad0, "geometry_pool32_reset", 0x0006fb10)
ensure_function(0x0006fb10, "geometry_pool32_acquire", 0x0006fb50)
ensure_function(0x0006fb50, "geometry_pool32_release", 0x0006fb84)
ensure_function(0x0006fb90, "geometry_record_initializer", 0x0006fd50)
ensure_function(0x0006fd50, "geometry_link_release", 0x0006fe70)
ensure_function(0x0006fec0, "geometry_device_command_initialize", 0x0006ff20)
ensure_function(0x0006ff20, "geometry_command_packet_builder", 0x00070000)
ensure_function(0x00070000, "geometry_command_packet_builder_variant_b", 0x000700e0)
ensure_function(0x000700e0, "geometry_command_packet_builder_variant_c", 0x000701a0)
ensure_function(0x000701a0, "geometry_clip_packet_builder", 0x00070970)
ensure_function(0x00070970, "geometry_extended_packet_builder", 0x00070c74)
ensure_function(0x00070c80, "geometry_command_packet_builder_variant_d", 0x00070fc0)
ensure_function(0x00070fc0, "geometry_command_packet_builder_variant_e", 0x00071080)
ensure_function(0x00071080, "geometry_object_match_update", 0x00072050)
ensure_function(0x00072c00, "match_object_state_service", 0x00072ea0)
ensure_function(0x00072ea0, "match_state_result_service", 0x00073490)
ensure_function(0x00073498, "match_result_counter_service", 0x00073500)
ensure_function(0x00073508, "signed_difference_band_classify", 0x000735d0)
ensure_function(0x000735d0, "match_result_state_dispatch", 0x00073618)
ensure_function(0x000736a0, "geometry_profile_handler_0", 0x000737c8)
ensure_function(0x000737c8, "geometry_profile_handler_1", 0x00073900)
ensure_function(0x00073900, "geometry_profile_handler_2", 0x00073a34)
ensure_function(0x00073a34, "geometry_profile_handler_3", 0x00073b68)
ensure_function(0x00073b68, "geometry_profile_handler_4", 0x00073c98)
ensure_function(0x00073c98, "geometry_profile_handler_5", 0x00073dcc)
ensure_function(0x00073dcc, "match_state_handler_6", 0x00073fdc)
ensure_function(0x00073fdc, "match_state_handler_7", 0x00073ffc)
ensure_function(0x00073ffc, "match_state_handler_8", 0x0007402c)
ensure_function(0x0007402c, "match_state_handler_9", 0x0007408c)
ensure_function(0x0007408c, "match_state_handler_10", 0x000740ec)
ensure_function(0x000745bc, "match_state_handler_11", 0x000745e4)
ensure_function(0x000745e4, "match_state_handler_12", 0x0007460c)
ensure_function(0x0007460c, "match_state_handler_13", 0x00074634)
ensure_function(0x00074634, "match_state_handler_14", 0x00074674)
ensure_function(0x00074674, "match_state_handler_15", 0x000746f4)
ensure_function(0x000746f4, "match_state_handler_16", 0x00074754)
ensure_function(0x00074754, "match_state_handler_17", 0x0007479c)
ensure_function(0x0007479c, "match_state_handler_18", 0x000747e4)
ensure_function(0x000747e4, "match_state_handler_19", 0x00074848)
ensure_function(0x00074848, "match_state_default_reject", 0x00074860)
ensure_function(0x00074860, "match_status_transition_update", 0x00074e60)
ensure_function(0x00074e60, "match_transition_state_dispatch", 0x00074ea4)
ensure_function(0x00074ec4, "match_transition_handler_0", 0x00074ef0)
ensure_function(0x00074ef0, "match_transition_handler_1", 0x00074f28)
ensure_function(0x00074f28, "match_transition_handler_2", 0x00074f3c)
ensure_function(0x00074f3c, "match_transition_handler_3", 0x00074f60)
ensure_function(0x00074f60, "match_transition_handler_4", 0x00074fa0)
ensure_function(0x00074fa0, "match_transition_handler_5", 0x00074fc8)
ensure_function(0x00074fc8, "match_transition_handler_6", 0x00075048)
ensure_function(0x00075048, "match_transition_handler_7", 0x0007510c)
ensure_function(0x0007510c, "match_transition_counter_clamp", 0x00075134)
ensure_function(0x00075134, "match_transition_common_update", 0x00075200)
ensure_function(0x00075200, "match_geometry_range_update", 0x00075230)
ensure_function(0x00075230, "match_result_phase_selector", 0x00075300)
ensure_function(0x00075300, "match_phase_advance_update", 0x0007539c)
ensure_function(0x00075404, "match_phase_selector_arm_0", 0x0007540c)
ensure_function(0x0007540c, "match_phase_selector_arm_1", 0x00075414)
ensure_function(0x00075414, "match_phase_selector_arm_2", 0x00075424)
ensure_function(0x00075424, "match_phase_selector_arm_3", 0x0007542c)
ensure_function(0x0007542c, "match_phase_selector_arm_4", 0x00075434)
ensure_function(0x00075434, "match_phase_selector_arm_5", 0x00075450)
ensure_function(0x00075450, "match_phase_substate_dispatch", 0x00075474)
ensure_function(0x00075cf0, "match_phase_substate_common_update", 0x00075cf8)
ensure_function(0x00075cf8, "match_phase_substate_counter_return", 0x00075d08)
ensure_function(0x00075d08, "match_phase_counter_dispatch", 0x00075d60)
ensure_function(0x00075bbc, "match_phase_secondary_selector", 0x00075c1c)
ensure_function(0x00075c58, "match_phase_late_selector", 0x00075cb4)
ensure_function(0x00075cb4, "match_phase_late_arm_0", 0x00075cbc)
ensure_function(0x00075cbc, "match_phase_late_arm_1", 0x00075cc4)
ensure_function(0x00075cc4, "match_phase_late_arm_2", 0x00075cdc)
ensure_function(0x00075cdc, "match_phase_late_arm_3", 0x00075ce4)
ensure_function(0x00075ce4, "match_phase_late_arm_4", 0x00075cf0)
ensure_function(0x00075c1c, "match_phase_secondary_arm_0", 0x00075c24)
ensure_function(0x00075c24, "match_phase_secondary_arm_1", 0x00075c2c)
ensure_function(0x00075c2c, "match_phase_secondary_arm_2", 0x00075c34)
ensure_function(0x00075c34, "match_phase_secondary_arm_3", 0x00075c3c)
ensure_function(0x00075c3c, "match_phase_secondary_arm_4", 0x00075c58)
ensure_function(0x00075d60, "match_phase_counter_arm_0", 0x00075d68)
ensure_function(0x00075d68, "match_phase_counter_arm_1", 0x00075d70)
ensure_function(0x00075d70, "match_phase_counter_arm_2", 0x00075d78)
ensure_function(0x00075d78, "match_phase_counter_arm_3", 0x00075d80)
ensure_function(0x00075d80, "match_phase_counter_arm_4", 0x00075d88)
ensure_function(0x00075d88, "match_phase_counter_default", 0x00075d90)
ensure_function(0x000754ac, "match_phase_substate_arm_0", 0x000754b4)
ensure_function(0x000754b4, "match_phase_substate_arm_1", 0x000754bc)
ensure_function(0x000754bc, "match_phase_substate_arm_2", 0x000754c4)
ensure_function(0x000754c4, "match_phase_substate_arm_3", 0x000754cc)
ensure_function(0x000754cc, "match_phase_substate_arm_4", 0x000754e4)
ensure_function(0x000754e4, "match_phase_substate_default", 0x000754e8)
ensure_function(0x00075d90, "stage_selector_setup", 0x000760c0)
ensure_function(0x000761b0, "geometry_object_threshold_query", 0x00076240)
ensure_function(0x00092730, "geometry_fifo_packet_stateful_site_a", 0x00092824)
ensure_function(0x00093240, "geometry_fifo_float_prologue", 0x000933b0)
ensure_function(0x00092830, "geometry_fifo_packet_template_site_a", 0x000928d4)
ensure_function(0x000933b0, "geometry_fifo_packet_stateful_site_b", 0x000934a4)
ensure_function(0x000934b0, "geometry_fifo_packet_template_site_b", 0x00093554)
ensure_function(0x00093560, "geometry_fifo_packet_sequencer", 0x000936f0)
ensure_function(0x00086240, "stage_post_setup", 0x00086624)
ensure_function(0x00086630, "stage_bucket_helper", 0x000866b0)
ensure_function(0x000866c0, "stage_record_tables_initialize", 0x00086958)
ensure_function(0x000881b8, "stage_slot_update", 0x000881f8)
ensure_function(0x0008d400, "geometry_batch_packet", 0x0008d5c0)
ensure_function(0x0008d5d0, "geometry_indexed_packet", 0x0008d6b8)
ensure_function(0x0008d850, "geometry_indexed_batch", 0x0008da54)
ensure_function(0x0008da60, "geometry_indexed_packet_variant", 0x0008dd30)
ensure_function(0x0008dd40, "geometry_object_packet", 0x0008dfb0)
ensure_function(0x0008dfc0, "geometry_object_packet_alt", 0x0008e300)
ensure_function(0x0008e310, "geometry_packet_tail_8e310", 0x0008e490)
ensure_function(0x0008e4a0, "geometry_diagnostic_packet_8e4a0", 0x0008ea00)
ensure_function(0x0008ea00, "geometry_diagnostic_variant_8ea00", 0x0008f004)
ensure_function(0x0008f010, "geometry_diagnostic_variant_b_8f010", 0x0008f1f0)
ensure_function(0x0008f1f0, "geometry_diagnostic_variant_c_8f1f0", 0x0008f620)
ensure_function(0x0008f620, "geometry_diagnostic_variant_d_8f620", 0x0008f810)
ensure_function(0x0009b288, "command_record_write", 0x0009b2f0)
ensure_function(0x000bd5a8, "startup_table_copy", 0x000bd6a0)
ensure_function(0x000bd6b8, "object_table_reset", 0x000bd708)
ensure_function(0x000bd730, "object_dispatch_prelude", 0x000bd7ec)
ensure_function(0x000bd810, "object_dispatch_prelude_alt", 0x000bd8e0)
ensure_function(0x000bf2f0, "geometry_constant_packet", 0x000bf3e0)
ensure_function(0x000bd8e0, "object_dual_admission", 0x000bddb0)
ensure_function(0x0009c050, "geometry_descriptor_select", 0x0009c2d0)
ensure_function(0x000bedf0, "geometry_table_select_bcc", 0x000beed0)
ensure_function(0x000beee0, "geometry_table_select_bcd", 0x000befc0)
ensure_function(0x000befd0, "geometry_table_select_bce", 0x000bf0b0)
ensure_function(0x000bf0c0, "object_last_active_row", 0x000bf120)
ensure_function(0x000bece0, "object_pair_scan", 0x000bedd0)
ensure_function(0x000bf120, "object_active_row_count", 0x000bf180)
ensure_function(0x000bf180, "object_dispatch_context_a", 0x000bf1bc)
ensure_function(0x000bf1c0, "object_dispatch_context_b", 0x000bf1fc)
ensure_function(0x000bf200, "object_dispatch_context_c", 0x000bf23c)
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
label(0x0001cc40, "ui_tile_writer",
      "Normalizes the incoming byte, routes controls through 0x1cbb8, and stores printable tiles at 0x01000000 with bit 15 and low-halfword 0x504cf4 attributes.")
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
ensure_function(0x00028840, "geometry_profile_constant_selector", 0x0002898c)
ensure_function(0x00028418, "geometry_initial_handshake", 0x00028464)
ensure_function(0x00028d08, "geometry_register_clear", 0x00028d24)
ensure_function(0x00028548, "texture_initializer", 0x000285f4)
ensure_function(0x00028120, "texture_loader_profile_setup", 0x000281dc)
ensure_function(0x000281f0, "texture_profile_setup", 0x00028268)
ensure_function(0x00028270, "texture_profile_match", 0x000282a4)
ensure_function(0x00027e50, "texture_decompressor", 0x000280bc)
ensure_function(0x00028d30, "geometry_auxiliary_submit_select", 0x00028d7c)

# Static hardware/data references used by the annotated notes.
label(0x00028170, "texture_load_done_message")
label(0x0002812c, "texture_load_message")
label(0x0002a4e0, "command_mode_validator")
label(0x0006ece0, "geometry_float_to_fixed_helper",
      "Coordinate lookup producer: truncates and bounds-checks two float inputs, submits opcode 0x41 with the 512x512 half-coordinate index, copies the selected 20-byte record's two output halfwords, and emits the shared 0x35 continuation before its final FIFO read.")
label(0x000bf0c0, "packed_bit_search_helper")
label(0x000e1f20, "text_byte_to_tile_planes")
label(0x000e1fb0, "text_byte_to_tile_planes_offset_100",
      "Same 64-triplet expansion as 0xe1f20, writing each plane into the +0x100 destination bank.")
label(0x000f5058, "runtime_prng_next",
      "Advances persistent state at 0x5785d0 with multiplier 0x5d588b65, folds the 64-bit product using low-word bit 31 as the chkbit carry, clears bit 31, stores the new state, and returns it to callers such as the slot-20 failure bridge.")
ensure_function(0x000f50a8, "runtime_prng_seed", 0x000f50bc)
label(0x000f50a8, "runtime_prng_seed",
      "Stores the caller-supplied 32-bit value into persistent PRNG state at 0x5785d0 and returns through the saved continuation.")
ensure_function(0x000f50c0, "text_string_length", 0x000f50f4)
label(0x000f50c0, "text_string_length",
      "Counts bytes from the caller pointer through the first NUL and returns the NUL-terminated length without modifying the string.")
label(0x000f5d40, "memcpy_aligned")
label(0x000f5c58, "memcmp_bytes")
label(0x000f5e80, "memmove_overlap_copy",
      "Overlap-aware copy sibling: checks source/destination interval overlap, delegates disjoint ranges to 0xf5d40, and copies overlapping ranges backward when destination is above source.")
label(0x000f5100, "text_string_render_dispatch")
label(0x000f5190, "text_format_parser_core",
      "Parses one formatter byte, bounds the dispatch index to 0..120, and jumps through the exact 121-entry table at 0xf5210; unsupported slots converge at 0xf5bf4.")
label(0x000f5210, "text_format_dispatch_table",
      "121-entry formatter table: index 0 emits an ordinary byte; sparse conversion handlers route to 0xf53f4, 0xf5408, 0xf5410, 0xf546c, 0xf5474, 0xf547c, 0xf5544, 0xf554c, 0xf5588, 0xf5590, 0xf5598, 0xf55a0, 0xf561c, 0xf5620, 0xf5688, 0xf5790, 0xf5800, 0xf5804, 0xf5860, 0xf58bc, 0xf5954, 0xf5958, 0xf59b4, and 0xf59bc; all other entries use 0xf5bf4.")
label(0x0002a430, "short_countdown_delay")
label(0x0002a458, "command_queue_space_check")
label(0x0002a4a8, "command_queue_byte_push")
label(0x0002a5f0, "command_mode_validator_alt")
label(0x0002a990, "geometry_command_packet_submit")
label(0x00079050, "randomized_record_state_dispatch",
      "Receives an object pointer in g0, loads the related pointer from object + 0x74 into r4, advances the 0x5785d0 PRNG through 0xf5058 (returned in g0 for the state arms), then dispatches the object state through 0x7907c; the reconstructed wrapper remains capture-bounded until pool rotation is traced.")
ensure_function(0x00079d60, "secondary_object_state_dispatch", 0x0007a218)
ensure_function(0x0007a3e0, "route_head_7a3e0", 0x0007a438)
label(0x0007a3e0, "route_head_entry",
      "Own state 8 takes the mode-11 state-8 route; other states continue through peer-state and ratio-head selection.")
label(0x0007a408, "route_head_peer_state_split",
      "Peer states 0 and 3 enter the ratio comparison at 0x7a504; otherwise own states 1, 3, 4, and 5 enter the ratio path and the remaining states take 0x7a4a8.")
label(0x0007a438, "route_head_ratio_arm",
      "Begins the mode-1 ratio comparison using the four sign-extended +0x1d0/+0x1d8 halfword values from own and peer records.")
ensure_function(0x0007a318, "transition_setup_7a318", 0x0007a3d0)
ensure_function(0x0007a9f0, "transition_route_7a9f0", 0x0007ad88)
ensure_function(0x0007b430, "transition_route_7b430", 0x0007b46c)
ensure_function(0x0007b46c, "transition_packet_body_7b46c", 0x0007b89c)
label(0x0007b46c, "transition_packet_body_7b46c_entry",
      "Non-sentinel 0x7b430 continuation: emits paired command-29/30 requests using the related record at object +0x74 and the 0x505060 table-derived record.")
label(0x0007b6a0, "transition_packet_body_7b46c_response_compare",
      "Compares response-derived signed bands, selects the +/-0x4000 coordinate frame, and classifies the object-relative difference through 0x73508.")
label(0x0007b744, "transition_packet_body_7b46c_table_exit",
      "Publishes action 10 and a 0x72630 table-derived transition, or follows the 0x728d0 selector override path.")
label(0x0007b7e4, "transition_packet_body_7b46c_global_tail",
      "Applies the final status/transition/action gates using 0x504da4, 0x504dc8, 0x504dc0, and object state 7.")
ensure_function(0x0007bf10, "transition_route_7bf10", 0x0007bf58)
ensure_function(0x0007bf58, "transition_packet_body_7bf58", 0x0007c464)
label(0x0007bf58, "transition_packet_body_7bf58_entry",
      "Non-sentinel 0x7bf10 continuation: emits the related-record command packet from table base 0x505060 and preserves the extra 0x504d84 status tail.")
label(0x0007c03c, "transition_packet_body_7bf58_state_gate",
      "Uses linked-record state 5/4 to select the 0x41200000 adjustment before the command-29/30 packet sequence.")
label(0x0007c218, "transition_packet_body_7bf58_response_compare",
      "Compares response-derived bands and routes either to the 0x726c0 table transition or the expanded command packet.")
label(0x0007c424, "transition_packet_body_7bf58_global_tail",
      "Applies the final 0x504d98/0x504da4/0x504dc8/0x504dc0 gate before returning.")
ensure_function(0x0007c470, "transition_route_7c470", 0x0007c4a8)
label(0x0007c470, "transition_route_7c470_entry",
      "Third sentinel/state sibling: states 2 and 7 call 0x78740, other states call 0x786d0, and non-sentinel selectors continue at packet arm 0x7c4a8.")
ensure_function(0x0007c4a8, "transition_packet_body_7c4a8", 0x0007c7a4)
label(0x0007c4a8, "transition_packet_body_7c4a8_entry",
      "Non-sentinel 0x7c470 continuation: mirrors the paired command-29/30 packet setup using table base 0x505060 and the related record at object +0x74.")
label(0x0007c6d8, "transition_packet_body_7c4a8_response_compare",
      "Compares response-derived signed bands and selects the +/-0x4000 coordinate frame before the 0x73508 classification and 0x72630 transition lookup.")
label(0x0007c7a8, "transition_packet_body_7c4a8_followup",
      "Invokes the shared follow-up packet helper after the first packet arm rejects its response-band condition.")
ensure_function(0x0007c7b0, "transition_packet_followup_7c7b0", 0x0007cb58)
label(0x0007c7b0, "transition_packet_followup_7c7b0_entry",
      "Follow-up packet helper: selects related-record versus 0x505060 table inputs from the 0x504e20 pair and emits the command-29/30 response sequence.")
label(0x0007c8f0, "transition_packet_followup_state_gate",
      "Applies the mode/control, linked-record state, 0x504e4c, and related-selector predicates before status/transition/action-20 promotion.")
label(0x0007c998, "transition_packet_followup_override_tail",
      "Publishes selector state 3, action 20, caller g14 as 0x504d94, and status 1 on the matched override arm.")
ensure_function(0x0007cb60, "transition_followup_gate_7cb60", 0x0007cbc0)
label(0x0007cb60, "transition_followup_gate_entry",
      "Dispatches the post-packet comparison: timing/selector rejection returns through 0x783c8, the accepted arm calls 0x7c7b0, and the clear arm calls 0x82800.")
label(0x0007cb84, "transition_followup_gate_selector_bound",
      "Selectors through 7 return through the action-5 wrapper; only selectors above 7 reach the final converted-value comparison.")
label(0x0007cbb0, "transition_followup_gate_followup_call",
      "Accepted final comparison calls the related-record follow-up helper at 0x7c7b0.")
label(0x0007cb9c, "transition_followup_gate_state_handler",
      "Clear final comparison loads object state at +0x64, calls 0x82800, and stores the returned state value at 0x504d80.")
ensure_function(0x0007cc50, "transition_mode_gate_7cc50", 0x0007ce0c)
label(0x0007cc50, "transition_mode_gate_entry",
      "Requires mode bit 1; when clear, delegates to the 0x7a3e0 route head, otherwise converts 0x504e0e and compares it with 0x504d60.")
label(0x0007ce40, "transition_mode_gate_action10",
      "Timing-passed arm calls the shared action-10 wrapper at 0x78408 and then tests the 0x504da4/0x504dc8 controls.")
label(0x0007ce74, "transition_mode_gate_periodic_selector",
      "When both controls equal 1 and the 0x5024e8 remainder is at most 59, publishes selector state 3.")
label(0x0007ce84, "transition_mode_gate_action30",
      "Timing-clear arm enters the shared tail that publishes status 1, selector 3, and action 30 without changing the transition field.")
ensure_function(0x0007ce10, "transition_mode2_gate_7ce10", 0x0007ceac)
label(0x0007ce10, "transition_mode2_gate_entry",
      "Requires mode bit 2; when clear, delegates to 0x7a3e0, otherwise compares converted 0x504e0e timing against 0x504d60.")
label(0x0007ce40, "transition_mode2_gate_action10",
      "Timing-passed arm calls 0x78408 and checks the 0x504da4/0x504dc8 controls before the periodic selector test.")
label(0x0007ce74, "transition_mode2_gate_periodic_selector",
      "Both controls equal 1 and a 0x5024e8 remainder at most 59 publish selector state 3.")
label(0x0007ce84, "transition_shared_action30_tail",
      "Shared timing-clear tail writes status 1, selector 3, and action 30 without changing the transition field.")
ensure_function(0x0007ceb0, "transition_mode5_route_7ceb0", 0x0007cfd8)
label(0x0007ceb0, "transition_mode5_route_entry",
      "Tests mode bit 5 and loads the related record at object +0x74; clear mode selects the action-30 coordinate/global path, while set mode enters the timing/table path.")
label(0x0007ceec, "transition_mode5_table_action10",
      "Timing-table arm loads 0x72840, publishes action 10, and upgrades control 1 to transition 2/action 25.")
label(0x0007cf34, "transition_mode5_coordinate_path",
      "Mode-clear continuation classifies the related/current coordinate difference for object state 3, or uses global selector 0x504d68 otherwise.")
label(0x0007cfb0, "transition_mode5_action30_tail",
      "Publishes the 0x72780 table result, action 30, and status 1 before returning.")
ensure_function(0x0007cfe0, "transition_mode5_dispatch_7cfe0", 0x0007d068)
label(0x0007cfe0, "transition_mode5_dispatch_entry",
      "Mode bit 5 calls the existing 0x79d60 secondary dispatcher and publishes status 1; clear mode proceeds through the 0x504e0c timing comparison.")
label(0x0007d008, "transition_mode5_dispatch_wrapper",
      "Timing-clear arm calls the shared wrapper at 0x78408.")
label(0x0007d010, "transition_mode5_dispatch_action10",
      "Timing-table arm loads 0x72840, publishes action 10, and control 1 upgrades transition to 2/action 25.")
label(0x0007d058, "transition_mode5_dispatch_secondary",
      "Mode-bit-5 arm calls 0x79d60 and then writes status 1.")
ensure_function(0x0007d100, "transition_mode1_route_7d100", 0x0007d1ec)
label(0x0007d100, "transition_mode1_route_entry",
      "Mode bit 1 delegates to 0x7a3e0; clear mode enters the 0x504e0e/0x504d60 timing split.")
label(0x0007d138, "transition_mode1_route_wrapper",
      "Timing wrapper arm calls 0x78408, then gates transition 2/action 30 on control 1 and the post-call mode bit.")
label(0x0007d184, "transition_mode1_route_table",
      "Timing table arm loads 0x72840 and initializes action 10; control 1 or the bounded selector test enters the transition-2/action-30 tail.")
label(0x0007d1c0, "transition_mode1_route_promotion_tail",
      "Publishes transition 2/action 30 and writes status 1 unless the object state is 7.")
ensure_function(0x0007d1f0, "state_byte_pair_scan_7d1f0", 0x0007d358)
ensure_function(0x0007d670, "state_route_select_7d670", 0x0007d7f4)
ensure_function(0x0007dcc0, "state_byte_window_7dcc0", 0x0007dd60)
ensure_function(0x0007e390, "state_geometry_descriptor_7e390", 0x0007e440)
ensure_function(0x0007e440, "state_geometry_packet_prefix_7e440", 0x0007e5e8)
ensure_function(0x0007ea10, "state31_initializer_7ea10", 0x0007eab0)
ensure_function(0x0007f4d0, "transition_scan_7f4d0", 0x0007f5ec)
ensure_function(0x0007fca0, "transition_precondition_7fca0", 0x0007fd24)
ensure_function(0x00080710, "transition_route_80710", 0x000807d0)
ensure_function(0x000810d0, "transition_mode_route_810d0", 0x000811b8)
ensure_function(0x00081120, "transition_mode_route_81120", 0x000811b8)
ensure_function(0x0008168c, "transition_status_tail_8168c", 0x000816cc)
ensure_function(0x00081e60, "state_dispatch_81e60", 0x00081f54)
ensure_function(0x00081f60, "timing_selector_81f60", 0x00082038)
ensure_function(0x00082ae0, "state_scheduler_gate_82ae0", 0x00082b38)
ensure_function(0x00082b38, "state_scheduler_dispatch_82b4c", 0x00082c08)
ensure_function(0x00082c08, "state_scheduler_handler_82c08", 0x00082c18)
ensure_function(0x00082c18, "state_scheduler_control_handler_82c18", 0x00082c28)
ensure_function(0x00082c28, "state_scheduler_control_handler_82c28", 0x00082c38)
ensure_function(0x00082c38, "state_scheduler_control_handler_82c38", 0x00082c54)
ensure_function(0x00082c54, "state_scheduler_control_handler_82c54", 0x00082c60)
ensure_function(0x00082c60, "state_scheduler_service_call_82c60", 0x00082c6c)
ensure_function(0x00082c6c, "state_scheduler_handler_82c6c", 0x00082cb0)
ensure_function(0x00082cc0, "state_scheduler_constant_handlers_82cc0", 0x00082ce8)
ensure_function(0x00082ce8, "state_scheduler_state4_handlers_82ce8", 0x00082d18)
ensure_function(0x00082d18, "state_scheduler_handler_82d18", 0x00082d34)
ensure_function(0x00082db0, "state_service_dispatch_82db0", 0x00082df8)
ensure_function(0x00082e40, "state_service_handler_82e40", 0x00082e64)
ensure_function(0x00082ea0, "state_service_handler_82ea0", 0x00082ed4)
ensure_function(0x00082ed4, "state_service_mod8_handlers_82ed4", 0x00082f10)
ensure_function(0x00082f6c, "state_service_handler_82f6c", 0x00082f84)
ensure_function(0x00082f84, "state_service_random_mod7_82f84", 0x00082f90)
ensure_function(0x00082f90, "state_service_high_dispatch_82f90", 0x00082fdc)
ensure_function(0x00082fac, "state_service_shared_dispatch_82fac", 0x00082fdc)
ensure_function(0x00082fdc, "state_service_shared_handler_prefix_82fdc", 0x000830c0)
ensure_function(0x000830c0, "state_service_postprocess_830c0", 0x00083108)
ensure_function(0x00083110, "state_scheduler_early_gate_83110", 0x00083148)
ensure_function(0x000834b0, "state_scheduler_early_gate_834b0", 0x000834e4)
ensure_function(0x000835f0, "state_scheduler_early_gate_835f0", 0x00083624)
ensure_function(0x00083624, "state_scheduler_state5_status_prefix_83624", 0x000836d0)
ensure_function(0x00083750, "state_scheduler_nonstate_status_prefix_83750", 0x000837cc)
ensure_function(0x00083884, "state_scheduler_state5_status_branch_83884", 0x000839a8)
ensure_function(0x00083850, "state_scheduler_early_gate_83850", 0x00083884)
ensure_function(0x00083f50, "state_scheduler_early_gate_83f50", 0x00083f84)
ensure_function(0x000840b0, "state_scheduler_early_gate_840b0", 0x000840e8)
ensure_function(0x000839a8, "state_scheduler_status_leaf_839a8", 0x00083ac0)
ensure_function(0x00083148, "state_scheduler_status_path_83148", 0x00083300)
ensure_function(0x00083568, "state_scheduler_quadword_adjust_83568", 0x000835e0)
ensure_function(0x000836d0, "state_scheduler_mod5_status_table_836d0", 0x00083750)
ensure_function(0x00083310, "state_scheduler_early_gate_83310", 0x00083348)
ensure_function(0x00083348, "state_scheduler_ratio_prefix_83310", 0x000833dc)
ensure_function(0x000833dc, "state_scheduler_ratio_handlers_833dc", 0x00083428)
ensure_function(0x0008342c, "state_scheduler_remainder_handler_8342c", 0x000834a8)
ensure_function(0x00082d74, "state_scheduler_tail_82d74", 0x00082da4)
ensure_function(0x00082040, "state_action_dispatch_82040", 0x00082088)
ensure_function(0x00082600, "state_random_status_82600", 0x00082650)
ensure_function(0x00082650, "state_status_prefix_82650", 0x000826b0)
ensure_function(0x00082800, "state_handler_dispatch_82800", 0x00082840)
ensure_function(0x00082840, "state_handler_status_82840", 0x00082958)
ensure_function(0x00082954, "state_handler_admission_82954", 0x00082a10)
ensure_function(0x00082a10, "state_handler_commit_82a10", 0x00082aac)
ensure_function(0x00082aac, "state_handler_override_82aac", 0x00082ae0)
ensure_function(0x00082df8, "state_service_mod4_handler_82df8", 0x00082e0c)
ensure_function(0x00082e0c, "state_service_mod4_handler_82e0c", 0x00082e40)
ensure_function(0x00082e64, "state_service_handler_82e64", 0x00082ea0)
label(0x00079d60, "secondary_object_state_dispatch",
      "Ten-entry object-state dispatcher through the table at 0x79d8c; state-arm predicates remain separate, while the common exits publish transitions 13, 14, and 15.")
label(0x00079d8c, "secondary_dispatch_state_table",
      "Ten target addresses for object states 0 through 9: 0x79db4, 0x79e10, 0x79e8c, 0x79ef4, 0x79f5c, 0x79ff4, 0x7a098, 0x7a150, 0x7a204, and 0x7a214.")
label(0x0007a080, "secondary_dispatch_exit_15")
label(0x0007a11c, "secondary_dispatch_exit_14")
label(0x0007a1f4, "secondary_dispatch_exit_13")
label(0x0007a204, "secondary_dispatch_state_8_exit_13")
label(0x0007a214, "secondary_dispatch_return")
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
label(0x0001c7d0, "paired_video_lane_expand",
      "Consumes eight source bytes per block, expands each bit into a color-A nibble pattern, multiplies by the low-byte color-B value for the carry recurrence, rotates the packed word by 16 bits, and stores eight destination words per block.")
label(0x0001c890, "packed_halfword_nibble_reduce",
      "Consumes one source halfword per iteration, uses its eight 2-bit fields to select low nibbles from the masked lookup word 0x0f0f0f0f, sums the eight nibbles, and stores one result word.")
label(0x0001ccf8, "video_command_byte_write")
label(0x0001d270, "text_two_row_pair_writer",
      "Subtracts 0x30, selects a nibble-indexed table window at 0x2ea1dd0, writes two adjacent bit-15-forced halfwords on each of two tile rows, and advances the text column by two through column 61.")
label(0x0001d310, "text_glyph_render_core")
label(0x0009e050, "geometry_record_upload_helper")
label(0x0001bb90, "text_bitplane_unpack")
label(0x0001bc20, "asset_halfword_byte_swap_copy",
      "Signed-guards the halfword count, then reverses each source halfword's byte lanes into the destination with 2-byte source/destination strides.")
label(0x0001bc90, "asset_tiled_row_copy",
      "Signed-guards the row count, calls 0xf5d40 once per row with halfwords*2 bytes, advances the destination by 0x80 bytes, and advances the source by the copied row width.")
label(0x0001bda0, "startup_asset_transfer_loader",
      "Selects the zero or alternate profile from g0, expands fixed asset blocks through 0x1bb90, byte-swaps bulk assets through 0x1bc20, and joins the shared fill/color-table transfer tail.")
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
label(0x0006fec0, "geometry_device_command_initialize",
      "Selector-zero geometry control pulse: writes 0x303 to 0x800030, then the paired 0x80/0x1f40204 store at 0x804000/0x804004 and 0xf80140 to 0x804008, 0x80400c, and 0x804000 twice.")
label(0x000027d8, "indirect_return_trampoline")
label(0x00073508, "signed_difference_band_classify",
      "Classifies the low 16 bits of a signed difference into ten inclusive bands (0..4 for nonnegative values, 5..9 for negative values); callers use the result as a profile/status table index.")
label(0x0007a318, "transition_setup_7a318",
      "Callback-returning setup reached from the 0x7802c action arm: control gate 0x504dc8 == 1 publishes 1 to 0x504d84 and 0x504d98; object states 1,2,4,5,7 publish the cursor-clamped value to 0x504db8, while other states select 12 or 13 at 0x504d94 through the literal-first unsigned cmpobl.")
label(0x0007a9f0, "transition_route_7a9f0",
      "Initializes 0x504db8 to 10, calls timing route 0x786d0 when 0x504e24 is the -1 sentinel or 0x504dc0 <= 99, and otherwise enters the 0x505060 packet-record path; packet arithmetic remains a separate boundary.")
label(0x0007b430, "transition_route_7b430",
      "When 0x504e20 is the -1 sentinel, object states 2 and 7 call 0x78740 and all other states call 0x786d0; non-sentinel values enter the 0x505060 packet path after reading object +0x74.")
label(0x0007bf10, "transition_route_7bf10",
      "When 0x504e20 is the -1 sentinel, object states 2 and 7 call 0x78740 and all other states call 0x786d0, then publish 1 to 0x504d84; non-sentinel values enter the 0x505060 packet path after reading object +0x74.")
label(0x0007d1f0, "state_byte_pair_scan_7d1f0",
      "Scans one byte at 0x504da0+0x9a and one at +0x98 for a nonzero value within the inclusive reference..reference+5 band; the 0x94..0x96 scan has no retained result. A shared gate then checks the 0x504d9c/0x504d94/0x504db4/base-offset and object-state predicates before the 0x7d358 selector table.")
label(0x0007d358, "state_selector_table_7d358",
      "Ten-entry state-handler table: states 0..9 branch to 0x7d380, 0x7d390, 0x7d3a4, 0x7d404, 0x7d4e8, 0x7d568, 0x7d5a4, 0x7d5dc, 0x7d604, and 0x7d660.")
ensure_function(0x0007d380, "state_selector_body_0_7d380", 0x0007d390)
label(0x0007d380, "state_selector_body_0_7d380",
      "State-0 body: mode bit 1 selects shared target 0x7d5f4; clear mode returns through 0x7d644.")
ensure_function(0x0007d390, "state_selector_body_1_7d390", 0x0007d3a4)
label(0x0007d390, "state_selector_body_1_7d390",
      "State-1 body: mode bit 1 selects 0x7d5f4, otherwise mode bit 2 selects 0x7d4b4, with 0x7d644 as fallback.")
ensure_function(0x0007d3a4, "state_selector_body_2_7d3a4", 0x0007d404)
label(0x0007d3a4, "state_selector_body_2_7d3a4",
      "State-2 body: mode bit 1 selects 0x7d5f4; clear mode rejects the coordinate band to 0x7d654, otherwise 0x5024e8 modulo 600 selects 0x7d644 through 449 and 0x7d654 above it.")
ensure_function(0x0007d404, "state_selector_body_3_7d404", 0x0007d4c4)
label(0x0007d404, "state_selector_body_3_7d404",
      "State-3 body: modulo-600 values through 299 return to 0x7d644; accepted control/coordinate predicates publish selector 3 at 0x7d4b4, otherwise the shared tail chooses 0x7d5f4 or 0x7d654 from g3/g13, control 0x504dc8, and mode bit 1.")
ensure_function(0x0007d4e8, "state_selector_body_4_7d4e8", 0x0007d568)
label(0x0007d4e8, "state_selector_body_4_7d4e8",
      "State-4 body: mode bit 1 selects 0x7d5f4; clear mode rejects the coordinate band or g3/g13/control gate to 0x7d654, otherwise modulo 600 through 199 selects 0x7d644 and larger values select 0x7d654.")
ensure_function(0x0007d568, "state_selector_body_5_7d568", 0x0007d5a4)
label(0x0007d568, "state_selector_body_5_7d568",
      "State-5 body: modulo 600 values through 119, missing g3/g13, control != 1, or clear mode bit 1 return to 0x7d644; the fully matched arm reaches 0x7d5f4.")
ensure_function(0x0007d5a4, "state_selector_body_6_7d5a4", 0x0007d5dc)
label(0x0007d5a4, "state_selector_body_6_7d5a4",
      "State-6 body: initial or post-control mode bit 1 selects 0x7d5f4; control != 1 returns to 0x7d644, otherwise the converted 0x504df8 comparison selects 0x7d4b4 or 0x7d644.")
ensure_function(0x0007d5dc, "state_selector_body_7_7d5dc", 0x0007d604)
label(0x0007d5dc, "state_selector_body_7_7d5dc",
      "State-7 body: mode bit 1 and control 0x504dc8 == 1 publish selector 2 and reach 0x7d5f4; either rejection returns through 0x7d654.")
ensure_function(0x0007d604, "state_selector_body_8_7d604", 0x0007d660)
label(0x0007d604, "state_selector_body_8_7d604",
      "State-8 body: mode bit 2 with control 0x504dc8 == 1 reaches selector-3 target 0x7d4b4; otherwise modulo 600 through 299 returns to 0x7d644 and larger values use 0x7d654.")
label(0x0007d4b4, "state_selector_shared_tail_3",
      "Shared selector tail writes selector value 3 to 0x504d98 and returns.")
label(0x0007d5f4, "state_selector_shared_tail_2",
      "Shared selector tail writes selector value 2 to 0x504d98 and returns.")
label(0x0007d644, "state_selector_shared_tail_1",
      "Shared selector tail writes selector value 1 to 0x504d98 and returns.")
label(0x0007d654, "state_selector_shared_tail_continuation",
      "Shared selector tail stores caller g14 to 0x504d98 and returns.")
label(0x0007d670, "state_route_select_7d670",
      "Scans seven six-byte records at 0x505060, skips zero +4 signed halfwords, selects the first minimum signed +2 halfword, and falls back to status 11 when 0x504d70 <= 4 or 10 otherwise; selected records branch to packet builder 0x7d7f4 and continue into the 0x884000 command path.")
label(0x0007d7f4, "state_route_selected_packet_builder",
      "Selected record path indexes the winning six-byte record from 0x505060 and emits its command-29/30 coordinate packet through 0x884000.")
ensure_function(0x0007d7f4, "state_selected_packet_builder_7d7f4", 0x0007d914)
label(0x0007d7f4, "state_selected_packet_builder_entry",
      "Computes selected-index times six from table 0x505060, reads record offsets +0/+2/+4, and begins the fixed command-10/29/30 FIFO sequence.")
label(0x0007d83c, "state_selected_packet_builder_command30",
      "Emits command 30 and the second coordinate payload after the command-29 response.")
label(0x0007d900, "state_selected_packet_builder_result_lookup",
      "Classifies the final signed difference through 0x73508, indexes 0x72630, and stores the result at 0x504d94.")
label(0x0007db80, "state_followup_handler_table_7db80",
      "Ten-entry follow-up handler table: indices 0/1 -> 0x7dba8, 2/3 -> 0x7dbb8, 4 -> 0x7dbc8, 5 -> 0x7dbd8, 6 -> 0x7dbf4, 7 -> 0x7dc04, 8 -> 0x7dc98, and 9 -> 0x7dca8.")
label(0x0007db70, "state_followup_dispatch_7db70",
      "Bounds selector g6 against the ten-entry table at 0x7db80; valid selectors branch through the table and larger selectors fall back to 0x7dca8.")
label(0x0007da8c, "state_followup_primary_table_7da8c",
      "24-entry primary follow-up table dispatches the earlier selector arms and the distinct handlers at 0x7daf0, 0x7db00, 0x7db1c, 0x7db2c, and 0x7db54.")
label(0x0007d920, "state_followup_producer_7d920",
      "Computes the follow-up status/result and selector gates before entering the primary or secondary handler tables.")
label(0x0007d930, "state_followup_range_class_7d930",
      "Masks state-base plus offsets 0xe24f/0xa24f/0x224f/0x624f to 16 bits and selects class 1 when any value is at most 0x49e.")
label(0x0007df00, "state_followup_selector_gate_7df00",
      "Routes selector r6 == 0x44 to 0x7df58; all other selectors publish status 7/control 1/selector r6 and call 0x79d60.")
label(0x0007df58, "state_followup_special_route_7df58",
      "Routes (g6 == 0x55 and r6 != 0x56) or (g6 == 0xa3 and object state +0x64 == 6) through table 0x72780, selector/control/action publication, and call 0x79050; other cases continue at 0x7dfb8.")
label(0x0007dfb8, "state_followup_class_route_7dfb8",
      "When g6 == 0xa3 and object state +0x64 is 3 or 6, derives the state-dependent classifier input, looks up 0x72780, publishes selector/control/action 30, and calls 0x79050; other cases continue to 0x7e064.")
label(0x0007e064, "state_followup_fallback_gate_7e064",
      "Admits the 0x81610 route for timing modulo 480 <= 239, object state not 3/7, 0x509b34 > 0x1f4, g5 != 4, and g6 == 0xa3; publishes continuation/control and optional selector 1, otherwise continues at 0x7e0d0.")
label(0x0007e0d0, "state_followup_state89_gate_7e0d0",
      "States 8/9 take the floating gate and either return through 0x7e130 or call 0x81610; other states continue at 0x7e144.")
label(0x0007e230, "state_followup_action25_publication_7e230",
      "Looks up classifier output through 0x72660, writes index-1 to 0x504db4, then publishes control 1/action 25/caller g14/result status to the transition cells.")
label(0x0007e278, "state_followup_record_probe_prelude_7e278",
      "Saves the existing transition control/selector/action values and initializes the probe publication cells before the indexed-record and callback gates.")
label(0x0007e2cc, "state_followup_record_probe_gate_7e2cc",
      "Saves the prior control/selector/action, publishes control 1/selector g6/action -1, then requires 0x5770f0 > 9, the indexed record halfword threshold, selector != 0xaf/0xa9, and callback 0x816d0 == 1 before the success publication; failures continue at 0x7e33c.")
label(0x0007e33c, "state_followup_descriptor_fallback_7e33c",
      "Calls 0x7e390 with saved selector inputs; zero result restores 0x504d9c/0x504da0/0x504db4, while nonzero result writes status 4 to 0x504d94 only when 0x504dc4 < -15.")
label(0x0007d9e4, "state_followup_publication_counter_clamp",
      "Publishes selected status/result to base 0x504d60 offsets +0x58/+0x34 (0x504db8/0x504d94), increments 0x51c930, and clamps the counter to 0..24 before the ratio gate.")
label(0x0007d9b4, "state_followup_result_status_select",
      "Uses nonzero range class g6 to select result table 0x72ab0[g6]; class zero enters a real-value threshold for 0x72630[0], with literal status 20 as the low fallback and status 31+g9 on table paths.")
label(0x0007da10, "state_followup_ratio_gate",
      "Zero-extends object halfwords +0x1d0/+0x1d8, divides them as i960 real values, and returns to 0x7db70 when the ratio is at most the literal 0.4 threshold.")
label(0x0007da54, "state_followup_span_gate",
      "Forms divisor r17+31, divides 0x503a14 by it, adds one, and routes spans at least 25 to 0x7db70; otherwise a counter above 24 reaches 0x7db54.")
label(0x0007daf0, "state_followup_primary_handler_20",
      "Publishes selector 20 to 0x504d98.")
label(0x0007db00, "state_followup_primary_handler_23_28",
      "Publishes selector 23 and status 28 to 0x504d98/0x504d94.")
label(0x0007db1c, "state_followup_primary_handler_21",
      "Publishes selector 21 to 0x504d98.")
label(0x0007db2c, "state_followup_primary_handler_status_counter",
      "Publishes caller g14 as status and decrements 0x51c930 when object field +0x172 equals 4.")
label(0x0007db54, "state_followup_primary_handler_continuation",
      "Publishes caller g14 as status and stores it at 0x51c930 when object field +0x170 is not 6.")
label(0x0007dba8, "state_followup_handler_19a",
      "Publishes selector 19 to 0x504d98.")
label(0x0007dbc8, "state_followup_handler_20",
      "Publishes selector 20 to 0x504d98.")
label(0x0007dbd8, "state_followup_handler_23_28",
      "Publishes selector 23 and status 28 to the transition cells.")
label(0x0007dbf4, "state_followup_handler_21",
      "Publishes selector 21 to 0x504d98.")
label(0x0007dc04, "state_followup_geometry_handler",
      "Negates object halfwords at +0x10/+0x8 for command 10, reads FIFO response and object +0x184 low halves, classifies through 0x73508/0x72b10, then writes g9+31, selector 23, and the result status.")
label(0x0007dbb8, "state_followup_handler_19b",
      "Second selector-19 handler arm: publishes selector 19 to 0x504d98.")
label(0x0007dbe8, "state_followup_handler_23_status28",
      "Publishes selector 23 to 0x504d98 and status 28 to 0x504d94.")
label(0x0007dc98, "state_followup_handler_29",
      "Publishes status/selector value 29 to 0x504d94.")
label(0x0007dca8, "state_followup_handler_counter_tail",
      "When object field +0x170 is not 6, stores caller g14 at 0x51c930.")
label(0x0007dcc0, "state_byte_window_7dcc0",
      "Entry guard requires signed 0x509b34 > 0x1f3. Per-slot byte window requires a nonzero status byte, zero masked 0x0f00 halfword gate, and object byte in the inclusive status..status+5 band before command-10 emission.")
label(0x0007dd00, "state_byte_window_scan_7dd00",
      "Scans 32 related-object slots against the two status bytes at 0x504e3a/0x504e3b, preserving the per-status match masks before the packet-selection path.")
label(0x0007e390, "state_geometry_descriptor_7e390",
      "Maps object slot through +0x200 with a 32-byte stride, uses the resulting byte as a 48-byte descriptor index from 0x562cb0, reads descriptor offsets +4/+0xc/+0x24, and selects the state-3 0x3ff80000 arithmetic arm; constants 0x40c00000 and 0x42f00000 are preserved raw.")
label(0x0007e440, "state_geometry_packet_prefix_7e440",
      "Emits the recovered eight-record command-29/30 prefix: signed descriptor halfwords become masked 16-bit lanes, with the first four lanes carrying the g5*g2 product and the next four carrying the g7*g6 product.")
label(0x0007e5e8, "state_geometry_difference_prep_7e5e8",
      "Consumes the packet responses, folds descriptor +0x18 into g13 and g2 with the live register differences, stores the derived g8 value at frame +0x60, and prepares the command-10 operand registers for the classifier chain.")
label(0x0007e6a0, "state_geometry_classifier_prep_7e6a0",
      "Sign-extends the low halfword of the command-10 response/object difference, combines the preceding raw mulr results with reverse-subtracts, and enters classifier 0x73508.")
label(0x0007e6d4, "state_geometry_packet31_gate_7e6d4",
      "Emits command 31 with descriptor/related fields, reads the FIFO response, and admits 0x7e788 only when the first three signed products are positive and the fourth is nonzero; zero or failed predicates continue at 0x7e778.")
label(0x0007e788, "state_geometry_packet10_classify_7e788",
      "Emits command 10 from the selected record fields, subtracts the sign-extended record +8 halfword from the FIFO response, branches on response-delta bit 15, sign-extends the object +0x184 halfword, applies the 0x504de4 bias arm, and enters classifier 0x73508 before table 0x72660.")
label(0x0007e834, "state_geometry_action30_publication_7e834",
      "Looks up classifier result through 0x72660, publishes action 30 and status, then admits the 0x7e864 threshold path only when 0x509b34 exceeds 0x5dc; equality exits at 0x7e9f4.")
label(0x0007e950, "state_geometry_status_dispatch_7e950",
      "Subtracts 8 from published status, dispatches indices 0-11 through the compact 0x7e96c table, preserves higher/underflow values at the common tail, optionally calls 0x79050 when 0x504da4 == 1, and republishes action 30.")
label(0x0007ea10, "state31_initializer_7ea10",
      "Requires signed 0x509b30 > 0x1f3; state 31 requires related/object state 6 and 0x504e48 == 3 before writing 3/0x64/1/7/30 to 0x504d9c/0x504da0/0x504d94/0x504d98/0x504db8. Other states use the exact eight-entry 0x7eab0 threshold dispatch.")
label(0x0007ebcc, "state31_slot_scan_7ebcc",
      "Scans 32 active related slots, emits command 62 with the four object/related fields, retains the lowest qualifying FIFO response and slot mask, and routes object state 8 through the 0x72780/table-3 publication tail.")
label(0x0007ecc0, "state31_global_callback_gate_7ecc0",
      "Uses 0x5770f0 > 9 to choose callback 0x816d0 versus 0x81b30, then repeats the zero-response test and admits selectors 0/2/5 with status 0/9 toward 0x7ed34; other paths split to 0x7ee28 or 0x7f0f8.")
label(0x0007ed34, "state31_selector_publication_7ed34",
      "Admits status 0/9 with related state 3 plus mode bit 2 or state 2 plus mode bit 1, requires selector 0, and publishes selector 2/action 25/control 3/caller status/continuation 0x64 for state 2; state 3 continues at 0x7edc4.")
label(0x0007edc4, "state31_range_publication_7edc4",
      "Routes related state 4 directly or accepts signed related +0x172 shifted by 16 only in the strict-lower/inclusive-upper 0x150000..0x190000 band; outside values publish status 23, then selector 3/action 20/control 3/continuation 0x64 converge at 0x7efd8.")
label(0x0007ee28, "state31_fallback_admission_7ee28",
      "After the nonnegative timing gate, requires object state 3, related state 5 or 6, and selector 0/2/5 before returning at 0x7ee8c; failed admissions continue through 0x7f0bc or the separate 0x7ee90 route.")
label(0x0007ee90, "state31_classifier_route_7ee90",
      "Partitions global 0x504d70 at 4 and selects classifier offsets -0xc00/-0x1800/-0x800 or +0x1800/+0x2800 from related/object states before the 0x72780 publication at 0x7efb0.")
label(0x0007efb0, "state31_common_publication_7efb0",
      "Publishes the 0x72780 classifier result to 0x504d94, calls 0x79050 with the related pointer, then writes action 30, control 3, and selector 0x64 before returning.")
label(0x0007eff0, "state31_classifier1_status_dispatch_7eff0",
      "Enters the 0x7f010 status table only when classifier result is 1, maps status-minus-8 indices to status 1/4/5/6/2/3 or preserves common values, calls 0x79050 at 0x7f08c, and otherwise continues at 0x7f098.")
label(0x0007f098, "state31_classifier1_bypass_7f098",
      "Requires object state 6, related state 3, and selector 0/2/5; the admitted path writes status 7, calls 0x79d60 with the related pointer, then publishes action 30/control 3/selector 0x64 before returning, while failures continue at 0x7f0f8.")
label(0x0007f0f8, "state31_zero_frame_admission_7f0f8",
      "Requires the saved frame value to compare equal to zero, excludes related state 7 with object state 5, and admits selector 3/6/1/4/7; selectors 3/6 continue to 0x7f168, other admitted selectors to 0x7f1f8, and failed gates to 0x7f32c.")
label(0x0007f168, "state31_timing_publication_gate_7f168",
      "Routes direct state pairs and the two 0x504d60-vs-0x40690000 timing arms through the final related-state 6/object-state 5 exclusion; accepted paths write status 7 and branch to 0x7f4ac, while rejected paths continue at 0x7f1f8.")
label(0x0007f1f8, "state31_double_state6_fastpath_7f1f8",
      "Checks object and related state together; the exact 6/6 pair sets the classifier input to zero and jumps to the 0x7f31c table lookup, while other pairs continue at 0x7f210.")
label(0x0007f210, "state31_selector_offset_route_7f210",
      "Builds the classifier offset from selector-minus-3 and object/related states: base 0x1000, 0x1800, or 0x3000, with signed positive/negative arms, then converges at the 0x72780 lookup through 0x7f31c.")
label(0x0007f31c, "state31_classifier_table_tail_7f31c",
      "Loads g4 from 0x72780[g0*4], moves the related-object pointer r5 into g0, and transfers to 0x7ecb0 with the table result and pointer preserved.")
label(0x0007f32c, "state31_classifier1_fast_publication_7f32c",
      "Admits classifier result 1, writes selector 3, and returns with control 0x64 when the r6-vs-zero compare is equal; the non-equal classifier-1 arm continues at 0x7f364 and other results branch to 0x7f44c.")
label(0x0007f364, "state31_threshold_status_dispatch_7f364",
      "Converts 0x504df4, compares the resulting threshold against r6, stores r8 to 0x504da0, then dispatches status-minus-8 through 0x7f3ac; mapped statuses converge at 0x7f428 for optional callback 0x79050 and action 30.")
label(0x0007f44c, "state31_special_status_publication_7f44c",
      "Admits r8/status 0x92 with related state 6, 0x44 unconditionally, or 0x56/0x57 with related state 7; accepted paths publish selector 3/status 7/control r8, call 0x79d60, write action 30, and return at 0x7f4c4.")
label(0x0007f4d0, "transition_scan_7f4d0",
      "Requires signed 0x509b28 > 0x1f3, then scans status bytes 0x504e38 and 0x504e39 across 32 object slots at related+0x200 with a 0x20 stride; each match uses the inclusive status..status+5 byte window before the later candidate/state route.")
label(0x0007f5ec, "transition_post_scan_admission_7f5ec",
      "Requires related +0x170 == 3 or +0x172 == 1, related state 3/8, unsigned published-status-minus-2 greater than 5, and an r6-vs-zero equality before continuing at 0x7f634; failures branch to 0x7f6b0.")
label(0x0007f634, "transition_timing_threshold_route_7f634",
      "Compares current timing with converted 0x504dec/0x504e06 thresholds; the lower pass calls 0x82800 and publishes selector 4/control 0x64, while the upper pass requires 0x504da4 == 1 and 0x504dc8 == 1 before writing state 1 and routing mode 10 to 0x7f8fc.")
label(0x0007f6b0, "transition_followup_admission_7f6b0",
      "Excludes related state 4, requires related +0x170 == 3, then applies the r6-vs-zero equality and unsigned published/global status-minus-2 > 5 guards before calling 0x80710 at 0x7f708; failures branch to 0x7f808.")
label(0x0007f70c, "transition_state4_threshold_prefix_7f70c",
      "After 0x80710, requires related state 4 and current timing below 0x407f4000; publishes selector 4/control 0x64, then uses 0x4072c000 to choose direct 0x72780 lookup/publication at 0x7f7d4 or the difference route at 0x7f774.")
label(0x0007f774, "transition_state4_difference_route_7f774",
      "Splits published status at 4, sign-extends related/current +0x184 values, adds or subtracts 0x5000 from the current value, reverse-subtracts through 0x73508, and converges on table 0x72780 at 0x7f7d4.")
label(0x0007f800, "transition_state4_fallback_gate_7f800",
      "Requires related state 4, current timing below 0x407f4000, r6-vs-zero equality, control 0x504e48 == 2, and shifted +0x172 <= 0x160000 or > 0x180000 before continuing at 0x7f878; failures branch to 0x7f91c.")
label(0x0007f878, "transition_state4_global_route_7f878",
      "Splits 0x504d70 into <=1 negative-bias, 2..7 direct-table, and >7 positive-bias arms; publishes the selected result, calls 0x79050 with r8, then writes action 30/control g14/selector 4 before returning at 0x7f918.")
label(0x0007f91c, "transition_r6_zero_gate_7f91c",
      "Repeats the r6-vs-zero comparison; equality returns at 0x7f934, while the non-equal arm enters the table lookup and floating scaling route at 0x7f938.")
label(0x0007f938, "transition_lookup_scale_7f938",
      "Forms a byte-derived index as lookup_byte*3 into table 0x562cd8 with 16-byte stride, clamps negative scaled values to 0x42960000, selects scalar 0x40100000 for object state 2 or 0x40080000 otherwise, and continues at 0x7f9b0.")
label(0x0007f9b0, "transition_state4_result_route_7f9b0",
      "Requires object state 4, derives +/-0x1000 or +/-0x4000 from global 0x504d70, classifies the signed +0x184 difference through 0x73508, selects table 0x72630 only for shifted +0x172 in (0x150000,0x190000], otherwise 0x72780, and publishes at 0x7fabc.")
label(0x0007fd24, "transition_dual_threshold_route_7fd24",
      "Uses two converted 0x504dec timing thresholds; the first threshold sends non-state-6 objects to 0x7fd58, while the second threshold admits states 0/6 to 0x7fd58 and routes other outcomes to 0x7fed0.")
label(0x0007fd58, "transition_selector6_publication_7fd58",
      "Publishes selector 6 and control 0x64, stores -1 to 0x504db4, and uses the inclusive 0x9c4 global-counter threshold to continue at 0x7fdd4 or 0x7fd90.")
label(0x0007fd90, "transition_selector6_counter_followup_7fd90",
      "Uses control 0x504e48 == 0 or related state 7 to return to 0x7fdd4; otherwise object state 8 publishes status/state 1, while other object states publish status 22, all toward 0x7ff28.")
label(0x0007fdd4, "transition_selector6_timing_publication_7fdd4",
      "Requires object and related states in {0,6} and shifted related +0x17a <= 0x90000, then publishes state 6 to 0x504d98 and action 20 before returning; other pairs continue at 0x7fe24.")
label(0x0007fe24, "transition_fallback_result_route_7fe24",
      "Uses the inclusive 0x2bc counter shortcut and table 0x72720; larger counters choose +/-0x6580 from global 0x504d70, classify through 0x73508, use table 0x72780, publish action 30/status, optionally call 0x79050 with r4, and return at 0x7fed0.")
label(0x0007fed4, "transition_selector6_status7_route_7fed4",
      "Requires related +0x172 equal to 27 or 30 and global 0x509b20 greater than 0x5dc, then publishes selector 6/control 0x64/counter -1/status 7, calls 0x79d60, writes action 30, and returns at 0x7ff34.")
label(0x0007ff40, "geometry_command_prefix_7ff40",
      "Selects an object byte from the +0x200 table with selector*0x20, preserves the raw byte in r8 for the 0x30-byte profile-table index at 0x562cb0, separately applies signed (byte-1) rem 6 in g4, derives the first profile sum, and begins FIFO command 30 at 0x884000.")
label(0x00080180, "geometry_command29_30_prefix_80180",
      "Emits command 29 and two command-30 geometry-board request triplets using ldos of object +0x08, biased by +/-0x6000 and masked to 16 bits; object +0x10 is a full-word response-difference source, with the shared runtime anchor.")
label(0x000803c8, "geometry_command10_classifier_prefix_803c8",
      "Builds command 10 from selected-record/object differences, reads the board reply, sign-loads object +0x184 with ldos, sign-normalizes reply minus that halfword to a low halfword, and passes the value to classifier 0x73508.")
label(0x00080400, "geometry_command62_packet_80400",
      "Emits the five-word command-62 packet [selected +0x10, object +0x08, selected +0x18, object +0x10], reads the board response, and enters floating-point gates at 0x80428.")
label(0x0008052c, "geometry_command10_followup_8052c",
      "Repeats command 10 with selected-record/object difference payloads, reads the board response, ldos-loads selected-record +0x08, and uses bit 15 of the response difference to select 0x80580 or 0x805a8.")
label(0x00080580, "geometry_response_route_80580",
      "Combines ldos-normalized record +0x08/object +0x184 halfwords with no-bias or -0x504de4 arms selected by response bit 15, classifies through 0x73508, looks up 0x72660, publishes action 20/status, calls 0x7d1f0, and gates on 0x509b24 > 0x5dc.")
label(0x00080650, "geometry_status_tail_80650",
      "Consumes the already-admitted status path, dispatches status-minus-8 through the 0x8066c table, mapping indices 0/1/2/3/10/11 to statuses 1/4/5/6/2/3 while preserving other values, optionally calls 0x79050 when 0x504da4 is 1, publishes status and action 30, and returns at 0x806f4.")
label(0x00080600, "geometry_publication_gate_80600",
      "Requires 0x509b24 > 0x5dc, then admits comparison values below the first threshold or below the mode-4/mode-5 secondary threshold; admitted paths enter 0x80650 and all other paths return at 0x806f4.")
label(0x0007fabc, "transition_result_publication_handoff_7fabc",
      "Stores the selected result at 0x504d94 and branches to the shared 0x7fc84 continuation.")
label(0x0007fc24, "transition_result_status_tail_7fc24",
      "Dispatches status-minus-8 through the 0x7fbf4 table, rewrites indices 0/1/2/3/10/11 to statuses 1/2/3/4/2/3, optionally calls 0x79050 with r8, writes action 30, and returns at 0x7fc90.")
label(0x0007f7d4, "transition_state4_publication_tail_7f7d4",
      "Publishes the classifier result to 0x504d94, optionally calls 0x79050 with r8 when 0x504da4 == 1, writes action 30, and returns at 0x7f7fc.")
label(0x0007fca0, "transition_precondition_7fca0",
      "Normalizes related +0x172 by zero-extending its low halfword; accepts the range arm for 0x10000 < value <= 0xd0000, or the state arm for related +0x64 in {0,6}, +0x172 in {1,14}, and +0x170 == 6. Later 0x504dec/current timing selection remains separate.")
label(0x00080710, "transition_route_80710",
      "Uses ldos-loaded +0x184 fields; 0x504d70 <= 1 subtracts 0x6800 from the current value, values 2..9 add 0x6800, and otherwise exits; classifies the related-current difference through 0x73508, selects 0x72630[g6], initializes 0x504db8 to 10, and calls 0x82800 only when current timing is below converted 0x504df8.")
label(0x000811b8, "transition_secondary_dispatch_811b8",
      "Dispatches object states 0..7 through the 0x811d0 table to 0x811f0, 0x81260, 0x812ac, 0x81300, 0x81390, 0x8140c, 0x81480, or 0x81528; states above 7 bypass the table at 0x815ac.")
label(0x000811f0, "transition_secondary_state0_811f0",
      "For object-state-0 dispatch, sign-loads related +0x172/+0x17e with ldos, checks related state 2 and +0x172 equal 24; a nonzero +0x17e diverts to 0x81498, while other outcomes continue at 0x81208.")
label(0x00081208, "transition_common_publication_81208",
      "Loads 0x728a0[0x504d68] and stores it to 0x504d94; control 0x504dc8 != 1 continues at 0x815e0, while control 1 publishes status 23 and uses the floating sign of 0x504d60 to branch to 0x81508 or 0x81518.")
label(0x00081260, "transition_secondary_state1_81260",
      "Routes related state 6 to 0x81414, state 4 to selector value 7 and 0x815d8, otherwise publishes the 0x728a0 result and uses control 0x504dc8 to select 0x815e0 or the repeated-state 6/normal paths at 0x81470/0x815d4.")
label(0x000812ac, "transition_secondary_state2_812ac",
      "Publishes the 0x728a0 result, requires control 0x504dc8 == 1 for status 23, then tests bit 2 of 0x504e30 to publish state 3 toward 0x815e0 or divert to 0x8159c.")
label(0x00081300, "transition_secondary_state3_81300",
      "Publishes the 0x728a0 result, requires control 0x504dc8 == 1 for status 23, then applies bit 2 of 0x504e30 to enable the shared 0x504d60 < 0x40518000 gate; when that gate does not route to 0x81570, the same 0x504d60 < 0x406f4000 gate selects 0x8159c or 0x815d4.")
label(0x00081390, "transition_secondary_state4_81390",
      "Publishes the 0x728a0 result, requires control 0x504dc8 == 1 for status 23, then applies bit 2 of 0x504e30 and a strict shared 0x504d60 < 0x4062c000 gate; a failed gate uses bit 1 to route 0x8158c or 0x8159c, while the passed gate routes 0x81570.")
label(0x0008140c, "transition_secondary_state5_8140c",
      "Checks object +0x64: state 6 selects 0x72750[g4] into 0x504d94 and exits through 0x815e0, state 4 writes selector 7 to 0x504d94 and returns through 0x815d8, and other states continue at the state-5 fall-through 0x81440.")
label(0x00081440, "transition_secondary_state5_fallback_81440",
      "State-5 fall-through republishes the 0x728a0 result, gates on control 0x504dc8 == 1, then checks object +0x64: state 6 publishes status 9 to 0x504d94 and exits through 0x815e0, while other values continue through 0x815d4.")
label(0x00081480, "transition_secondary_state6_81480",
      "For object +0x64 == 2, sign-loaded related +0x172 == 24, and sign-loaded related +0x17e == 0, selects 0x72780[g4] into 0x504d94 and exits through 0x815e0; all other combinations fall through to 0x814b4.")
label(0x000814b4, "transition_secondary_fallback_814b4",
      "Publishes the 0x728a0 result, requires control 0x504dc8 == 1, writes status 23, then compares 0x504d60 strictly below 0x40690000: the pass writes state 1 to 0x504d98 and the fail writes status 8; both exit through 0x815e0.")
label(0x00081528, "transition_secondary_state7_81528",
      "Publishes the 0x728a0 result, requires control 0x504dc8 == 1, writes provisional status 9, then publishes state 3 when object +0x64 == 3 or flag bit 2 is set, otherwise state 2 when bit 1 is set, otherwise state 1; all admitted routes exit through 0x815e0.")
label(0x000815ac, "transition_secondary_bypass_815ac",
      "The >7 unsigned-state bypass publishes 0x728a0[0x504d68] to 0x504d94, overwrites it with status 8 when control 0x504dc8 == 1, then always writes 10 to 0x504db8, 2 to 0x504d9c, and 0x64 to 0x504da0 before returning.")
label(0x000810d0, "transition_mode_route_810d0",
      "Requires signed 0x509b2c > 0x1f3 and normalized related +0x172 strictly above 0x150000 through 0x190000, then enters 0x81120 for the mode/state route.")
label(0x00081120, "transition_mode_route_81120",
      "For nonpositive current timing requires mode bit 3; accepts object state 1 or 5 and rejects related states 1,5,6,7, then writes 7/30/2/0x64 to 0x504d94/0x504db8/0x504d9c/0x504da0, calls 0x79d60, and returns 0.")
label(0x00081610, "transition_offset_classifier_81610",
      "Uses signed g2-3 to route values below 6 to the 0x8168c status tail; otherwise sign-normalizes low16(g1), chooses -0x4000 for global state <=4 or +0x4000 for state >4, calls the signed-halfword classifier at 0x73508, indexes 0x72780, publishes action 30, and calls 0x79050.")
label(0x0008168c, "transition_status_tail_8168c",
      "Publishes status 18 for global state 2 or 7; otherwise computes signed 0x5024e8 remainder by 240 and publishes 18 for remainder <= 0x77 or 19 above that boundary.")
label(0x00081e60, "state_dispatch_81e60",
      "Calls 0x84d90 only for globals 0x5039f4 == 4, 0x503a00 == 10, and mode 0x504e42 == 0; then dispatches mode-zero object states 0..9 through the exact table at 0x81eb4.")
label(0x00081f60, "timing_selector_81f60",
      "Classifies the state/timing prefix, updates the paired 0x504d78/0x504d7c cells, and clears 0x504d88 on the fallback arm; state 6 takes the fast path when floating-point 0x504d60 is below 0x404e0000, state 3 can advance to state 4 for selector 1, and states 4/5 select value 2 for selector 1.")
label(0x00082ae0, "state_scheduler_gate_82ae0",
      "Runs 0x81f60 first; when 0x503a14 <= (g28+31), 0x5039f4 == 4, and 0x504dbc < 6, object states through 8 call 0x82db0 while states above 8 call 0x81e60 only for 0x504d7c == 5; otherwise control continues into the downstream scheduler. The C plan exposes both call targets.")
label(0x00082b38, "state_scheduler_dispatch_82b4c",
      "After requiring status 0x504d84 == 1, rejects selectors above g28+12 and dispatches the bounded selector through the 44-entry table at 0x82b58.")
label(0x00082c08, "state_scheduler_handler_82c08",
      "Table selector 6 writes state 7 to 0x504d7c when 0x504e1c == 0; otherwise it calls the existing 0x81e60 state dispatcher, then joins the common scheduler tail.")
label(0x00082c18, "state_scheduler_control_handlers_82c18",
      "Entries 0x82c18, 0x82c28, and 0x82c38 write state 7 when 0x504e1c is zero, otherwise call 0x81e60; 0x82c54 is the unconditional 0x81e60 call arm.")
label(0x00082c60, "state_scheduler_service_call_82c60",
      "Passes the incoming object pointer to 0x840b0 and rejoins the common scheduler tail at 0x82d74.")
label(0x00082df8, "state_service_mod4_handlers_82df8",
      "Normalizes signed random values into a modulo-4 selector; 0x82e0c adds 4 unless object state is 3, which selects 7 for the shared dispatch.")
label(0x00082e64, "state_service_handler_82e64",
      "Accepts random remainders 4 or 6 modulo 7 only for object states 0, 1, 5, or 6, then selects downstream value 2.")
label(0x00082c6c, "state_scheduler_handler_82c6c",
      "Table selector 19 writes status 2 for object states other than 4; state 4 writes status 8 when signed 0x504dc0 <= 0x78000, otherwise writes status 3 and selects state 28 for 0x504e28 == 1 or state 5.")
label(0x00082cc0, "state_scheduler_constant_handlers_82cc0",
      "Constant scheduler entries write 0x504d98: 0x82cc0 -> 3, 0x82cc8 -> 1, 0x82cd0 -> 13, 0x82cd8 -> 14, and 0x82ce0 -> 15, then join the common tail.")
label(0x00082ce8, "state_scheduler_state4_handlers_82ce8",
      "Target 0x82ce8 writes status 3 plus state 28 for object state 4, otherwise status 2; target 0x82d04 writes status 2 for state 4, otherwise status 3.")
label(0x00082d18, "state_scheduler_handler_82d18",
      "Writes status 3 and selector 20 for object state 8; all other states take the shared status-8 path.")
label(0x00082d68, "state_scheduler_reject_82d68",
      "Writes status 8 to 0x504d80 and falls directly into the common scheduler tail at 0x82d74.")
label(0x00082600, "state_random_status_82600",
      "Reduces the external 0xf5058 value with signed remi 3; remainders 0, 1, and 2 write statuses 20, 19, and 33 to 0x504d80, while negative or unmatched remainders return without a store.")
label(0x00082db0, "state_service_dispatch_82db0",
      "Dispatches object states 0..8 through the exact table at 0x82dd4; states above 8 take the high-state route at 0x82f90.")
label(0x00082e40, "state_service_handler_82e40",
      "Requires signed remi-5 remainder 4; then selects downstream value 2 for object state 3 or 5 for all other states, while all other remainders use the shared fallback.")
label(0x00082ea0, "state_service_handler_82ea0",
      "Requires object state 3; random remainder 4 modulo 6 selects downstream value 3, remainder 5 selects value 6, and all other combinations use the shared fallback.")
label(0x00082ed4, "state_service_mod8_handlers_82ed4",
      "The 0x82ed4 handler maps signed normalized remainder < 3 plus object state 3 to value 3 and remainder 6 to value 4; 0x82f10 maps remainders 4/5 plus state 3 to value 3 and remainder 7 plus state 3 to value 6; all other cases share fallback.")
label(0x00082f6c, "state_service_handler_82f6c",
      "Requires random remainder 4 modulo 5 and object state 3, then selects shared downstream value 2; every other combination falls through to the common dispatch.")
label(0x00082f84, "state_service_random_mod7_82f84",
      "Computes remi 7 on the random helper result and passes the signed remainder to the shared 0x82fac selector table.")
label(0x00082f90, "state_service_high_dispatch_82f90",
      "Adjusts negative random results by 3, subtracts the value masked with ~3 to form the selector, and dispatches unsigned selectors 0..7 through the table at 0x82fbc; nonnegative inputs normalize to 0..3, while negative or larger results use the shared reject path.")
label(0x00082fbc, "state_service_high_dispatch_82f90_table",
      "Targets: 0x82fdc, 0x82ff4, 0x8300c, 0x83024, 0x8303c, 0x83050, 0x83058, and 0x8307c.")
label(0x00082fac, "state_service_shared_dispatch_82fac",
      "Unsigned selector <= 7 dispatches through the shared eight-entry table at 0x82fbc; larger selectors take the 0x830a0 reject path.")
label(0x00082fdc, "state_service_shared_handler_prefix_82fdc",
      "Selectors 0..3 publish d94 values 5/6/2/3 and call 0x79050 before selecting 30; selectors 4..6 publish d98 1/2/3 with selector 20 and caller g14 to d94; selector 7 publishes d94 7, calls 0x79d60, and selects 30; reject publishes d98 1, d94 g14, and selector 10.")
label(0x000830c0, "state_service_postprocess_830c0",
      "If current object state is 3 and status is 9, rewrites status to 12; then if the related object state is 0, overrides status to 1, selector to 10, and d94 to caller g14.")
label(0x00083110, "state_scheduler_early_gate_83110",
      "For signed 0x504dc0 <= 149 and related +0x172 equal to 19 or 20, writes caller g14 to 0x504d98 and returns; all other inputs continue into the timing/status path.")
label(0x000834b0, "state_scheduler_early_gate_834b0",
      "Sibling early gate with the same signed 0x504dc0 <= 149 and related 19/20 predicate; admitted inputs write caller g14 to 0x504d98 and return.")
label(0x000835f0, "state_scheduler_early_gate_835f0",
      "Sibling early gate with the same signed 0x504dc0 <= 149 and related 19/20 predicate; admitted inputs write caller g14 to 0x504d98 and return.")
label(0x00083624, "state_scheduler_state5_status_prefix_83624",
      "State-5 continuation publishes 0x504e1c = 1, calls 0x82800 when current timing is below converted 0x504df8, selects status 18 for negative timing, then uses control 0x504e28 and signed remi 10: remainders through 3 enter the remi-5 table, while larger remainders use a second random bit to select status 35 or 42.")
label(0x00083750, "state_scheduler_nonstate_status_prefix_83750",
      "Non-state continuation calls 0x82800 below converted 0x504df8, selects status 18 for negative timing, then uses control 0x504e28 and signed remi 10: remainders through 3 enter the 0x837d0 remi-5 table, while larger remainders consume a second random value and publish status 42.")
label(0x00083884, "state_scheduler_state5_status_branch_83884",
      "State-5 continuation publishes 0x504e1c = 1, calls 0x82800 below converted 0x504df8, and then applies the control-1 initial remi-10 fast status-28 arm. The follow-up remi-10 path uses the secondary timing threshold, remi-6 and remi-1 partitions, control/pair equality, and statuses 21/27/19/28/37.")
label(0x00083850, "state_scheduler_early_gate_83850",
      "Sibling early gate with the same signed 0x504dc0 <= 149 and related 19/20 predicate; admitted inputs write caller g14 to 0x504d98 and return.")
label(0x00083f50, "state_scheduler_early_gate_83f50",
      "Sibling gate with the same signed 0x504dc0 <= 149 and related 19/20 predicate; admitted inputs write caller g14 to 0x504d98 and return, while other inputs publish 0x504e1c = 1 and dispatch state 5 to 0x83f9c or other states to 0x84018.")
label(0x000840b0, "state_scheduler_early_gate_840b0",
      "Sibling gate with the same signed 0x504dc0 <= 149 and related 19/20 predicate; admitted inputs write caller g14 to 0x504d98 and return, while other inputs publish 0x504e1c = 1 and dispatch state 5 to 0x84104 or other states to 0x841a0 in the shared random/timing model.")
label(0x000840e8, "state_scheduler_random_timing_prefix_840e8",
      "Normalizes signed random output into the modulo-8 helper, applies the converted-timing call gate, selects the state-5/non-state helper contracts at 0x84150/0x841ec, and joins the appropriate tail.")
label(0x000839a8, "state_scheduler_status_leaf_839a8",
      "State-5 status leaf: calls 0x82800 when current timing is below converted 0x504df8, then applies the control-1 initial remi-10 fast status-28 arm. The remaining remi-10 values use the secondary timing gate, remi-6/remi-1 partitions, mode bits, and pair equality to select statuses 19/21/27/28/37 before the caller-g14/status-15 tail.")
label(0x00083d58, "state_scheduler_state5_leaf_83d58",
      "State-5 sibling leaf calls 0x82800 below the converted negative timing limit, writes status 18 for negative timing, and otherwise uses signed remi 10: remainders above 5 select status 25, remainders through 3 select status 33, and remainders 4/5 use the control/pair equality for status 27 or 19.")
label(0x00083de4, "state_scheduler_nonstate_prefix_83de4",
      "Non-state sibling prefix calls 0x82800 below the converted negative timing limit, writes status 18 for negative timing, and otherwise uses signed remi 18: remainders through 11 hand off to the remi-6 continuation, while larger values use remi 3 to call 0x82800 for remainder 2 or select status 25/34 through the evenization test.")
label(0x00083e74, "state_scheduler_nonstate_remainder6_83e74",
      "Non-state remi-6 continuation sends remainders through 2, or any value with mode bit 1 clear, through the signed parity call/tail test using preserved g0; larger remainders with mode bit 1 set use the control/pair equality for status 27, otherwise consume signed remi 3 and publish status 40 for 0/1 or 19 for 2, with negative results taking the common tail.")
label(0x00083568, "state_scheduler_quadword_adjust_83568",
      "Normalizes signed random output into the modulo-8 remainder, adds 2 for remainders at least 3, checks control bit 2 first for an add of 1, otherwise selects add 7 only for positive remainders below 3 with control bit 1, preserves the high word, and stores 15 to 0x504d90.")
label(0x000836d0, "state_scheduler_mod5_status_table_836d0",
      "Maps signed remi-5 remainders 0..4 to statuses 35, 19, 36, 40, and 42 after an unsigned cmpobl 4 gate; negative results reject, while the sibling table at 0x837d0 uses the same values before the caller-g14/status-15 tail.")
label(0x00083310, "state_scheduler_early_gate_83310",
      "Sibling gate: for signed 0x504dc0 <= 149 and related +0x172 equal to 19 or 20, writes caller g14 to 0x504d98 and returns; all other inputs continue into the ratio/status path.")
label(0x00083348, "state_scheduler_ratio_prefix_83310",
      "Publishes 0x504e1c = 1, compares the converted 0x5042a8/0x5042a2 ratio against the 0.9 double constant, clears mode bit 2 above the threshold, and dispatches state 5 only when signed remi-5 output passes the unsigned cmpobl 4 table gate at 0x833c8.")
label(0x000833c8, "state_scheduler_ratio_prefix_83310_table",
      "Targets: 0x833dc, 0x833e8, 0x833f8, 0x83408, and 0x83418.")
label(0x000833dc, "state_scheduler_ratio_handlers_833dc",
      "Ratio-table selector 0 calls 0x79d60; selectors 1 and 2 publish status 28, selector 3 publishes 26, and selector 4 publishes 21 to 0x504d80.")
label(0x0008342c, "state_scheduler_remainder_handler_8342c",
      "Remainder 5 selects status 21; remainder 4 with mode bit 1 selects 26; positive remainders with mode bit 2 select 28; all other paths call 0x79d60, then write caller g14 to 0x504d8c and 15 to 0x504d90.")
label(0x00083ac0, "state_scheduler_dispatch_83ac0",
      "Early gate: signed 0x504dc0 <= 149 and related +0x172 equal to 19/20 writes caller g14 to 0x504d98. Otherwise publishes 0x504e1c = 1, calls 0x82800 when current timing is below converted 0x504df8, selects status 18 for negative timing, and uses state-5 remi-6 entries 0/1 call 0x79d60, 2/3 publish 28, 4 publish 26, and 5 publish 21. Other states use remi 7: below 4 calls 0x79d60, remainder 4 uses mode bit 1 for 26, and positive higher values use mode bit 2 for 28 or default 21 before publishing g14/15.")
label(0x00083cc0, "state_scheduler_early_gate_83cc0",
      "For signed 0x504dc0 <= 149 and related +0x172 equal to 19 or 20, writes caller g14 to 0x504d98 and returns; all other inputs continue after loading 0x504d7c. The continuation has distinct state-5 mode/timing and other-state remainder-18 paths.")
label(0x00083f9c, "state_scheduler_state5_handler_83f9c",
      "State-5 continuation: mode bit 1 selects status 26 when 0x504e28 == 1, otherwise status 37; with bit 1 clear, status 39 is selected only when current timing exceeds converted 0x504dd8 and mode bit 2 is set, otherwise status 37.")
label(0x00084018, "state_scheduler_quadword_tail_84018",
      "Loads the 0x504d80 quadword, replaces its first word with the candidate status, preserves the remaining three words, and publishes 0x504d90 = 30 exactly for status 26 or 31 + 0x504e30; all other statuses publish 15 before the stq commit.")
label(0x00084150, "state_scheduler_random_handler_84150",
      "Consumes the signed helper value from the 0x840b0 state-5 random/timing prefix: values above 4 with mode bit 2 select status 32; positive values with mode bit 1 select status 37; all other values select status 33.")
label(0x000841ec, "state_scheduler_nonstate_handler_841ec",
      "Non-state continuation: helper values above 4 with mode bit 2 select status 32; positive helper values with mode bit 1 select status 37; otherwise status 33 is selected.")
label(0x00084228, "state_scheduler_nonstate_tail_84228",
      "Commits the selected non-state status to 0x504d80, publishes caller g14 to 0x504d8c, and stores selector 15 to 0x504d90 before returning.")
label(0x00084240, "state_scheduler_initializer_84240",
      "Installs the 0x84290 return trampoline, clears callback g14, publishes 0x504e1c = 1, initializes status 0x504d80 = 43, selector 0x504d90 = 15, caller field 0x504d8c = 0, and 0x504d9c = 7 before bx(g1).")
label(0x000842d0, "scheduler_wrapper_842d0",
      "Returns when 0x504e50 bit 0 is set; otherwise calls 0x84330, 0x85c00, 0x848d0, 0x84b10, and 0x858f0 in order, then calls 0x85b00 only when the low byte of 0x5024e8 is zero.")
label(0x00084330, "scheduler_setup_prefix_84330",
      "Adjusts the stack by 16, masks 0x5024e8 with 3, and when the result is zero clears three halfword slots (six bytes) at 0x509a60 using the incoming g14 value before continuing into the bitfield setup.")
label(0x00084368, "scheduler_flag_synthesis_84368",
      "For source masks 0x100, 0x200, and 0x400, prefers 0x5024a4 and sets destination bits 4, 0, and 2; when absent, falls back to 0x50249c and sets bits 5, 1, and 3. A final 0x20000 pair repeats the bit-2/bit-3 preferred/fallback mapping in the selected 0x509a60 slot.")
label(0x00084470, "scheduler_flag_finalize_84470",
      "Reads the synthesized 0x509a60 halfword; sets bit 7 when bits 5 and 1 are both set, otherwise sets bit 6 when bit 4 is paired with bit 0 or 1, or when bit 5 is paired with bit 0.")
label(0x000844f4, "scheduler_counter_prefix_844f4",
      "Uses (0x5024e8 & 3) as a slot selector; nonzero slots jump to 0x847b0, while slot 0 increments 0x509a68, compares it against caller-derived g28 + 31, subtracts 60 only above that supplied limit, and continues packet construction.")
label(0x00084524, "scheduler_packet_header_84524",
      "Builds the selected 16-byte scheduler record header from object +0x1d0, 0x504d70, the converted 0x504e28 value, and packed 0x504e28/0x504e2c; because r13 is formed as 0-1, stores g14 at field +0x6 and continues with r7=16 only when 0x504e20 equals 0xffffffff.")
label(0x0008459c, "scheduler_packet_fifo_prelude_8459c",
      "Emits the eight-word scheduler packet prelude to 0x884000, masks the returned word to 16 bits, stores the record g7 value at header field +0x6, and continues into 0x8467c; table-derived arithmetic remains explicit at the model boundary.")
label(0x0008467c, "scheduler_frame_publication_8467c",
      "Derives row flags from 0x509ac0/0x509b10, calls the shared candidate selector at 0x847c0, and publishes its result plus the packed frame fields at row offsets +0xa and +0x8.")
label(0x00084724, "scheduler_frame_field_c_84724",
      "Packs the four scheduler halfwords into the row +0xc high byte, derives the normal object +0x108 value from bits 8-11 and 0-3, and uses the state-31 replacement packed value after setting frame bit 3.")
label(0x000847c0, "scheduler_candidate_selector_847c0",
      "States 2 through 13 take the zero-result exit; states above 13 scan 32 candidates through the external 0x86638 classifier. The low-state +0x64/mode/related-state/0x504dc8 predicates can also force result 0; otherwise the routine retains the lowest result through 5, emits a three-word delta packet for each improvement, and returns the selected result plus the last low-16-bit FIFO response.")
label(0x000848d0, "scheduler_counter_update_848d0",
      "For nonnegative 0x509a6c, increments and stores the counter, resetting it to zero above 120; for negative values, returns unless 0x503a14 exceeds 239, then continues into 0x8490c.")
label(0x00084b10, "scheduler_recovery_gate_84b10",
      "Updates 0x509a70 with a 120 ceiling/reset, derives table base 0x5074a0 + related field +0x64 times 1088 (17*64), and enters the recovery scan only for 0x509ac0 == 1, clear 0x504e50 bit 2, 0x503a14 > 239, and updated counter zero.")
label(0x00084b7c, "scheduler_recovery_search_entry_84b7c",
      "Routes failed recovery-gate predicates to 0x84d60; admitted inputs initialize 0x509a6c to 1 and enter the eight-record recovery search at 0x84bb4 with index zero.")
label(0x00084bb4, "scheduler_recovery_search_84bb4",
      "Scans eight recovery records at 136-byte stride using signed halfword field +0x86; -1 selects the current record, and target-greater records are selected and replace the target before continuing.")
label(0x00084bec, "scheduler_recovery_row_seed_84bec",
      "Seeds the recovery row source at (0x509a68 - 1) modulo 60, sets the inclusive scan limit to 59, masks the frame field, and loads the source frame's low flag nibble before the row-copy decision.")
label(0x00084c98, "scheduler_recovery_row_84c98",
      "Builds a recovery row at table base + selected index * 144, copies six scalar fields to offsets 0/2/4/6/8/a, stores 240 - 4*normalized delay at +0x84, computes the scalar source index as counter-minus-delay with one negative +60 correction, then copies the +0xc halfwords from source index zero through the bounded loop and writes 100 to the selected recovery record +0x86.")
label(0x00084d60, "scheduler_recovery_status_tail_84d60",
      "Stores the recovery flag to 0x509ac0, extracts bit 3 from the 0x504e50 control byte, and stores that boolean to 0x509b10 before returning.")
label(0x00084d90, "scheduler_control_gate_84d90",
      "Saves g8 at fp+0x40, tests bit 0 of 0x504e50, restores g8 and returns when set, otherwise restores g8 and continues at 0x84dc4.")
label(0x00084dac, "scheduler_success_publication_84dac",
      "Sets bit 8 in live g13, stores the result at 0x504e42, stores caller g14 at 0x504e44, and branches to 0x84f10.")
label(0x00084dc4, "scheduler_fallback_row_scan_84dc4",
      "Scans eight fallback rows, accepting a row whose field +0x86 exceeds 49, whose local match count is below 2, and whose global match flag is set; success reaches 0x84dac, while exhaustion continues at 0x84f10.")
label(0x00084f10, "scheduler_alternate_row_scan_84f10",
      "Scans eight alternate rows, accepting a row whose field +0x7c exceeds 49, whose local match count exceeds 2, and whose global match flag is set; success reaches 0x85058, while exhaustion returns after the scan.")
label(0x00085058, "scheduler_success_publication_85058",
      "Loads matched row +0x8c, sets bit 9 in g13, stores the result at 0x504e42, stores the row value at 0x504e44, restores g8, and returns.")
label(0x00085080, "scheduler_control_gate_85080",
      "Saves g8 and g12 at fp+0x50/fp+0x60, tests bit 0 of 0x504e50, restores both registers and returns when set, otherwise continues at 0x850ac.")
label(0x000850ac, "scheduler_ratio_gate_850ac",
      "Masks 0x5024e8 to a byte and uses literal-first cmpobl 10,g4: values above 10 exit to 0x85128, while 0 through 10 continue into the ratio setup.")
label(0x000850c0, "scheduler_ratio_predicate_850c0",
      "Sign-extends the object/related +0x1d0 and +0x1d8 halfwords, forms first/second ratios, subtracts related from object, and exits on nonnegative difference; negative difference continues at 0x85134.")
label(0x00085134, "scheduler_frame_scan_prefix_85134",
      "Selects frame record 0x5096a0 + slot*16 and table row 0x5074a0 + state*1088, derives upper-halfword targets minus 70, masks row field +0x86 with the frame g8 upper-halfword, and branches to 0x853a0 when that masked value is <=49.")
label(0x000851a8, "scheduler_frame_row_global_match_851a8",
      "Masks the selected row's field +0, compares it with 0x504d68, and sets the r7 match flag when equal; unequal rows leave r7 clear.")
label(0x000851c0, "scheduler_frame_row_band_flag_851c0",
      "Masks row field +6 and sets r5 when it is within frame_upper+/-70; for frame_upper <=69 the lower-bound check is bypassed, otherwise the interval is inclusive.")
label(0x00085204, "scheduler_frame_row_secondary_match_85204",
      "Masks row field +4 and the loaded frame g9 low halfword, increments r5 when they are equal, and then reaches the shared 0x847c0 call.")
label(0x0008521c, "scheduler_frame_row_call_setup_8521c",
      "Reloads the original object's +0x74 value into g0, passes fp+0x40 and fp+0x44 in g1/g2, and calls the shared row handler at 0x847c0.")
label(0x0008522c, "scheduler_frame_row_frame_match_8522c",
      "Masks row field +6 to a byte, compares it with the value restored from fp+0x40, and increments r7 on equality.")
label(0x000852ac, "scheduler_frame_scan_terminal_gate_852ac",
      "Branches to 0x853a0 when r5 <= 2 or r7 <= 1; only r5 >= 3 and r7 >= 2 continue at 0x852b4.")
label(0x000852b4, "scheduler_frame_scan_publication_852b4",
      "Sets bit 10 in r10 and publishes row +0x84 to 0x504e44; selector 0..6 dispatches statuses 6,5,4,2,3,1,1, while larger selectors publish caller g14, then restores g8/g12.")
label(0x000853a0, "scheduler_frame_scan_loop_853a0",
      "Increments the row index, advances both scan pointers by 0x88, loops while the new index is <=7, and restores g8/g12 after the eighth failed row.")
label(0x000853c0, "scheduler_frame_decode_853c0",
      "Decodes 0x504e42/0x504e44 into object +0xec +0x1c: bit 8 selects 0x5050a0/state*1152/selector*144+20 versus 0x5074a0/state*1088/selector*136+12, indexes by value_504e44>>2, packs table bits 8-11 into destination bits 12-15 with the low nibble preserved, increments 0x504e44, and resets 0x504e42 above 239 before returning through 0x85494.")
label(0x0008552c, "scheduler_callback_flag_decode_8552c",
      "Extracts the selected word high byte and derives callback g1/g2, g3, and g13 from bit-pair predicates: !4|5, 0|!1, 2|!3, and 6|!7.")
label(0x0008558c, "scheduler_callback_alignment_8558c",
      "Rounds positive 0x504e44 up and nonpositive values down to a 4-byte boundary, computes original-aligned delta, and uses cmpibge 1,delta to select fallback dimensions 8/8 below delta 1.")
label(0x000855b8, "scheduler_callback_global_gate_855b8",
      "Requires 0x503a80 == 0 and 0x504dc0 <= 149, derives 0x503a14/48 + 1, and exits to 0x85678 when 0x503a18 minus that target is <=20; otherwise continues to object-ratio checks.")
label(0x000855f8, "scheduler_callback_object_gate_855f8",
      "Requires signed object +0x1d0 > (+0x1d8 >> 2); when timing difference exceeds 45, computes 0x5024e8 modulo 300 and forces dimensions 1/1 only for remainders above 45.")
label(0x00085634, "scheduler_callback_timing_gate_85634",
      "Recomputes 0x503a14/48 + 1, exits when 0x503a18 minus that target is <=20 or 0x5024e8 modulo 300 is <=90; an earlier difference above 45 with remainder above 45 forces g1/g2 to 1/1, as does the final difference-above-20 and remainder-above-90 path.")
label(0x00085678, "scheduler_callback_selector_gate_85678",
      "Branches to 0x85784 for every decoded low-nibble selector other than 1; selector 1 alone enters the repeated timing/position gate.")
label(0x00085784, "scheduler_callback_selector2_ratio_85784",
      "Branches to 0x857e4 unless selector is 2; selector 2 with 0x504dc0 <=149, object ratio +0x1d0/+0x1d8 >1.65, and dimensions 2/2 changes g1 to 1.")
label(0x000857e4, "scheduler_callback_selector3_ratio_857e4",
      "Branches to 0x85844 unless selector is 3; selector 3 with 0x504dbc <=32, object ratio +0x1d0/+0x1d8 >1.65, and dimensions 2/1 changes g1 to 1.")
label(0x00085844, "scheduler_callback_finalize_85844",
      "Converts g1/g2 to persistent dimensions 1/2/4 using 0x504dac/0x504db0 bit 0, then sets mode bits 3/4/5 from g3/g13 ==16 and source bit 3, storing the results to 0x504dac/0x504db0.")
label(0x000858f0, "scheduler_callback_object_scale_858f0",
      "Snapshots object +0x48/+0x4a at 0x509b8c/0x509b90; unless 0x503a78 is -1, stores caller g14 as the second snapshot, while the -1 case selects related +0x63c/+0x640 for related state 11/14, divides by 100, and scales the second field. The object +0x190 compare is overwritten before this branch and does not gate it.")
label(0x000859b8, "scheduler_callback_result_dispatch_859b8",
      "Masks 0x509b8c to a byte, calls helper 0x86638 (the recovered 0x86630 stage-bucket entry), subtracts 1, exits to 0x85af0 above index 4, and dispatches indices 0..4 to 0x859ec/0x85a20/0x85a54/0x85a88/0x85abc.")
label(0x000859ec, "scheduler_callback_accumulator_update_859ec",
      "The five result handlers divide 0x509b90 by 0x503a78+1, add the quotient to 0x509b24/28/2c/30/34 by dispatch index, clamp at 10000, store, and return.")
label(0x00085af0, "scheduler_callback_result_reject_85af0",
      "Empty reject/return stub reached when the normalized callback result index exceeds 4.")
label(0x00085b00, "scheduler_callback_frame_build_85b00",
      "Loads six published accumulator words, writes scaled callback-frame fields at fp+0x40..0x54, then scans the six values for the three smallest signed entries; a spread above 0x1f3 publishes mode 6, otherwise it publishes the lowest entry index to 0x504e48.")
label(0x00085c00, "scheduler_callback_variant_scale_85c00",
      "Suppresses the signed object +0x4a working value when object +0x190 is nonzero; for related states 11/14, divides related +0x63c/+0x640 by 100 and multiplies the result by object +0x4a.")
label(0x00085d04, "scheduler_callback_table_row_adjust_85d04",
      "For the g2-selected callback-table path, addresses 0x5050a0 + state*1152 + selector*144 + 0x8e, adds 30 to the current halfword, and writes 1000 to the paired row only when its value exceeds 1000.")
label(0x00085e20, "scheduler_callback_table_row_decay_85e20",
      "Addresses the same state/selector row, subtracts 10 from its current halfword, and writes 40 to the paired row when the paired value is <=49; values above 49 take the direct reject/return branch.")
label(0x00085ef8, "scheduler_callback_byte_map_finalize_85ef8",
      "Walks 32 records with 32-byte strides and fills zero odd-byte map entries with the 0x504e42 low nibble plus bit 7 when the object byte/halfword are nonzero and 0x504e42 bit 11 is set.")
label(0x00085f8c, "scheduler_callback_secondary_gate_85f8c",
      "Checks the current outer-loop record's sibling map byte for bit 6 and routes it through 0x86000 when previous bits 9/8/11, current halfword zero, or object byte zero holds; otherwise it routes through 0x860a0, while non-bit-6 records continue through the shared return path.")
label(0x00086000, "scheduler_callback_secondary_primary_86000",
      "Replaces the selected 0x509ad0 bit-6 map entry with g14 before rescanning that map for the original low-nibble collision; a collision exits through 0x86174, while a unique candidate updates 0x5074a0 + state*1088 + selector*136 + 0x86 by +30 and caps the paired row at 1000 when above it.")
label(0x000860a0, "scheduler_callback_secondary_fallback_gate_860a0",
      "Requires the selected map byte's bit 6 and admits the fallback mutation when previous-halfword bit 10 is set or the working scale from 0x85c00 is nonzero; otherwise it exits through 0x86174.")
label(0x000860d4, "scheduler_callback_secondary_fallback_mutation_860d4",
      "Uses the secondary state/selector row, subtracts 10 from the current halfword, writes paired value 40 when it is <=49, and writes callback g14 to the selected 0x509ad0 map entry after its 32-entry low-nibble scan reaches the unchanged candidate before the 0x86174 continuation.")
label(0x00086174, "scheduler_callback_secondary_byte_map_finalize_86174",
      "Walks 32 secondary records with +0x20 strides and fills zero 0x509ad0 odd-byte map slots with (0x504e42 low nibble)|0x40 when the object byte/halfword are nonzero and global bit 11 is set.")
label(0x000861e0, "scheduler_callback_halfword_setup_861e0",
      "Captures return trampoline 0x86238, sign-extends input halfwords into 0x509b94/0x509b98, zeroes the second value when 0x503b18 is zero, and lets nonzero 0x503b1a override it before bx(g2).")
label(0x000865e0, "stage_mode_publication_865e0",
      "Publishes the selected four-word/two-word mode values to previous, current, and active threshold snapshots at 0x509b60/0x509b70, 0x509b20/0x509b30, and 0x509b40/0x509b50, then writes callback g14 to latches 0x509b80/0x509b84/0x509b88.")
label(0x00085c88, "scheduler_callback_byte_map_scan_85c88",
      "Scans 32 odd-byte map entries for bit-7 candidates, applies the primary previous-halfword bit-10 gate or fallback bit-9/8/11/zero tests, replaces a candidate with g14, marks primary-path low-nibble matches with bit 5 before row adjustment, and rejects only fallback-path collisions.")
label(0x00085a20, "scheduler_callback_accumulator_update_85a20", "Alias-shaped accumulator handler storing the clamped quotient sum at 0x509b28.")
label(0x00085a54, "scheduler_callback_accumulator_update_85a54", "Alias-shaped accumulator handler storing the clamped quotient sum at 0x509b2c.")
label(0x00085a88, "scheduler_callback_accumulator_update_85a88", "Alias-shaped accumulator handler storing the clamped quotient sum at 0x509b30.")
label(0x00085abc, "scheduler_callback_accumulator_update_85abc", "Alias-shaped accumulator handler storing the clamped quotient sum at 0x509b34.")
label(0x0008490c, "scheduler_object_ratio_prefix_8490c",
      "Rejects nonzero object +0x190; related state 11 selects object +0x63c and state 14 selects +0x640, divides the selected value by immediate 100, multiplies object +0x4a by that quotient, and exits through 0x84b08 when the product is zero.")
label(0x00084980, "scheduler_record_search_entry_84980",
      "Routes a zero ratio product to 0x84b08; nonzero products initialize 0x509a6c to 1 and enter the eight-record search at 0x84994 with index zero.")
label(0x00084994, "scheduler_record_search_84994",
      "Scans up to eight records with a 16-byte stride, comparing the working target against each record's halfword at +0x8e; when target > record, selects that record and replaces the working target with its value before continuing.")
label(0x000849d0, "scheduler_frame_slot_849d0",
      "Forms the 0x8d2a0 result minus one, replaces it with 180 when nonnegative, subtracts it from 0x509a68, adds 60 when the resulting slot is nonnegative, and scales the frame slot by 16 for 0x5096a0 access.")
label(0x00084a04, "scheduler_frame_row_input_84a04",
      "Loads the selected 0x5096a0 frame halfwords at offsets 0/2/4/6/a, computes the 144-byte destination row from the selected index, and passes the sources plus 240-4*normalized_delay into the 0x84a34 row writer.")
label(0x00084a34, "scheduler_packet_row_84a34",
      "Builds the selected record row at table base + selected index * 144, writes source halfwords at offsets 0xa/0xc/0xe/0x10/0x12, and writes 240 - 4*normalized delay at row offset 0x8c.")
label(0x00084a74, "scheduler_packet_row_copy_entry_84a74",
      "Advances the packet-row source cursor through index 59, wraps it to zero after the upper bound, scales the next index by 16, and enters the bulk row-copy loop at 0x84a80.")
label(0x00084a80, "scheduler_packet_row_copy_84a80",
      "Copies scalar halfwords from the 0x5096a0 frame record to the row, copies 60 +0xc halfwords into row offsets beginning at +0x14, and writes immediate 100 at row offset +0x8e before returning through 0x84b08.")
label(0x00082dd4, "state_service_dispatch_82db0_table",
      "Targets: 0x82df8, 0x82e0c, 0x82e40, 0x82e64, 0x82ea0, 0x82ed4, 0x82f10, 0x82f6c, and 0x82f84.")
label(0x00082d74, "state_scheduler_tail_82d74",
      "Copies the 0x504d80 quadword while clearing its second word; publishes 0x504d90 = 15 when status is unsigned <= 6 or exactly 8, then returns.")
label(0x00082b58, "state_scheduler_dispatch_82b4c_table",
      "44-entry scheduler table; shared reject target is 0x82d68, with handler targets spanning 0x82c08..0x82d48 and final target 0x82d5c.")
label(0x00082040, "state_action_dispatch_82040",
      "Rejects object states above 9, then dispatches states 0..9 through the exact action table at 0x82060.")
label(0x00082650, "state_status_prefix_82650",
      "The exact early prefix writes status 8 for r5/r6 == 0/0, writes 3 or 4 for 0/1 based on 0x504d70 <= 4, and otherwise continues into the state/descriptor path.")
label(0x00082800, "state_handler_dispatch_82800",
      "Unsigned selector <= 9 dispatches through the exact ten-entry table at 0x82818; values above 9 take the shared reject/return path.")
label(0x00082818, "state_handler_dispatch_82800_table",
      "Targets: 0x82840, 0x82874, 0x8288c, 0x828a4, 0x828bc, 0x828d4, 0x828f0, 0x8293c, 0x828e8, 0x82950.")
label(0x00082840, "state_handler_status_82840",
      "Selector handlers use signed remi 3 or 10 and choose status 13, 29, or 30; negative remainders remain signed for the branch thresholds, while selector 0 and negative-global selector 6 consume a second random value on their low-remainder arms.")
label(0x00082954, "state_handler_admission_82954",
      "Status 29/30/31 require control bits 3/4/5 and 0x504dc8 == 1 for the 0x82a10 commit; statuses 13-15 use the negative-global state-6 timing window, with all other cases entering 0x82aac.")
label(0x00082a10, "state_handler_commit_82a10",
      "Normalizes status 13 through 31 into action 6, 16, 17, or 18 and writes -1 and 20 to the paired control cells before publishing the selected action.")
label(0x00082aac, "state_handler_override_82aac",
      "For object state 3, control bit 2 set, and control bits 3/4 clear, rewrites action 6 at 0x504d98 and republishes 20 at 0x504db8.")
label(0x00082060, "state_action_dispatch_82040_table",
      "Ten action targets: 0x82088, 0x820cc, 0x82120, 0x8218c, 0x82248, 0x82330, 0x823cc, 0x824b8, 0x82534, and 0x825c0.")
label(0x00081eb4, "state_dispatch_81e60_table",
      "Ten state targets: 0x81edc, 0x81ee8, 0x81ef4, 0x81f00, 0x81f0c, 0x81f18, 0x81f24, 0x81f30, 0x81f3c, and 0x81f48.")
label(0x0007eab0, "state31_threshold_dispatch_table",
      "Eight selector targets at 0x7eab0: threshold sources 0x504e3c, 0x504e40, 0x504e3c, 0x504e3e, 0x504e40, 0x504e3c, 0x504e40, and 0x504e40.")
label(0x000017c8, "startup_device_mode_select")
label(0x00001348, "startup_device_mode_enable")
label(0x00001380, "startup_device_mode_transition",
      "Clears the requested source mask from the host-control mirror and MMIO, then routes exact masks 1/2/0x800/0x200/0x400 to their system, fatal, text, and audio paths while acknowledging other sources.")
label(0x00001424, "startup_mode_one_device_sequence",
      "Mask-1 dispatcher continuation: calls video transfer 0x1c2c0, upload selector 0x29d50, asset helper 0xe2330, audio record/status upload 0x29b20, then input initializer 0x2cb0 before returning to the common tail.")
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
label(0x00070000, "geometry_command_packet_builder_variant_b",
      "Callback-style packet builder: emits caller vector words and fixed 0x01540601/0x7f000000/1.0 fields through 0x804000, then branches through g7.")
label(0x000700e0, "geometry_command_packet_builder_variant_c",
      "Emits fixed 0x202 setup, 1.0 and 0x01540601/0x7f000000 constants, followed by caller vector words through 0x804000.")
label(0x000701a0, "geometry_clip_packet_builder",
      "Selects one of four signed coordinate-ordering arms, emits the matching geometry packet through 0x804000, and converges on the shared internal tail at 0x70950.")
label(0x00070970, "geometry_extended_packet_builder",
      "Builds the extended multi-command geometry packet sequence through 0x804000, including transformed coordinate pairs and fixed 1.0/0x01540601 fields.")
label(0x00070c80, "geometry_command_packet_builder_variant_d",
      "Emits the extended geometry packet variant through 0x804000, initializing four frame words before publishing transformed coordinate fields.")
label(0x00070fc0, "geometry_command_packet_builder_variant_e",
      "Emits a compact geometry packet through 0x804000 with caller coordinates, fixed 1.0/0x01540601/0x7f000000 fields, and a final frame word.")
label(0x00071080, "geometry_object_match_update",
      "Match-phase object geometry update: reads the object record, derives transformed frame values, emits geometry packets through 0x884000/0x804000, and updates the associated runtime counters.")
label(0x00072c00, "match_object_state_service",
      "State-gated object service: checks match mode and object fields, dispatches object-side services, updates shared result/status fields, and returns through its frame epilogue.")
label(0x00072c10, "match_state_geometry_orchestrator",
      "Gates geometry work, invokes threshold/transition services, funnels through the match-result cluster, and publishes the final result pair.")
label(0x00072ea0, "match_state_result_service",
      "Match-state/result service: selects mode-dependent parameters, updates shared result fields and object state, and emits the resulting command data.")
label(0x00073498, "match_result_counter_service",
      "Increments the second word of the 0x504db0 pair through the supplied limit; on overflow stores 0xffffffff, clears 0x504d9c, conditionally clears 0x504da4, and returns through g6.")
label(0x000735d0, "match_result_state_dispatch",
      "If 0x504e42 is nonzero, diverts to 0x853c8; otherwise bounds 0x504d94 at 33 and selects the exact 34-entry target table rooted at 0x73618, with 0x74848 as the default route.")
label(0x000736a0, "geometry_profile_handler_0",
      "Profile-table handler 0: scans nine geometry records, emits selector 29/30 packets, classifies residuals, and branches to the shared continuation.")
label(0x000737c8, "geometry_profile_handler_1",
      "Profile-table handler 1: scans nine geometry records with its profile-specific packet bit and branches to the shared continuation.")
label(0x00073900, "geometry_profile_handler_2",
      "Profile-table handler 2: scans nine geometry records with its profile-specific packet bit and branches to the shared continuation.")
label(0x00073a34, "geometry_profile_handler_3",
      "Profile-table handler 3: scans nine geometry records with its profile-specific packet bit and branches to the shared continuation.")
label(0x00073b68, "geometry_profile_handler_4",
      "Profile-table handler 4: scans nine geometry records with its profile-specific packet bit and branches to the shared continuation.")
label(0x00073c98, "geometry_profile_handler_5",
      "Profile-table handler 5: scans nine geometry records with its profile-specific packet bit and branches to the shared continuation.")
label(0x00073dcc, "match_state_handler_6",
      "State-table handler 6: applies the mode/status gate, updates the shared packet selector, and branches or returns through the common result path.")
label(0x00073fdc, "match_state_handler_7",
      "State-table handler 7: derives a mode-indexed status value and updates the shared result selector, with local early-return arms.")
label(0x00073ffc, "match_state_handler_8",
      "State-table handler 8: selects a mode-indexed parameter, publishes selector 5, and stores the resulting status value.")
label(0x0007402c, "match_state_handler_9",
      "State-table handler 9: applies the object-state gate and publishes status selector 10 or the default bit-10 marker.")
label(0x0007408c, "match_state_handler_10",
      "State-table handler 10: mirrors the neighboring object-state gate and publishes status selector 4 or the default bit-2 marker.")
label(0x000745bc, "match_state_handler_11",
      "Status-table handler 11: adjusts the shared status selector from the signed result counter and returns or branches to the common path.")
label(0x000745e4, "match_state_handler_12",
      "Status-table handler 12: publishes the bit-10 marker and conditionally updates the shared result selector.")
label(0x0007460c, "match_state_handler_13",
      "Status-table handler 13: publishes selector 4 and conditionally updates the shared result selector.")
label(0x00074634, "match_state_handler_14",
      "Status-table handler 14: gates on object state and counter phase before publishing selector 0x206.")
label(0x00074674, "match_state_handler_15",
      "Status-table handler 15: gates on object substate, updates the counter and selector, and returns through the shared path.")
label(0x000746f4, "match_state_handler_16",
      "Status-table handler 16: applies the neighboring counter/substate gate and publishes its state selector.")
label(0x00074754, "match_state_handler_17",
      "Status-table handler 17: evaluates the result counter and object substate before writing the status selector.")
label(0x0007479c, "match_state_handler_18",
      "Status-table handler 18: handles the alternate counter/substate arm and publishes its status value.")
label(0x000747e4, "match_state_handler_19",
      "Status-table handler 19: final compact status arm before the shared 0x74848 continuation.")
label(0x00074848, "match_state_default_reject",
      "Shared status-table reject path: writes 0xffff to the caller status field and returns immediately.")
label(0x00074860, "match_status_transition_update",
      "Computes shared status/result command fields from mode, counter, object flags, and alignment state before returning at 0x74e50.")
label(0x00076b00, "match_geometry_state_transition",
      "Geometry-state transition entry called by 0x72c10; returns immediately when object field +0x64 equals 9 before its state-dependent updates.")
label(0x00074e60, "match_transition_state_dispatch",
      "Clamps the shared transition counter, stores its boolean result, and dispatches through the eight-entry state table at 0x74ea4.")
label(0x00074ec4, "match_transition_handler_0",
      "Transition-table handler 0: updates the threshold boolean and selects state 3 before the shared continuation.")
label(0x00074ef0, "match_transition_handler_1",
      "Transition-table handler 1: updates the threshold boolean, clears the auxiliary field, and selects state 3.")
label(0x00074f28, "match_transition_handler_2",
      "Transition-table handler 2: stores the threshold boolean for the shared transition state.")
label(0x00074f3c, "match_transition_handler_3",
      "Transition-table handler 3: stores the alternate threshold boolean for the shared transition state.")
label(0x00074f60, "match_transition_handler_4",
      "Transition-table handler 4: initializes the transition state and selects the zero/nonzero auxiliary path.")
label(0x00074fa0, "match_transition_handler_5",
      "Transition-table handler 5: selects state 6 and initializes the transition auxiliary fields.")
label(0x00074fc8, "match_transition_handler_6",
      "Transition-table handler 6: applies the object-state/counter threshold and selects the shared transition state.")
label(0x00075048, "match_transition_handler_7",
      "Transition-table handler 7: applies the high-counter threshold, selects state 3 or 6, and updates auxiliary fields.")
label(0x0007510c, "match_transition_counter_clamp",
      "Out-of-range transition clamp: converts the shared counter threshold to a boolean, selects state 3, and joins the common continuation.")
label(0x00075134, "match_transition_common_update",
      "Common transition update: advances the shared counter, schedules the next service, applies the floating timing gate, and returns through its local epilogues.")
label(0x00075200, "match_geometry_range_update",
      "Updates the match geometry range state by classifying the object coordinate, then returns immediately for the zero classification.")
label(0x00077470, "match_geometry_profile_dispatch",
      "Consumes object +0x1c4 and signed +0x18e with 0x504d94/0x504db4 state, then dispatches through the 21-entry profile table at 0x77508.")
label(0x00075230, "match_result_phase_selector",
      "Selects a result phase through the compact table at 0x75294, publishes the selected status value, advances the shared phase counter, and returns.")
label(0x00075300, "match_phase_advance_update",
      "Advances the phase index, classifies the selected coordinate, refreshes shared result fields, and returns at 0x75398.")
label(0x00075404, "match_phase_selector_arm_0",
      "Nested phase-table arm: selects status value 5 and joins the common phase continuation.")
label(0x0007540c, "match_phase_selector_arm_1",
      "Nested phase-table arm: selects status value 4 and joins the common phase continuation.")
label(0x00075414, "match_phase_selector_arm_2",
      "Nested phase-table arm: selects status value 10 and updates the shared phase fields.")
label(0x00075424, "match_phase_selector_arm_3",
      "Nested phase-table arm: selects status value 9 and joins the common phase continuation.")
label(0x0007542c, "match_phase_selector_arm_4",
      "Nested phase-table arm: selects status value 16 and joins the common phase continuation.")
label(0x00075434, "match_phase_selector_arm_5",
      "Nested phase-table arm: selects status value 17 and joins the common phase continuation.")
label(0x00075450, "match_phase_substate_dispatch",
      "Normalizes the nested phase/substate index and dispatches through the 13-entry table at 0x75474.")
label(0x000754ac, "match_phase_substate_arm_0",
      "Substate-table arm: selects phase value 5 and joins the shared phase continuation.")
label(0x000754b4, "match_phase_substate_arm_1",
      "Substate-table arm: selects phase value 1 and joins the shared phase continuation.")
label(0x000754bc, "match_phase_substate_arm_2",
      "Substate-table arm: selects phase value 8 and joins the shared phase continuation.")
label(0x000754c4, "match_phase_substate_arm_3",
      "Substate-table arm: selects phase value 14 and joins the shared phase continuation.")
label(0x000754cc, "match_phase_substate_arm_4",
      "Substate-table arm: selects phase value 15, updates the secondary phase value, and returns.")
label(0x000754e4, "match_phase_substate_default",
      "Substate-table default arm: returns without changing the selected phase value.")
label(0x00075cf0, "match_phase_substate_common_update",
      "Shared phase-substate continuation: publishes the selected status at 0x504d94.")
label(0x00075cf8, "match_phase_substate_counter_return",
      "Phase-substate counter return: writes counter value 10 to 0x504db8 and returns.")
label(0x00075d08, "match_phase_counter_dispatch",
      "Phase-counter dispatcher: normalizes 0x504d94 and selects one of five counter/status arms.")
label(0x00075bbc, "match_phase_secondary_selector",
      "Parallel phase selector: normalizes r4 and 0x504d94 through the 0x75be0 table.")
label(0x00075c58, "match_phase_late_selector",
      "Late phase selector: subtracts five from r4 and dispatches normalized status through 0x75c7c.")
label(0x00075cb4, "match_phase_late_arm_0",
      "Late phase arm: selects status value 5 and joins the shared status writer.")
label(0x00075cbc, "match_phase_late_arm_1",
      "Late phase arm: selects status value 1 and joins the shared status writer.")
label(0x00075cc4, "match_phase_late_arm_2",
      "Late phase arm: selects status and counter value 10, then returns.")
label(0x00075cdc, "match_phase_late_arm_3",
      "Late phase arm: selects status value 8 and joins the shared status writer.")
label(0x00075ce4, "match_phase_late_arm_4",
      "Late phase arm: selects status value 14 and joins the shared status writer.")
label(0x00075c1c, "match_phase_secondary_arm_0",
      "Parallel phase arm: selects status value 5 and joins the shared status writer.")
label(0x00075c24, "match_phase_secondary_arm_1",
      "Parallel phase arm: selects status value 4 and joins the shared status writer.")
label(0x00075c2c, "match_phase_secondary_arm_2",
      "Parallel phase arm: selects status value 9 and joins the shared status writer.")
label(0x00075c34, "match_phase_secondary_arm_3",
      "Parallel phase arm: selects status value 16 and joins the shared status writer.")
label(0x00075c3c, "match_phase_secondary_arm_4",
      "Parallel phase arm: selects status value 17 and publishes counter 10.")
label(0x00075d60, "match_phase_counter_arm_0",
      "Phase-counter arm: selects status value 6 and rejoins the shared status writer.")
label(0x00075d68, "match_phase_counter_arm_1",
      "Phase-counter arm: selects status value 1 and rejoins the shared status writer.")
label(0x00075d70, "match_phase_counter_arm_2",
      "Phase-counter arm: selects status value 11 and rejoins the shared status writer.")
label(0x00075d78, "match_phase_counter_arm_3",
      "Phase-counter arm: selects status value 8 and rejoins the shared status writer.")
label(0x00075d80, "match_phase_counter_arm_4",
      "Phase-counter arm: selects status value 14 and rejoins the shared status writer.")
label(0x00075d88, "match_phase_counter_default",
      "Phase-counter default arm: returns without changing the selected status.")
label(0x00075d90, "stage_selector_setup",
      "Selects the stage mode selector, derives the stage-table index and geometry scale, computes bounded 0x504dbc/0x504dc0 timing values, and seeds shared stage setup fields; the row-copy tail begins at 0x75fe4.")
label(0x00075fe4, "stage_selector_descriptor_copy",
      "Indexes the 0x72050 descriptor table by object state and copies the selected 18-word, 0x48-byte record into 0x504dd4..0x504e1c; the pure copy contract is recovered as object_state_descriptor_75f00.")
label(0x00076030, "stage_post_setup_call",
      "Calls 0x86240 after descriptor copying, marks 0x504e1c complete, publishes the related-object packed 14-byte profile at 0x504e34, conditionally replaces it from the current-object profile table, and clears stage status latches at 0x504e42/0x504e44.")
label(0x000760c0, "stage_profile_setup_related_record",
      "Indexes the packed 14-byte profile table at 0x72370 by related-object state +0x64, publishing its 8-byte value, word, and halfword into 0x504e34/0x504e3c/0x504e40.")
label(0x00076128, "stage_profile_setup_current_record",
      "When global 0x5039f4 is not four, selects one of the 0x503a98/0x503a9c row selectors by current-object +0x68, indexes the same 0x72370 profile table, and overwrites the related profile result window.")
label(0x000761b0, "geometry_object_threshold_query",
      "Consumes 0x504dc0, maps its bounded stage threshold through four IEEE-754 constants, emits geometry selector 29, and continues with the object-relative command-10 query and signed residual checks.")
label(0x000761d0, "geometry_object_threshold_query_band_45000000",
      "Selects 0x45000000 for counters through 0x54, including the initial <=0x4f/<=0x54 branches.")
label(0x000761f0, "geometry_object_threshold_query_band_45800000",
      "Selects 0x45800000 for counters 0x55 through 0x59.")
label(0x00076204, "geometry_object_threshold_query_band_46000000",
      "Selects 0x46000000 for counters 0x5a through 0x5e.")
label(0x00076218, "geometry_object_threshold_query_band_46800000",
      "Selects the final 0x46800000 threshold for counters above 0x5e, then emits selector 29 at 0x76234.")
label(0x0007669c, "geometry_object_threshold_query_left",
      "Calls geometry_object_threshold_query for the first object after publishing the paired signed displacement bands at 0x504d64/0x504d68, then stores its result at 0x504dcc.")
label(0x000766dc, "geometry_object_threshold_query_right",
      "Calls geometry_object_threshold_query for the second object after publishing the second signed displacement band at 0x504d6c/0x504d70; the shared query result continues into the projection setup.")
label(0x00076240, "geometry_fifo_argument_prefix",
      "Sign-extends object coordinate +0x184, forms the 16-bit-wrapped plus/minus 0x6000 arguments, and begins the command-29/30 FIFO request sequence.")
label(0x00076340, "geometry_fifo_response_transform",
      "Continues the command-29/30 response reads into masked coordinates and the floating-point cross-product/sign-selection sequence; response semantics remain hardware-boundary evidence.")
label(0x00076590, "geometry_object_cross_request_pair",
      "Builds reversed command-10 request pairs from current/related object offsets +0x08/+0x10, subtracts the two FIFO responses from signed +0x184 coordinates, and feeds the low halfwords through 0x73508.")
label(0x00076624, "geometry_object_cross_request_band_left",
      "Stores the first signed coordinate delta at 0x504d64 and its ten-band classification at 0x504d68 before preparing the reversed request pair.")
label(0x00076678, "geometry_object_cross_request_band_right",
      "Stores the second signed coordinate delta at 0x504d6c and its ten-band classification at 0x504d70 before entering the threshold query.")
label(0x00076808, "geometry_projection_threshold_reclamp",
      "Recomputes the 0x504dc0 threshold from quantized projection g4 and r4, selecting the 3/2 or 100 base, adding 0x50+r4, clamping to 300, and forcing nonpositive results to 1.")
label(0x00076848, "geometry_projection_threshold_publish",
      "Publishes the re-clamped projection threshold at 0x504dc0 before the mode-dependent object-state gates.")
label(0x00076858, "geometry_projection_mode_threshold_gates",
      "For mode != 1, applies the object +0x1d0/+0x1d8 and 0x503a14/0x503a18 span gates before raising 0x504dc0 to 101; then applies the r4 <= 2 and r4 <= 4 raises to 90 and 100.")
label(0x000768b8, "geometry_projection_low_r4_threshold_gates",
      "Applies the final low-r4 threshold guards: thresholds above 85 become 90 for r4 <= 2, and thresholds above 90 become 100 for r4 <= 4.")
label(0x000768f4, "geometry_related_threshold_bias",
      "Adds 10 to 0x504dc0 when related-object state +0x64 is 0, 3, 4, or 6, or when global stage ordinal 0x503a80 is 2; otherwise preserves the threshold.")
label(0x00076934, "geometry_profile_result_pair_dispatch",
      "Passes the current and related objects through the shared 0x778b0 profile-result helper using shared fp+0x40/fp+0x44 outputs, publishes 0x504e20/0x504e24 and 0x504e28/0x504e2c, then synthesizes 0x504e30 from object flag bits.")
label(0x000778b0, "match_profile_result_select",
      "Scans eight six-byte 0x505060 records, rejects zero +4 entries and wrapped gate values above 0x7ffe, then retains the first strict minimum returned metric before the packet path at 0x779f0.")
label(0x000779f0, "match_profile_packet_prefix",
      "Indexes the selected six-byte 0x505060 record and emits the fixed command-31 prefix [31, converted record +0, object +0x08, converted record +2, object +0x10], reads its response at 0x77a5c, and then prepares command 29.")
label(0x00077a64, "match_profile_command29_30_pair",
      "Adds 0x3000 to the command-31 response, masks the result to 16 bits, and emits matching three-word command-29 and command-30 requests with converted record +4 before the response read at 0x77af0.")
label(0x00092830, "geometry_fifo_packet_template_site_a",
      "Emits the fixed 12-word command-5/18/21/19 FIFO packet, masks g3 to its low halfword, and tail-calls 0x8e310 with site-specific base 0x02b4a4bc, offset 0x98750, and [0x562494].")
label(0x000929e4, "geometry_table_service_multiarm_929e4",
      "Loads divisor/table source 0x5624b0, tests g7-0x3c, g7-0x46, and g7-0x50 against 15<<3, and routes to the 0x929fc, 0x92b2c, or 0x92c5c table packet arms with b800/c000/c800 operands; an all-clear path converges at 0x92d84.")
label(0x00092da0, "geometry_fifo_packet_service_92da0",
      "Builds the shared 0x92db0 command-5/18/21/19 packet after dividing the persistent source at 0x5624b8 by the caller-provided divisor; later remainder/table dispatch and 0x8e310 service selection remain bounded separately.")
label(0x00092db0, "geometry_fifo_packet_service_92da0_prefix",
      "Emits [5,18,g0,g1,g2,21,g3&0xffff,19,0.2f,0.2f,0.2f] while retaining the divi quotient used by the following modulo/table branches.")
label(0x00093240, "geometry_fifo_float_prologue",
      "Selects a low/high real-arithmetic leg from (g3 + 0xbfff) & 0xffff, adjusts the persistent 0x562530 float by +/-0.2 with +/-30.0 fallbacks, emits the 12-word command-5/18/21/19 packet, and tail-calls 0x8e310 with modulo-30 state.")
label(0x000934b0, "geometry_fifo_packet_template_site_b",
      "Emits the matching fixed 12-word command-5/18/21/19 FIFO packet, masks g3 to its low halfword, and tail-calls 0x8e310 with base 0x02b68d3a, offset 0x79e2a, and [0x562490].")
label(0x00093560, "geometry_fifo_packet_sequencer",
      "Emits the shared 11-word command-5/18/21/19 FIFO prefix, selects the C8-gated modulo-120 or modulo-168 tail sequence using 0x5624c8/0x5624cc, tail-calls 0x8e310 once, then emits completion selector 6.")
label(0x000935d8, "geometry_fifo_packet_sequencer_c8_gate",
      "When 0x5624cc is zero, advances 0xf5058 and stores its low two bits into 0x5624c8 before selecting the modulo-120 or modulo-168 path.")
label(0x00093624, "geometry_fifo_packet_sequencer_mod168",
      "Advances 0x5624cc modulo 168 and applies the exact 59/23/59 unsigned branch mapping to the 0x8e310 third argument.")
label(0x000936b8, "geometry_fifo_packet_sequencer_mod120",
      "Advances 0x5624cc modulo 120 and selects base 0x02b5c3a6 or 0x02b60728 from C8, with shared second argument 0x02be2b64.")
label(0x00092730, "geometry_fifo_packet_stateful_site_a",
      "Emits the stateful 13-word command-5/44/21/19 FIFO packet with both g14 payload words, toggles the 0x5624f0 cell through the 0xf5058 result, and tail-calls 0x8e310 with the selected 0x02b53ca2 base variant.")
label(0x000933b0, "geometry_fifo_packet_stateful_site_b",
      "Twin stateful command-5/44/21/19 FIFO packet site using the alternate 0x5624ac/0x5624f4 RAM cells; shares the g14/toggle/tail contract with 0x92730.")
label(0x00086240, "stage_post_setup",
      "Normalizes stage-dependent threshold words into 0x509b20..0x509b50, maintains active/previous stage snapshots, initializes stage tables, and dispatches mode-specific setup data; exact hardware/object ownership remains a separate bounded target.")
label(0x00086438, "stage_working_table_clear",
      "Clears the packed 0x5096a0 halfword lanes, 0x509a60 seed words, two 0x40-byte stage byte tables, and scalar latches before mode-specific setup; lane layout is modeled as a write plan.")
label(0x00086534, "stage_mode_seed_dispatch",
      "Gates mode-specific threshold publication on nonzero stage and zero 0x503a74, then dispatches the mode byte to four fixed preset arms.")
label(0x00086570, "stage_mode_seed_1",
      "Publishes preset (0x2bd, 0x1f5, 0x1f5, 0x1f5; pair 0x1f5/0x1f5) to the stage threshold and snapshot fields.")
label(0x0008658c, "stage_mode_seed_2",
      "Publishes preset (0x9c5, 0x5dd, 0x4b1, 0x5dd; pair 0x7d1/0x5dd) to the stage threshold and snapshot fields.")
label(0x000865a8, "stage_mode_seed_3",
      "Publishes the signed negative sentinel 0xfffffd44 to all four threshold words and both pair words.")
label(0x000865c8, "stage_mode_seed_default",
      "Publishes zero to all four threshold words and both pair words for unrecognized mode bytes.")
label(0x00086630, "stage_bucket_helper",
      "Maps a nonnegative stage/profile counter through the (value - 1) modulo-6 residue: residues 1..3 return 4, residue 4 returns 3, and residues 0/5 select the ceiling bucket from the byte table at 0x842a0.")
label(0x000866c0, "stage_record_tables_initialize",
      "Boot-time initializer called at 0x189f8: constructs eight batches of eight packed records (64 per table) at 0x5050a0 and 0x5074a0 by storing incoming g14 into the proven lanes using the 0x86810 cursor gate, then clears the stage working tables and threshold/snapshot globals before returning at 0x86958; record-field semantics remain unresolved.")
label(0x00086810, "stage_record_tables_reset_tail",
      "Reset tail of the boot initializer: conditionally repeats the packed stage working-table clear, zeros threshold/current and active/previous snapshot groups at 0x509b20..0x509b70, clears guards 0x509b80..0x509b88, and clears scalar latches before returning at 0x86958.")
label(0x00086828, "stage_record_tables_working_clear",
      "Packed halfword/byte clear loop shared in shape with the 0x86240 stage post-setup clear; destination ownership remains address-specific until the initializer's record layout is recovered.")
label(0x000868f0, "stage_record_tables_snapshot_zero",
      "Zeroes the 0x509b60/0x509b70 previous snapshot, 0x509b20/0x509b30 current values, 0x509b40/0x509b50 active snapshot, and 0x509b80..0x509b88 guards.")
label(0x00086960, "stage_asset_dispatch_86960",
      "Adds 31 to the two incoming helper arguments, selects descriptor 0x2fd8872 or 0x2fd8876 from 0x504e42 bits 8/9/10, and dispatches with g1=1,g2=2: bit 8 uses 0x1dc10, bit 9 uses 0x1d7d0, and the remaining path uses 0x1dc10.")
label(0x000869d0, "stage_callback_dispatch_869d0",
      "Preserves the input through frame builder 0x85b00, invokes helper 0x1cac8 with g0=10 and the saved input as g1, then dispatches selectors 0..6 through the 0x869fc table; selectors above 6 return, with descriptor bytes at 0x869c8/0x869ca and targets 0x1d7d0/0x1d9e0/0x1d880/0x1d930.")
label(0x00086a90, "stage_service_prologue_86a90",
      "Publishes g14 to 0x503a60 and the low halfword of 0x504b94, then calls 0xde630, 0xc8f10, 0x6fec0, 0x9b308, 0x6fec0, and 0xc8f60 in order; both 0x6fec0 calls receive g0=0 before fall-through to 0x86ac0.")
label(0x00086ac0, "stage_asset_copy_gate_86ac0",
      "Calls 0x9baa0 with g0=0x503ad0, then enables two 0x600-byte 0xf5d40 copies only when 0x503a04 equals 0x5a: 0x51c9e0 to 0x503ad0 and 0x51cfe0 to 0x5040d0 before continuing at 0x86b0c.")
label(0x00086b80, "stage_optional_buffer_cleanup_86b80",
      "Tests 0x503a7c and calls 0xdf070 with 0x5040d0 only when the control value is zero; nonzero values skip to 0x86b98.")
label(0x00086b98, "stage_post_copy_tail_86b98",
      "Runs 0xbece0, 0x9b320, 0x41f20, and 0xc5530, copies halfwords 0x51cbb0/0x51d1b0 to 0x503ca0/0x5042a0, calls 0x23d60 with g0=1, then calls 0x71080 with g0=0x503ad0 before 0x86be4.")
label(0x00086be4, "stage_post_copy_route_gate_86be4",
      "Requires 0x503a04 to equal the preserved 0x5a marker; then routes to 0x86c08 when 0x503ca2 is zero or 0x5042a2 is zero, otherwise to 0x86c64, while a marker mismatch routes to 0x86cb8.")
label(0x00086c08, "stage_publication_map_86c08",
      "Publishes 0x51c9a4/0x51c9ac from 0x503aa4: the 0x86c08 path maps 0/1/2/other to (12,1)/(19,0xb4)/(12,0xb4)/(19,0xb4), while the 0x86c64 path maps 0 or 1 to (12,1) and all other values to (12,0xb4), then converges at 0x86cb8.")
label(0x00086cb8, "stage_countdown_gate_86cb8",
      "Decrements 0x503a04 and routes to 0x86d38, where 0x1fe90 receives inherited g0, when the result is zero, when a result through 0x57 has bit 4 set in 0x5024a4, or when nonzero 0x503a7c permits the 0x5024f4 exception word values 0x60/0x62; otherwise returns at 0x86db4.")
label(0x00086d38, "stage_clear_publication_86d38",
      "After the clear-service gate, calls 0x1fe90 with inherited g0, then 0x1f080 with g0=0 and 0x423a8; publishes 0x51c9a4/0x51c9ac to 0x503a00/0x503a04, sets 0x503a60, selects 0x60 or 0x62 for 0x5032f4 from 0x503a70 versus 0x503a78, and stores g14 at 0x51c942/0x51d5e0/0x51c9c0 before returning at 0x86db4.")
label(0x00086df0, "stage_slot20_timing_86df0",
      "Normalizes 0x51c9b0: indices through 0x77 preserve the marker/timing pair, while larger indices use remainder modulo 120 and a 4-byte group bucket, substitute g14 when the bucket reaches 120, clamp the state by one 120-step, and publish 0x51d5e4/0x51d5e8 before 0x86e74.")
label(0x00086b0c, "stage_post_copy_services_86b0c",
      "Runs the fixed post-copy services 0xde990, 0xbe1f0, 0xbd730, callx(0x503ad4), 0x23980, 0xdf070, 0x26cb8, 0xbd810, and callx(0x5040d4), using 0x503ad0 for the first buffer group and 0x5040d0 for the second before the 0x86b80 gate.")
label(0x000189f8, "startup_stage_record_tables_call",
      "Boot sequence call into stage_record_tables_initialize at 0x866c0 after device/video setup and before the startup loop continuation.")
label(0x000842a0, "stage_bucket_table_842a0",
      "48-byte stage/profile bucket result table consumed by stage_bucket_helper at 0x866a4; extracted ROM bytes are modeled by recovered_stage_bucket_86630.c.")
label(0x005050a0, "stage_record_table_5050a0",
      "First boot-built packed stage record table: 64 0x90-byte sparse records initialized in eight batches by stage_record_tables_initialize at 0x866c0.")
label(0x005074a0, "stage_record_table_5074a0",
      "Second boot-built packed stage record table: 64 0x88-byte sparse records initialized in eight batches by stage_record_tables_initialize at 0x866c0.")
label(0x000881b8, "stage_slot_update",
      "Reduces 0x51c9b0 modulo 120, scales the slot by 12 bytes, and stores caller words at offsets +4 and +8 in the 0x561e90 table before returning through the local thunk at 0x881f4.")
label(0x00072e90, "stage_slot_update_call",
      "Loads the two publication words from 0x504dac and 0x504db0, then calls stage_slot_update at 0x881b8.")
label(0x00561e90, "stage_slot_table_561e90",
      "120-entry, 12-byte stage publication table indexed by 0x51c9b0 modulo 120; the 0x881b8 helper writes words at offsets +4 and +8.")
label(0x0009b288, "command_record_write",
      "Selects record ((0x562b70 & 0xf) * 16) at 0x562b80, writes active=1/reserved=0, copies caller offsets 0x8/0x10/0x14/0x18 into record offsets 0x2/0x4/0x8/0xc, and advances the normalized cursor.")
label(0x0009b320, "command_record_scan",
      "Scans all sixteen records at 0x562b80, emits the selected-record packet for each nonzero active byte, then clears the active byte when bits 5-7 are absent or increments it otherwise; packet/FPU/MMIO details remain separate.")
label(0x00562b70, "command_record_cursor",
      "Rolling command-record cursor normalized to its low nibble by command_record_write at 0x9b288.")
label(0x00562b80, "command_record_table",
      "Sixteen 16-byte command records populated by command_record_write at 0x9b288 and scanned by the adjacent command emitter.")
label(0x000bd5a8, "startup_table_copy",
      "Copies ROM blocks of 39, 0x99b, 0x333, and 0x3fff words into 0x565e30, 0x562cb0, 0x565ed0, and 0x566ba0, then emits FIFO word 0x44 and stores 0xffffffff at 0x577170.")
label(0x000189f4, "startup_table_copy_call",
      "Boot call into startup_table_copy at 0xbd5a8 immediately before stage_record_tables_initialize at 0x866c0.")
label(0x000bd6b8, "object_table_reset",
      "Clears 32 bytes at object offset 0x200, clears 0x576ba0 when the object equals 0x503ad0 or 0x576ba4 otherwise, and always clears 0x576ba8.")
label(0x000bd730, "object_dispatch_prelude",
      "Copies 0x576ba8 to 0x576ba4, scans 32 object-table entries at offset 0x200, accepts byte values through 0xcc, looks up 0xbcf40[index*8], masks record halfwords with 0xffe0, and rejoins after the indirect dispatch/error path.")
label(0x000bd810, "object_dispatch_prelude_alt",
      "Copies 0x576ba8 to 0x576ba0, returns when 0x503a7c is nonzero, otherwise scans 32 object-table entries, dispatches accepted values through 0xbcf40[index*8], uses context base 0x5658a0 with 0x2c stride, masks halfwords with 0xffe0, and republishes 0x576ba4 to 0x576ba8.")
label(0x000bf2f0, "geometry_constant_packet",
      "Requires 0x503a08 == 2, matches object byte 0 and halfword 0x4 against 0xc4f40[index*8] or its predecessor, then emits the fixed 5/16/18 packet with 1.0 and 58, control 0x101, window quad [0,0x40005c,0x8f31a0,0], completion 6, and readback publication at 0x801008.")
label(0x000bd8e0, "object_dual_admission",
      "Scans 32 object-linked entries: requires a nonzero active byte, bit 15 set in the preceding halfword at object+0x202, and bit 15 clear in the current halfword at object+0x204; admitted entries emit selector 72, linked fields +0xc/+0x10/+0x14, and mode-table fields +0x24/+0x28 before the paired-object packet path.")
label(0x0009c050, "geometry_descriptor_select",
      "Reuses the normalized grid-index arithmetic for current and linked coordinates, accepts indices through 0x23f, falls back to table entry zero through 0x9ba50 otherwise, and publishes values into 0x562c80 and 0x562c84.")
label(0x0008d400, "geometry_batch_packet",
      "Builds the per-record geometry FIFO packet, masks record halfwords and the computed source-table value, stores record words +0/+0x4 and sign-extended record halfword +0x6 in the 0x804000 command window, and publishes the 0x802008 readback plus 0x34 at 0x801008.")
label(0x0008d5d0, "geometry_indexed_packet",
      "Builds the indexed geometry prefix: compares the signed object +0x4 index with incoming g2, uses g2 above the bound or index-1 otherwise, forms a 12*adjusted-index*object-signed(+0x6) table offset, sign-extends and negates the first three selected-record ldos coordinates as full 32-bit values, preserves sign extension for the final three selected-record ldos values before XORing bit 15, and gates the 0x8d6ec continuation after absolute-value normalization of the object signed +0x6; that continuation processes N-1 records with source offset 12 and destination offset 12*N when N>1.")
label(0x0008d6b8, "geometry_indexed_packet_8d6b8_record_header",
      "Indexed geometry record header: advances the 12-byte record cursor, emits command 47, XORs three record halfwords with the per-record mask, and branches to 0x8d848 or the indexed record body at 0x8d6ec.")
label(0x0008d6ec, "geometry_indexed_packet_8d6ec_record_gate",
      "Indexed geometry record gate: advances source/table cursors, computes the 12-byte-stride record address, tests the active word, and routes inactive records to 0x8d834 or active records to 0x8d704.")
label(0x0008d704, "geometry_indexed_packet_8d704_record_emit",
      "Indexed active-record emitter: builds the 13-word 5/47/22/21/20/58 packet from masked and sign-extended record fields, writes the 0x804000 window and 0x800010=0x101 control, emits completion 6, and loops at 0x8d704 or returns at 0x8d848.")
label(0x0008d850, "geometry_indexed_batch",
      "Returns before emission for zero absolute signed count; otherwise builds the indexed batch packet with selectors 5/47/22/21/20/58, masked source halfwords, command-window words from the current record, and control 0x101/completion 6; it uses the bounded 12*adjusted-index*signed(+0x6) lookup and traverses N records from the first record when the absolute signed count N is positive.")
label(0x0008da60, "geometry_indexed_packet_variant",
      "Returns before emission for zero absolute signed count; otherwise builds the sibling indexed prefix with selectors 20/21/22 followed by selector 58 and three sign-extended halfwords XORed with bit 15, publishes the selected record dword and +0x8 word to 0x562480/0x562488, and uses the same bounded 12*adjusted-index*signed(+0x6) lookup and N-1 continuation-record control through 0x8dd30.")
label(0x0008e310, "geometry_packet_tail_8e310",
      "Classifies the byte-indexed geometry record and, on admission, emits selector 5, three masked vector halfwords, selector 46 (31+15), three masked byte values, selector 58 (31+27), and the frame readback word; returns at 0x8e490.")
label(0x0008e000, "geometry_first_packet_8e000",
      "Stores the absolute signed object +0x6 value at object +0x24c, then emits the first-record 11-word packet with selectors 20/21/22, negated signed halfwords, selector 46, sign-extended halfwords XORed with bit 15, and selector 58; publishes the paired record value to 0x562480/0x562488 and, for normalized count N>1, hands N-1 records to 0x8e120 with selected-record/table/auxiliary/destination offsets +8/+12/+2/+8.")
label(0x0008e4a0, "geometry_diagnostic_packet_8e4a0",
      "Adjusts the stack by 0x50, saves the g8 register pair at fp+0x80, loads the persistent seed from 0x503b38, then emits the bounded 16-word diagnostic prefix at 0x8e4b0; later diagnostic iteration remains separate.")
label(0x0008ea00, "geometry_diagnostic_variant_8ea00",
      "Adjusts the stack by 0x80, saves the g8 register pair at fp+0xb0, loads the persistent seed from 0x503b38, then emits the sibling 16-word diagnostic prefix at 0x8ea10; later response and window branches remain separate through the 0x8f004 return.")
label(0x0008eaf4, "geometry_diagnostic_variant_response_gate_8eaf4",
      "Publishes the frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on the persistent seed flag to 0x8eb18 or 0x8eb6c.")
label(0x0008ebb8, "geometry_diagnostic_variant_window_tail_8ebb8",
      "Selects the variant's zero/nonzero three-word window, writes control 0x101, emits completion 6, advances both record streams by 0x2c, and loops to 0x8ea60 while the primary cursor remains <= 0x142354.")
label(0x0008ec84, "geometry_diagnostic_variant_window_8ec84",
      "Selects the r12-zero window 0x403800/0x403930/0x8500a2/0 or the nonzero window 0x403800/0x5afede/0x8500a2/g14, writes control 0x101, and continues at 0x8ed7c.")
label(0x0008ed7c, "geometry_diagnostic_variant_fixed_8ed7c",
      "Emits the fixed 11-word 6/5/44 packet with constants 0x40c01a37, 0x413672b0, 0x3f3a9931, 0x3511, 0x1084, 0xf3e7, selector 44, and the frame readback.")
label(0x0008ee14, "geometry_diagnostic_variant_window_8ee14",
      "Repeats the r12-selected 0x403800/0x403930 or 0x5afede command window with 0x8500a2 and g14/zero, then continues at 0x8eeb4.")
label(0x0008eeb4, "geometry_diagnostic_variant_fixed_8eeb4",
      "Emits the second fixed 11-word 6/5/44 packet with constants 0xc0c01a37, 0x413672b0, 0x3f3a9931, 0x3511, 0xef7c, 0xc19, selector 44, and the frame readback.")
label(0x0008ef48, "geometry_diagnostic_variant_final_8ef48",
      "Selects the final r12-zero window 0x45e76c/0x45ec4c/0x8b518a/g14 or nonzero window 0x45e76c/0x5baf2a/0x8b518a/g14, writes control 0x101, emits completion 6 twice, and returns at 0x8f004.")
label(0x0008f010, "geometry_diagnostic_variant_b_8f010",
      "Emits the sibling 15-word diagnostic prefix: 5/19, three 0x40000000 words, 5/44, record/payload words, three masked halfwords, selector 58 (31+27), and the frame readback; later window and terminal branches remain separate through 0x8f1ec.")
label(0x0008f1f0, "geometry_diagnostic_variant_c_8f1f0",
      "Adjusts the stack by 0x40, saves the g8 register pair at fp+0x70, loads the persistent seed from 0x503b38, then reuses the 15-word 5/19/44/58 diagnostic prefix at 0x8f200 with record bases 0x142380 and 0x142358; its response windows and later packets remain separate through the 0x8f618 return.")
label(0x0008f620, "geometry_diagnostic_variant_d_8f620",
      "Loads the persistent seed from 0x503b38 and emits the initial selector 5, then emits the 15-word 5/19/0x3fd9999a/44/58 diagnostic prefix at 0x8f634 with record bases 0x142a8c and 0x142a64; its response window and later packet remain separate through the 0x8f800 return.")
label(0x0008f730, "geometry_diagnostic_variant_d_window_8f730",
      "Selects the zero/nonzero record windows, writes the fourth word as zero or the frame value, repeats control 0x101, and continues at 0x8f7d4.")
label(0x0008f710, "geometry_diagnostic_variant_d_response_gate_8f710",
      "Publishes the frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on the persistent seed flag to 0x8f734 or 0x8f788.")
label(0x0008f7d4, "geometry_diagnostic_variant_d_loop_8f7d4",
      "Advances the primary and auxiliary record pointers by 0x2c, compares the primary pointer inclusively against 0x142b94, and emits terminal completion 6 before returning at 0x8f800.")
label(0x00090540, "geometry_diagnostic_variant_e_90540",
      "Emits the sibling 15-word 5/19/44/58 diagnostic prefix with three 0x40000000 setup words and record/payload/masked fields; its loop and response window remain separate.")
label(0x00090590, "geometry_diagnostic_variant_e_loop_90590",
      "Advances record pointers by 0x2c, compares the next primary pointer inclusively against 0x1427a0, and emits completion 6 for each loop body before the next packet.")
label(0x0009070c, "geometry_diagnostic_variant_e_packet_9070c",
      "Emits the seven-word 5/18 packet with frame word, constants 0x4187f454/0x3f0346dc, selector 58, and the 0x802008 frame readback.")
label(0x00090788, "geometry_diagnostic_variant_e_window_90788",
      "Selects 0x4029f4/0x402e34/0x84f00d/0 or 0x4029f4/0x5afcbe/0x84f00d/frame, writes control 0x101, emits completion 6 twice, and returns at 0x9089c.")
label(0x000908a0, "geometry_diagnostic_variant_f_908a0",
      "Builds the distinct diagnostic variant-F record packet, then selects its 0x90900 response window; the packet body is modeled through the dynamic halfword masks.")
label(0x00090900, "geometry_diagnostic_variant_f_packet_908a0",
      "Emits [5,19,0x40000000,0x40000000,0x40000000,5,44,record,payload0,payload1,raw0&0xffff,raw1&0xffff,raw2&0xffff,58].")
label(0x00090994, "geometry_diagnostic_variant_f_window_90994",
      "Selects the zero/nonzero three-word response window from r14-relative records, appends a zero fourth word, publishes it under control g13, and continues to the 0x90a58 record loop.")
label(0x00090a58, "geometry_diagnostic_variant_f_loop_90a58",
      "Advances both diagnostic record pointers by 0x2c, compares the next primary pointer inclusively against 0x142dd0, and emits completion 6 before either looping to 0x90900 or entering the next packet.")
label(0x00090a7c, "geometry_diagnostic_variant_g_packet_90a7c",
      "Emits the six-word continuation packet [5,18,g14,0x41900000,0xbf800000,58] before the nested 0x5624e4/0x503b38 response-window selectors.")
label(0x00090af8, "geometry_diagnostic_variant_g_window_90af8",
      "Selects one of four exact three-word response windows from the 0x5624e4 state and 0x503b38 mode, appends zero or g14, publishes under control 0x101, and emits completion 6 twice.")
label(0x00090c10, "geometry_table_packet_90c10",
      "Emits the 14-word 5/18 table-diagnostic packet with remainder, 0x40e00000/0x41800000, frame, 21, 0xb800, 19, three 0x40400000 words, selector 58, and frame readback.")
label(0x00090ccc, "geometry_table_window_90ccc",
      "Indexes table 0x2be52b0 by remainder*12; a nonzero first table word publishes the three table words at 0x804000 under control 0x101, while completion 6 is emitted in either path.")
label(0x00090d50, "geometry_table_packet_90d50",
      "Emits the sibling 14-word 5/18 table packet, using operand word 0xc000 in the 21-slot before the three 0x40400000 words and selector 58.")
label(0x00090e08, "geometry_table_window_90e08",
      "Repeats the 0x2be52b0 plus remainder*12 table gate and publishes three table words only when the first entry is nonzero; completion 6 terminates the helper.")
label(0x00090e80, "geometry_table_packet_90e80",
      "Emits the sibling 14-word 5/18 table packet, using operand word 0xc800 in the 21-slot before the three 0x40400000 words and selector 58.")
label(0x00090f3c, "geometry_table_window_90f3c",
      "Repeats the 0x2be52b0 plus remainder*12 table gate for the 0x90e80 sibling and publishes three table words only when the first entry is nonzero.")
label(0x00091624, "geometry_table_dispatch_91624",
      "Dispatches to 0x90c10, 0x90d50, and 0x90e80 with packet operands 0xb800, 0xc000, and 0xc800 when source value minus 0x109, 0x113, or 0x11d is <= 15<<4 (240), then emits completion 6.")
label(0x00091690, "geometry_calibration_secondary_entry_91690",
      "Saves g2/g14, loads paired calibration source 0x562498, derives the threshold from g28+31, and enters 0x91a74 directly or the threshold partition at 0x916d8.")
label(0x000916d8, "geometry_calibration_secondary_threshold_gate_916d8",
      "Compares the paired calibration source against threshold 0x8b, converging at 0x91a74 for the low arm or entering the first floating-point arm at 0x9174c.")
label(0x000916e0, "geometry_calibration_secondary_partition_916e0",
      "Partitions paired calibration source thresholds 0x8b/0x9f/0xb3/0xb8/0xcc/0xf4/0x108/0x11c/0x1f8/0x234/0x270/0x284/0x2c0/0x2d4/0x310/0x315/0x379 before converging at 0x91a74; per-arm real arithmetic remains unresolved.")
label(0x00091df4, "geometry_table_dispatch_91df4",
      "Repeats the 0x91624 three-helper dispatch: independent source-minus-0x109/0x113/0x11d comparisons against 240, calls to 0x90c10/0x90d50/0x90e80, then completion 6 and return at 0x91e54.")
label(0x00090fc0, "geometry_calibration_90fc0",
      "Partitions the calibration source through the ordered thresholds 0x8b, 0x9f, 0xb3, 0xb8, 0xcc, 0xf4, 0x108, 0x11c, 0x1f8, 0x234, 0x270, 0x284, 0x2c0, 0x2d4, 0x310, 0x315, and 0x379 before converging at 0x9139c; real arithmetic writes remain unresolved.")
label(0x0009139c, "geometry_calibration_packet_9139c",
      "Emits the seven-word 5/18 packet formed by three input words plus the persistent calibration words, selector 21, and shlo 14 of 3 (0xc000), then calls shared helper 0x8e310.")
label(0x0009140c, "geometry_calibration_helper_handoff_9140c",
      "Calls shared helper 0x8e310 for table offsets 0x9cb7a and 0x9cbf2 from base 0x2b4613a, then emits completion 6 before the 0x91434 packet.")
label(0x00096964, "geometry_calibration_callsite_96964",
      "Enters the 0x90fc0 calibration service with fixed input words 0x41e00000, 0x41d66666, and 0xc17b3333; the convergent 0x9139c packet adds the runtime calibration triple before helper 0x8e310.")
label(0x00091434, "geometry_calibration_packet_91434",
      "Emits the nine-word 5/18 packet with computed/address words, selector 21, a distinct r4 secondary word, selector 58, and the 0x802008 frame readback.")
label(0x000914d8, "geometry_calibration_window_914d8",
      "Publishes the fixed command window 0x403968/0x4039f0/0x850225/0 under control 0x101 at 0x804000, then emits completion 6.")
label(0x00091510, "geometry_calibration_packet_91510",
      "Emits the 16-word 6/5/18 packet with three address-derived words, selectors 21/47/19, 0x4000 bit mask, two XOR payload slots, an auxiliary word, and three 0x3e4ccccd (0.2) literals.")
label(0x000915d0, "geometry_calibration_helper_gate_915d0",
      "Branches on r15 and source remi 3: r15 nonzero with remainder != 2 calls 0x8e310 using table base 0x2be2a14 and flag 1; the alternate path uses 0x2be296c and flag 0 before converging at 0x91624.")
label(0x00091d94, "geometry_calibration_helper_gate_91d94",
      "Repeats the 0x915d0 flag/r15/remainder-3 gate from its cmpi at 0x91d94: helper 0x8e310, bases 0x2be2a14/0x2be296c, flags 1/0, and convergence at the 0x91df4 dispatcher.")
label(0x00091dac, "geometry_calibration_helper_gate_91dac_remi",
      "Computes 0x562498 modulo 3 for the paired 0x91d94 gate; remainder 2 joins the alternate 0x2be296c/flag-0 path before the 0x91df4 dispatcher.")
label(0x00091a74, "geometry_calibration_packet_91a74",
      "Emits the paired nine-word 5/18 packet with three already-combined input words, selector 21, shlo 14 of 3 (0xc000), selector 58, and frame readback.")
label(0x000969c4, "geometry_calibration_callsite_969c4",
      "Enters the 0x91e60 paired calibration service with fixed input words 0x41b00000, 0x41ef3333, and 0xc141999a; its 0x91a74 packet adds the runtime calibration triple and carries the frame readback explicitly.")
label(0x00091b10, "geometry_calibration_window_91b10",
      "Publishes the fixed command window 0x403a90/0x403b18/0x850387/0 under control 0x101 at 0x804000, then emits completion 6.")
label(0x00091e98, "geometry_calibration_secondary_partition_91e60",
      "Partitions the paired calibration value at 0x12b/0x149/0x275/0x293 into branch paths 0x91ea8, 0x91f30, 0x91edc, 0x91f30, and 0x91f44; repeated real arithmetic remains unresolved.")
label(0x00091e60, "geometry_calibration_secondary_entry_91e60",
      "Saves the paired-service frame, preserves g0/g1/g2 context, loads source 0x56249c, establishes threshold 0x12b and table base 0x2b46134, and enters the 0x91e98 partition.")
label(0x00091f44, "geometry_calibration_packet_91f44",
      "Emits the five-word 5/21 packet with r4 after setbit 15 (0x8000), selector 58, and the 0x802008 frame readback before the next selector-5 helper packet.")
label(0x00091fac, "geometry_calibration_packet_91fac",
      "Emits the seven-word 5/18 packet with three combined words, selector 21, shlo 14 of 3 (0xc000), and then calls shared helper 0x8e310 without a frame readback at this boundary.")
label(0x00092010, "geometry_calibration_secondary_math_handoff_92010",
      "Calls shared helper 0x8e310 with table addresses 0x2be2cb4 and 0x2be2d2c, combines response/context words, applies explicit 0xcccccccd/0x3feccccc and 0xcccccccd/0x400ccccc math constants, and enters the 0x92070 packet.")
label(0x00092070, "geometry_calibration_packet_92070",
      "Emits the ten-word 6/5/18 packet with the record word, two computed words, selector 21, shlo 14 of 3 (0xc000), loaded auxiliary word, and 0x802008 frame readback.")
label(0x000920fc, "geometry_calibration_window_920fc",
      "Publishes the fixed response window 0x403968/0x4039f0/0x850225/0 under control 0x101 at 0x804000, then emits completion 6 before the 0x92144 packet.")
label(0x00092144, "geometry_calibration_packet_92144",
      "Emits the paired 16-word 6/5/18 packet with three leading words, setbit-14 (0x4000), selector 47, two XOR payloads using r4, an auxiliary word, selector 19, and three 0.2 literals.")
label(0x000921d8, "geometry_calibration_flag_gate_921d8",
      "Tests g13 after the paired 16-word packet, emits three 0x3e4ccccd literals, and routes the clear flag to 0x9224c or the set-flag path to the r10/remainder gate at 0x921f8.")
label(0x000921f8, "geometry_calibration_helper_gate_921f8",
      "Checks r10 and source remi 3: the active path calls 0x8e310 with base 0x2be2a14 and stores flag 1 at 0x5624d8; the alternate path uses 0x2be296c and stores zero before 0x9224c.")
label(0x0009224c, "geometry_table_entry_gate_9224c",
      "Reloads source 0x56249c, compares it against 0x12c, and routes the normal indexed packet to 0x9225c or larger values to the subtract-15 arm at 0x92380.")
label(0x0009225c, "geometry_table_packet_callsite_9225c",
      "Reuses the 0x90c10 table packet shape with remainder 30 modulo g7, operand 0xb800, table base 0x2be52b0, and three-word conditional publication.")
label(0x00092380, "geometry_table_packet_callsite_92380",
      "Reuses the 0x90d50 table packet shape after subtracting 15 from g7; the 0xc000 operand is followed by the same scaled 0x2be52b0 table response and completion path.")
label(0x000924ac, "geometry_table_packet_callsite_924ac",
      "Reuses the 0x90d50 table packet shape after subtracting 0x14a from g7, with the same 0xc000 operand and 0x2be52b0 response publication.")
label(0x000925dc, "geometry_table_packet_callsite_925dc",
      "Reuses the 0x90d50 table packet shape after subtracting 0x159 from g7, with the same 0xc000 operand and table-backed response window.")
label(0x00092910, "geometry_fifo_packet_92900",
      "Emits the shared 12-word 5/18/21/19 packet with incoming g0/g1/g2, g3 masked to its low halfword, three 0.2 literals, and completion 6 before the modulo/division gate.")
label(0x00092db0, "geometry_fifo_packet_92db0",
      "Twin of the 0x92910 packet: the same incoming 5/18/21/19 shape and low-halfword g3 projection, followed by the alternate modulo/division helper gate.")
label(0x000929a0, "geometry_fifo_helper_gate_929a0",
      "Uses divisor cell 0x5624b0: divisor remainder 2 selects alternate argument (31+r29) remi divisor, base 0x2be296c, and flag 0x5624d0=0; otherwise g7 remi divisor selects base 0x2be2a14 and flag 1 for 0x8e310.")
label(0x00092e28, "geometry_fifo_helper_gate_92e28",
      "Twin helper gate using divisor cell 0x5624b8 and flag cell 0x5624e4; remainder 2 selects the alternate 0x2be296c path, otherwise the 0x2be2a14 path calls 0x8e310.")
label(0x00092e84, "geometry_table_entry_gate_92e84",
      "Reloads source 0x5624b8, compares g7-0x3c against 15<<3, and enters the 0x92e9c b800 table arm at or below the threshold or the 0x92fc0 continuation above it.")
label(0x00092e9c, "geometry_table_packet_callsite_92e9c",
      "Emits the 0x90c10 table packet shape with g7 remainder-30, operand 0xb800, and the scaled 0x2be52b0 response publication.")
label(0x00092fc0, "geometry_table_entry_gate_92fc0",
      "Compares g7-0x46 against 15<<3, falling through to the 0x92fcc c000 table arm at or below the threshold or advancing to 0x930f0 above it.")
label(0x00092fcc, "geometry_table_packet_callsite_92fcc",
      "Emits the 0x90d50 table packet shape with g7 remainder-30, operand 0xc000, and the scaled 0x2be52b0 response publication.")
label(0x000930f0, "geometry_table_entry_gate_930f0",
      "Compares g7-0x50 against 15<<3, falling through to the 0x930fc c000 table arm at or below the threshold or advancing to 0x93224 above it.")
label(0x000930fc, "geometry_table_packet_callsite_930fc",
      "Emits the 0x90d50 table packet shape with g7-20 remainder-30, operand 0xc000, and the scaled 0x2be52b0 response publication.")
label(0x00093700, "geometry_packet_93700",
      "Emits the 11-word 5/18/19 packet with incoming g0/g1/g2, three 0.1 literals, addo 31,27, and the 0x802008 frame readback before the fixed response window.")
label(0x00093774, "geometry_window_93774",
      "Publishes [0x400cec, 0x400d1c, 0x84ce4f, 0] under control 0x101 at 0x804000, then reaches the paired selector-6 packet.")
label(0x000937ec, "geometry_packet_937ec",
      "Emits the paired 12-word 6/5/18/19 packet with three computed words, three 0.1 literals, tail word, and frame readback before its fixed response window.")
label(0x000938b0, "geometry_window_938b0",
      "Publishes the paired [0x400cec, 0x400d1c, 0x84ce4f, 0] response window under control 0x101 and emits completion 6.")
label(0x000938d0, "geometry_packet_938d0",
      "Emits the 11-word 6/5/44 packet with computed words, setbit-14 repeated twice, context/tail words, and 0x802008 frame readback.")
label(0x00093964, "geometry_window_93964",
      "Selects [0xcb094,0xcb120,0xa1cc84,0] or [0xcb094,0x59598e,0xa1cc84,g14] from the r3 predicate, publishes under control 0x101, and emits completion 6.")
label(0x00093a1c, "geometry_packet_93a1c",
      "Emits the paired 12-word 6/5/44 packet with three computed words, a repeated third computed word, 0x6080/0x3c80 constants, context, addo 31,27, and frame readback.")
label(0x00093dec, "geometry_packet_93dec",
      "Emits the five-word 5/21 packet [5,21,setbit15,addo31,27,frame_readback] before the paired helper packet.")
label(0x00093e54, "geometry_packet_93e54",
      "Emits the seven-word 5/18 packet with three address-adjusted words and 0xc000, then calls 0x8e310 twice using base 0x2b4613a, offsets 0x9cb7a/0x9cbf2, and shared third argument 31+r28.")
label(0x00093edc, "geometry_packet_93edc",
      "Emits the ten-word 6/5/18 packet with r11, g7+r3, g6+g12, 21, 0xc000, r6, and the 0x802008 frame readback.")
label(0x00093f8c, "geometry_window_93f8c",
      "Publishes [0x403968,0x4039f0,0x850225,0] under control 0x101 at 0x804000, followed by completion 6.")
label(0x00093fe4, "geometry_packet_93fe4",
      "Emits the 16-word 6/5/18 packet with computed words, selector 44, mask word, selector 47, XOR payloads, auxiliary word, selector 19, and three 0.2 literals.")
label(0x00094080, "geometry_helper_gate_94080",
      "Checks r9 and [0x5624a4] remi 3, calling 0x8e310 with base 0x2be2a14/0x2be296c and flag 1/0 at 0x5624e0 before the table arm at 0x9410c.")
label(0x00094bf0, "geometry_packet_94bf0",
      "Emits the five-word 5/21 packet [5,21,setbit15,addo31,27,frame_readback] before the paired selector-5/18 helper sequence.")
label(0x00094d90, "geometry_packet_service_94d90",
      "Selects threshold-dependent address adjustments, then reaches the shared seven-word 5/18/21 packet and paired 0x8e310 tails at 0x95074; the threshold table itself remains outside the bounded model.")
label(0x00095074, "geometry_packet_94d90_emit",
      "Emits [5,18,g0+state0,g1+state1,g2+selected_offset,21,0xc000] and calls 0x8e310 with base 0x2b4613a, offsets 0x9cb7a/0x9cbf2, and the selected offset as the shared third argument.")
label(0x00099198, "geometry_packet_callsite_99198",
      "Calls the 0x94d90 service with fixed input words 0x41766666, 0x41bf3333, and 0xc0fccccd; threshold-selected adjustments and the shared 0x8e310 third argument remain runtime-dependent.")
label(0x000951ec, "geometry_packet_951ec",
      "Emits the 16-word 6/5/18 packet with r13+r8, incoming g0/g5, selector 21, setbit-14 mask, selector 47, XOR payloads masked by g6|setbit15, g7, selector 19, and three 0.2 literals.")
label(0x00095360, "geometry_packet_95360",
      "Emits the 11-word 5/18 packet with incoming g0/g1/g2, selector 21, the low 16 bits of g3, selector 19, and three 0.2 literals before the response lookup arms.")
label(0x00095470, "geometry_packet_callsite_95470",
      "Reuses the 0x95360 11-word 5/18 packet shape with incoming g0/g1/g2 and low-16-bit g3; its response lookup begins from 0x5624c0.")
label(0x000956c0, "geometry_packet_callsite_956c0",
      "Reuses the 0x95360 11-word 5/18 packet shape with incoming g0/g1/g2 and low-16-bit g3; its response lookup begins from 0x5624c4.")
label(0x00095910, "geometry_runtime_state_init_95910",
      "Initializes the 0x562490 stride-12 record table with the 0x1c618 result, clears four 0x562500 records, and publishes 31+r9 at 0x5624ac, 0xb4 at 0x5624b8, and 0xfa at 0x5624c4.")
label(0x00095984, "geometry_runtime_state_init_95984",
      "Publishes 0xc059999a at 0x562538, clears doublewords at 0x5624f0/0x562530, fills six 0x5624d0 words with the 0x1c618 result, and initializes the 0x562b40 state cluster.")
label(0x00095a00, "geometry_asset_dispatch_95a00",
      "Stores mode 15 for record type 5 and 18 otherwise, then dispatches e2120 selectors 1/3/5/7 with type<<2 indices; type 7 with a zero flag repeats indices 0/1 for the latter pair.")
label(0x00095c20, "geometry_packet_95c20",
      "Emits the distinct five-word packet [5,21,setbit15,5,addo31,27] before the paired 0x401e08/0x401e50 and 0x401e5c/0x401e9c response windows.")
label(0x00095c80, "geometry_window_95c80",
      "Publishes four windows [0x401e08,0x401e50,0x84e1d1,0], [0x401e5c,0x401e9c,0x84e232,0], [0x401ea4,0x401ebc,0x84e289,0], and [0x401ec0,0x401f78,0x84e2ae,g14] under control 0x101 through 0x6fec0.")
label(0x00095db4, "geometry_packet_95db4",
      "Emits the ten-word 6/5/18 packet with fixed 0x413e7803/0xc0c66666/0xc0828db9 payload, selector 21, setbit-16 mask, addo31,27, and frame readback.")
label(0x00095e90, "geometry_packet_95e90",
      "Emits the six-word 6/5/21 packet with setbit-15 mask, addo31,27, and frame readback before the next fixed response window.")
label(0x00095f1c, "geometry_packet_95f1c",
      "Emits the eight-word 6/5/18 packet with fixed 0x3f8ccccd/0xc00ccccd/0xc0800000 payload, addo31,27, and frame readback.")
label(0x00095f0c, "geometry_sequencer_callsite_95f0c",
      "Calls the recovered 0x93560 FIFO sequencer with payload inputs 0xc0c66666, 0x41a33333, 0x40900000, and zero before the 0x95f1c packet arm.")
label(0x00095fac, "geometry_window_95fac",
      "Publishes [0x40368c,0x4037e0,0x84feed,g14] and [0x404a64,0x404ac4,0x851590,g14] under control 0x101 at 0x804000 before the next selector-6 packet.")
label(0x000964a0, "geometry_window_964a0",
      "Publishes [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14] under control 0x101 at 0x804000 around the 0x91690 response path.")
label(0x0009687c, "geometry_sequencer_callsite_9687c",
      "Calls the 0x93560 sequencer with fixed payload words 0x40000000, 0x41b4cccd, 0xc18c0000, and 0x4000.")
label(0x000968a0, "geometry_stateful_packet_callsite_968a0",
      "Calls the 0x92730 stateful packet model with fixed payload words 0xc12ccccd, 0x4227999a, 0x3f800000, and 0x1500.")
label(0x000968c4, "geometry_stateful_packet_callsite_968c4",
      "Calls the 0x933b0 stateful packet twin with fixed payload words 0xc1066666, 0x42293333, 0x3fe66666, and 0xffffa000.")
label(0x000968e4, "geometry_fifo_packet_callsite_968e4",
      "Calls the 0x92830 packet template with fixed payload words 0x411e6666, 0x422d999a, 0x40933333, and zero.")
label(0x00096908, "geometry_packet_callsite_96908",
      "Calls the 0x95360 5/18 packet family with fixed payload words 0xc12ccccd, 0x42293333, 0x3f8ccccd, and 0xffffd820.")
label(0x00096928, "geometry_packet_callsite_96928",
      "Calls the 0x95470/0x95360 5/18 packet family with fixed payload words 0x40333333, 0x41cf3333, zero, and 0xffff8000.")
label(0x00096948, "geometry_fifo_packet_callsite_96948",
      "Calls the 0x92900 packet wrapper with fixed payload words 0xc089999a, 0x421c6666, 0x40466666, and zero.")
label(0x00096988, "geometry_fifo_packet_callsite_96988",
      "Calls the 0x934b0 packet template with fixed payload words 0x40800000, 0x4240cccd, 0x416ccccd, and 0xffffc000.")
label(0x000969a4, "geometry_fifo_prologue_callsite_969a4",
      "Calls the 0x93240 floating prologue with fixed payload words zero, 0x41b40000, 0xc195999a, and zero.")
label(0x00096ef4, "geometry_fifo_service_callsite_96ef4",
      "Calls the 0x92da0 service prefix with fixed payload words 0x4151999a, 0x420b3333, 0xbfe66666, and 0xffff8500; divisor/table state remains caller and runtime dependent.")
label(0x00096de0, "geometry_stateful_packet_callsite_96de0",
      "Calls the 0x933b0 stateful packet twin with fixed payload words 0xc0833333, 0x41e9999a, 0xc039999a, and zero.")
label(0x00096f24, "geometry_stateful_packet_callsite_96f24",
      "Calls the 0x92730 stateful packet model with fixed payload words 0xc0c00000, 0x42206666, 0xbe99999a, and 0xffffa000.")
label(0x00096f48, "geometry_fifo_packet_callsite_96f48",
      "Calls the 0x92830 packet template with fixed payload words 0x40e66666, 0x42213333, 0xbe99999a, and 0xffffc000.")
label(0x00096e04, "geometry_fifo_packet_callsite_96e04",
      "Calls the 0x92900 packet wrapper with fixed payload words 0x4019999a, 0x4213999a, 0xc059999a, and 0xffff8000.")
label(0x00096f68, "geometry_packet_callsite_96f68",
      "Calls the 0x95360 5/18 packet family with fixed payload words 0xc1066666, 0x42226666, zero, and 0xffffd820.")
label(0x00096f8c, "geometry_packet_callsite_96f8c",
      "Calls the 0x95470/0x95360 5/18 packet family with fixed payload words 0x406ccccd, 0x41e9999a, 0xc0466666, and 0xffff8000.")
label(0x00097134, "geometry_sequencer_callsite_97134",
      "Calls the 0x93560 sequencer with fixed payload words 0xc0200000, 0x41b40000, 0xc195999a, and 0x4000.")
label(0x00097150, "geometry_fifo_prologue_callsite_97150",
      "Calls the 0x93240 floating prologue with fixed payload words zero, 0x41b4cccd, 0xc19a6666, and zero.")
label(0x000971f4, "geometry_fifo_packet_callsite_971f4",
      "Calls the 0x92830 packet template with fixed payload words 0xc1a10831, 0x422c6666, 0x3f50e560, and 0xffff8300.")
label(0x00097210, "geometry_fifo_prologue_callsite_97210",
      "Calls the 0x93240 floating prologue with fixed payload words zero, 0x41b4cccd, 0xc19a6666, and zero.")
label(0x00097230, "geometry_sequencer_callsite_97230",
      "Calls the 0x93560 sequencer with fixed payload words 0xbf19999a, 0x41b4cccd, 0xc1840000, and setbit-14 g3.")
label(0x00097254, "geometry_fifo_packet_callsite_97254",
      "Calls the 0x92900 packet wrapper with fixed payload words 0x40326e98, 0x41e66666, 0x3fcb020c, and 0x7500.")
label(0x00097274, "geometry_packet_callsite_97274",
      "Calls the 0x95470/0x95360 5/18 packet family with fixed payload words 0xc06ccccd, 0x41ec0000, 0xbfa66666, and zero.")
label(0x000972c8, "geometry_window_callsite_972c8",
      "Reuses the 0x95c80 four-window response publication contract with tuples [0x401e08,0x401e50,0x84e1d1,0], [0x401e5c,0x401e9c,0x84e232,0], [0x401ea4,0x401ebc,0x84e289,0], and [0x401ec0,0x401f78,0x84e2ae,g14].")
label(0x0009747c, "geometry_window_callsite_9747c",
      "Reuses the 0x95fac two-window response publication contract with [0x40368c,0x4037e0,0x84feed,g14] and [0x404a64,0x404ac4,0x851590,g14].")
label(0x000975e4, "geometry_window_callsite_975e4",
      "Reuses the 0x964a0 two-window response publication contract with [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14].")
label(0x00097760, "geometry_packet_callsite_97760",
      "Calls the 0x94bf0 five-word packet family with fixed payload words 0x41c00000, 0x41b80000, 0x40f00000, and addo 31,28.")
label(0x00097780, "geometry_stateful_packet_callsite_97780",
      "Calls the 0x92730 stateful packet with fixed payload words 0xc0c00000, 0x42040000, 0xc0800000, and zero.")
label(0x000977a4, "geometry_fifo_packet_callsite_977a4",
      "Calls the 0x92900 packet wrapper with fixed payload words 0x400947ae, 0x42040000, 0x405374bc, and 0xffffae00.")
label(0x000977c8, "geometry_packet_callsite_977c8",
      "Calls the 0x956c0/0x95360 5/18 packet family with fixed payload words 0x4112cccd, 0x41b80000, 0x3fc00000, and 0xffff8780.")
label(0x000977ec, "geometry_packet_callsite_977ec",
      "Calls the 0x95470/0x95360 5/18 packet family with fixed payload words 0xc120978d, 0x41dc0000, 0xc100e560, and 0x3c80.")
label(0x00097d50, "geometry_indexed_table_update_97d50",
      "Updates per-index words at 0x562540/0x562740/0x562940 on the negative-table-entry path using 0xf5058-derived quantization; otherwise falls through to the indexed 0x97e10 packet consumer.")
label(0x00097d74, "geometry_indexed_table_update_97d50_negative_path",
      "For a negative existing 0x562740 entry, adds real 0.5 and stores only the middle table word before handing control to 0x97e10.")
label(0x00097da4, "geometry_indexed_table_update_97d50_quantize_path",
      "Calls 0xf5058 twice with index plus 0x5024e8, masks each result to 8 bits, biases by -0x7f, divides by 20, and stores the converted values around fixed 0xc1880000.")
label(0x00097de4, "geometry_indexed_table_update_97d50_table_writes",
      "Publishes the first quantized word to 0x562540, fixed 0xc1880000 to 0x562740, and the second quantized word to 0x562940 before the 0x97e10 packet consumer.")
label(0x00097fac, "geometry_indexed_update_loop_97f20_seed_40",
      "Seeds the first indexed-table loop at 0x40 with setbit 6,0 before the inclusive call sequence and exclusive 0x4f bound.")
label(0x00098078, "geometry_indexed_update_loop_98000_seed_50",
      "Seeds the second indexed-table loop at 0x50 before the inclusive call sequence and exclusive 0x5f bound.")
label(0x00098144, "geometry_indexed_update_loop_98114_seed_60",
      "Forms index 0x60 with shlo 5,3 before the inclusive call sequence and exclusive 0x6f bound.")
label(0x00098248, "geometry_indexed_update_loop_98200_seed_70",
      "Forms index 0x70 with shlo 4,7 before the inclusive call sequence and exclusive 0x7f bound.")
label(0x000097e10, "geometry_indexed_packet_97e10",
      "Consumes 0x562540/0x562740/0x562940[index] and emits [5,18,three table words,21,0x10000-0x562b68,19,0.25,1.0,1.0,58].")
label(0x00097f20, "geometry_indexed_update_loop_97f20",
      "Initializes the 0xc2700000/0x4089999a/0xc1a00000 packet preamble, then calls 0x97d50 for indices 0x40 through 0x4e before emitting completion 6.")
label(0x00098000, "geometry_indexed_update_loop_98000",
      "Initializes the 0x42700000/0x4089999a/0xc1a00000 packet preamble, then calls 0x97d50 for indices 0x50 through 0x5e before emitting completion 6.")
label(0x00098114, "geometry_indexed_update_loop_98114",
      "Initializes the 0xc1a00000/0x4089999a/0xc2700000 packet preamble, then calls 0x97d50 for indices 0x60 through 0x6e before emitting completion 6.")
label(0x00098200, "geometry_indexed_update_loop_98200",
      "Uses the indexed response setup without a local 5/18 preamble, then calls 0x97d50 for indices 0x70 through 0x7e before emitting completion 6 and entering a separate command-29/30 packet path.")
label(0x00098268, "geometry_indexed_post_loop_98200_service",
      "After the 0x70..0x7e loop, emits completion 6 and calls 0x2a990 with (ldob 0x5024e8 << 8, 0x6a00) before the command-29/30 response setup.")
label(0x00098298, "geometry_indexed_post_loop_98200_command29",
      "Emits command 29 with the 0x562b68 context and fixed 0x40b33333 word, reads the first response, then prepares command 30 with the same context/constant and a zero response slot.")
label(0x000982f8, "geometry_indexed_response_packet_982f8",
      "Emits [18,response0,response1,response2,21,0x10000-0x562b68,19,0x3f88f5c3,1.0,1.0,58] after the command-29/30 helper pipeline.")
label(0x00098a94, "geometry_fifo_packet_callsite_98a94",
      "Calls the 0x92830 packet template with fixed payload words 0xc10b3333, 0x421c0000, 0xbdcccccd, and 0x7200.")
label(0x00098ab8, "geometry_fifo_packet_callsite_98ab8",
      "Calls the 0x92900 packet wrapper with fixed payload words 0x40733333, 0x421e6666, 0xbf666666, and 0x7d00.")
label(0x00098adc, "geometry_packet_callsite_98adc",
      "Calls the 0x956c0/0x95360 5/18 packet family with fixed payload words 0x410e6666, 0x421a6666, 0x3f4ccccd, and 0xffffa200.")
label(0x00098d4c, "geometry_fifo_service_callsite_98d4c",
      "Calls the 0x92da0 service prefix with fixed payload words 0x412b3333, 0x42053333, 0xbe4ccccd, and 0xffff8500; divisor/table state remains caller and runtime dependent.")
label(0x00098cc8, "geometry_packet_callsite_98cc8",
      "Calls the 0x94bf0 five-word packet family with fixed payload words 0x41c9999a, 0x41ea6666, 0xbf800000, and addo 31,28.")
label(0x00098f58, "geometry_packet_callsite_98f58",
      "Calls the 0x95470/0x95360 5/18 packet family with fixed payload words 0xc0c33333, 0x41db3333, 0x3f333333, and 0x1600.")
label(0x0009911c, "geometry_sequencer_callsite_9911c",
      "Calls the 0x93560 sequencer with fixed payload words 0x3fe66666, 0x41d4cccd, 0x40c9999a, and 0xffffa900.")
label(0x0009615c, "geometry_fifo_packet_callsite_9615c",
      "Calls the 0x92830 packet template with arithmetic g0/g1/g2 payloads and a fixed zero g3; g0 is seeded from 0x40d66666 after the preceding real-arithmetic setup.")
label(0x00099234, "geometry_packet_callsite_99234",
      "Calls the 0x956c0/0x95360 5/18 packet family with fixed payload words 0x40833333, 0x41e5999a, 0x4089999a, and 0xffff9700.")
label(0x00099254, "geometry_fifo_packet_callsite_99254",
      "Calls the 0x92830 packet template with fixed payload words 0x4109999a, 0x4224cccd, 0x3f99999a, and setbit-11 g3.")
label(0x00099274, "geometry_fifo_packet_callsite_99274",
      "Calls the 0x92900 packet wrapper with fixed payload words 0xc059999a, 0x4224cccd, 0x3fe66666, and 0xd00.")
label(0x00099298, "geometry_stateful_packet_callsite_99298",
      "Calls the 0x92730 stateful packet with fixed payload words 0xc0e66666, 0x4224cccd, 0x3ecccccd, and 0xffffef00.")
label(0x000992bc, "geometry_stateful_packet_callsite_992bc",
      "Calls the 0x933b0 stateful packet twin with fixed payload words 0xc079999a, 0x41c66666, 0xc0400000, and 0xffffbb00.")
label(0x000992e0, "geometry_packet_callsite_992e0",
      "Calls the 0x95360 5/18 packet family with fixed payload words 0xc0b33333, 0x41c4cccd, 0xc06ccccd, and 0x1200.")
label(0x0009933c, "geometry_window_callsite_9933c",
      "Reuses the 0x95c80 four-window response publication contract with tuples [0x401e08,0x401e50,0x84e1d1,0], [0x401e5c,0x401e9c,0x84e232,0], [0x401ea4,0x401ebc,0x84e289,0], and [0x401ec0,0x401f78,0x84e2ae,g14].")
label(0x00099480, "geometry_window_callsite_99480",
      "Reuses the 0x95fac two-window response publication contract with [0x40368c,0x4037e0,0x84feed,g14] and [0x404a64,0x404ac4,0x851590,g14].")
label(0x000995d4, "geometry_window_callsite_995d4",
      "Reuses the 0x964a0 two-window response publication contract with [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14].")
label(0x0009966c, "geometry_fifo_service_callsite_9966c",
      "Calls the 0x92da0 service prefix with fixed payload words 0x3dcccccd, 0x42040000, 0x4101999a, and 0xffffc000; divisor/table state remains caller and runtime dependent.")
label(0x00099790, "geometry_window_callsite_99790",
      "Reuses the 0x95c80 four-window response publication contract with tuples [0x401e08,0x401e50,0x84e1d1,0], [0x401e5c,0x401e9c,0x84e232,0], [0x401ea4,0x401ebc,0x84e289,0], and [0x401ec0,0x401f78,0x84e2ae,g14].")
label(0x000998d4, "geometry_window_callsite_998d4",
      "Reuses the 0x95fac two-window response publication contract with [0x40368c,0x4037e0,0x84feed,g14] and [0x404a64,0x404ac4,0x851590,g14].")
label(0x000999d4, "geometry_window_callsite_999d4",
      "Reuses the 0x964a0 two-window response publication contract with [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14].")
label(0x00097838, "geometry_window_callsite_97838",
      "Reuses the 0x95c80 four-window response publication contract with tuples [0x401e08,0x401e50,0x84e1d1,0], [0x401e5c,0x401e9c,0x84e232,0], [0x401ea4,0x401ebc,0x84e289,0], and [0x401ec0,0x401f78,0x84e2ae,g14].")
label(0x00097a14, "geometry_window_callsite_97a14",
      "Reuses the 0x95fac two-window response publication contract with [0x40368c,0x4037e0,0x84feed,g14] and [0x404a64,0x404ac4,0x851590,g14].")
label(0x00097bb0, "geometry_window_callsite_97bb0",
      "Reuses the 0x964a0 two-window response publication contract with [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14].")
label(0x000969f4, "geometry_window_callsite_969f4",
      "Reuses the 0x964a0 two-window publication contract: [0x402218,0x4022c8,0x84e6bf,g14] and [0x4029bc,0x4029ec,0x84efca,g14].")
label(0x00096b20, "geometry_packet_callsite_96b20",
      "Reuses the 0x95c20 five-word [5,21,setbit15,5,addo31,27] packet before the repeated four-window response publication.")
label(0x00096b50, "geometry_window_callsite_96b50",
      "Reuses the 0x95c80 four-window response publication contract with the same fixed tuples and g14 fourth words.")
label(0x00096044, "geometry_packet_callsite_96044",
      "Reuses the 0x95e90 six-word 6/5/21 packet shape with setbit-15 mask, addo31,27, and frame readback.")
label(0x0009620c, "geometry_packet_callsite_9620c",
      "Calls the 0x95360 5/18 packet family with computed g0/g1/g2 payloads and fixed packed-source word 0xfffff820.")
label(0x0009629c, "geometry_packet_callsite_9629c",
      "Calls the 0x95470/0x95360 5/18 packet family with computed g0/g1/g2 payloads and fixed packed-source word 0x7300.")
label(0x00096310, "geometry_fifo_packet_callsite_96310",
      "Calls the 0x92900 12-word 5/18/21/19 packet wrapper with computed g0/g1/g2 payloads and fixed packed-source word 0xd00.")
label(0x000963bc, "geometry_packet_callsite_963bc",
      "Reuses the 0x94bf0 five-word [5,21,setbit15,addo31,27,frame] packet after the preceding geometry helper calls.")
label(0x00096444, "geometry_packet_completion_callsite_96444",
      "Completes the packet produced by the preceding 0x91690 helper with selector 6, then enters a separate response-packet sequence.")
label(0x00094c44, "geometry_packet_callsite_94c44",
      "Reuses the seven-word 5/18/21/0xc000 packet shape with incoming g0/g1/g2 and two 0x8e310 calls using offsets 0x9cb7a/0x9cbf2.")
label(0x00094ccc, "geometry_packet_callsite_94ccc",
      "Reuses the ten-word 6/5/18 packet with incoming g0/g1/g2, 21/0xc000, completion 6, and frame readback before the fixed 0x403968 response window.")
label(0x0009410c, "geometry_table_packet_callsite_9410c",
      "Reuses the 0x90c10 table packet shape with g7-10 remainder-30 and operand 0xb800, followed by the 0x2be52b0 response publication.")
label(0x00094238, "geometry_table_packet_callsite_94238",
      "Reuses the 0x90d50 table packet shape with g7-20 remainder-30 and operand 0xc000, followed by the 0x2be52b0 response publication.")
label(0x00094364, "geometry_table_packet_callsite_94364",
      "Reuses the 0x90e80 table packet shape with g7-30 remainder-30 and operand 0xc800, followed by the 0x2be52b0 response publication.")
label(0x00094498, "geometry_table_packet_callsite_94498",
      "Reuses the 0x90c10 table packet shape with g7-0xdee remainder-30 and operand 0xb800, followed by the 0x2be52b0 response publication.")
label(0x000945cc, "geometry_table_packet_callsite_945cc",
      "Reuses the 0x90d50 table packet shape with g7-0x21c remainder-30 and operand 0xc000, followed by the 0x2be52b0 response publication.")
label(0x000946fc, "geometry_table_packet_callsite_946fc",
      "Reuses the 0x90e80 table packet shape with g7-0x226 remainder-30 and operand 0xc800, followed by the 0x2be52b0 response publication.")
label(0x00091b58, "geometry_calibration_packet_91b58",
      "Emits the seven-word 5/18 packet with three combined input words, selector 21, an explicit carried r4 secondary word, then calls shared helper 0x8e310 and emits completion 6.")
label(0x00091bc8, "geometry_calibration_packet_91bc8",
      "Repeats the seven-word 5/18 packet shape at the paired calibration site, with three combined words and carried r4 secondary value before helper 0x8e310 and completion 6.")
label(0x00091c58, "geometry_calibration_packet_91c58",
      "Repeats the seven-word 5/18 packet shape at the second paired calibration site, with three combined words and carried r4 secondary value before helper 0x8e310 and completion 6.")
label(0x00091ccc, "geometry_calibration_packet_91ccc",
      "Emits the paired 16-word 6/5/18 packet with address-derived words, selectors 21/47/19, 0x4000 mask, XOR payloads, auxiliary word, and three 0.2 literals before the flag-dependent helper branch.")
label(0x0008f810, "geometry_diagnostic_math_8f810",
      "Adjusts the stack by 0xc0, saves g8 at fp+0xe0 and g12 at fp+0xf0, loads the persistent seed from 0x503b38, then builds the math-driven prefix: source halfword minus 0x253 masked to 9 bits and shifted left 7, selector 5/27 framing, response-dependent real calculation, selectors 18/58, -1.0, and frame readback; the mulr/mulrl numeric seam remains explicit.")
label(0x000985d8, "geometry_diagnostic_math_callsite_985d8",
      "Calls the shared 0x8f810 diagnostic-math entry immediately after service 0x2a990; its continuation updates the 0x562540/0x562740/0x562940 diagnostic values before emitting the next selector-5/18 packet.")
label(0x0008f928, "geometry_diagnostic_math_packet_8f928",
      "Emits the second math-driven nine-word packet: selectors 5/44, constants 0xbfe820c5/0x4189f8a1/0x3f6c7e28, literals 0x3c0f/0xdfc5, the response-derived word, and frame readback.")
label(0x0008f910, "geometry_diagnostic_math_response_handoff_8f910",
      "Publishes the math packet frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and enters the next 5/44 packet at 0x8f928.")
label(0x0008f9d0, "geometry_diagnostic_math_window_8f9d0",
      "Selects the r3-zero window 0x12a7ee/0x12a80e/0xa8b135/0 or nonzero window 0x12b8fc/0x5a36f2/0xa8c5fc/g14, writes control 0x101, emits completion 6, and calls 0x6fec0.")
label(0x0008f9ac, "geometry_diagnostic_math_window_gate_8f9ac",
      "Publishes the math follow-up frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on r3 to 0x8f9d4 or 0x8fa08.")
label(0x0008fa78, "geometry_diagnostic_math_post_service_8fa78",
      "Emits the post-0x6fec0 ten-word 5/44 packet with three payload words, three masked halfwords, selector 58 (31+27), and frame readback.")
label(0x0008fb0c, "geometry_diagnostic_math_post_response_gate_8fb0c",
      "Publishes the post-service frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on r3 to 0x8fb30 or 0x8fb84.")
label(0x0008fb2c, "geometry_diagnostic_math_post_window_tail_8fb2c",
      "Selects the r3-dependent post-service three-word window, writes control 0x101 and a zero fourth word, advances primary/auxiliary cursors by 0x2c, and loops to 0x8fa78 while the primary cursor remains <= 0x14292c.")
label(0x0008fbf4, "geometry_diagnostic_math_setup_8fbf4",
      "Emits the eight-word 5/44 setup packet containing g14, constants 0x419993a9/0xbdb39c0f, 0xf099, and two repeated g14 words before the second math sequence.")
label(0x0008fc54, "geometry_diagnostic_math_second_8fc54",
      "Builds the second math-driven 13-word packet with selectors 5/18/27/20/58, -1.0, 0x40000000, 0xbe800000, the normalized shifted operand twice, the computed word, and frame readback; real arithmetic remains unresolved.")
label(0x0008fd64, "geometry_diagnostic_math_second_window_8fd64",
      "Selects the r3-zero window 0x12d368/0x12d3b0/0xa8e799/g14 or nonzero window 0x12d368/0x5a3a32/0xa8e799/g14, writes control 0x101, and publishes the window at 0x804000.")
label(0x0008fd3c, "geometry_diagnostic_math_second_window_gate_8fd3c",
      "Publishes the second math frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on r3 to 0x8fd68 or 0x8fda4.")
label(0x0008fdf0, "geometry_diagnostic_math_terminal_8fdf0",
      "Emits the terminal 14-word 6/5/18 math packet with -1.0, 0x40000000, 0xbe800000, repeated normalized operand, selector 20, computed word, selector 58, and frame readback; real arithmetic remains unresolved.")
label(0x0008fddc, "geometry_diagnostic_math_terminal_handoff_8fddc",
      "Commits the selected four-word response window to 0x804000, emits completion selector 6, and enters the terminal math packet at 0x8fdf0.")
label(0x0008fee4, "geometry_diagnostic_math_third_window_gate_8fee4",
      "Publishes the third math frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on r3 to 0x8ff04 or 0x8ff40.")
label(0x0008ff00, "geometry_diagnostic_math_third_window_8ff00",
      "Selects the third r3-zero window 0x12d3b4/0x12d3fc/0xa8e818/0 or nonzero window 0x12d3b4/0x5a3a36/0xa8e818/frame, writes control 0x101, publishes at 0x804000, and emits completion 6.")
label(0x0008ff98, "geometry_diagnostic_math_third_setup_8ff98",
      "Emits the eight-word 5/44 setup packet containing frame, 0x415c7ae1, 0xbfe66666, 0x71, and repeated frame words before the following math sequence.")
label(0x0008fff4, "geometry_diagnostic_math_third_8fff4",
      "Builds the third math-driven 15-word packet with selectors 5/18/27/20/58, constants 0xbf000000/0x3f800000/0xbfa66666, -0x800, repeated normalized shifted operand, computed word, and frame readback; real arithmetic remains unresolved.")
label(0x00090124, "geometry_diagnostic_math_third_window_90124",
      "Selects the r3-zero window 0x12d400/0x12d464/0xa8e897/frame or nonzero window 0x12d400/0x5a3a3a/0xa8e897/frame, writes control 0x101, publishes at 0x804000, emits completion 6 twice, and calls 0x6fec0.")
label(0x000901b0, "geometry_diagnostic_math_record_packet_901b0",
      "Emits the 14-word record-loop math packet with selectors 5/18/21/27/27/20/58, shifted source words from 0x562b40, and an explicit computed-word boundary before the 0x902b4 response gate.")
label(0x000902b4, "geometry_diagnostic_math_record_window_gate_902b4",
      "Publishes the record-loop frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on r3 to 0x902e0 or 0x9031c.")
label(0x000902e0, "geometry_diagnostic_math_record_window_902e0",
      "Selects the record-loop zero/nonzero four-word window, writes control 0x101, publishes at 0x804000, emits completion 6 twice, and calls 0x6fec0 before 0x90398.")
label(0x00090398, "geometry_diagnostic_math_record_packet_90398",
      "Emits the ten-word 5/44 record packet with record/payload words, three masked halfwords, selector 58, and frame readback before the 0x9044c response window.")
label(0x0009044c, "geometry_diagnostic_math_record_window_9044c",
      "Selects a supplied zero/nonzero three-word record window, writes a zero or frame fourth word, control 0x101, and publishes the quartet at 0x804000; pointer-loop mechanics remain separate.")
label(0x000904f4, "geometry_diagnostic_math_record_loop_904f4",
      "Advances the primary and auxiliary record pointers by 0x2c, repeats while the incremented primary pointer is <= 0x142a60, emits per-iteration completion 6 plus a final completion 6, and returns at 0x9052c.")
label(0x0008f3cc, "geometry_diagnostic_variant_c_packet_8f3cc",
      "Emits the nine-word 5/18 packet with frame word, constants 0x418edaee/0xbed6a162, selectors 20/0x441/44, and frame readback.")
label(0x0008f458, "geometry_diagnostic_variant_c_window_8f458",
      "Selects the r12-zero window 0xed0ba/0xed378/0xa466a5/0 or nonzero window 0xed0ba/0x599a7a/0xa466a5/g14, writes control 0x101, and continues at 0x8f4d0.")
label(0x0008f4d0, "geometry_diagnostic_variant_c_fixed_8f4d0",
      "Emits the 11-word 6/5/44 packet with 0x4019999a, g14, 0x3f333333, 0x11e, 0xf8ce, 0xfccf, selector 44, and frame readback.")
label(0x0008f57c, "geometry_diagnostic_variant_c_final_8f57c",
      "Selects the final r12-zero window 0x402f58/0x403138/0x84f601/g14 or nonzero window 0x402f58/0x5afdda/0x84f601/g14, writes control 0x101, emits completion 6 twice, and returns at 0x8f618.")
label(0x0008f120, "geometry_diagnostic_variant_b_loop_8f120",
      "Selects zero/nonzero frame windows from the current record base, writes control 0x101, advances both record pointers by 0x2c, compares the primary pointer inclusively against 0x14250c, and emits terminal completion 6 only when the loop ends.")
label(0x0008f0f8, "geometry_diagnostic_variant_b_response_gate_8f0f8",
      "Publishes the frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on the persistent seed flag to 0x8f120 or 0x8f174.")
label(0x0008e5b4, "geometry_diagnostic_window_select_8e5b4",
      "Selects one of two three-word command-window payloads from the state word, writes a zero fourth word, repeats control 0x101 at 0x800010, emits completion selector 6, advances both record streams by 0x2c, and repeats while the incremented pointer is <= 0x142170.")
label(0x0008e590, "geometry_diagnostic_response_gate_8e590",
      "Publishes the frame readback plus 0x34 at 0x801008, reloads the FIFO response from 0x884000, and routes on the preserved 0x503b38-derived r15 flag to 0x8e5b8 or 0x8e60c.")
label(0x0008e67c, "geometry_diagnostic_terminal_packet_8e67c",
      "After the 0x2c-stride scan terminates, emits the fixed seven-word 5/18 packet with constants 0xc0789518, 0x4192b46e, bit 31, selector 46, and the frame readback.")
label(0x0008e6f8, "geometry_diagnostic_route_select_8e6f8",
      "Routes after comparing 0x5624d4 and r15: zero 0x5624d4 selects 0x8e774, otherwise zero r15 selects 0x8e704 and nonzero r15 selects 0x8e738.")
label(0x0008e704, "geometry_diagnostic_route_packet_8e704",
      "Writes the fixed 0x400de4/0x400ea4/0x84cf72/0 command window with control 0x101 and continues at 0x8e7f4.")
label(0x0008e738, "geometry_diagnostic_route_packet_8e738",
      "Writes 0x400de4/0x5af93a/0x84cf72 and the frame-supplied fourth word with control 0x101, then continues at 0x8e7ec.")
label(0x0008e774, "geometry_diagnostic_zero_state_8e774",
      "Selects the r15-zero frame quartet at offsets +0x50/+0x54/+0x58/+0x5c or the nonzero quartet at +0x60/+0x64/+0x68/+0x6c, repeats control 0x101, and converges at 0x8e7ec.")
label(0x0008e7f4, "geometry_diagnostic_mod_gate_8e7f4",
      "Computes 0x562b40 modulo 0x168, emits completion selector 6, and routes remainder <= 19 to 0x8e818 or larger remainders to 0x8e834.")
label(0x0008e818, "geometry_diagnostic_table_select_8e818",
      "Selects the diagnostic table family: low remainders use 0x2be4d10 with a -0x5a60 adjustment for zero r15, 20..139 index (remainder-20)>>1, 140..239 use 0x2be4fd4 with the same zero-r15 adjustment, and 240..359 index (0x167-remainder)>>1 from 0x2be4770 or 0x2be4d10.")
label(0x0008e8f4, "geometry_diagnostic_converged_packet_8e8f4",
      "Emits the converged ten-word 5/44 packet with constants 0x4071ff2e/0x41417c85/0x3fae1134, 0x1588, frame payload, 0xfff8, selector 46, and readback; writes the selected table words plus g14 to 0x804000, stores/reloads g14 through [fp+0x7c] for word 3, and emits completion 6.")
label(0x0008e120, "geometry_inner_packet",
      "Builds the inner per-record packet with masked first-three ldos fields and sign-extended later-three fields, then tests incoming g6 for object +0x4 versus +0x8 selection independently of the FIFO readback; the upstream 0x8e2b4 table arm selects 0x562430 + index*12, while the alternate path publishes directly at +0x174/+0x17c.")
label(0x0008e110, "geometry_first_continuation_handoff",
      "Advances the first-record table cursor by 12, auxiliary cursor by 2, source cursor by 8, and destination cursor by 8 before entering the shared 0x8e120 continuation loop.")
label(0x0008e2b0, "geometry_inner_continuation_tail",
      "Publishes an admitted continuation record through 0x562430 + index*12, advances the table, auxiliary, source, destination, object, and record cursors, and loops back to 0x8e120 until the record limit is reached.")
label(0x0008dd40, "geometry_object_packet",
      "Scans bounded geometry records, masks the first three ldos packet fields, preserves sign extension for the later three ldos fields, emits the object packet, and tests incoming g6 separately from the FIFO readback to select object +0x4 versus +0x8; the 0x8df64 table arm is admitted upstream and still requires index through 5.")
label(0x0008dfc0, "geometry_object_packet_alt",
      "Parallel conditional geometry writer with the alternate returned-vector destination.")
label(0x000bedf0, "geometry_table_select_bcc",
      "Selects a bccxx table from signed fields at +0x172/+0x188 and field +0x64.")
label(0x000beee0, "geometry_table_select_bcd",
      "Parallel table selector using the bcdxx table family.")
label(0x000bf0c0, "object_last_active_row",
      "Scans caller-supplied 0x20-byte rows backward and returns the first nonzero active-row index or -1.")
label(0x000befd0, "geometry_table_select_bce",
      "Parallel table selector using the bcexx table family.")
label(0x000bece0, "object_pair_scan",
      "Scans two 32-entry object tables, suppresses record bit-8 entries, and dispatches admitted values through 0xbcf44.")
label(0x000be1f0, "object_service_prelude",
      "Scans paired active records for selector-7 service requests, then requests nonzero +0x48 status updates before the packet path.")
label(0x000be304, "object_profile_packet_prefix",
      "Gates linked record halfword +2, then emits selector 70, linked fields, a 1.0/0.5-scaled profile word, and profile record fields.")
label(0x000bf120, "object_active_row_count",
      "Counts nonzero row bytes in reverse over a caller-supplied 0x20-byte-stride object range.")
label(0x000bf180, "object_dispatch_context_a",
      "Routes the special object to context 0x565320 and all others to 0x5658a0 before calling 0xa1050.")
label(0x000bf1c0, "object_dispatch_context_b",
      "Shares object/context routing with the 0xbf180 helper and calls 0xa98f0.")
label(0x000bf200, "object_dispatch_context_c",
      "Shares object/context routing with the 0xbf180 helper and calls 0xa55e0.")
label(0x0009b498, "command_record_pool_clear",
      "Clears the first byte of each of the sixteen 0x10-byte records at 0x562b80, walking offsets 0xf0 through 0, then resets the allocation cursor at 0x562b70.")
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
      "Reads backup byte 0x1d00027 and publishes profile words to 0x512bd4/0x512bd8/0x512bdc; default words are 0x3f0ccccd, 0x3f59999a, and 0x3e19999a. Ten indexed routes are recovered: the first nine are full raw triples, while backup value 10 selects first word 0x3f266666 and the default second/third words.")
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
      "First returns the source slot through the 32-entry release leaf at 0x6fb58, then uses 999 as the no-record sentinel to redirect record offsets 0x14/0x18 or side-table offsets 0x5c4/0x5c8 and decrements the reference count.")
label(0x00023ca0, "geometry_cleanup_helper",
      "Clears object bytes 0xa0, 0xa1, and 0xa2; publishes float bits 0x41200000 to 0x504d54 and 0x504d58; returns through 0x23cd8.")
label(0x00023954, "geometry_object_lifecycle_tail",
      "Increments byte offset 0x19 only when byte offset 0x18 is zero and the prior value is at most 31; otherwise preserves it.")
label(0x000783c8, "transition_wrapper",
      "Indexes table 0x72690 with selector 0x504d68 and sets action 5.")
ensure_function(0x00078120, "transition_helper_78120", 0x00078190)
label(0x00078120, "transition_helper_78120",
      "Transition helper prefix: gates 0x504dc0/0x504dd0, masks 0x504d6c, publishes state 2, and selects bit-15 helper paths.")
ensure_function(0x00078448, "transition_action10_table_wrapper_78448", 0x00078478)
ensure_function(0x00078488, "transition_action10_table_wrapper_78488", 0x000784b8)
label(0x00078448, "transition_action10_table_wrapper_78448",
      "Action-10 wrapper: indexes table 0x72990 by 0x504d68 and publishes the selected transition.")
label(0x00078488, "transition_action10_table_wrapper_78488",
      "Action-10 wrapper: indexes table 0x729f0 by 0x504d68 and publishes the selected transition.")
label(0x00078190, "transition_helper_state2_packet",
      "State-2 packet body: emits selectors 29/30/10 with signed halfword-adjusted object fields, classifies the response, and selects table 0x72930.")
label(0x00078264, "transition_helper_state2_packet_alt",
      "Alternate state-2 packet body: uses -0x4000 halfword adjustment and result table 0x72960 before the shared result tail.")
label(0x00078334, "transition_helper_state2_result_tail",
      "State-2 result tail: publishes counter 5 and the selected table result to 0x504d94, then returns.")
ensure_function(0x0007834c, "transition_helper_bypass", 0x00078390)
label(0x0007834c, "transition_helper_bypass",
      "Transition-helper bypass: publishes state 3, selects status 12/13 from 0x504d68, writes counter 5, and returns.")
label(0x00078640, "object_action_state_gate_78640",
      "Object-action state gate: state 8 calls 0x78790; other states continue through the inline 0x78658 timing path.")
label(0x00078658, "object_action_inline_timing_78658",
      "Inline object-action timing route: calls 0x784c8, rejects invalid absolute differences, then selects action 5 or action 10.")
ensure_function(0x00078408, "transition_wrapper_action10", 0x00078438)
label(0x00078410, "transition_wrapper_action10_table_lookup",
      "Indexes the action-10 transition table at 0x72750 with selector 0x504d68, writes the selected transition to 0x504d94, and publishes action 10 at 0x504db8.")
ensure_function(0x00078818, "transition_conditioned_wrapper", 0x00078880)
label(0x00078830, "transition_conditioned_wrapper_table_lookup",
      "Indexes table 0x72690 and normally publishes action 5; when bit 5 of 0x504e30 is set and 0x504dc8 equals 1, writes status 1, selector state 6, and action 20 before the fixed 0x78880 continuation.")
ensure_function(0x00078bd8, "transition_state3_wrapper", 0x00078c74)
label(0x00078c04, "transition_state3_priority_gate",
      "For object state 3 with mode bits 2 and 3 both set, publishes selector state 18 and status 1; otherwise the bit-3 plus gate-1 path publishes selector state 16. Both overrides set action 20 after the normal table-0x72690/action-5 setup.")
ensure_function(0x00078c80, "transition_state3_variant", 0x00078d44)
label(0x00078cb4, "transition_state3_variant_priority_gate",
      "Uses the state-3/mode-mask-0xc selector-18 override first; otherwise bit 4 plus gate 1 selects state 17, with state 3 plus bit 2 upgrading it to 18. Override paths publish status 1 and action 20.")
ensure_function(0x00078d50, "transition_conditioned_wrapper_18", 0x00078dc0)
label(0x00078d78, "transition_conditioned_wrapper_18_gate",
      "Shares the bit-5 plus gate-1 predicate with 0x78818, but publishes selector state 18 and action 20 instead of selector state 6; normal execution retains action 5.")
ensure_function(0x00079c10, "transition_timing_threshold_helper", 0x00079cb8)
label(0x00079c18, "transition_timing_lower_threshold",
      "Converts the lower timing threshold word at 0x504e04 and compares it with current timing at 0x504d60 before publishing the default selector/action state.")
label(0x00079c44, "transition_timing_upper_threshold",
      "Converts the upper timing threshold word at 0x504e06 and performs the second bounded comparison against 0x504d60.")
label(0x00079c88, "transition_timing_threshold_recheck",
      "Rechecks the current value against the lower threshold before routing to the action-10 or action-5 transition wrappers.")
label(0x00079c9c, "transition_timing_action5_gate",
      "Compares the current timing value with the upper threshold and routes the accepted interval to the action-5 wrapper at 0x783c8.")
ensure_function(0x00079cc0, "transition_timing_threshold_helper_variant", 0x00079d1c)
label(0x00079cc0, "transition_timing_variant_lower_threshold",
      "Converts the lower threshold at 0x504e04 and compares it with current timing at 0x504d60 before selecting the action-10 path or checking the upper threshold.")
label(0x00079cdc, "transition_timing_variant_action10_route",
      "Routes the first threshold outcome through the action-10 wrapper at 0x78408.")
label(0x00079ce4, "transition_timing_variant_upper_threshold",
      "Converts the upper threshold at 0x504e06 and compares it with current timing before the action-5/action-10 split.")
label(0x00079d00, "transition_timing_variant_state_dispatch",
      "Dispatches the accepted threshold case by state through action-10 wrappers at 0x78488 or 0x78448.")
ensure_function(0x00079630, "transition_post_threshold_selector", 0x00079714)
label(0x00079630, "transition_post_threshold_time_gate",
      "Converts threshold word 0x504dfc, compares it with current timing 0x504d60, and enters the normalized selector fan-out only on the accepted side; the fallback routes to the action-5 wrapper.")
label(0x0007967c, "transition_post_threshold_selector_table",
      "Eight-entry normalized selector table maps indices to transition values 1, 1, 2, 2, 3, 3, 5, and 6 before the shared object-state update at 0x79050.")
label(0x000796ec, "transition_post_threshold_action30_tail",
      "Re-enters the shared object-state dispatcher with the normalized value, then publishes action 30 at 0x504db8.")
ensure_function(0x00079720, "transition_dispatch_79720", 0x00079834)
label(0x00079720, "transition_dispatch_79720_threshold_gate",
      "Converts threshold word 0x504dfc and compares it with timing 0x504d60 before the ten-entry caller-state dispatch; the opposite comparison tail may route to action 5.")
label(0x00079750, "transition_dispatch_79720_state_table",
      "Ten-entry table maps caller states 0/1 to 0x79784/0x79794, 2-4 to transition 12, 5-7 to transition 13, and 8/9 to 0x797d0/0x797e0.")
label(0x000797ec, "transition_dispatch_79720_shared_state_tail",
      "Gate-1 arms publish status 1, re-enter 0x79050, overwrite transition with 1, and publish action 30.")
ensure_function(0x00079840, "transition_dispatch_728d0_variant", 0x0007990c)
label(0x00079840, "transition_dispatch_728d0_variant_threshold_gate",
      "Converts threshold word 0x504dfa and compares it with timing 0x504d60 before loading the caller-state transition from table 0x728d0.")
label(0x0007985c, "transition_dispatch_728d0_variant_table_lookup",
      "Loads table 0x728d0 using the caller-state index, initializes action 5, and routes the low-state and high-state groups through separate gates.")
label(0x00079880, "transition_dispatch_728d0_variant_low_state_gate",
      "For the low-state group, gate 1 publishes status 1 and re-enters 0x79050 before writing transition 1 and action 30; the alternate arm writes transition 18.")
label(0x000798b4, "transition_dispatch_728d0_variant_high_state_gate",
      "For caller states at least 7, gate 1 re-enters 0x79050 and publishes transition 3/action 30; the alternate arm writes transition 19.")
ensure_function(0x00079910, "transition_dual_window_variant", 0x00079a8c)
label(0x00079910, "transition_dual_window_lower_threshold",
      "Converts threshold word 0x504e0e and compares it with timing 0x504d60 before checking upper threshold word 0x504e10.")
label(0x00079944, "transition_dual_window_gate_override",
      "When the timing window and gate 1 both pass, publishes selector state 3, clears the transition field, and sets status 1/action 20; otherwise the 0x728d0 action-10 table path remains active.")
label(0x00079980, "transition_dual_window_table_path",
      "Loads 0x728d0 by caller state, initializes action 10, and upgrades states 0 or 9 to selector state 3 with status 1/action 20.")
label(0x000799fc, "transition_dual_window_state8_tail",
      "Applies the later state-8 and state-9 selector/gate overrides, each publishing selector state 3, status 1, and action 20 when its bounded selector predicate passes.")
ensure_function(0x00079a90, "transition_mode2_window_variant", 0x00079c04)
label(0x00079a90, "transition_mode2_window_gate",
      "Tests mode state 1, then converts threshold words 0x504e0e/0x504e10 and gates the selector-3 override on mode bit 2 plus transition gate 1.")
label(0x00079b28, "transition_mode2_window_table_path",
      "Loads the 0x728d0 table for the alternate timing path, initializes action 10, and promotes caller states 0 or 9 to selector state 3/action 20 with status 1.")
label(0x00079b74, "transition_mode2_window_state_tail",
      "Applies state-8 and state-9 checks against the current selector and gate, publishing selector state 3, status 1, and action 20 on the matched path.")
label(0x00078dd0, "geometry_entry_state_gate",
      "Reads object state at offset 0x64; states 2 and 4 call the service at 0x7cbc0 immediately, while all other states continue into the geometry packet builder.")
label(0x00078de4, "geometry_entry_packet_path",
      "Non-service states begin the command-29 geometry packet path using object and shared-state fields.")
ensure_function(0x00078dec, "geometry_packet_timing_route", 0x00079040)
label(0x00078dec, "geometry_packet_timing_prologue",
      "Loads and converts 0x504e0c, reads 0x504dbc and the related-object pointer from object +0x74, then begins the command-29/30 response sequence.")
label(0x00078e48, "geometry_packet_command30_setup",
      "Publishes command 30 after the first response and derives the paired coordinate payload from object +0x184 and the related record.")
label(0x00078ef0, "geometry_packet_primary_timing_split",
      "Compares the first response-derived value with the 0x40510000 floor; the accepted arm publishes status/transition overrides or continues to the secondary timing test.")
label(0x00078f5c, "geometry_packet_secondary_timing_split",
      "Converts the second response-derived threshold, compares current timing at 0x504d60, and routes accepted values through the existing action-10/action-5 wrappers.")
label(0x00078fa0, "geometry_packet_selector_fallback",
      "Maps the related selector around 0x504d68 to transition 12 or 13 and publishes the default action 5 when timing remains in the bounded interval.")
label(0x00078fdc, "geometry_packet_control_override",
      "Publishes status 1 and transition 2/3, upgrades state 4 to transition 3, and replaces the action with 25 before returning.")
ensure_function(0x0007cbc0, "transition_service_7cbc0", 0x0007cc44)
label(0x0007cbd4, "transition_service_timing_gate",
      "Compares the converted 0x504e0c field against the 0x504d60 timing quad; the clear path calls action-5 wrapper 0x783c8, while the passed path selects the 0x72900 action-10 service.")
label(0x0007cbe4, "transition_service_action10_arm",
      "Loads selector table 0x72900, publishes action 10, and conditionally enters the control-1 transition override.")
label(0x0007cc0c, "transition_service_control_override",
      "Control value 1 publishes status 1, transition 2 or 3 by object state 4, and replaces the action with 25.")
ensure_function(0x000784c8, "transition_status_dispatch_784c8", 0x0007863c)
label(0x000784c8, "transition_status_dispatch_entry",
      "Ten-entry status predicate dispatcher; selector arms conditionally write 1 to 0x504d84 and return through the saved continuation.")
label(0x00078508, "transition_status_selector_0_bit1",
      "Selector 0 status arm: writes status 1 when mode bit 1 is set.")
label(0x00078524, "transition_status_selector_1_bit2",
      "Selector 1 status arm: writes status 1 when mode bit 2 is set.")
label(0x00078540, "transition_status_selector_2_mode6",
      "Selector 2 status arm: writes status 1 when either mode bit 1 or bit 2 is set.")
label(0x00078638, "transition_status_dispatch_return",
      "Default/out-of-range return path with no status write.")
label(0x000784c8, "transition_selector_dispatch",
      "Has ten targets from 0x78508 through 0x78618; selectors at or above 10 return immediately. Action-5 values are 8,12,12,12,12,13,13,13,19,8; action-10 values are 9,16,12,12,12,13,13,13,17,9.")
label(0x000786d0, "object_action_timing_split",
      "Runs the shared 0x784c8 status dispatcher on object state, then uses a floating absolute-difference validity check; valid values route to action 5 when current is at least threshold, otherwise action 10, while nonfinite differences reject.")
ensure_function(0x00078740, "timing_status_variant_78740", 0x00078780)
label(0x00078740, "timing_status_variant_entry",
      "Runs the shared status dispatcher, then compares the timer against converted 0x504dd8: strictly greater selects action 10, while less-than-or-equal writes status 1 directly.")
label(0x00078774, "timing_status_variant_status_arm",
      "Non-greater comparable timing values publish status 1 without calling an action wrapper.")
ensure_function(0x00078790, "state8_action_route_78790", 0x00078808)
label(0x00078790, "state8_action_route_entry",
      "State-8 timing route: validates the 0x504d60 versus converted 0x504dd6 difference, then selects action 10/action 5 or the 0x72990/0x729f0 action-10 variants.")
label(0x000787c0, "state8_action_invalid_timing",
      "Unordered normalized timing publishes status 1 and returns without an action call.")
label(0x000787d4, "state8_action_control_split",
      "For current timing above threshold, control 0x504e28 selects the action-5 fallback or the related-band action-10 table variant.")
ensure_function(0x00078890, "state_geometry_packet_78890", 0x00078a28)
label(0x00078890, "state_geometry_packet_prologue",
      "Converts the 0x504df8 divisor prologue, selects the 0x729c0 table value, and begins paired command-29/30 requests using object +0x184 plus 0x5000 and the derived scale word.")
label(0x00078950, "state_geometry_command10_delta_pair",
      "Forms command-10 operands from object +0x08/+0x10, related +0x08/+0x10, and the two preceding FIFO responses.")
label(0x000789b0, "state_geometry_command31_tail",
      "Emits the six-word 31+31 tail [62, current-minus-response, related +0x08, current +0x10 plus response, related +0x10, scale].")
label(0x000789e8, "state_geometry_packet_control_override",
      "When mode bit 5 and 0x504dc8 == 1, writes status 1, transition 6, and action 20 after the command-31 response.")
ensure_function(0x00078a30, "state_geometry_packet_78a30", 0x00078bc8)
label(0x00078a30, "state_geometry_packet_78a30_prologue",
      "Sibling of 0x78890: selects table 0x72a20 and emits the same command-29/30/10/31 packet flow with object +0x184 minus 0x5000 before the shared bit-5/control-1 override.")
label(0x00024690, "geometry_command6_dynamic_loop",
      "Starts at index 0, increments by 1, requires active-mask bit 2, and emits six-word packets with header 5,19 and trailer 1,58; readback is at 0x802008, publish is at 0x801008, and computed values divide by 600.")
label(0x000df0cc, "geometry_object_response_vector_selector",
      "Sign-extended related-object halfword selects triplet 0, 1, or 2; other selectors write three zero words.")
label(0x00077e60, "action_jump_dispatch",
      "Uses a 44-entry jump table at 0x77e7c; selectors at or above 44 fall back to 0x78084, with table targets spanning 0x77f2c through 0x7807c.")
ensure_function(0x00077de0, "state_history_shift_forward", 0x00077e10)
ensure_function(0x00077e20, "state_history_shift_reverse", 0x00077e50)
label(0x00077de0, "state_history_shift_forward",
      "Copies 0xf4 bytes from 0x504f60 to 0x504d60, then copies the resulting 0x504d60 state to 0x504e60 through 0xf5d40.")
label(0x00077e20, "state_history_shift_reverse",
      "Copies 0xf4 bytes from 0x504e60 to 0x504d60, then copies 0xf4 bytes from 0x504f60 to 0x504e60 through 0xf5d40.")
ensure_function(0x00077c40, "record_flag_scan", 0x00077dd0)
label(0x00077c40, "record_flag_scan",
      "Scans 32 records from object +0x200 at 0x20-byte stride in two passes, initializes output byte 0x504e50, counts bit-13 matches against threshold 20, and updates output bits 2/3/4/5/6/7; one second-pass bound remains register-derived.")
ensure_function(0x00078090, "divisor_clamp_78090", 0x00078110)
label(0x000780a4, "divisor_clamp_mode_gate",
      "Selects the wide divisor 0xbb8 for modes 4 and 7; the literal-first cmpibge arm preserves the separate mode-7 check.")
label(0x000780d0, "divisor_clamp_signed_divide",
      "Divides the signed dividend at 0x504dc0 by the selected divisor, then clamps the quotient to the upper bound 90.")
label(0x000780e4, "divisor_clamp_flag_gate",
      "Compares the original dividend against 120 (15 shifted left three); values above the threshold publish flag 1.")
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
      "Derives positions with offsets +2, -1, +12, -7; stage sources are 0x2fde9d0, 0x2fe1606, and 0x2fe158e, with dimensions (g24+31)x8, (g3+31)x2, and 30x2 and helpers 0x1dc10/0x1dc90/0x1df00 by mode.")
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
      "Initializes a 22x2 clear at (g11+31,g11+31), routes values above 99 through message 0x20040/helper 0x1d1f0, values at or below 1 through clear, and values 2..99 through digit helper 0x1ff50 plus the two tile sources 0x2fdfc00/0x2fdfbfc.")
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
      "Renders latches 21..32 from source 0x2fda1d0 through 0x1dc10 at column 0, row latch*4-84, as 0x40x4; latch 33 clears eight marker words at 0x504d24..0x504d32, and latch 34+ hands off to downstream logic at 0x21af0.")
label(0x00021af0, "status_latch_record_text_routes",
      "Routes latches 34..35 through 0x211f0 mode 0 and three 0x1d250 text records, latch 36 through the shared 0x21fa4 tail, latches 37..48 through 0x211f0 mode 1 and three 0x1d210 records, and leaves higher values at 0x21cf8 for downstream logic.")
label(0x00021cf8, "status_latch_strip_handoff",
      "For latch values at or below 50, writes origin (7,8), calls 0x20a20 with input 1, width/scale 0x118, zero pattern and zero fill, then joins 0x21fa4; values above 50 continue at 0x21d44.")
label(0x00021d44, "status_latch_command_dispatch",
      "Admits exact latch 56 and 66 cases: latch 56 calls 0x2a4e0 with 0x1322 when selector 0x503a7c is zero, otherwise loads a signed-halfword command from 0x21180[selector*4]; latch 66 continues at 0x21ef8; other values join 0x21fa4.")
label(0x00021d98, "status_latch_glyph_record_route",
      "For exact latch 86 with selector 0x503a7c clear, maps mode 2/6/other to columns 26/23/25, calls 0x1d880 on 0x20ba8+mode*104, then loads record offsets 0x4c/0x50/0x54 from 0x20b50[glyph*0x68] and transfers through 0x1dc10 at row 8.")
label(0x00021e7c, "status_latch_panel87_route",
      "For exact latch 87, transfers a 20x15 source from 0x211b0[0x5770f0] through 0x1dc10 at (0x5770f0,24), derives a 0x21060 table source for 0x1d1d0 at (0x5770f0+31,26), then reaches the fixed 0x1111 command at 0x21ef8.")
label(0x00021f08, "status_latch_service_routes",
      "Routes latch 156 through 0x22c78 then command 0x133f/0x2a4e0, latch 157 through 0x20ae8(0), latches 158..185 through two 0xf5058 calls and masked 0x504d28/0x504d30 updates, latch 186 through 0x22cb8, and latches 187+ through the 0x504d10 decrement.")
label(0x00021fa4, "status_latch_shared_tail_prefix",
      "Derives latch-36; latches 0..155 use the bit-1 prefix (bit 1 set transfers 0x2fe8ec2 through 0x1dc10, bit 1 clear calls 0x1df00), while latches 156+ continue at 0x22108; both prefix arms converge at 0x2201c.")
label(0x0002201c, "status_latch_selector_pair",
      "When selector latch 0x503a7c is zero, loads selector 0x5770f0, uses origin (selector+31,selector+9), transfers 0x20f60+selector*16 and +8 twice through 0x1d880 for selectors <=7 or 0x1d7d0 above 7, then continues at 0x22108; nonzero selector latch branches to 0x220b8.")
label(0x00022108, "status_latch_timing_gate",
      "Exits status mode 2 to 0x223fc, otherwise admits only latch == 31+r9 or continues at 0x221b8; computes 0x504cd0 from 1000*0x1d00058/0x1d00054 with g14 fallback, publishes 0x1d0004c/0x1d00050 with negative-value fallbacks, and exits at 0x223fc.")
label(0x000222b8, "status_latch_decimal_renderer",
      "For exact latch 70, renders 0x504cd0 and 0x504cd4 as four decimal digits with a 31+r15 separator and renders 0x504cd8 as three digits, using 13 calls to 0x1d090 before 0x223fc.")
label(0x000221b8, "status_latch_text_schedule",
      "For latch values below 70, calls 0xf5058 ten times, reduces results modulo 10, emits twelve values through 0x1cd18 with two 31+r15 separators, and uses column 13 with row bases r11/r13 before 0x223fc; latch 70+ continues at 0x222b8.")
label(0x000223fc, "status_latch_convergence_gate",
      "Requires selector latch 0x503a7c nonzero and latch-87 <= 68; bit 3 selects attributed 0x2241c or plain 0x224e4, while rejected cases continue at 0x22590.")
label(0x0002241c, "status_latch_attributed_render_arm",
      "Selects mode columns 26/23/25, transfers record offsets 0x4c/0x50/0x54 through 0x1dc10 at row 8, then matches 0x20ba8+mode*104 through 0x1d880 before 0x22590.")
label(0x000224e4, "status_latch_plain_render_arm",
      "Selects mode columns 26/23/25, clears record offsets 0x50/0x54 through 0x1df00 at row 11, then matches 0x20ba8+mode*104 through 0x1d880 at row 8 before 0x22590.")
label(0x00022590, "status_latch_table_initializer",
      "Builds two 25-entry tables at 0x51a0c0 and 0x51a190 with destination stride 8 and source stride 0x20 from 0x180099c/0x180099e; bit 0 of 0x5024e8 selects fixed 0x1df/0x7fe0 or g14 values, then increments 0x504d10.")
label(0x00022670, "status_latch_table_initializer_epilogue",
      "Restores integer quadwords, g13/g14 from frame offsets 0x40/0x44, four floating-point values from 0x48/0x58/0x68/0x78, and returns after the 0x22590 initializer.")
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
      "Clears an 84-byte record image, copies eleven template words into the recovered offsets, narrows source +0x24 to the unaligned destination +0x3e halfword, stores association or sentinel 999, and initializes the second association field to 999.")
label(0x0006fa40, "geometry_pool64_acquire",
      "Increments the 64-entry geometry slot cursor at 0x51c880 before loading a slot from 0x51c85c; counts above 63 return 0xffffffff without changing the cursor.")
label(0x0006fa90, "geometry_pool64_release",
      "Decrements the 64-entry geometry slot cursor and stores the released value into 0x51c860 at the new index.")
label(0x0006f9e0, "geometry_pool64_reset",
      "Clears the 64-entry pool at 0x51c860, clears the corresponding field in each 0x54-byte record at 0x51c5b0, and resets 0x51c880 to zero.")
label(0x0006fad0, "geometry_pool32_reset",
      "Clears all 32 words of the secondary geometry pool at 0x51c890 and resets its cursor at 0x51c910.")
label(0x0006fb10, "geometry_pool32_acquire",
      "Increments the 32-entry geometry slot cursor at 0x51c910 before loading a slot from 0x51c88c; counts above 31 return 0xffffffff without changing the cursor.")
label(0x0006fb50, "geometry_pool32_release",
      "Decrements the 32-entry geometry slot cursor and stores the released value into 0x51c890 at the new index.")
label(0x00020ae0, "hardware_strip_clear",
      "Fills 0x5ff words at 0x100d000 with either 0xffff or zero based on mode, then returns through stub 0x20b48 with the fill register cleared.")
label(0x00022d30, "hud_reset_route",
      "Fills 4-halfword groups at 0x100c940 for caller g1+31 groups, clears four status fields, reduces the generator modulo 5, and uses fallback 0x503a98+4 only when the result exceeds 3.")
label(0x00022c70, "plane_full_clear_thunks",
      "Clears 0xfff words at either plane base 0x1000000 or 0x1004000, with variant-specific return stubs 0x22ca4/0x22ce4; sibling 0x22cf0 clears 0x1001280.")
label(0x00022cf0, "status_tile_plane_partial_clear",
      "Clears 61 halfwords at 0x1001280 from a 31+31 pre-decrement bound and returns through 0x22d24.")
ensure_function(0x00022c70, "plane_full_clear_wrapper_1000000", 0x00022ca4)
ensure_function(0x00022cb0, "plane_full_clear_wrapper_1004000", 0x00022ce4)
ensure_function(0x00022cf0, "status_tile_plane_partial_clear", 0x00022d24)
label(0x000e3830, "text_two_digit_formatter",
      "Formats nonnegative values as two decimal digits, saturating values above 99 to 99; negative values produce no output.")
label(0x000201a0, "video_profile_upload",
      "Uploads from 0x1004000 through helper 0x1bc90 to the profile-selected destination 0x1fcfd20/0x1fd49d0/0x1fd1520 using 0x40 halfwords per row and caller g17+31 rows.")
label(0x0001fbe0, "status_value_renderer",
      "Negative values use block source 0x2fe17ec and call 0x1e7c0 for the 0x2ea1fd0 glyph table, yielding a 4x3 0x1dc10 transfer with index ((value-0x30)&0xf); nonnegative values clear 25x3 with helper 0x1df00.")
label(0x0001fc30, "status_scoreboard_renderer",
      "Normalizes sign-bit 0x8000 values to zero, emits 0x2fe14fe as 31x2 through 0x1dc10, renders all four decimal digits from 0x2ea1e50 with 0x1dc90, and early-returns for state 0/mode 4; separator/suffix sources are 0x2fe158a/0x2fe157a through 0x1dc10.")
label(0x0001fa00, "continued_message_renderer",
      "Selects message 0x1f9e0, calls helper 0x1da90, preserves the caller column, and uses row 20.")
label(0x0001fa30, "status_panel5_source_fill",
      "Uses source 0x2fe053a/helper 0x1dc10 when present, otherwise fill helper 0x1df00; column/row 2,20, width caller value plus 31, height 5.")
label(0x0001fa80, "status_panel6_source_fill",
      "Uses source 0x2fe099a/helper 0x1dc90 when present, otherwise fill helper 0x1df00; column/row 8,10, width caller value plus 31, height 5.")
label(0x0001f4c0, "status_panel_two_block_builder",
      "Uses source 0x2fe01d4 at rectangle 4,10,(g25+31),5; selects table 0x2ea2010 by low nibble after subtracting 0xd0; second rectangle is 28,20,8,5.")
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
