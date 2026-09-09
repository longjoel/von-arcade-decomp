/* Completion retry bridge recovered from i960 0x8d0a4-0x8d0b0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 retry_target;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8d0a4_retry_bridge_result;

recovered_startup_mode4_arm_8d0a4_retry_bridge_result
recovered_startup_mode4_arm_8d0a4_retry_bridge(void)
{
    recovered_startup_mode4_arm_8d0a4_retry_bridge_result result;

    result.retry_target = 0x0008ccf0U;
    result.continuation = result.retry_target;
    return result;
}
