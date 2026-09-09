/* Slot-12 counter dispatcher recovered from i960 0x1b61c-0x1b650. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 progress_address, progress_value;
    recovered_u32 limit_address, limit_value;
    recovered_u32 secondary_counter_address, secondary_counter_value;
    recovered_u32 progress_exceeded;
    recovered_u32 secondary_within_limit;
    recovered_u32 selected_state;
    recovered_u32 branch;
    recovered_u32 helper_call, helper_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_1b61c_counter_dispatch;

int recovered_startup_mode4_arm_1b61c_counter_dispatch(
    recovered_u32 progress_value, recovered_u32 limit_value,
    recovered_u32 secondary_counter_value,
    recovered_startup_mode4_arm_result_1b61c_counter_dispatch *result)
{
    recovered_startup_mode4_arm_result_1b61c_counter_dispatch r = {0};

    r.progress_address = 0x503a6cU;
    r.progress_value = progress_value;
    r.limit_address = 0x503a78U;
    r.limit_value = limit_value;
    r.secondary_counter_address = 0x503a70U;
    r.secondary_counter_value = secondary_counter_value;
    r.progress_exceeded = (int32_t)progress_value > (int32_t)limit_value ? 1U : 0U;
    r.secondary_within_limit = (int32_t)secondary_counter_value <= (int32_t)limit_value ? 1U : 0U;
    if (r.progress_exceeded == 0U && r.secondary_within_limit != 0U) {
        r.selected_state = 8U;
        r.branch = 1U;
        r.continuation_target = 0x1b800U;
    } else if (r.secondary_within_limit != 0U) {
        r.branch = 2U;
        r.continuation_target = 0x1b780U;
    } else {
        r.branch = 3U;
        r.helper_call = 0x31c0U;
        r.helper_target = 0x1b650U;
        r.continuation_target = 0x1b650U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
