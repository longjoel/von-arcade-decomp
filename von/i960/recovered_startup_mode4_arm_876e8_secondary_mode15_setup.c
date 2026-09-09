/* Secondary response-1 setup recovered from i960 0x876e8-0x87704. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_address, source_value;
    recovered_u32 mode_address, flag_value, buffer_address, continuation_target;
} recovered_startup_mode4_arm_result_876e8_secondary_mode15_setup;

int recovered_startup_mode4_arm_876e8_secondary_mode15_setup(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_876e8_secondary_mode15_setup *result)
{
    recovered_startup_mode4_arm_result_876e8_secondary_mode15_setup r = {
        15U, 1U, 0x51c990U, source_value, 0x51c97cU, 1U, 0x5040d0U, 0x87864U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
