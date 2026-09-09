/* Shared startup mode handlers 8/15 recovered from i960 0x18620-0x18648. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode_address, mode_before, mode_after;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 return_thunk, branch_target;
    recovered_u32 return_target;
} recovered_startup_mode_handler_8_result_18620;

int recovered_startup_mode_handler_8_18620(
    recovered_u32 mode_value, recovered_u32 phase_value,
    recovered_startup_mode_handler_8_result_18620 *result)
{
    recovered_startup_mode_handler_8_result_18620 r = {0};
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = 0U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = 0U;
    r.return_thunk = 0x18644U;
    r.branch_target = r.return_thunk;
    r.return_target = r.return_thunk;
    if (result != (void *)0)
        *result = r;
    return 1;
}
