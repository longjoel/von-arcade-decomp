/* Upload descriptor recovered from the 0x1f060 wrapper. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_video_upload_wrapper_plan {
    u32 source;
    u32 destination;
    u32 halfwords_per_row;
    u32 rows;
};

void recovered_text_video_upload_wrapper_plan(u32 caller_g17,
                                              struct recovered_text_video_upload_wrapper_plan *plan)
{
    plan->source = 0x01004000U;
    plan->destination = 0x02fd2520U;
    plan->halfwords_per_row = 0x40U;
    plan->rows = caller_g17 + 31U;
}
