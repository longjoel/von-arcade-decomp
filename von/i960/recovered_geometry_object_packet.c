/*
 * Recovered from the object packet emitters at i960 0x3403c, 0x346f0, and
 * 0x34de8. These are host-side geometry packets, not SHARC dispatcher
 * opcodes. The three parameter words are sign-extended halfwords loaded from
 * 0x562440, 0x56243e, and 0x56243c in the ROM.
 */
typedef unsigned int u32;

/* Legal 3x4 geometry matrix command: opcode followed by 12 IEEE-754 words. */
u32 recovered_geometry_matrix_submission(const u32 matrix[12], u32 packet[13])
{
    u32 index;
    packet[0] = 0x05800000U;
    for (index = 0U; index < 12U; ++index)
        packet[index + 1U] = matrix[index];
    return 13U;
}

/* The legal Model 2 polygon-ROM display command's four-word object record. */
u32 recovered_geometry_polygon_object_submission(u32 tpa, u32 tha, u32 oba,
                                                 u32 count, u32 packet[4])
{
    packet[0] = tpa;
    packet[1] = tha;
    packet[2] = oba;
    packet[3] = count;
    return 4U;
}

/* Emit the common ten-word prefix. Callers append object-dependent fields. */
u32 recovered_geometry_object_packet_prefix(const u32 base[3],
                                            u32 parameter_16,
                                            u32 parameter_15,
                                            u32 parameter_14,
                                            u32 packet[10])
{
    packet[0] = 0x2fU;
    packet[1] = base[0];
    packet[2] = base[1];
    packet[3] = base[2];
    packet[4] = 0x16U;
    packet[5] = parameter_16;
    packet[6] = 0x15U;
    packet[7] = parameter_15;
    packet[8] = 0x14U;
    packet[9] = parameter_14;
    return 10U;
}

/*
 * Emit the two-emitter transform/copy variant after the common prefix:
 *
 *   0x15, secondary_15, 0x14, secondary_14, 0x3a, copy_target
 *
 * The 0x3403c and 0x346f0 paths use this record. The 0x34de8 path instead
 * follows the common prefix with a different command sequence. The target is
 * read from the geometry-board window at 0x802008 by the ROM;
 * it is an argument here because it is runtime state. The command following
 * this record differs by object path (0x06, 0x10, etc.).
 */
u32 recovered_geometry_object_packet_transform_prefix(const u32 base[3],
                                                      u32 parameter_16,
                                                      u32 parameter_15,
                                                      u32 parameter_14,
                                                      u32 secondary_15,
                                                      u32 secondary_14,
                                                      u32 copy_target,
                                                      u32 packet[16])
{
    recovered_geometry_object_packet_prefix(
        base, parameter_16, parameter_15, parameter_14, packet);
    packet[10] = 0x15U;
    packet[11] = secondary_15;
    packet[12] = 0x14U;
    packet[13] = secondary_14;
    packet[14] = 0x3aU;
    packet[15] = copy_target;
    return 16U;
}

/* The 0x34de8 path takes the common prefix into a one-word 0x20 request. */
u32 recovered_geometry_object_packet_status_request(const u32 base[3],
                                                    u32 parameter_16,
                                                    u32 parameter_15,
                                                    u32 parameter_14,
                                                    u32 packet[11])
{
    recovered_geometry_object_packet_prefix(
        base, parameter_16, parameter_15, parameter_14, packet);
    packet[10] = 0x20U;
    return 11U;
}

/*
 * The 0x3403c continuation emits a six-word endpoint-pair request to SHARC
 * service 0x1f. The general packet form stays available for callers whose
 * source is not yet identified.
 */
u32 recovered_geometry_object_length_request(const u32 endpoints[6],
                                             u32 packet[7])
{
    packet[0] = 0x1fU;
    packet[1] = endpoints[0];
    packet[2] = endpoints[1];
    packet[3] = endpoints[2];
    packet[4] = endpoints[3];
    packet[5] = endpoints[4];
    packet[6] = endpoints[5];
    return 7U;
}

/*
 * The concrete 0x3403c caller obtains a profile direction triple from
 * 0x142fd4 + profile*12 and publishes it as 0x577100/104/108. Pipeline-aware
 * tracing shows that its six payload writes are [0, x, 0, 0, 0, z]. Thus the
 * distance service measures the XZ projection length; the Y component is
 * reserved for the following opcode-0x0a scalar request.
 */
u32 recovered_geometry_object_profile_length_request(
    const u32 profile_vector[3], u32 packet[7])
{
    u32 endpoints[6] = {
        0U, profile_vector[0],
        0U, 0U,
        0U, profile_vector[2],
    };
    return recovered_geometry_object_length_request(endpoints, packet);
}

u32 recovered_geometry_object_scalar_request(u32 length_response,
                                             u32 second_parameter,
                                             u32 packet[3]);

/* Concrete first 0x3403c submission captured from the original FIFO. */
u32 recovered_geometry_object_profile_submission(const u32 base[3],
                                                 const u32 profile_vector[3],
                                                 u32 length_response,
                                                 u32 angle_response,
                                                 u32 packet[29])
{
    u32 index;
    index = recovered_geometry_object_packet_transform_prefix(
        base, 0x6cU, 0x17U, 0xffffff80U, 0U, 0U, 0x0fecU, packet);
    packet[index++] = 0x06U;
    packet[index++] = 0x05U;
    packet[index++] = 0x06U;
    index += recovered_geometry_object_profile_length_request(
        profile_vector, packet + index);
    index += recovered_geometry_object_scalar_request(
        length_response, angle_response, packet + index);
    return index;
}

