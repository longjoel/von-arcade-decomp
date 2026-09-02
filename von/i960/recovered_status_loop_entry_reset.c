/* Entry/reset contract recovered from i960 0x218f0-0x21968. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_loop_entry_reset_plan {
    u32 fill_value_after_entry;
    u32 reset_branch_taken;
    u32 marker_value;
    u32 marker_address[4];
    u32 shared_clear_address;
    u32 shared_clear_value;
};

void recovered_status_loop_entry_reset_plan(int32_t status_latch,
                                            struct recovered_status_loop_entry_reset_plan *plan)
{
    plan->fill_value_after_entry = 0U;
    plan->reset_branch_taken = status_latch >= 0 ? 1U : 0U;
    plan->marker_value = 0x8000U;
    plan->marker_address[0] = 0x00504d2cU;
    plan->marker_address[1] = 0x00504d30U;
    plan->marker_address[2] = 0x00504d2eU;
    plan->marker_address[3] = 0x00504d32U;
    plan->shared_clear_address = 0x01800000U;
    plan->shared_clear_value = 0U;
}
