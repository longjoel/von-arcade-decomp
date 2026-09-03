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
label(0x0002a430, "audio_scsp_settle_delay",
      "Short volatile delay between SCSP control writes; recovered as four countdown iterations.")
label(0x0002a458, "audio_scsp_fifo_send_u16",
      "Host-side SCSP command producer. Queues 0xae, high byte, low byte; 0xff is a one-byte special command.")
label(0x0002a4e0, "audio_scsp_fifo_enqueue")
label(0x0002a5f0, "audio_scsp_fifo_send_u16_idle_gate",
      "Sibling command producer with the mode-1/board-status-zero suppression gate.")
label(0x0002a690, "audio_scsp_send_level",
      "Clamps signed level to 1..127 and emits the 0xa0, selector-1, level frame.")
label(0x0002a870, "audio_scsp_send_selector_zero",
      "Emits the 0xa0, selector-0, low-byte frame.")
label(0x0002a8a0, "audio_scsp_initialize",
      "Initializes the 64-byte host FIFO and writes the recovered SCSP control sequence 0,0,0,0x40,0x4e,0x37 before queuing 0xff.")
label(0x00001348, "audio_scsp_service_request",
      "Raises interrupt-control bit 10 in the host mirror and MMIO register to request SCSP FIFO service.")
label(0x000016dc, "audio_scsp_fifo_consumer",
      "Interrupt route 0x400: consumes one queued byte only when the FIFO is nonempty and SCSP status bit 0 is set, then writes it to SCSP command port 0x009c0000.")
label(0x00501cd0, "audio_interrupt_control_mirror")
label(0x0051aa70, "audio_fifo_read_index")
label(0x0051aa74, "audio_fifo_write_index")
label(0x0051aa80, "audio_fifo_bytes_64")
label(0x009c0000, "scsp_command_port")
label(0x009c0004, "scsp_status_control_port")
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
label(0x0002d9a0, "geometry_transform_dispatch",
      "Emits the transformed geometry packet and stores the derived frame fields at 0x51aad0–0x51aae4.")
label(0x0002e1c8, "geometry_status_continuation_trampoline",
      "Continuation trampoline that clears g14 and branches through the caller-supplied continuation.")
label(0x0002e1e8, "geometry_status_continuation_trampoline_alt",
      "Alternate continuation trampoline with the same g14 indirect-return sequence.")
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
      "Updates one runtime object through its state dispatch, geometry motion, profile output, and frame-result paths.")
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
label(0x000f3ec0, "diagnostic_service_handler_table",
      "Literal diagnostic service-handler targets selected by startup mode handler 6.")
label(0x00018620, "startup_mode_handler_8_and_15")
ensure_function(0x00003c40, "startup_mode_handler_0", 0x00003d64)
ensure_function(0x0002b9e0, "startup_mode_handler_1_status_dispatch", 0x0002bb5c)
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
label(0x000e9140, "geometry_runtime_event_dispatch",
      "Updates the rolling geometry-event fields, computes pair deltas, and dispatches the next event arm.")
label(0x000e91f0, "geometry_runtime_event_arm_table",
      "Twelve-entry event-arm table selected from the rolling event counter.")
label(0x000eaa60, "geometry_event_setup_helper",
      "Emits the event setup packet, derives shared geometry fields, and updates the event workspace.")
label(0x000ead20, "geometry_event_lookup_data",
      "Literal geometry-event lookup records following the setup helper.")
label(0x000eada0, "runtime_flag_gate_a",
      "Tests the runtime feature flags and returns a boolean through the supplied continuation.")
label(0x000eade0, "runtime_flag_gate_b",
      "Tests the alternate runtime feature flags and returns a boolean through the supplied continuation.")
label(0x000eae20, "runtime_flag_gate_c",
      "Tests the geometry feature flags and returns a boolean through the supplied continuation.")
label(0x000eae60, "runtime_byte_copy_continuation",
      "Copies a byte span and returns through the caller-supplied continuation.")
label(0x000eaeb0, "runtime_format_value",
      "Formats the supplied runtime value through the shared text conversion helper.")
label(0x000eaed0, "runtime_format_value_adjusted",
      "Formats an adjusted runtime value and selects the board-specific output path.")
label(0x000eaf20, "runtime_render_value_string",
      "Renders the supplied runtime value through the alternate printable-string path.")
label(0x000eaf40, "diagnostic_menu_strings",
      "Literal diagnostic-menu strings used by the runtime test/status screen.")
