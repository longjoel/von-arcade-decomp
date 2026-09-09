/* Slot-10 state-specific setup/warning arms recovered from i960 0x1aca8-0x1ada0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_address, state_value;
    recovered_u32 ready_address, ready_value, row_address, row_value;
    recovered_u32 hardware_address, hardware_mode;
    recovered_u32 setup_helper, setup_call_count, setup_argument;
    recovered_u32 warning_service, warning_call_count, warning_code;
    recovered_u32 recognized_state, continuation;
} recovered_startup_mode4_arm_1aca8_state_setup_warning_result;

int recovered_startup_mode4_arm_1aca8_state_setup_warning(
    recovered_u32 state_value, recovered_u32 ready_value, recovered_u32 row_value,
    recovered_u32 hardware_mode,
    recovered_startup_mode4_arm_1aca8_state_setup_warning_result *result)
{
    recovered_startup_mode4_arm_1aca8_state_setup_warning_result r = {0};
    r.state_address = 0x503ab0U;
    r.state_value = state_value;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.row_address = 0x503a80U;
    r.row_value = row_value;
    r.hardware_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.setup_helper = 0x2a4e0U;
    r.warning_service = 0x184e8U;
    r.continuation = 0x1ada0U;
    if (state_value == 0U) {
        r.setup_argument = 0x1314U;
    } else if (state_value == 1U) {
        r.setup_argument = 0x1315U;
    } else if (state_value == 2U) {
        r.setup_argument = 0x1313U;
    } else if (state_value == 5U) {
        r.setup_argument = 0x1312U;
    } else {
        return result != (void *)0 ? (*result = r, 1) : 1;
    }
    r.recognized_state = 1U;
    r.setup_call_count = (ready_value != 0U || row_value != 9U) ? 1U : 0U;
    if (state_value == 0U)
        r.warning_code = hardware_mode == 0U ? 0x93U : 0x9bU;
    else
        r.warning_code = hardware_mode == 0U ? 0x97U : 0x9fU;
    r.warning_call_count = 1U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
