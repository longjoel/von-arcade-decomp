/* Attributed/plain render arms recovered from i960 0x2241c-0x2258c. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_render_arm {
    RECOVERED_STATUS_LATCH_RENDER_ATTRIBUTED = 0,
    RECOVERED_STATUS_LATCH_RENDER_PLAIN = 1
};

struct recovered_status_latch_render_arms_plan {
    u32 arm;
    u32 mode;
    u32 column;
    u32 row;
    u32 record_table;
    u32 record_stride;
    u32 record_source_first;
    u32 record_source_second;
    u32 record_source_third;
    u32 record_helper;
    u32 matcher;
    u32 matcher_source;
    u32 matcher_stride;
    u32 matcher_column;
    u32 matcher_row;
    u32 record_call_count;
    u32 matcher_call_count;
    u32 continuation_target;
};

static u32 recovered_status_render_column(u32 mode)
{
    return mode == 2U ? 26U : mode == 6U ? 23U : 25U;
}

void recovered_status_latch_render_arms_plan(
    u32 attributed, u32 mode, u32 record_source_first,
    u32 record_source_second, u32 record_source_third,
    struct recovered_status_latch_render_arms_plan *plan)
{
    plan->arm = attributed != 0U
        ? RECOVERED_STATUS_LATCH_RENDER_ATTRIBUTED
        : RECOVERED_STATUS_LATCH_RENDER_PLAIN;
    plan->mode = mode;
    plan->column = recovered_status_render_column(mode);
    plan->row = attributed != 0U ? 8U : 11U;
    plan->record_table = 0x00020b50U + mode * 0x68U;
    plan->record_stride = 0x68U;
    plan->record_source_first = record_source_first;
    plan->record_source_second = record_source_second;
    plan->record_source_third = attributed != 0U ? record_source_third : 0U;
    plan->record_helper = attributed != 0U ? 0x0001dc10U : 0x0001df00U;
    plan->matcher = 0x0001d880U;
    plan->matcher_source = 0x00020ba8U + mode * 104U;
    plan->matcher_stride = 104U;
    plan->matcher_column = recovered_status_render_column(mode);
    plan->matcher_row = 8U;
    plan->record_call_count = 1U;
    plan->matcher_call_count = 1U;
    plan->continuation_target = 0x00022590U;
}
