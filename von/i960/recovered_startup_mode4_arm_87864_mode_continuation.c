/* Slot-20 mode continuation recovered from i960 0x87864-0x87884. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_value, source_shifted;
    recovered_u32 mode_address, flag_address, shifted_address, buffer_address;
    recovered_u32 helper_call, continuation_target;
} recovered_startup_mode4_arm_result_87864_mode_continuation;

int recovered_startup_mode4_arm_87864_mode_continuation(
    recovered_u32 mode, recovered_u32 source_value,
    recovered_startup_mode4_arm_result_87864_mode_continuation *result)
{
    recovered_startup_mode4_arm_result_87864_mode_continuation r = {0};
    r.mode = mode;
    r.flag = 1U;
    r.source_value = source_value;
    r.source_shifted = source_value >> 8U;
    r.mode_address = 0x51c97cU;
    r.flag_address = 0x51c9a0U;
    r.shifted_address = 0x51c994U;
    r.buffer_address = 0x503ad0U;
    r.helper_call = 0x88a10U;
    r.continuation_target = 0x878f8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
