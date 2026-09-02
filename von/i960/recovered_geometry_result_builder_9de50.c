/* Shared result-builder entry recovered from i960 0x9de50-0x9e044. */
#include <stdint.h>

typedef uint32_t u32;

/* The selector path at 0x9de54-0x9de90 addresses a six-byte signed-halfword
 * record in the table at 0x562436. */
void recovered_geometry_result_builder_selector_parameters(
    const int16_t *parameter_table, u32 selector, int16_t parameters[3])
{
    const int16_t *record = parameter_table + selector * 3U;

    parameters[0] = record[0];
    parameters[1] = record[1];
    parameters[2] = record[2];
}

struct recovered_geometry_result_builder_9de50_plan {
    u32 selector;
    u32 selector_stride_bytes;
    u32 parameter_table_address;
    u32 parameter_halfword_offset[3];
    u32 request38_address;
    u32 request38_word_count;
    u32 response_scratch_offset;
    u32 paired_record_offset[3];
    u32 paired_record_mirror_offset[3];
    u32 flag_offset;
    u32 flag_set_delta_request;
    u32 flag_clear_fallback_table;
    u32 common_request31;
    u32 common_request31_word_count;
    u32 final_sharc_handler;
    u32 final_sharc_parameter_count;
    u32 final_host_parameter_count;
    u32 final_sharc_output_pc;
    u32 final_host_read_pc;
    u32 final_host_read_count;
    u32 final_output_register[3];
    u32 final_output_state_offset[3];
    u32 final_distance_operand_pair[3][2];
    u32 final_first_output_is_first_host_operand;
    u32 final_host_stream_requires_followup_words;
    u32 final_flag0_means_input_fifo_empty;
    u32 final_response_offset;
};

void recovered_geometry_result_builder_9de50_plan(
    u32 selector, u32 object_flag_a0,
    struct recovered_geometry_result_builder_9de50_plan *plan)
{
    plan->selector = selector;
    plan->selector_stride_bytes = 12U;
    plan->parameter_table_address = 0x00562436U;
    plan->parameter_halfword_offset[0] = 0U;
    plan->parameter_halfword_offset[1] = 2U;
    plan->parameter_halfword_offset[2] = 4U;
    plan->request38_address = 0x00884000U;
    plan->request38_word_count = 4U;
    plan->response_scratch_offset = 0x40U;
    plan->paired_record_offset[0] = 0U;
    plan->paired_record_offset[1] = 4U;
    plan->paired_record_offset[2] = 8U;
    plan->paired_record_mirror_offset[0] = 0x10U;
    plan->paired_record_mirror_offset[1] = 0x14U;
    plan->paired_record_mirror_offset[2] = 0x18U;
    plan->flag_offset = 0xa0U;
    plan->flag_set_delta_request = object_flag_a0 != 0U;
    plan->flag_clear_fallback_table = 0x00562cdeU;
    plan->common_request31 = 31U;
    plan->common_request31_word_count = 7U;
    /* Host command 31 is decimal 31 (SHARC opcode 0x1f), not opcode 0x31.
     * The latter is the unrelated matrix/projection routine at 0x20762. */
    plan->final_sharc_handler = 0x000203eaU;
    plan->final_sharc_parameter_count = 6U;
    plan->final_host_parameter_count = 6U;
    plan->final_sharc_output_pc = 0x00020409U;
    plan->final_host_read_pc = 0x0009e240U;
    plan->final_host_read_count = 1U;
    plan->final_output_register[0] = 0U;
    plan->final_output_register[1] = 0U;
    plan->final_output_register[2] = 0U;
    plan->final_output_state_offset[0] = 0U;
    plan->final_output_state_offset[1] = 0U;
    plan->final_output_state_offset[2] = 0U;
    plan->final_distance_operand_pair[0][0] = 1U;
    plan->final_distance_operand_pair[0][1] = 4U;
    plan->final_distance_operand_pair[1][0] = 2U;
    plan->final_distance_operand_pair[1][1] = 5U;
    plan->final_distance_operand_pair[2][0] = 3U;
    plan->final_distance_operand_pair[2][1] = 6U;
    plan->final_first_output_is_first_host_operand = 0U;
    plan->final_host_stream_requires_followup_words = 0U;
    plan->final_flag0_means_input_fifo_empty = 1U;
    plan->final_response_offset = 0x28U;
}

u32 recovered_geometry_result_command31_result_is_length(void)
{
    return 1U;
}

/* Packet indices include the command at index 0. */
void recovered_geometry_result_command31_operand_pairs(const u32 packet[7],
                                                       u32 differences[3])
{
    differences[0] = packet[1] - packet[4];
    differences[1] = packet[2] - packet[5];
    differences[2] = packet[3] - packet[6];
}

/* Flag-set path at 0x9dee8-0x9ded8: the related record's three fields are
 * subtracted from the response scratch words and mirrored into both records.
 * Keep this unsigned so the host model preserves i960 word wraparound. */
void recovered_geometry_result_builder_related_differences(
    const u32 response[3], const u32 related_fields[3],
    u32 output_fields[3], u32 mirror_fields[3])
{
    for (u32 i = 0; i != 3U; ++i) {
        u32 difference = related_fields[i] - response[i];
        output_fields[i] = difference;
        mirror_fields[i] = difference;
    }
}

struct recovered_geometry_result_builder_clear_fields {
    u32 output_0c;
    u32 output_0e;
    u32 output_10;
    u32 output_14;
    u32 mirror_04;
    u32 mirror_06;
    u32 mirror_08;
    u32 mirror_0a;
    u32 mirror_1c;
};

/* Clear-flag path at 0x9df9c-0x9dfdc. The first table value and +0x184 are
 * loaded as signed halfwords; the later 0x562cb0 value is a raw word. */
void recovered_geometry_result_builder_clear_fields(
    int16_t fallback_halfword, int16_t object_184, u32 control_word,
    u32 raw_table_word,
    struct recovered_geometry_result_builder_clear_fields *fields)
{
    fields->output_0c = (u32)(int32_t)fallback_halfword;
    fields->output_0e = (u32)(int32_t)object_184;
    fields->output_10 = control_word;
    fields->output_14 = raw_table_word;
    fields->mirror_04 = control_word;
    fields->mirror_06 = fields->output_0c;
    fields->mirror_08 = fields->output_0e;
    fields->mirror_0a = control_word;
    fields->mirror_1c = control_word;
}
