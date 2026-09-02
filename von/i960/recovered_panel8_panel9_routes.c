/* Adjacent panel routes recovered from i960 0x1fb10 and 0x1fb50. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel8_plan {
    u32 helper;
    u32 source;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

struct recovered_panel9_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel8_plan(u32 caller_g17, struct recovered_panel8_plan *plan)
{
    plan->helper = 0x0001dc90U;
    plan->source = 0x02fe1170U;
    plan->column = 7U;
    plan->row = 10U;
    plan->width = caller_g17 + 31U;
    plan->height = 5U;
}

void recovered_panel9_plan(u32 source_present, u32 caller_g22,
                           struct recovered_panel9_plan *plan)
{
    plan->source = source_present ? 0x02fe0d42U : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column = 5U;
    plan->row = 10U;
    plan->width = caller_g22 + 31U;
    plan->height = 5U;
}
