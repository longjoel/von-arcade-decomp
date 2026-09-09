/* Slot-10 accepted ready ratio/counter arm recovered from i960 0x1a904-0x1a9e0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 retry_address, retry_before, retry_after, retry_limit;
    recovered_u32 first_numerator_address, first_numerator_raw;
    recovered_u32 first_denominator_address, first_denominator_raw;
    recovered_u32 second_numerator_address, second_numerator_raw;
    recovered_u32 second_denominator_address, second_denominator_raw;
    recovered_u32 callback_register;
    recovered_u32 state_address, state_value, command_address, command_value;
    recovered_u32 phase_address, phase_value, continuation;
    recovered_u32 ratio_less, ratio_equal, ratio_greater, threshold_fallback;
    recovered_u32 invalid_denominator;
} recovered_startup_mode4_arm_1a904_accepted_ratio_result;

int recovered_startup_mode4_arm_1a904_accepted_ratio(
    recovered_u32 retry_value,
    recovered_u32 first_numerator_raw, recovered_u32 first_denominator_raw,
    recovered_u32 second_numerator_raw, recovered_u32 second_denominator_raw,
    recovered_u32 callback_register, recovered_u32 phase_value,
    recovered_startup_mode4_arm_1a904_accepted_ratio_result *result)
{
    recovered_startup_mode4_arm_1a904_accepted_ratio_result r = {0};
    int16_t first_numerator = (int16_t)(first_numerator_raw & 0xffffU);
    int16_t first_denominator = (int16_t)(first_denominator_raw & 0xffffU);
    int16_t second_numerator = (int16_t)(second_numerator_raw & 0xffffU);
    int16_t second_denominator = (int16_t)(second_denominator_raw & 0xffffU);

    r.retry_address = 0x504cc8U;
    r.retry_before = retry_value;
    r.retry_after = retry_value + 1U;
    r.retry_limit = 4U;
    r.first_numerator_address = 0x503ca2U;
    r.first_numerator_raw = first_numerator_raw;
    r.first_denominator_address = 0x503ca8U;
    r.first_denominator_raw = first_denominator_raw;
    r.second_numerator_address = 0x5042a2U;
    r.second_numerator_raw = second_numerator_raw;
    r.second_denominator_address = 0x5042a8U;
    r.second_denominator_raw = second_denominator_raw;
    r.callback_register = callback_register;
    r.state_address = 0x503ab0U;
    r.command_address = 0x5032f4U;
    r.phase_address = 0x503a00U;
    r.phase_value = phase_value;
    r.continuation = 0x1ac44U;

    /* cmpi 4,g4 / bge tests the old counter; four accepted visits use this arm. */
    if (retry_value >= r.retry_limit) {
        r.threshold_fallback = 1U;
        r.continuation = 0x1a9e0U;
    } else if (first_numerator == 0 || second_numerator == 0) {
        r.invalid_denominator = 1U;
    } else {
        double first_ratio = (double)first_denominator / (double)first_numerator;
        double second_ratio = (double)second_denominator / (double)second_numerator;
        if (first_ratio < second_ratio) {
            r.ratio_less = 1U;
            r.state_value = 1U;
            r.command_value = 0x41U;
        } else if (first_ratio > second_ratio) {
            r.ratio_greater = 1U;
            r.state_value = callback_register;
            r.command_value = 0x40U;
        } else {
            r.ratio_equal = 1U;
            r.state_value = 2U;
            r.command_value = 0x42U;
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
