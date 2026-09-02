/* Mid-latch route recovered from i960 0x219a8-0x21a18. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_mid_latch_route_plan {
    u32 selected;
    u32 special_latch_9;
    u32 masked_generator_0;
    u32 state_504d28_after;
    u32 state_504d30_after;
    u32 source;
    u32 helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_status_mid_latch_route_plan(
    int32_t latch, u32 state_504d28, u32 generator_0, u32 generator_1,
    struct recovered_status_mid_latch_route_plan *plan)
{
    u32 first = generator_0 & 0x1ffU;
    plan->selected = latch >= 9 && latch <= 20 ? 1U : 0U;
    plan->special_latch_9 = latch == 9 ? 1U : 0U;
    plan->masked_generator_0 = first;
    plan->state_504d28_after = (state_504d28 + first) & 0x1ffU;
    plan->state_504d30_after = generator_1 & 0x1ffU;
    plan->source = 0x02feab34U;
    plan->helper = 0x0001de00U;
    plan->column = 0U;
    plan->row = (u32)(latch * 4 - 36);
    plan->width = 0x40U;
    plan->height = 4U;
}
