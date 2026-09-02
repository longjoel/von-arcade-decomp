/* Explicit-position source-or-clear route recovered from i960 0x1ffb0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel15_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel15_plan(u32 source_present, u32 caller_g23,
                            struct recovered_panel15_plan *plan)
{
    plan->source = source_present ? 0x02fe0f54U : 0U;
    plan->source_helper = source_present ? 0x0001dd10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df70U;
    plan->column = 4U;
    plan->row = 17U;
    plan->width = caller_g23 + 31U;
    plan->height = 5U;
}
