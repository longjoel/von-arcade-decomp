/* Post-state dispatch gate recovered from i960 0x9ddac-0x9de44. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_post_state_gate_plan {
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word;
    int32_t countdown[3];
    u32 countdown_address[3];
    u32 frame_value;
    u32 gate_before;
    u32 gate_after;
    u32 startup_call;
    u32 startup_argument;
};

void recovered_geometry_post_state_gate_plan(
    u32 frame_value, u32 gate_before, const int32_t countdown[3],
    struct recovered_geometry_post_state_gate_plan *plan)
{
    static const u32 addresses[3] = {
        0x00562c9cU, 0x00562ca0U, 0x00562ca4U,
    };
    plan->fifo_address = 0x00884000U;
    plan->fifo_word_count = 1U;
    plan->fifo_word = 6U;
    plan->frame_value = frame_value;
    plan->gate_before = gate_before;
    plan->gate_after = gate_before;
    plan->startup_call = 0U;
    plan->startup_argument = 0x114cU;
    for (u32 i = 0; i != 3U; ++i) {
        plan->countdown[i] = countdown[i];
        plan->countdown_address[i] = addresses[i];
    }

    if (gate_before != 0U) {
        plan->gate_after = frame_value;
        return;
    }

    if (countdown[0] != 30 || countdown[1] != 30 || countdown[2] != 30) {
        plan->gate_after = frame_value;
        return;
    }

    plan->startup_call = 1U;
    plan->gate_after = 1U;
}
