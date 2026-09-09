/* Slot-20 response-0x31 wrapper recovered from i960 0x87248-0x87260. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_handler;
    recovered_u32 real_input;
    recovered_u32 real_compare_low;
    recovered_u32 real_compare_high;
    recovered_u32 real_less;
    recovered_u32 failure_target;
    recovered_u32 success_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_87248_response31;

int recovered_startup_mode4_arm_87248_response31(
    recovered_u32 real_input, recovered_u32 real_less,
    recovered_startup_mode4_arm_result_87248_response31 *result)
{
    recovered_startup_mode4_arm_result_87248_response31 r = {0};

    r.response_handler = 0x31U;
    r.real_input = real_input;
    r.real_compare_low = 0U;
    r.real_compare_high = 0x40590000U;
    r.real_less = real_less != 0U ? 1U : 0U;
    r.failure_target = 0x878e8U;
    r.success_target = 0x87394U;
    r.continuation_target = r.real_less != 0U ? r.failure_target :
                            r.success_target;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
