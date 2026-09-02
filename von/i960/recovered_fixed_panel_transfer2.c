/* Second fixed transfer descriptor recovered from i960 0x1f660. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_fixed_panel_transfer2_plan {
    u32 helper;
    u32 source;
    u32 width;
    u32 height;
    u32 uses_current_position;
};

void recovered_fixed_panel_transfer2_plan(struct recovered_fixed_panel_transfer2_plan *plan)
{
    plan->helper = 0x0001dc90U;
    plan->source = 0x02fdeda0U;
    plan->width = 6U;
    plan->height = 8U;
    plan->uses_current_position = 1U;
}
