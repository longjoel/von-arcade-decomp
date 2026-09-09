/* Secondary response-49 compare wrapper recovered from i960 0x8779c-0x877d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, first_pair_low, first_pair_high;
    recovered_u32 second_pair_low, second_pair_high;
    recovered_u32 below_first, above_or_equal_second;
    recovered_u32 failure_target, middle_target, high_target;
} recovered_startup_mode4_arm_result_8779c_secondary_compare_49;

int recovered_startup_mode4_arm_8779c_secondary_compare_49(
    recovered_u32 real_value, recovered_u32 below_first,
    recovered_u32 above_or_equal_second,
    recovered_startup_mode4_arm_result_8779c_secondary_compare_49 *result)
{
    recovered_startup_mode4_arm_result_8779c_secondary_compare_49 r = {
        real_value, 0U, 0x40590000U, 0U, 0x4072c000U,
        below_first != 0U ? 1U : 0U, above_or_equal_second != 0U ? 1U : 0U,
        0x878e8U, 0x878a4U, 0x878a0U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
