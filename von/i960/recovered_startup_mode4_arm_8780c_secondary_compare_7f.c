/* Secondary response-7f compare wrapper recovered from i960 0x8780c-0x87828. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 real_value, compare_pair_low, compare_pair_high, less_than;
    recovered_u32 failure_target, success_target;
} recovered_startup_mode4_arm_result_8780c_secondary_compare_7f;

int recovered_startup_mode4_arm_8780c_secondary_compare_7f(
    recovered_u32 real_value, recovered_u32 less_than,
    recovered_startup_mode4_arm_result_8780c_secondary_compare_7f *result)
{
    recovered_startup_mode4_arm_result_8780c_secondary_compare_7f r = {
        real_value, 0U, 0x40590000U, less_than != 0U ? 1U : 0U,
        0x878e8U, 0x878a0U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
