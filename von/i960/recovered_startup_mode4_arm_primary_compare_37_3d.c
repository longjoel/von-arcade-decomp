/* Primary response-37/3d compare wrappers recovered from i960 0x87264/0x87280. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, compare_pair_low, compare_pair_high, less_than;
    recovered_u32 failure_target, success_target;
} recovered_startup_mode4_arm_result_primary_compare_37_3d;

int recovered_startup_mode4_arm_primary_compare_37_3d(
    recovered_u32 real_value, recovered_u32 less_than,
    recovered_startup_mode4_arm_result_primary_compare_37_3d *result)
{
    recovered_startup_mode4_arm_result_primary_compare_37_3d r = {
        real_value, 0U, 0x40590000U, less_than != 0U ? 1U : 0U,
        0x878e8U, 0x87394U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
