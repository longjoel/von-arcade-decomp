/* Source-or-clear route recovered from i960 0x1fa80. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel6_source_fill_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel6_source_fill_plan(u32 source_present, u32 caller_g14,
                                       struct recovered_panel6_source_fill_plan *plan)
{
    plan->source = source_present ? 0x02fe099aU : 0U;
    plan->source_helper = source_present ? 0x0001dc90U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column = 8U;
    plan->row = 10U;
    plan->width = caller_g14 + 31U;
    plan->height = 5U;
}
