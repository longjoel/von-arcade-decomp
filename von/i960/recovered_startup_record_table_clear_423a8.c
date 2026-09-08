/* Exact table/pool initialization schedule recovered from 0x423a8. */

#include <stdint.h>

struct recovered_startup_record_table_clear_plan {
    uint32_t first_table;
    uint32_t first_stride;
    uint32_t first_limit;
    uint32_t second_table;
    uint32_t second_stride;
    uint32_t second_limit;
    uint32_t sentinel;
    uint32_t pool_a;
    uint32_t pool_b;
    uint32_t pool_stride;
    uint32_t pool_count;
    uint32_t pool_field_offset;
    uint32_t cleared_global[2];
};

void recovered_startup_record_table_clear_plan(
    struct recovered_startup_record_table_clear_plan *plan)
{
    plan->first_table = 0x0051ad10U;
    plan->first_stride = 0x24U;
    plan->first_limit = 0x33cU;
    plan->second_table = 0x0051b070U;
    plan->second_stride = 0x38U;
    plan->second_limit = 0x508U;
    plan->sentinel = 0xffffU;
    plan->pool_a = 0x0051b5b0U;
    plan->pool_b = 0x0051b850U;
    plan->pool_stride = 0x1cU;
    plan->pool_count = 11U;
    plan->pool_field_offset = 0x150U;
    plan->cleared_global[0] = 0x0051baf4U;
    plan->cleared_global[1] = 0x0051baf0U;
}

uint32_t recovered_startup_record_table_entry_count(uint32_t limit,
                                                     uint32_t stride)
{
    return limit / stride + 1U;
}
