/* Source-or-clear route recovered from i960 0x1fa30. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel5_source_fill_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel5_source_fill_plan(u32 source_present, u32 caller_g27,
                                       struct recovered_panel5_source_fill_plan *plan)
{
    plan->source = source_present ? 0x02fe053aU : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column = 2U;
    plan->row = 20U;
    plan->width = caller_g27 + 31U;
    plan->height = 5U;
}
