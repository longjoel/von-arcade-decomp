/* Slot-11 state-2 counter arm recovered from i960 0x1b2cc-0x1b2fc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_6c_address, counter_6c_before, counter_6c_after;
    recovered_u32 counter_70_address, counter_70_before, counter_70_after;
    recovered_u32 callback_address, callback_value;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1b2cc_state2_counters_result;

int recovered_startup_mode4_arm_1b2cc_state2_counters(
    recovered_u32 counter_6c_value, recovered_u32 counter_70_value,
    recovered_u32 callback_value,
    recovered_startup_mode4_arm_1b2cc_state2_counters_result *result)
{
    recovered_startup_mode4_arm_1b2cc_state2_counters_result r = {0};
    r.counter_6c_address = 0x503a6cU;
    r.counter_6c_before = counter_6c_value;
    r.counter_6c_after = counter_6c_value + 1U;
    r.counter_70_address = 0x503a70U;
    r.counter_70_before = counter_70_value;
    r.counter_70_after = counter_70_value + 1U;
    r.callback_address = 0x504b94U;
    r.callback_value = callback_value;
    r.continuation = 0x1b2fcU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
