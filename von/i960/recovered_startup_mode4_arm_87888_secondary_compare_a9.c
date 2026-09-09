/* Secondary response-a9 compare wrapper recovered from i960 0x87888-0x878a0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, compare_pair_low, compare_pair_high, less_than;
    recovered_u32 failure_target, success_target;
} recovered_startup_mode4_arm_result_87888_secondary_compare_a9;

int recovered_startup_mode4_arm_87888_secondary_compare_a9(
    recovered_u32 real_value, recovered_u32 less_than,
    recovered_startup_mode4_arm_result_87888_secondary_compare_a9 *result)
{
    recovered_startup_mode4_arm_result_87888_secondary_compare_a9 r = {
        real_value, 0U, 0x40590000U, less_than != 0U ? 1U : 0U,
        0x878e8U, 0x878a0U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
