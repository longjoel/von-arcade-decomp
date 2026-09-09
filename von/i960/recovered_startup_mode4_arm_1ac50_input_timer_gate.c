/* Slot-10 common-service timer/input gate recovered from i960 0x1ac50-0x1ac8c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 threshold_address, threshold_raw, threshold_signed;
    recovered_u32 timer_address, timer_raw, timer_signed;
    recovered_u32 shifted_threshold;
    recovered_u32 timer_nonpositive, timer_reaches_threshold;
    recovered_u32 controller_address, controller_word, controller_low_six;
    recovered_u32 controller_gate_open;
    recovered_u32 setup_helper, setup_call_count, setup_argument;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1ac50_input_timer_gate_result;

int recovered_startup_mode4_arm_1ac50_input_timer_gate(
    recovered_u32 threshold_raw, recovered_u32 timer_raw,
    recovered_u32 controller_word,
    recovered_startup_mode4_arm_1ac50_input_timer_gate_result *result)
{
    recovered_startup_mode4_arm_1ac50_input_timer_gate_result r = {0};
    int16_t threshold = (int16_t)(threshold_raw & 0xffffU);
    int16_t timer = (int16_t)(timer_raw & 0xffffU);
    r.threshold_address = 0x503ca8U;
    r.threshold_raw = threshold_raw;
    r.threshold_signed = (recovered_u32)(int32_t)threshold;
    r.timer_address = 0x503ca0U;
    r.timer_raw = timer_raw;
    r.timer_signed = (recovered_u32)(int32_t)timer;
    r.shifted_threshold = (recovered_u32)threshold >> 3U;
    r.timer_nonpositive = timer <= 0 ? 1U : 0U;
    /* The timer is loaded as a signed halfword.  Keep this predicate signed;
     * the separate nonpositive branch is evaluated before it in the listing. */
    r.timer_reaches_threshold = (int32_t)timer >= (int32_t)r.shifted_threshold ? 1U : 0U;
    r.controller_address = 0x5024e8U;
    r.controller_word = controller_word;
    r.controller_low_six = controller_word & 0x3fU;
    r.controller_gate_open = (timer > 0 && r.timer_reaches_threshold == 0U &&
                              r.controller_low_six == 0U) ? 1U : 0U;
    r.setup_helper = 0x2a4e0U;
    r.setup_argument = 0x1110U;
    r.setup_call_count = r.controller_gate_open;
    r.continuation = 0x1ac8cU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