/* The following 0x0a request consumes the 0x1f response as its first input. */
u32 recovered_geometry_object_scalar_request(u32 length_response,
                                             u32 second_parameter,
                                             u32 packet[3])
{
    packet[0] = 0x0aU;
    packet[1] = length_response;
    packet[2] = second_parameter;
    return 3U;
}

/*
 * The post-gate i960 path emits decimal host command 26, which dispatches to
 * SHARC opcode 0x1a (not opcode 0x26). It transforms the selected XZ slice
 * through the persistent matrix/state tail; the missing Y input is literal 0.
 */
u32 recovered_geometry_object_xz_state_output_request(
    const u32 selected_vector[3], u32 packet[4])
{
    packet[0] = 26U;
    packet[1] = selected_vector[0];
    packet[2] = 0U;
    packet[3] = selected_vector[2];
    return 4U;
}

/*
 * Object initialization at 0x278b4 copies this descriptor quartet into the
 * related record. The source offsets are descriptor-relative; the destination
 * offsets are byte offsets in the runtime record.
 */
void recovered_geometry_descriptor_parameter_copy(const u32 descriptor[0x68 / 4U],
                                                  u32 related_record[0x64 / 4U])
{
    related_record[0x54U / 4U] = descriptor[0x67cU / 4U];
    related_record[0x58U / 4U] = descriptor[0x680U / 4U];
    related_record[0x5cU / 4U] = descriptor[0x684U / 4U];
    related_record[0x60U / 4U] = descriptor[0x688U / 4U];
}

/*
 * Opcode 0x2f updates the SHARC translation/state tail at offsets 0x09..0x0b;
 * opcode 0x20 reads those three words back. The 0x34de8 path stores that
 * transformed state-tail vector at object +0x20/+0x24/+0x28 in read order.
 */
void recovered_geometry_object_response_copy(const u32 responses[3],
                                             u32 object_record[11])
{
    object_record[8] = responses[0];
    object_record[9] = responses[1];
    object_record[10] = responses[2];
}

/*
 * The later 0x346f0 readback stores the same state-tail (x,y,z) components at
 * the path-specific offsets +0x20, +0x18, +0x28.
 */
void recovered_geometry_object_state_response_copy(const u32 responses[3],
                                                   u32 object_record[11])
{
    object_record[8] = responses[0];
    object_record[6] = responses[1];
    object_record[10] = responses[2];
}

/*
 * The later 0x346f0 continuation (0x34b00) emits another 0x2f transform and
 * 0x20 state-tail readback after a second tagged-field group. Its three
 * transformed state-tail components are written much farther into the object
 * record, at byte offsets +0x158/+0x15c/+0x160, immediately before 0x06.
 */
void recovered_geometry_object_late_response_copy(const u32 responses[3],
                                                  u32 object_record[89])
{
    object_record[0x158U / 4U] = responses[0];
    object_record[0x15cU / 4U] = responses[1];
    object_record[0x160U / 4U] = responses[2];
}

/* The immediately following tagged transform plus 0x20 writes the next triplet. */
void recovered_geometry_object_late_followup_response_copy(
    const u32 responses[3], u32 object_record[92])
{
    object_record[0x164U / 4U] = responses[0];
    object_record[0x168U / 4U] = responses[1];
    object_record[0x16cU / 4U] = responses[2];
}

/*
 * The downstream consumer at 0xdf0cc selects one of three vector layouts
 * using the object field at +0x02. Selector zero uses the earlier local
 * triplet; selectors one and two use the two late 0x20 response triplets.
 * Values outside 0..2 produce the observed zero vector.
 */
void recovered_geometry_object_select_response_vector(const u32 object_record[92],
                                                      u32 selector,
                                                      u32 vector[3])
{
    u32 base = 0U;
    if (selector == 0U)
        base = 0x14U / 4U;
    else if (selector == 1U)
        base = 0x158U / 4U;
    else if (selector == 2U)
        base = 0x164U / 4U;

    if (base == 0U) {
        vector[0] = 0U;
        vector[1] = 0U;
        vector[2] = 0U;
    } else {
        vector[0] = object_record[base + 0U];
        vector[1] = object_record[base + 1U];
        vector[2] = object_record[base + 2U];
    }
}

/*
 * State setup emitted by the 0x346f0 branch after its 0x3a target:
 * 0x10 (identity reset), 0x12 plus three tail words, then 0x2a plus one
 * scale word. The values are runtime object data, so they remain arguments.
 */
u32 recovered_geometry_object_state_setup(u32 tail_0, u32 tail_1, u32 tail_2,
                                           u32 scale, u32 packet[7])
{
    packet[0] = 0x10U;
    packet[1] = 0x12U;
    packet[2] = tail_0;
    packet[3] = tail_1;
    packet[4] = tail_2;
    packet[5] = 0x2aU;
    packet[6] = scale;
    return 7U;
}

/*
 * Bridge emitted after the 0x346f0 state setup:
 * 0x15 plus the derived object value, a no-payload 0x05 state step, then the
 * header and base words of the next 0x2f packet.
 */
u32 recovered_geometry_object_state_bridge(u32 derived_value,
                                           const u32 next_base[3],
                                           u32 packet[7])
{
    packet[0] = 0x15U;
    packet[1] = derived_value;
    packet[2] = 0x05U;
    packet[3] = 0x2fU;
    packet[4] = next_base[0];
    packet[5] = next_base[1];
    packet[6] = next_base[2];
    return 7U;
}

/* The tagged-field continuation ends with SHARC 0x1a and three input words. */
u32 recovered_geometry_object_affine_request(const u32 inputs[3],
                                             u32 packet[4])
{
    packet[0] = 0x1aU;
    packet[1] = inputs[0];
    packet[2] = inputs[1];
    packet[3] = inputs[2];
    return 4U;
}
