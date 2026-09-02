/* Geometry-result builder recovered from i960 0x9e880-0x9eaa8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_result_builder_9e880_plan {
    u32 selector;
    u32 selector_stride_bytes;
    u32 parameter_table_address;
    u32 request38_address;
    u32 request38_word_count;
    u32 response_scratch_offset;
    u32 paired_record_offset[3];
    u32 paired_record_mirror_offset[3];
    u32 flag_offset;
    u32 flag_set_delta_command;
    u32 flag_set_delta_word_count;
    u32 flag_set_delta_response_output_offset;
    u32 flag_clear_source_offset;
    u32 flag_clear_additional_source_offset;
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

void recovered_geometry_result_builder_9e880_plan(
    u32 selector, u32 object_flag_a0,
    struct recovered_geometry_result_builder_9e880_plan *plan)
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
    plan->flag_set_delta_command = object_flag_a0 != 0U ? 10U : 0U;
    plan->flag_set_delta_word_count = object_flag_a0 != 0U ? 3U : 0U;
    plan->flag_set_delta_response_output_offset = 0x0eU;
    plan->flag_clear_source_offset = 0x184U;
    plan->flag_clear_additional_source_offset = 0x34U;
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

/* 0x9e920-0x9e94c: ldq stages response0..response2 in r4..r6, then
 * subtracts response2 from linked.+0x1c and response0 from linked.+0x14. */
void recovered_geometry_result_builder_9e880_flag_set_packet(
    const u32 linked_record_fields[3], const u32 response_words[3],
    u32 packet[3])
{
    packet[0] = 10U;
    packet[1] = linked_record_fields[2] - response_words[2];
    packet[2] = linked_record_fields[0] - response_words[0];
}
