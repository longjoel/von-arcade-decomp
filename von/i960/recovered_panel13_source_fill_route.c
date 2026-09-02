/* Source-or-clear route recovered from i960 0x1ff20. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel13_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
    u32 width;
    u32 height;
};

void recovered_panel13_plan(u32 source_present, u32 caller_g3,
                            struct recovered_panel13_plan *plan)
{
    plan->source = source_present ? 0x02fe0b5cU : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
    plan->width = caller_g3 + 31U;
    plan->height = 5U;
}
