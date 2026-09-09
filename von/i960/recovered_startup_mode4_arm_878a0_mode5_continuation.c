/* Secondary slot-20 mode-5 continuation recovered from i960 0x878a0-0x878e4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_value, source_shifted;
    recovered_u32 mode_address, flag_address, shifted_address, buffer_address;
    recovered_u32 first_helper, second_helper, continuation_target;
} recovered_startup_mode4_arm_result_878a0_mode5_continuation;

int recovered_startup_mode4_arm_878a0_mode5_continuation(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_878a0_mode5_continuation *result)
{
    recovered_startup_mode4_arm_result_878a0_mode5_continuation r = {0};
    r.mode = 5U;
    r.flag = 1U;
    r.source_value = source_value;
    r.source_shifted = source_value >> 8U;
    r.mode_address = 0x51c97cU;
    r.flag_address = 0x51c9a0U;
    r.shifted_address = 0x51c994U;
    r.buffer_address = 0x5040d0U;
    r.first_helper = 0x888f0U;
    r.second_helper = 0x88af0U;
    r.continuation_target = 0x878f8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
