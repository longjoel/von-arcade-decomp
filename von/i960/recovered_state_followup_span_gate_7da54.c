/* Alternate span gate recovered from i960 0x7da54-0x7da80. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_state_followup_span_gate_7da54_plan {
    s32 caller_r17;
    s32 divisor;
    s32 frame_quotient;
    s32 frame_target;
    s32 target_difference;
    u32 continues_to_dispatch;
    u32 falls_to_7db54;
};

struct recovered_state_followup_span_gate_7da54_plan
recovered_state_followup_span_gate_7da54(
    s32 value_503a14, s32 value_503a18, s32 caller_r17, u32 counter)
{
    struct recovered_state_followup_span_gate_7da54_plan out;

    out.caller_r17 = caller_r17;
    out.divisor = caller_r17 + 31;
    out.frame_quotient = value_503a14 / out.divisor;
    out.frame_target = out.frame_quotient + 1;
    out.target_difference = value_503a18 - out.frame_target;
    out.continues_to_dispatch = out.target_difference >= 25 ? 1U : 0U;
    out.falls_to_7db54 = out.continues_to_dispatch == 0U && counter > 24U
        ? 1U : 0U;
    return out;
}
