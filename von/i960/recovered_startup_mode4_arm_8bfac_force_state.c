/* Selector-1 success epilogue recovered from i960 0x8bfac-0x8bfd0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c9b4;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8bfac_force_state_result;

recovered_startup_mode4_arm_8bfac_force_state_result
recovered_startup_mode4_arm_8bfac_force_state(void)
{
    recovered_startup_mode4_arm_8bfac_force_state_result result;

    result.state_51c9b4 = 1U;
    result.continuation = 0x0008bfc0U;
    return result;
}
