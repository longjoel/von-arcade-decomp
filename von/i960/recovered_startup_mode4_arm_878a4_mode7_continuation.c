/* Secondary slot-20 mode-7 continuation recovered from i960 0x878a4-0x878d8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_value, source_shifted;
    recovered_u32 mode_address, flag_address, shifted_address, buffer_address;
    recovered_u32 first_helper, second_helper, continuation_target;
} recovered_startup_mode4_arm_result_878a4_mode7_continuation;

int recovered_startup_mode4_arm_878a4_mode7_continuation(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_878a4_mode7_continuation *result)
{
    recovered_startup_mode4_arm_result_878a4_mode7_continuation r = {
        7U, 1U, source_value, source_value >> 8U,
        0x51c97cU, 0x51c9a0U, 0x51c994U, 0x503ad0U,
        0x888f0U, 0x88af0U, 0x878f8U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
