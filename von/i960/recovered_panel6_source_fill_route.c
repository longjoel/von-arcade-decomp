/* Source-or-clear route recovered from i960 0x1fa80. */

#include <stdint.h>
#include "recovered_common.h"

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
    RECOVERED_SET_SOURCE_OR_CLEAR(plan, source_present, 0x02fe099aU,
                                  0x0001dc90U, RECOVERED_HELPER_CLEAR);
    plan->column = 8U;
    plan->row = 10U;
    plan->width = caller_g14 + 31U;
    plan->height = 5U;
}
