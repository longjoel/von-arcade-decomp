/* Converted-threshold/status dispatch recovered from i960 0x7f364-0x7f448. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_threshold_status_dispatch_7f364_plan {
    u32 current_status;
    u32 normalized_index;
    u32 below_converted_threshold;
    u32 control_value;
    u32 callback_gate;
    u32 threshold_gate_passed;
    u32 table_target;
    u32 published_status;
    u32 control_destination;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 target;
};

void recovered_state31_threshold_status_dispatch_7f364(
    u32 current_status, u32 below_converted_threshold, u32 control_value,
    u32 callback_gate, u32 related_pointer,
    struct recovered_state31_threshold_status_dispatch_7f364_plan *plan)
{
    static const u32 targets[12] = {
        0x0007f3dcU, 0x0007f404U, 0x0007f40cU, 0x0007f41cU,
        0x0007f428U, 0x0007f428U, 0x0007f428U, 0x0007f428U,
        0x0007f428U, 0x0007f428U, 0x0007f3ecU, 0x0007f3f4U
    };
    const u32 index = current_status - 8U;
    u32 published = current_status;
    u32 target = 0x0007f428U;

    if (index <= 11U) {
        target = targets[index];
        if (index <= 3U)
            published = index + 1U;
        else if (index == 10U)
            published = 2U;
        else if (index == 11U)
            published = 3U;
    }

    plan->current_status = current_status;
    plan->normalized_index = index;
    plan->below_converted_threshold = below_converted_threshold ? 1U : 0U;
    plan->control_value = control_value;
    plan->callback_gate = callback_gate;
    plan->threshold_gate_passed = plan->below_converted_threshold;
    plan->table_target = target;
    plan->published_status = published;
    plan->control_destination = 0x00504da0U;
    plan->callback_target = plan->below_converted_threshold && callback_gate == 1U
                                ? 0x00079050U : 0U;
    plan->callback_argument = plan->callback_target ? related_pointer : 0U;
    plan->action_destination = plan->below_converted_threshold ? 0x00504db8U : 0U;
    plan->action_value = plan->below_converted_threshold ? 30U : 0U;
    plan->target = plan->below_converted_threshold ? 0x0007f448U : 0x0007f448U;
}
