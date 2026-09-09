/* Slot-20 response-0x1f wrapper recovered from i960 0x87210-0x87228. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_handler;
    recovered_u32 real_input;
    recovered_u32 real_compare_low;
    recovered_u32 real_compare_high;
    recovered_u32 real_less;
    recovered_u32 common_failure_target;
    recovered_u32 common_success_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_87210_response1f;

int recovered_startup_mode4_arm_87210_response1f(
    recovered_u32 real_input, recovered_u32 real_less,
    recovered_startup_mode4_arm_result_87210_response1f *result)
{
    recovered_startup_mode4_arm_result_87210_response1f r = {0};

    r.response_handler = 0x1fU;
    r.real_input = real_input;
    r.real_compare_low = 0U;
    r.real_compare_high = 0x40590000U;
    r.real_less = real_less != 0U ? 1U : 0U;
    r.common_failure_target = 0x878e8U;
    r.common_success_target = 0x87394U;
    r.continuation_target = r.real_less != 0U ? r.common_failure_target :
                            r.common_success_target;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
