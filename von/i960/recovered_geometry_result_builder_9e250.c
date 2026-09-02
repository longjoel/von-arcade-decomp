/* Shared result-builder variant recovered from i960 0x9e250-0x9e444. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_result_builder_9e250_plan {
    u32 selector;
    u32 selector_stride_bytes;
    u32 parameter_table_address;
    u32 request38_address;
    u32 request38_word_count;
    u32 response_scratch_offset;
    u32 paired_record_offset[3];
    u32 paired_record_mirror_offset[3];
    u32 flag_offset;
    u32 flag_set_delta_request;
    u32 flag_set_compare_uses_signed_paired_halfword;
    u32 flag_set_alternate_table;
    u32 flag_clear_constant;
    u32 flag_clear_writes_output_offset;
    u32 common_request31;
    u32 common_request31_word_count;
    u32 final_sharc_handler;
    u32 final_host_read_pc;
    u32 final_response_offset;
};

void recovered_geometry_result_builder_9e250_plan(
    u32 selector, u32 object_flag_a0,
    struct recovered_geometry_result_builder_9e250_plan *plan)
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
    plan->flag_set_delta_request = object_flag_a0 != 0U;
    /* 0x9e250 compares the signed existing +0x06 halfword against the
     * primary table value before optionally replacing it from the alternate
     * table.  This is not the 0x8000 sentinel test used by 0x9de50. */
    plan->flag_set_compare_uses_signed_paired_halfword = 1U;
    plan->flag_set_alternate_table = 0x00562cb0U;
    /* The flag-clear arm loads this immediate directly. */
    plan->flag_clear_constant = 0xffffe000U;
    plan->flag_clear_writes_output_offset = 0x0cU;
    plan->common_request31 = 31U;
    plan->common_request31_word_count = 7U;
    plan->final_sharc_handler = 0x000203eaU;
    plan->final_host_read_pc = 0x0009e438U;
    plan->final_response_offset = 0x28U;
}
