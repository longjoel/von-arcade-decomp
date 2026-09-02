/* Geometry-result builder recovered from i960 0x9e450-0x9e870. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_result_builder_9e450_plan {
    u32 selector;
    u32 selector_stride_bytes;
    u32 parameter_table_address;
    u32 request38_address;
    u32 request38_word_count;
    u32 response_scratch_offset;
    u32 paired_record_offset[3];
    u32 paired_record_mirror_offset[3];
    u32 flag_offset;
    u32 flag_set_delta_command_base;
    u32 flag_set_delta_word_count;
    u32 flag_set_delta_response_output_offset;
    u32 flag_clear_source_offset;
    u32 flag_clear_response_output_offset;
    u32 common_request31;
    u32 common_request31_word_count;
    u32 final_response_offset;
    u32 followup_command29;
    u32 followup_command29_word_count;
    u32 followup_command29_response_output_offset;
    u32 followup_command29_response_transform;
    u32 followup_command30;
    u32 followup_command30_word_count;
    u32 followup_command30_response_output_offset;
    u32 followup_command30_table_base;
    u32 followup_table_output_offset[2];
};

void recovered_geometry_result_builder_9e450_plan(
    u32 selector, u32 object_flag_a0,
    struct recovered_geometry_result_builder_9e450_plan *plan)
{
    plan->selector = selector;
    plan->selector_stride_bytes = 12U;
    plan->parameter_table_address = 0x00562436U;
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
    plan->flag_set_delta_command_base = object_flag_a0 != 0U ? 31U : 0U;
    plan->flag_set_delta_word_count = object_flag_a0 != 0U ? 4U : 0U;
    plan->flag_set_delta_response_output_offset = 0x0eU;
    plan->flag_clear_source_offset = 0x184U;
    plan->flag_clear_response_output_offset = 0x0eU;
    plan->common_request31 = 31U;
    plan->common_request31_word_count = 7U;
    plan->final_response_offset = 0x28U;
    plan->followup_command29 = 29U;
    plan->followup_command29_word_count = 3U;
    plan->followup_command29_response_output_offset = 0x18U;
    /* 0x9e7e0 is NOTBIT 31: only the IEEE sign bit is toggled. */
    plan->followup_command29_response_transform = 0x80000000U;
    plan->followup_command30 = 30U;
    plan->followup_command30_word_count = 3U;
    plan->followup_command30_response_output_offset = 0x20U;
    plan->followup_command30_table_base = 0x00562cb0U;
    plan->followup_table_output_offset[0] = 0x14U;
    plan->followup_table_output_offset[1] = 0x24U;
}

u32 recovered_geometry_result_builder_command29_response(u32 response)
{
    return response ^ 0x80000000U;
}

/* 0x9e4e8-0x9e52c: the flagged arm sends a dynamic command-31 packet.
 * SUBR a,b,d computes b-a on this target, so each delta is the linked
 * record field minus the corresponding command-38 response. */
void recovered_geometry_result_builder_flag_set_delta_packet(
    const u32 linked_record_fields[3], const u32 response_words[3],
    u32 packet[4])
{
    u32 delta0 = linked_record_fields[0] - response_words[0];
    packet[0] = delta0 + 31U;
    packet[1] = delta0;
    packet[2] = linked_record_fields[1] - response_words[1];
    packet[3] = linked_record_fields[2] - response_words[2];
}

struct recovered_geometry_result_builder_followups {
    u32 command29[3];
    u32 command30[3];
    u32 output_18;
    u32 output_20;
};

/* 0x9e7a8-0x9e834: build the two post-distance requests. */
void recovered_geometry_result_builder_followups(
    int16_t paired_field, u32 command29_table_word,
    u32 command30_table_word, u32 command29_response,
    u32 command30_response,
    struct recovered_geometry_result_builder_followups *followups)
{
    followups->command29[0] = 29U;
    followups->command29[1] = (u32)(int32_t)paired_field;
    followups->command29[2] = command29_table_word;
    followups->command30[0] = 30U;
    /* The AND 0xffff before command 30 zero-extends this halfword. */
    followups->command30[1] = (u32)(uint16_t)paired_field;
    followups->command30[2] = command30_table_word;
    followups->output_18 = command29_response ^ 0x80000000U;
    followups->output_20 = command30_response;
}

/* The ldob state is multiplied by three, then used as a 16-byte scaled
 * index.  addend is 0 for command 29/30, 0x10 for output +0x14, and 0x14 for
 * output +0x24. */
u32 recovered_geometry_result_builder_followup_table_address(
    u32 state_byte, u32 addend)
{
    return 0x00562cb0U + (state_byte & 0xffU) * 3U * 16U + addend;
}
