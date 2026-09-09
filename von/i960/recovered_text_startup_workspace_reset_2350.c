/* Text-startup workspace reset recovered from i960 0x2350-0x2414. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_startup_workspace_reset_plan {
    u32 zeroed_header_count;
    u32 zeroed_header_addresses[10];
    u32 record_count;
    u32 record_stride;
    u32 record_zero_field_count;
    u32 record_zero_offsets[4];
    u32 record_zero_write_count;
    u32 sentinel_address;
    int32_t sentinel_value;
    u32 status_latch_address;
    u32 status_latch_value;
    u32 table_initializer_called;
    u32 table_copy_called;
    u32 table_initializer_address;
    u32 table_copy_address;
};

void recovered_text_startup_workspace_reset_plan(
    struct recovered_text_startup_workspace_reset_plan *plan)
{
    static const u32 header_addresses[10] = {
        0x01d00038U, 0x01d0003cU, 0x01d00040U, 0x01d00044U,
        0x01d00048U, 0x01d0004cU, 0x01d00050U, 0x01d00054U,
        0x01d00058U, 0x01d0005cU
    };
    static const u32 zero_offsets[4] = {0xa4U, 0xa8U, 0xacU, 0xb0U};
    u32 i;

    plan->zeroed_header_count = 10U;
    for (i = 0U; i < 10U; ++i) {
        plan->zeroed_header_addresses[i] = header_addresses[i];
    }
    plan->record_count = 10U;
    plan->record_stride = 0x10U;
    plan->record_zero_field_count = 4U;
    for (i = 0U; i < 4U; ++i) {
        plan->record_zero_offsets[i] = zero_offsets[i];
    }
    plan->record_zero_write_count = 40U;
    plan->sentinel_address = 0x01d00060U;
    plan->sentinel_value = -1;
    plan->status_latch_address = 0x005039f8U;
    plan->status_latch_value = 0U;
    plan->table_initializer_called = 1U;
    plan->table_copy_called = 1U;
    plan->table_initializer_address = 0x000e3740U;
    plan->table_copy_address = 0x00002330U;
}
