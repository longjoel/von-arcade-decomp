/* Geometry-board update gate recovered from i960 0x9d170-0x9d1ec. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_board_update_gate_plan {
    u32 state_word;
    u32 state_bit0;
    u32 control_address;
    u32 control_value;
    u32 frame_address[2];
    u32 frame_value;
    u32 fifo_address;
    u32 update_enabled;
    u32 prefix_count;
    u32 prefix[5];
};

void recovered_geometry_board_update_gate_plan(
    u32 state_word, struct recovered_geometry_board_update_gate_plan *plan)
{
    plan->state_word = state_word;
    plan->state_bit0 = state_word & 1U;
    plan->control_address = 0x00800090U;
    plan->control_value = 0x909U;
    plan->frame_address[0] = 0x00804000U;
    plan->frame_address[1] = 0x00804004U;
    plan->frame_value = 0x44160000U;
    plan->fifo_address = 0x00884000U;
    plan->update_enabled = plan->state_bit0;
    plan->prefix_count = plan->update_enabled ? 5U : 0U;

    if (!plan->update_enabled)
        return;

    plan->prefix[0] = 5U;
    plan->prefix[1] = 55U; /* addo 31,24 */
    plan->prefix[2] = 0x3e23d70aU;
    plan->prefix[3] = 0xbdf92c60U;
    plan->prefix[4] = 0x3f800000U;
}
