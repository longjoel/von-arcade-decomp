/* Secondary response-25 compare wrapper recovered from i960 0x87720-0x87738. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, compare_pair_low, compare_pair_high, less_than;
    recovered_u32 failure_target, success_target;
} recovered_startup_mode4_arm_result_87720_secondary_compare_25;

int recovered_startup_mode4_arm_87720_secondary_compare_25(
    recovered_u32 real_value, recovered_u32 less_than,
    recovered_startup_mode4_arm_result_87720_secondary_compare_25 *result)
{
    recovered_startup_mode4_arm_result_87720_secondary_compare_25 r = {
        real_value, 0U, 0x40590000U, less_than != 0U ? 1U : 0U,
        0x878e8U, 0x878a0U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
