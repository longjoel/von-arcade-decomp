/* Status strip reset recovered from i960 0x23510-0x23554. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_strip_reset_plan {
    u32 upload_helper;
    u32 upload_source;
    u32 upload_row_count;
    u32 upload_width;
    u32 upload_height;
    u32 clear_destination;
    u32 clear_halfword_count;
    u32 clear_value;
    u32 cleared_state_count;
    u32 cleared_state_address[2];
};

void recovered_status_strip_reset_plan(
    u32 caller_g14, struct recovered_status_strip_reset_plan *plan)
{
    plan->upload_helper = 0x0001dfd0U;
    plan->upload_source = 0U;
    plan->upload_row_count = caller_g14 + 31U;
    plan->upload_width = 0x40U;
    plan->upload_height = 4U;
    plan->clear_destination = 0x0100c000U;
    plan->clear_halfword_count = 0xfffU;
    plan->clear_value = 0U;
    plan->cleared_state_count = 2U;
    plan->cleared_state_address[0] = 0x00504d26U;
    plan->cleared_state_address[1] = 0x00504d24U;
}
