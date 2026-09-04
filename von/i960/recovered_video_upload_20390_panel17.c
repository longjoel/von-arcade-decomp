/* Upload and panel helpers recovered from i960 0x20390/0x203b0. */

#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_upload_20390_plan {
    u32 source;
    u32 destination;
    u32 flags;
    u32 halfwords_per_row;
    u32 rows;
    u32 helper;
};

struct recovered_panel17_plan {
    u32 source;
    u32 helper;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
    u32 width;
    u32 height;
};

void recovered_upload_20390_plan(u32 caller_g17,
                                 struct recovered_upload_20390_plan *plan)
{
    RECOVERED_SET_UPLOAD_PLAN(plan, 0x01fccd20U, caller_g17 + 31U);
}

void recovered_panel17_plan(struct recovered_panel17_plan *plan)
{
    plan->source = 0x02fe0864U;
    plan->helper = 0x0001dc90U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
    plan->width = 31U;
    plan->height = 5U;
}