label(0x000eb060, "diagnostic_menu_render",
      "Renders the diagnostic menu strings and updates the selected test-menu tile state.")
label(0x000eb1c0, "runtime_packed_record_scan",
      "Scans packed runtime records and records matching entry pointers in the shared workspace.")
label(0x000eb2c0, "runtime_record_table_init",
      "Initializes the packed-record workspace, rebuilds its match markers, and advances the status counter.")
label(0x000eb3b0, "runtime_record_base_select",
      "Selects the runtime record base address from the accumulated match markers.")
label(0x000eb450, "runtime_record_match_scan_alt",
      "Scans the alternate packed-record table and records matching entry pointers.")
label(0x000eb510, "runtime_record_table_reset_copy",
      "Resets the packed-record table and copies the selected record words into the active workspace.")
label(0x000eb5b0, "runtime_rom_bank_loader_5e",
      "Loads the packed runtime table from ROM bank 0x5e0000 and refreshes the active matches.")
label(0x000eb600, "runtime_rom_bank_loader_5c",
      "Loads the packed runtime table from ROM bank 0x5c0000 and refreshes the active matches.")
label(0x000eb650, "runtime_rom_bank_loader_5a",
      "Loads the packed runtime table from ROM bank 0x5a0000 and refreshes the active matches.")
label(0x000eb6a0, "runtime_rom_bank_loader_58",
      "Loads the packed runtime table from ROM bank 0x580000 and refreshes the active matches.")
label(0x000eb6f0, "runtime_rom_bank_loader_56",
      "Loads the packed runtime table from ROM bank 0x560000 and refreshes the active matches.")
label(0x000eb740, "runtime_rom_bank_loader_54",
      "Loads the packed runtime table from ROM bank 0x540000 and refreshes the active matches.")
label(0x000eb790, "runtime_rom_bank_loader_52",
      "Loads the packed runtime table from ROM bank 0x520000 and refreshes the active matches.")
label(0x000eb7e0, "runtime_rom_bank_loader_50",
      "Loads the packed runtime table from ROM bank 0x502000 and refreshes the active matches.")
label(0x000eb830, "runtime_rom_bank_load_all",
      "Runs the runtime ROM-bank loaders, normalizes match markers, and advances the status counter.")
label(0x000eb8a0, "runtime_packed_record_match_scan",
      "Copies packed records into the active workspace and records four masked match locations.")
label(0x000ebba0, "runtime_alt_packed_record_scan",
      "Scans the alternate packed-record format and records two masked match locations.")
label(0x000ebc60, "runtime_alt_record_table_init",
      "Initializes the alternate packed-record workspace and rebuilds its match markers.")
label(0x000ebd20, "runtime_alt_packed_record_scan_b",
      "Scans the second alternate packed-record format and records two masked matches.")
label(0x000ebe20, "runtime_alt_record_table_init_b",
      "Initializes the second alternate packed-record workspace and its match markers.")
label(0x000ebf10, "runtime_alt_packed_record_scan_c",
      "Scans the third packed-record format and records its two masked matches.")
label(0x000ebfd0, "runtime_alt_record_table_init_c",
      "Initializes the third alternate packed-record workspace and match markers.")
label(0x000ec090, "runtime_alt_packed_record_scan_d",
      "Scans the fourth packed-record format and records its masked match location.")
label(0x000ec140, "runtime_alt_record_table_init_d",
      "Initializes the fourth alternate packed-record workspace and match marker.")
label(0x000ec1e0, "runtime_alt_packed_record_scan_e",
      "Scans the fifth packed-record format and records its masked match location.")
label(0x000ec290, "runtime_alt_record_table_init_e",
      "Initializes the sixth alternate packed-record workspace and match marker.")
label(0x000ec330, "runtime_alt_packed_record_scan_f",
      "Scans the sixth packed-record format and records its masked match location.")
label(0x000ec3e0, "runtime_alt_record_table_init_f",
      "Initializes the seventh alternate packed-record workspace and match marker.")
label(0x000ec480, "runtime_alt_record_base_select",
      "Selects the active alternate ROM base from the accumulated match markers.")
label(0x000ec630, "runtime_alt_record_table_copy",
      "Copies the selected alternate record table into the active workspace.")
label(0x000ec6a0, "runtime_alt_packed_record_scan_g",
      "Scans the selected alternate table and records its masked match location.")
label(0x000ec760, "runtime_alt_record_table_init_g",
      "Initializes the final alternate packed-record workspace and match marker.")
