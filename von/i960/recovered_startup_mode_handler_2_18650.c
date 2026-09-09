/* Startup mode handler 2 recovered from i960 0x18650-0x18678. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 helper_call;
    recovered_u32 helper_argument;
    recovered_u32 helper_argument_count;
    recovered_u32 mode_address, mode_before, mode_after;
    recovered_u32 phase_address, phase_after;
    recovered_u32 mode_increment;
    recovered_u32 return_target;
} recovered_startup_mode_handler_2_result_18650;

int recovered_startup_mode_handler_2_18650(
    recovered_u32 mode_value,
    recovered_startup_mode_handler_2_result_18650 *result)
{
    recovered_startup_mode_handler_2_result_18650 r = {0};
    r.helper_call = 0x1ccf8U;
    r.helper_argument = 0U;
    r.helper_argument_count = 1U;
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = mode_value + 1U;
    r.phase_address = 0x503a00U;
    r.phase_after = 0U;
    r.mode_increment = 1U;
    r.return_target = 0x18678U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
