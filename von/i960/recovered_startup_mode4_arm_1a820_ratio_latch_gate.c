/* Slot-10 ratio/latch warning gate recovered from i960 0x1a820-0x1a8d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 numerator_address, numerator_raw, numerator_signed;
    recovered_u32 denominator_address, denominator_raw, denominator_signed;
    recovered_u32 alternate_numerator_address, alternate_numerator_raw;
    recovered_u32 alternate_denominator_address, alternate_denominator_raw;
    recovered_u32 hardware_mode_address, hardware_mode;
    recovered_u32 latch_address, latch_before, latch_after;
    recovered_u32 ratio_less, ratio_equal_or_greater, invalid_denominator;
    recovered_u32 warning_service, warning_call_count, warning_code;
    recovered_u32 register_r14, continuation;
} recovered_startup_mode4_arm_1a820_ratio_latch_gate_result;

int recovered_startup_mode4_arm_1a820_ratio_latch_gate(
    recovered_u32 numerator_raw, recovered_u32 denominator_raw,
    recovered_u32 alternate_numerator_raw, recovered_u32 alternate_denominator_raw,
    recovered_u32 hardware_mode, recovered_u32 latch_value, recovered_u32 register_r14,
    recovered_startup_mode4_arm_1a820_ratio_latch_gate_result *result)
{
    recovered_startup_mode4_arm_1a820_ratio_latch_gate_result r = {0};
    int16_t numerator = (int16_t)(numerator_raw & 0xffffU);
    int16_t denominator = (int16_t)(denominator_raw & 0xffffU);
    int16_t alternate_numerator = (int16_t)(alternate_numerator_raw & 0xffffU);
    int16_t alternate_denominator = (int16_t)(alternate_denominator_raw & 0xffffU);
    r.numerator_address = 0x503ca2U;
    r.numerator_raw = numerator_raw;
    r.numerator_signed = (recovered_u32)(int32_t)numerator;
    r.denominator_address = 0x503ca8U;
    r.denominator_raw = denominator_raw;
    r.denominator_signed = (recovered_u32)(int32_t)denominator;
    r.alternate_numerator_address = 0x5042a2U;
    r.alternate_numerator_raw = alternate_numerator_raw;
    r.alternate_denominator_address = 0x5042a8U;
    r.alternate_denominator_raw = alternate_denominator_raw;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.latch_address = 0x504cc4U;
    r.latch_before = latch_value;
    r.latch_after = latch_value;
    r.warning_service = 0x184e8U;
    r.register_r14 = register_r14;
    r.continuation = 0x1a8d0U;
    if (denominator == 0 || alternate_denominator == 0) {
        r.invalid_denominator = 1U;
    } else {
        double first_ratio = (double)denominator / (double)numerator;
        double second_ratio = (double)alternate_denominator / (double)alternate_numerator;
        if (first_ratio < second_ratio) {
            r.ratio_less = 1U;
            if (latch_value == 0U) {
                r.warning_call_count = 1U;
                r.warning_code = hardware_mode == 0U ? 0x97U : 0x9fU;
                r.latch_after = 1U;
            }
        } else {
            r.ratio_equal_or_greater = 1U;
            if (latch_value == 0U) {
                r.warning_call_count = 1U;
                r.warning_code = hardware_mode == 0U ? 0x91U : 0x99U;
                r.latch_after = register_r14;
            }
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