label(0x000ec820, "geometry_event_lookup_table_build",
      "Expands the geometry-event lookup records into the command lookup table.")
label(0x000ec8f0, "runtime_alt_record_pipeline_dispatch",
      "Runs the alternate record pipeline and advances the runtime service counter.")
label(0x000ec920, "runtime_event_counter_step",
      "Runs the shared event service and advances the runtime service counter.")
label(0x000ec940, "runtime_event_mode_flag_set",
      "Sets the event-mode workspace flag and returns through the caller continuation.")
label(0x000ec970, "runtime_record_checksum_4stride",
      "Accumulates the packed record bytes at four-byte stride and returns through a continuation.")
label(0x000ec9d0, "runtime_record_checksum_3stride",
      "Accumulates the alternate packed record bytes at three-byte offset and returns through a continuation.")
label(0x000eca30, "runtime_event_result_publish_a",
      "Computes and publishes the first event result into the runtime workspace.")
label(0x000eca60, "runtime_event_result_publish_b",
      "Computes and publishes the alternate event result into the runtime workspace.")
label(0x000eca90, "runtime_event_result_publish_c",
      "Publishes the fixed event-source result into the runtime workspace.")
label(0x000ecac0, "runtime_event_result_publish_d",
      "Publishes the alternate fixed event-source result into the runtime workspace.")
label(0x000ecaf0, "runtime_event_result_publish_e",
      "Computes and publishes the flag-derived event result.")
label(0x000ecb20, "runtime_event_result_publish_f",
      "Computes and publishes the alternate flag-derived event result.")
label(0x000ecb50, "runtime_event_handler_table",
      "Literal event-handler dispatch table for the runtime menu/service states.")
label(0x000ecbb8, "diagnostic_result_strings",
      "Literal result-format, GOOD/BAD, and IC-number strings used by diagnostics.")
label(0x000ecbe0, "diagnostic_result_format",
      "Formats a diagnostic result and selects the corresponding GOOD/BAD text.")
label(0x000ecc40, "diagnostic_result_format_compare",
      "Formats a diagnostic result with an expected-value comparison.")
label(0x000ecd80, "diagnostic_result_menu_render",
      "Renders the diagnostic IC result menu and its accumulated runtime results.")
label(0x000ed0d0, "runtime_record_workspace_reset",
      "Clears the packed-record match/result workspace and returns through a continuation.")
label(0x000ed1e0, "diagnostic_wait_prompt_strings",
      "Literal diagnostic prompts for the test-button and wait states.")
label(0x000ed220, "diagnostic_result_service",
      "Initializes diagnostic result state, renders the result menu, and dispatches the next handler.")
label(0x000ed2e4, "diagnostic_result_service_fallback",
      "Handles the diagnostic result fallback and advances the service state.")
label(0x000ed320, "diagnostic_input_test_service",
      "Renders the input-test state and updates the diagnostic input status.")
label(0x000ed440, "diagnostic_input_status_strings",
      "Literal input-test status strings for directional, shot, dash, start, and coin inputs.")
label(0x000ed5c0, "diagnostic_input_status_render",
      "Renders the input-test status rows and transitions the diagnostic service state.")
label(0x000ed970, "diagnostic_billboard_test_strings",
      "Literal Versus City billboard, winner-lamp, 7-segment, and start-lamp test strings.")
label(0x000eda30, "diagnostic_billboard_test_render",
      "Runs the billboard and lamp-test state machine, rendering test patterns and advancing its state.")
label(0x000edd20, "diagnostic_sde_name_records",
      "Indexed SDE diagnostic event-name records used by the runtime trace/debug services.")
label(0x000eff60, "diagnostic_sdb_name_records",
      "Indexed SDB diagnostic event-name records used by the runtime trace/debug services.")
label(0x000f0674, "diagnostic_crt_pattern_handler_table",
      "Six-entry internal handler table for the CRT diagnostic pattern service.")
label(0x000f04d0, "diagnostic_crt_test_service",
      "Initializes and renders the CRT/test-pattern diagnostic, cycling indexed pattern data.")
label(0x000f08c0, "diagnostic_crt_pattern_buffer_fill",
      "Fills the CRT diagnostic pattern buffer with the indexed bit-plane test layout.")
label(0x000f0980, "diagnostic_match_time_test_service",
      "Renders the match/time diagnostic and builds its associated test video structures.")
label(0x000f1c90, "diagnostic_coin_credit_service",
      "Runs the coin/credit diagnostic state service and dispatches its indexed display pattern.")
