/* Profile-selected video upload recovered from i960 0x201a0. */

#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_video_profile_upload_plan {
    u32 source;
    u32 destination;
    u32 flags;
    u32 halfwords_per_row;
    u32 rows;
    u32 origin;
    u32 helper;
};

void recovered_video_profile_upload_plan(u32 profile, u32 caller_g14,
                                         u32 caller_g17,
                                         struct recovered_video_profile_upload_plan *plan)
{
    u32 destination = profile == 0U ? 0x01fcfd20U
        : profile == 1U ? 0x01fd49d0U : 0x01fd1520U;
    RECOVERED_SET_UPLOAD_PLAN(plan, destination, caller_g17 + 31U);
    plan->origin = caller_g14;
}
