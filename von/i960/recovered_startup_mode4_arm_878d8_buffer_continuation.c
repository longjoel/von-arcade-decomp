/* Slot-20 buffer continuation recovered from i960 0x878d8-0x878e4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 buffer_address, helper_call, continuation_target;
} recovered_startup_mode4_arm_result_878d8_buffer_continuation;

int recovered_startup_mode4_arm_878d8_buffer_continuation(
    recovered_startup_mode4_arm_result_878d8_buffer_continuation *result)
{
    recovered_startup_mode4_arm_result_878d8_buffer_continuation r = {
        0x5040d0U, 0x88af0U, 0x878f8U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