label(0x000f1db0, "diagnostic_credit_math_formatter",
      "Formats credit arithmetic and comparison results for the coin diagnostic display.")
label(0x000f1f20, "diagnostic_coin_chute_status_render",
      "Renders coin-chute type and credit status using the live input/status bytes.")
label(0x000f2de0, "diagnostic_bookkeeping_handler_table_a",
      "Primary bookkeeping diagnostic handler table selected by the service state.")
label(0x000f2e00, "diagnostic_bookkeeping_handler_table_b",
      "Alternate bookkeeping diagnostic handler table selected by the service state.")
label(0x000f2e20, "diagnostic_bookkeeping_service",
      "Advances bookkeeping diagnostic state and dispatches the active accounting sub-handler.")
label(0x000f33a0, "diagnostic_game_time_statistics_render",
      "Renders bookkeeping/game-time statistics from the diagnostic accounting fields.")
label(0x000f3ab0, "diagnostic_eeprom_write_confirmation",
      "Runs the EEPROM write-frequency warning and YES/NO confirmation state service.")
label(0x000f3c50, "diagnostic_test_mode_exit_reset",
      "Resets test-mode video/input state and advances the diagnostic mode counter.")
label(0x000f2940, "diagnostic_bookkeeping_arm_validate",
      "Validates the active bookkeeping record and updates the associated credit/runtime state.")
label(0x000f2a60, "diagnostic_bookkeeping_arm_credit_a",
      "Processes the first bookkeeping credit-counter update and publishes the result.")
label(0x000f2ae0, "diagnostic_bookkeeping_arm_credit_b",
      "Processes the alternate bookkeeping credit-counter update and publishes the result.")
label(0x000f2b60, "diagnostic_bookkeeping_arm_coin",
      "Processes the coin-count bookkeeping update and publishes the result.")
label(0x000f2bc0, "diagnostic_bookkeeping_arm_credit_reset",
      "Processes the credit reset/update arm and synchronizes the bookkeeping state.")
label(0x000f2c20, "diagnostic_bookkeeping_arm_input_a",
      "Updates the first diagnostic input byte at 0x1d00035 and publishes the state.")
label(0x000f2c90, "diagnostic_bookkeeping_arm_input_b",
      "Updates the second diagnostic input byte at 0x1d00036 and publishes the state.")
label(0x000f2d00, "diagnostic_bookkeeping_arm_coin_chute_a",
      "Updates the first coin-chute bookkeeping counter at 0x1d00030.")
label(0x000f2d70, "diagnostic_bookkeeping_arm_coin_chute_b",
      "Updates the second coin-chute bookkeeping counter at 0x1d00032.")
label(0x000f2170, "diagnostic_coin_settings_render",
      "Renders the coin-chute type, credit-to-start, and manual coin/credit settings.")
label(0x000f2770, "diagnostic_coin_input_matrix_render",
      "Renders the coin/input matrix and multiplier values from the live diagnostic input bytes.")
label(0x000f19e8, "diagnostic_coin_config_decode",
      "Decodes the selected coin configuration into the live diagnostic input and coin fields.")
label(0x000f23e0, "diagnostic_coin_credit_matrix_builder",
      "Builds the nine-entry coin/credit arithmetic matrix from the live diagnostic input bytes.")
label(0x000f1ac0, "diagnostic_site_status_sync",
      "Synchronizes site/status data from the hardware windows into the diagnostic workspace.")
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
ensure_function(0x0002b700, "startup_status_arm_post_test_transition", 0x0002b770)
ensure_function(0x0002b770, "startup_status_arm_subcounter_decrement", 0x0002b7b0)
ensure_function(0x0002b940, "startup_status_arm_continuation_trampoline", 0x0002b960)
ensure_function(0x0002bdd0, "startup_geometry_status_dispatch", 0x0002be30)
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
ensure_function(0x0006f6f0, "geometry_float_transform_helper", 0x0006f900)
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
ensure_function(0x00073508, "geometry_range_classify", 0x000735d0)
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
label(0x00072ea0, "match_state_result_service",
      "Match-state/result service: selects mode-dependent parameters, updates shared result fields and object state, and emits the resulting command data.")
label(0x00073498, "match_result_counter_service",
      "Updates the shared result pair and counter state, then returns through the continuation saved in g6.")
label(0x000735d0, "match_result_state_dispatch",
      "Dispatches result-state handling through the mode/count table at 0x73618 after selecting the object-side context.")
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
