/* Slot-20 failure bridge recovered from i960 0x878e8-0x878f8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 helper_call;
    recovered_u32 helper_result;
    recovered_u32 mask;
    recovered_u32 stored_address;
    recovered_u32 stored_value;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_878e8_failure_bridge;

int recovered_startup_mode4_arm_878e8_failure_bridge(
    recovered_u32 helper_result,
    recovered_startup_mode4_arm_result_878e8_failure_bridge *result)
{
    recovered_startup_mode4_arm_result_878e8_failure_bridge r = {0};

    r.helper_call = 0xf5058U;
    r.helper_result = helper_result;
    r.mask = 1U;
    r.stored_address = 0x51c97cU;
    r.stored_value = helper_result & r.mask;
    r.continuation_target = 0x878f8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
