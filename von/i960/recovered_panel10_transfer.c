/* Fixed plain transfer recovered from i960 0x1fba0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel10_transfer_plan {
    u32 helper;
    u32 source;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel10_transfer_plan(struct recovered_panel10_transfer_plan *plan)
{
    plan->helper = 0x0001dc10U;
    plan->source = 0x02fe0404U;
    plan->column = 10U;
    plan->row = 20U;
    plan->width = 31U;
    plan->height = 5U;
}
