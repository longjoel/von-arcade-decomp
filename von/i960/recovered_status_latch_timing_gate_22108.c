/* Timing/status gate recovered from i960 0x22108-0x221b4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_timing_gate_route {
    RECOVERED_STATUS_LATCH_TIMING_EXIT_223FC = 0,
    RECOVERED_STATUS_LATCH_TIMING_NEXT_221B8 = 1,
    RECOVERED_STATUS_LATCH_TIMING_ADMITTED = 2
};

struct recovered_status_latch_timing_gate_plan {
    u32 route;
    u32 status_mode;
    u32 latch;
    u32 compare_value;
    u32 base_54;
    u32 base_58;
    u32 raw_timing;
    u32 timing_after;
    u32 word_4c_before;
    u32 word_4c_after;
    u32 word_50_before;
    u32 word_50_after;
    u32 fallback_g14;
    u32 timing_address;
    u32 word_4c_address;
    u32 word_50_address;
    u32 continuation_target;
};

void recovered_status_latch_timing_gate_plan(
    u32 status_mode, u32 latch, u32 compare_base,
    u32 base_54, u32 base_58, u32 word_4c, u32 word_50,
    u32 fallback_g14,
    struct recovered_status_latch_timing_gate_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_TIMING_EXIT_223FC;
    plan->status_mode = status_mode;
    plan->latch = latch;
    plan->compare_value = compare_base + 31U;
    plan->base_54 = base_54;
    plan->base_58 = base_58;
    plan->raw_timing = 0U;
    plan->timing_after = fallback_g14;
    plan->word_4c_before = word_4c;
    plan->word_4c_after = word_4c;
    plan->word_50_before = word_50;
    plan->word_50_after = word_50;
    plan->fallback_g14 = fallback_g14;
    plan->timing_address = 0x00504cd0U;
    plan->word_4c_address = 0x00504cd4U;
    plan->word_50_address = 0x00504cd8U;
    plan->continuation_target = 0x000223fcU;

    if (status_mode == 2U) {
        return;
    }
    if (latch != plan->compare_value) {
        plan->route = RECOVERED_STATUS_LATCH_TIMING_NEXT_221B8;
        plan->continuation_target = 0x000221b8U;
        return;
    }

    plan->route = RECOVERED_STATUS_LATCH_TIMING_ADMITTED;
    if (base_54 != 0U) {
        plan->raw_timing = (base_58 * 1000U) / base_54;
        plan->timing_after = ((int32_t)plan->raw_timing < 0)
            ? fallback_g14 : plan->raw_timing;
    }
    plan->word_4c_after = ((int32_t)word_4c < 0) ? fallback_g14 : word_4c;
    plan->word_50_after = ((int32_t)word_50 < 0) ? fallback_g14 : word_50;
}
