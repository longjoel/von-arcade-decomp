/* Exact 64-slot geometry-pool reset recovered from i960 0x6f9e8. */

#include <stdint.h>

struct recovered_geometry_pool64_reset_plan {
    uint32_t slot_table;
    uint32_t slot_count;
    uint32_t record_table;
    uint32_t record_stride;
    uint32_t record_clear_offset;
    uint32_t cursor_address;
    uint32_t cursor_value;
};

void recovered_geometry_pool64_reset_plan(
    struct recovered_geometry_pool64_reset_plan *plan)
{
    plan->slot_table = 0x0051c860U;
    plan->slot_count = 64U;
    plan->record_table = 0x0051c5b0U;
    plan->record_stride = 0x54U;
    plan->record_clear_offset = 0U;
    plan->cursor_address = 0x0051c880U;
    plan->cursor_value = 0U;
}

uint32_t recovered_geometry_pool64_slot_count(void)
{
    return 0x40U;
}
