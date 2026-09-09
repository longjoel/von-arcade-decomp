/* Slot-20 response-0x49 wrapper recovered from i960 0x8729c-0x872cc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_handler;
    recovered_u32 real_input;
    recovered_u32 first_compare_low, first_compare_high;
    recovered_u32 second_compare_low, second_compare_high;
    recovered_u32 below_first_threshold, below_second_threshold;
    recovered_u32 intermediate_path, intermediate_register_5;
    recovered_u32 failure_target, success_target, intermediate_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_8729c_response49;

int recovered_startup_mode4_arm_8729c_response49(
    recovered_u32 real_input, recovered_u32 below_first_threshold,
    recovered_u32 below_second_threshold,
    recovered_startup_mode4_arm_result_8729c_response49 *result)
{
    recovered_startup_mode4_arm_result_8729c_response49 r = {0};

    r.response_handler = 0x49U;
    r.real_input = real_input;
    r.first_compare_low = 0U;
    r.first_compare_high = 0x40590000U;
    r.second_compare_low = 0U;
    r.second_compare_high = 0x4072c000U;
    r.below_first_threshold = below_first_threshold != 0U ? 1U : 0U;
    r.below_second_threshold = below_second_threshold != 0U ? 1U : 0U;
    r.failure_target = 0x878e8U;
    r.success_target = 0x87394U;
    r.intermediate_target = 0x87398U;
    if (r.below_first_threshold != 0U) {
        r.continuation_target = r.failure_target;
    } else if (r.below_second_threshold != 0U) {
        r.intermediate_path = 1U;
        r.intermediate_register_5 = 6U;
        r.continuation_target = r.intermediate_target;
    } else {
        r.continuation_target = r.success_target;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
