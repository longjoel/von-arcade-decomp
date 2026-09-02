/* Fixed attributed transfer recovered from i960 0x1fad0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel7_transfer_plan {
    u32 helper;
    u32 source;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel7_transfer_plan(u32 caller_g12,
                                   struct recovered_panel7_transfer_plan *plan)
{
    plan->helper = 0x0001dc10U;
    plan->source = 0x02fe1350U;
    plan->column = 10U;
    plan->row = 10U;
    plan->width = caller_g12 + 31U;
    plan->height = 5U;
}
