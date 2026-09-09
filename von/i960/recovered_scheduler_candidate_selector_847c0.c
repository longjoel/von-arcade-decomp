/* Candidate selector recovered from i960 0x847c0-0x848cc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_candidate_selector_847c0 {
    u32 selected_result;
    u32 selected_index;
    u32 last_fifo_result;
    u32 fifo_packets;
    u32 early_zero_gate;
};

static u32 early_zero_gate_847c0(int32_t object_state_172,
                                 u32 object_field_64, u32 mode_504e30,
                                 int32_t related_state_172,
                                 int32_t related_field_170,
                                 u32 control_504dc8)
{
    if (object_state_172 > 1)
        return object_state_172 <= 13 ? 1U : 0U;
    if (object_field_64 == 0U)
        return 1U;
    if (object_field_64 != 6U || (mode_504e30 & (1U << 5)) == 0U)
        return 0U;
    if (related_state_172 != 1 && related_state_172 != 14)
        return 0U;
    return related_field_170 == 6 && control_504dc8 == 1U ? 1U : 0U;
}

struct recovered_scheduler_candidate_selector_847c0
recovered_scheduler_candidate_selector_847c0(
    int32_t object_state_172, u32 object_field_64, u32 mode_504e30,
    int32_t related_state_172, int32_t related_field_170,
    u32 control_504dc8, const int32_t classifier_results[32],
    const u32 delta_g6[32], const u32 delta_g4[32],
    const u32 fifo_results[32])
{
    u32 early_zero_gate = early_zero_gate_847c0(
        object_state_172, object_field_64, mode_504e30,
        related_state_172, related_field_170, control_504dc8);
    struct recovered_scheduler_candidate_selector_847c0 out = {
        7U, 0xffffffffU, 0U, 0U, early_zero_gate != 0U ? 1U : 0U
    };
    u32 index;

    (void)delta_g6;
    (void)delta_g4;
    if (early_zero_gate != 0U) {
        out.selected_result = 0U;
        return out;
    }
    for (index = 0U; index < 32U; ++index) {
        int32_t result = classifier_results[index];

        if (result <= 5 && result < (int32_t)out.selected_result) {
            out.selected_result = (u32)result;
            out.selected_index = index;
            out.last_fifo_result = fifo_results[index] & 0xffffU;
            out.fifo_packets += 1U;
        }
    }
    return out;
}
