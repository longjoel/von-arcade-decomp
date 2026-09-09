/* Slot-10 ready-clear ratio state arm recovered from i960 0x1ab40-0x1abec. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_numerator_address, first_numerator_raw;
    recovered_u32 first_denominator_address, first_denominator_raw;
    recovered_u32 second_numerator_address, second_numerator_raw;
    recovered_u32 second_denominator_address, second_denominator_raw;
    recovered_u32 callback_register;
    recovered_u32 counter_address, counter_before, counter_after;
    recovered_u32 state_address, state_value, command_address, command_value;
    recovered_u32 ratio_less, ratio_equal, ratio_greater, invalid_denominator;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1ab40_ratio_state_arm_result;

int recovered_startup_mode4_arm_1ab40_ratio_state_arm(
    recovered_u32 first_numerator_raw, recovered_u32 first_denominator_raw,
    recovered_u32 second_numerator_raw, recovered_u32 second_denominator_raw,
    recovered_u32 callback_register, recovered_u32 counter_value,
    recovered_startup_mode4_arm_1ab40_ratio_state_arm_result *result)
{
    recovered_startup_mode4_arm_1ab40_ratio_state_arm_result r = {0};
    int16_t first_numerator = (int16_t)(first_numerator_raw & 0xffffU);
    int16_t first_denominator = (int16_t)(first_denominator_raw & 0xffffU);
    int16_t second_numerator = (int16_t)(second_numerator_raw & 0xffffU);
    int16_t second_denominator = (int16_t)(second_denominator_raw & 0xffffU);
    r.first_numerator_address = 0x503ca2U;
    r.first_numerator_raw = first_numerator_raw;
    r.first_denominator_address = 0x503ca8U;
    r.first_denominator_raw = first_denominator_raw;
    r.second_numerator_address = 0x5042a2U;
    r.second_numerator_raw = second_numerator_raw;
    r.second_denominator_address = 0x5042a8U;
    r.second_denominator_raw = second_denominator_raw;
    r.callback_register = callback_register;
    r.counter_address = 0x503a90U;
    r.counter_before = counter_value;
    r.counter_after = counter_value;
    r.state_address = 0x503ab0U;
    r.command_address = 0x5032f4U;
    r.continuation = 0x1ac50U;
    if (first_numerator == 0 || second_numerator == 0) {
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
            r.counter_after = counter_value + 1U;
        } else {
            r.ratio_equal = 1U;
            r.state_value = 2U;
            r.command_value = 0x42U;
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
