/* Status routes recovered from i960 0x207e0 and 0x20810. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_transition_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
    u32 width;
    u32 height;
};

void recovered_status_transition_plan(u32 attributed, u32 source_present,
                                      struct recovered_status_transition_plan *plan)
{
    plan->source = source_present ? (attributed ? 0x02fcf988U : 0x02fcf708U) : 0U;
    plan->source_helper = source_present ? (attributed ? 0x0001dc90U : 0x0001dc10U) : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
    plan->width = attributed ? 23U : 20U;
    plan->height = attributed ? 2U : 4U;
}
