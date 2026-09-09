/* Selector-1 success epilogue recovered from i960 0x8bd60-0x8bd74. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 g14_value;
    recovered_u32 state_51c9b4;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8bd60_force_state_result;

recovered_startup_mode4_arm_8bd60_force_state_result
recovered_startup_mode4_arm_8bd60_force_state(recovered_u32 g14_value)
{
    recovered_startup_mode4_arm_8bd60_force_state_result result;

    result.g14_value = g14_value;
    result.state_51c9b4 = g14_value;
    result.continuation = 0x0008bd70U;
    return result;
}
