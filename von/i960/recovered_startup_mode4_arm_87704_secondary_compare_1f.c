/* Secondary response-1f compare wrapper recovered from i960 0x87704-0x8771c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, compare_low, compare_high;
    recovered_u32 low_pair_word, high_pair_word, less_than;
    recovered_u32 failure_target, success_target;
} recovered_startup_mode4_arm_result_87704_secondary_compare_1f;

int recovered_startup_mode4_arm_87704_secondary_compare_1f(
    recovered_u32 real_value, recovered_u32 less_than,
    recovered_startup_mode4_arm_result_87704_secondary_compare_1f *result)
{
    recovered_startup_mode4_arm_result_87704_secondary_compare_1f r = {
        real_value, 0x40590000U, 0U, 0U, 0x40590000U,
        less_than != 0U ? 1U : 0U, 0x878e8U, 0x878a0U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
