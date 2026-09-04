/* Upload and status-panel routes recovered from i960 0x20460/0x20480. */

#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_upload_20460_plan {
    u32 source;
    u32 destination;
    u32 flags;
    u32 halfwords_per_row;
    u32 rows;
    u32 helper;
};

struct recovered_panel18_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_advance;
    u32 width;
    u32 height;
};

void recovered_upload_20460_plan(u32 caller_g17,
                                 struct recovered_upload_20460_plan *plan)
{
    RECOVERED_SET_UPLOAD_PLAN(plan, 0x01fd89d0U, caller_g17 + 31U);
}

void recovered_panel18_plan(u32 source_present,
                            struct recovered_panel18_plan *plan)
{
    plan->source = source_present ? 0x02fcf468U : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_advance = 4U;
    plan->width = 8U;
    plan->height = 4U;
}
