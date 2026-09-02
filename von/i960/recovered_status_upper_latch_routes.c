/* Upper-latch routes recovered from i960 0x21a1c-0x21adc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_upper_latch_plan {
    u32 render_selected;
    u32 clear_selected;
    u32 masked_generator_0;
    u32 state_504d28_after;
    u32 state_504d30_after;
    u32 source;
    u32 helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 clear_count;
    u32 clear_address[8];
};

void recovered_status_upper_latch_plan(
    int32_t latch, u32 state_504d28, u32 generator_0, u32 generator_1,
    struct recovered_status_upper_latch_plan *plan)
{
    static const u32 clear_addresses[8] = {
        0x00504d24U, 0x00504d2cU, 0x00504d28U, 0x00504d30U,
        0x00504d26U, 0x00504d2eU, 0x00504d2aU, 0x00504d32U
    };
    u32 first = generator_0 & 0x1ffU;

    plan->render_selected = latch >= 21 && latch <= 95 ? 1U : 0U;
    plan->clear_selected = latch > 95 ? 1U : 0U;
    plan->masked_generator_0 = first;
    plan->state_504d28_after = (state_504d28 + first) & 0x1ffU;
    plan->state_504d30_after = generator_1 & 0x1ffU;
    plan->source = 0x02fda1d0U;
    plan->helper = 0x0001dc10U;
    plan->column = 0U;
    plan->row = (u32)(latch * 4 - 84);
    plan->width = 0x40U;
    plan->height = 4U;
    plan->clear_count = plan->clear_selected ? 8U : 0U;
    for (u32 i = 0; i < 8U; ++i)
        plan->clear_address[i] = clear_addresses[i];
}
