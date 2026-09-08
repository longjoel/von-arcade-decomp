/* Bounded pool-scan and command-5/9 arm of i960 0x41f20. */

#include <stdint.h>

struct recovered_geometry_runtime_packet_dispatch_plan {
    uint32_t status_pool;
    uint32_t status_pool_stride;
    uint32_t status_pool_count;
    uint32_t status_offset;
    uint32_t handler_table;
    uint32_t selector_mask;
    uint32_t runtime_pool;
    uint32_t runtime_pool_stride;
    uint32_t runtime_pool_count;
    uint32_t runtime_active_mask;
    uint32_t command_selectors[2];
    uint32_t command_selector_count;
    uint32_t readback_address;
    uint32_t publication_address;
    uint32_t completion_address;
    uint32_t completion_value;
};

void recovered_geometry_runtime_packet_dispatch_plan(
    struct recovered_geometry_runtime_packet_dispatch_plan *plan)
{
    plan->status_pool = 0x0051ad10U;
    plan->status_pool_stride = 0x24U;
    plan->status_pool_count = 24U;
    plan->status_offset = 2U;
    plan->handler_table = 0x00041c50U;
    plan->selector_mask = 0xffffU;
    plan->runtime_pool = 0x0051b070U;
    plan->runtime_pool_stride = 0x38U;
    plan->runtime_pool_count = 24U;
    plan->runtime_active_mask = 0xffffU;
    plan->command_selectors[0] = 5U;
    plan->command_selectors[1] = 9U;
    plan->command_selector_count = 2U;
    plan->readback_address = 0x00802008U;
    plan->publication_address = 0x00801008U;
    plan->completion_address = 0x00800010U;
    plan->completion_value = 6U;
}

uint32_t recovered_geometry_runtime_packet_selector(uint32_t selector)
{
    return selector & 0xffffU;
}
