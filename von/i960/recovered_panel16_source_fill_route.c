/* Source-or-clear route recovered from i960 0x1fff0. */

#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_panel16_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

void recovered_panel16_plan(u32 source_present, u32 caller_g9,
                            struct recovered_panel16_plan *plan)
{
    RECOVERED_SET_SOURCE_OR_CLEAR(plan, source_present, 0x02fdff54U,
                                  0x0001dc90U, RECOVERED_HELPER_CLEAR);
    plan->column = 11U;
    plan->row = 21U;
    plan->width = caller_g9 + 31U;
    plan->height = 8U;
}
