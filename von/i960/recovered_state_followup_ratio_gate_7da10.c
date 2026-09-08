/* Ratio gate recovered from i960 0x7da10-0x7da54. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_ratio_gate_7da10_plan {
    u32 object_1d0_zero_extended;
    u32 object_1d8_zero_extended;
    float ratio;
    float threshold;
    u32 continues_to_dispatch;
};

struct recovered_state_followup_ratio_gate_7da10_plan
recovered_state_followup_ratio_gate_7da10(uint16_t object_1d0,
                                          uint16_t object_1d8)
{
    struct recovered_state_followup_ratio_gate_7da10_plan out;

    out.object_1d0_zero_extended = (u32)object_1d0;
    out.object_1d8_zero_extended = (u32)object_1d8;
    out.ratio = (float)object_1d0 / (float)object_1d8;
    out.threshold = 0.4F;
    out.continues_to_dispatch = out.ratio <= out.threshold ? 1U : 0U;
    return out;
}
