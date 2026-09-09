/* Primary response-8b/9d setup wrappers recovered from i960 0x87344/0x87360. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_address, source_value;
    recovered_u32 mode_address, flag_value, buffer_address, continuation_target;
} recovered_startup_mode4_arm_result_primary_setup_8b_9d;

int recovered_startup_mode4_arm_primary_setup_8b_9d(
    recovered_u32 mode, recovered_u32 source_value,
    recovered_startup_mode4_arm_result_primary_setup_8b_9d *result)
{
    recovered_startup_mode4_arm_result_primary_setup_8b_9d r = {
        mode, 1U, 0x51c98cU, source_value, 0x51c97cU, 1U, 0x5040d0U, 0x87864U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
