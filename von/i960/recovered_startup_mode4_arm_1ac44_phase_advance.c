/* Shared slot-10 phase advance recovered from i960 0x1ac44-0x1ac50. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 increment;
    recovered_u32 next_address;
} recovered_startup_mode4_arm_1ac44_phase_advance_result;

int recovered_startup_mode4_arm_1ac44_phase_advance(
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_1ac44_phase_advance_result *result)
{
    recovered_startup_mode4_arm_1ac44_phase_advance_result r = {0};
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.increment = 1U;
    r.phase_after = phase_value + r.increment;
    r.next_address = 0x1ac50U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
