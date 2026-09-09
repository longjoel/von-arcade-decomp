/* Slot-12 common completion bridge recovered from i960 0x1b614-0x1b61c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 call_count;
    recovered_u32 call_target[2];
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1b614_completion_bridge_result;

int recovered_startup_mode4_arm_1b614_completion_bridge(
    recovered_startup_mode4_arm_1b614_completion_bridge_result *result)
{
    recovered_startup_mode4_arm_1b614_completion_bridge_result r = {0};
    r.call_count = 2U;
    r.call_target[0] = 0x43ee8U;
    r.call_target[1] = 0x423a8U;
    r.continuation = 0x1b61cU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
