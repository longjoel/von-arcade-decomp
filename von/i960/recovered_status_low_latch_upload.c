/* Low-latch branch recovered from i960 0x2196c-0x219a4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_low_latch_upload_plan {
    u32 selected;
    u32 source;
    u32 helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 attribute_mask;
};

void recovered_status_low_latch_upload_plan(int32_t latch,
                                            struct recovered_status_low_latch_upload_plan *plan)
{
    plan->selected = latch <= 8 ? 1U : 0U;
    plan->source = 0x02fe8fc4U;
    plan->helper = 0x0001de80U;
    plan->column = 0U;
    plan->row = (u32)(latch - 8);
    plan->width = 0x40U;
    plan->height = 8U;
    plan->attribute_mask = 0x40U;
}
