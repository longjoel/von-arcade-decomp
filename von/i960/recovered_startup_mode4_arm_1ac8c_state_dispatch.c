/* Slot-10 common-service state dispatch recovered from i960 0x1ac8c-0x1aca8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_address, state_value;
    recovered_u32 state_zero_target, state_one_target, state_two_target;
    recovered_u32 state_five_target, generic_target;
    recovered_u32 selected_target, generic_selected;
} recovered_startup_mode4_arm_1ac8c_state_dispatch_result;

int recovered_startup_mode4_arm_1ac8c_state_dispatch(
    recovered_u32 state_value,
    recovered_startup_mode4_arm_1ac8c_state_dispatch_result *result)
{
    recovered_startup_mode4_arm_1ac8c_state_dispatch_result r = {0};
    r.state_address = 0x503ab0U;
    r.state_value = state_value;
    r.state_zero_target = 0x1ad14U;
    r.state_one_target = 0x1ace0U;
    r.state_two_target = 0x1ad5cU;
    r.state_five_target = 0x1acacU;
    r.generic_target = 0x1ada0U;
    if (state_value == 0U)
        r.selected_target = r.state_zero_target;
    else if (state_value == 1U)
        r.selected_target = r.state_one_target;
    else if (state_value == 2U)
        r.selected_target = r.state_two_target;
    else if (state_value == 5U)
        r.selected_target = r.state_five_target;
    else {
        r.selected_target = r.generic_target;
        r.generic_selected = 1U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
