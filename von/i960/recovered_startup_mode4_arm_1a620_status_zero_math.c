/* Slot-10 status-zero arithmetic recovered from i960 0x1a620-0x1a690. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_word, phase_divisor;
    recovered_u32 register_r17, register_r16;
    recovered_u32 status_nonzero_bypass, invalid_divisor;
    recovered_u32 record_helper_address, record_helper_call_count;
    recovered_u32 record_helper_argument0, record_helper_argument1;
    recovered_u32 arithmetic_helper_address, arithmetic_helper_call_count;
    recovered_u32 arithmetic_helper_argument0, arithmetic_helper_argument1;
    recovered_u32 base_value, base_remainder, base_quotient;
    recovered_u32 derived_stride, result_r5, result_r6;
    recovered_u32 setup_call, setup_call_count, setup_argument;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1a620_status_zero_math_result;

int recovered_startup_mode4_arm_1a620_status_zero_math(
    recovered_u32 status_word, recovered_u32 phase_divisor,
    recovered_u32 register_r17, recovered_u32 register_r16,
    recovered_startup_mode4_arm_1a620_status_zero_math_result *result)
{
    recovered_startup_mode4_arm_1a620_status_zero_math_result r = {0};
    r.status_word = status_word;
    r.phase_divisor = phase_divisor;
    r.register_r17 = register_r17;
    r.register_r16 = register_r16;
    r.record_helper_address = 0x1cac8U;
    r.record_helper_argument0 = 6U;
    r.record_helper_argument1 = 3U;
    r.arithmetic_helper_address = 0x1e800U;
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 0x1148U;
    r.continuation = 0x1a690U;
    if (status_word != 0U) {
        r.status_nonzero_bypass = 1U;
        r.continuation = 0x1a7c8U;
    } else if (phase_divisor == 0U) {
        r.invalid_divisor = 1U;
    } else {
        r.base_value = 31U + register_r17;
        r.base_remainder = r.base_value % phase_divisor;
        r.base_quotient = r.base_value / phase_divisor;
        r.derived_stride = 35U * ((31U + register_r16) - r.base_remainder);
        if (r.derived_stride == 0U) {
            r.invalid_divisor = 1U;
        } else {
            r.result_r6 = r.base_quotient / r.derived_stride;
            r.result_r5 = (r.base_quotient + 1U) - status_word;
            r.record_helper_call_count = 1U;
            r.arithmetic_helper_call_count = 1U;
            r.arithmetic_helper_argument0 = r.result_r5;
            r.arithmetic_helper_argument1 = r.result_r6;
            if (r.base_remainder == 0U && r.result_r5 <= 9U) {
                r.setup_call_count = 1U;
            }
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
