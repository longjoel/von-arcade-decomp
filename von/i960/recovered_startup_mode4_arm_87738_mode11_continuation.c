/* Slot-20 response-25 continuation recovered from i960 0x87738-0x87758. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_address, source_value, source_shifted;
    recovered_u32 mode_address, flag_address, shifted_address, buffer_address;
    recovered_u32 helper_call, continuation_target;
} recovered_startup_mode4_arm_result_87738_mode11_continuation;

int recovered_startup_mode4_arm_87738_mode11_continuation(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_87738_mode11_continuation *result)
{
    recovered_startup_mode4_arm_result_87738_mode11_continuation r = {
        11U, 1U, 0x51c990U, source_value, source_value >> 8U,
        0x51c97cU, 0x51c9a0U, 0x51c994U, 0x503ad0U, 0x8c970U, 0x878f8U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
