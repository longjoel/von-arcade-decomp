/* Bounded nested phase selector and dispatch table at i960 0x7539c. */

#include <stdint.h>

struct recovered_match_phase_selector_7539c_plan {
    uint32_t frame_source_offset;
    uint32_t frame_gate_subtract;
    uint32_t frame_gate_bound;
    uint32_t state_source_register;
    uint32_t state_gate;
    uint32_t status_source;
    uint32_t status_decrement;
    uint32_t status_lower_bound;
    uint32_t status_upper_bound;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[15];
    uint32_t reject_target;
    uint32_t first_arm;
    uint32_t last_arm;
};

void recovered_match_phase_selector_7539c_plan(
    struct recovered_match_phase_selector_7539c_plan *plan)
{
    static const uint32_t targets[15] = {
        0x00075404U, 0x00075cf8U, 0x00075cf8U, 0x00075cf8U,
        0x00075cf8U, 0x0007540cU, 0x00075cf8U, 0x00075414U,
        0x00075cf8U, 0x00075cf8U, 0x00075424U, 0x00075cf8U,
        0x00075cf8U, 0x0007542cU, 0x00075434U
    };
    uint32_t index;

    plan->frame_source_offset = 0x40U;
    plan->frame_gate_subtract = 2U;
    plan->frame_gate_bound = 5U;
    plan->state_source_register = 4U; /* r4 */
    plan->state_gate = 2U;
    plan->status_source = 0x00504d94U;
    plan->status_decrement = 1U;
    plan->status_lower_bound = 1U;
    plan->status_upper_bound = 14U;
    plan->dispatch_table = 0x000753c8U;
    plan->dispatch_count = 15U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->reject_target = 0x00075cf8U;
    plan->first_arm = 0x00075404U;
    plan->last_arm = 0x00075434U;
}

uint32_t recovered_match_phase_selector_index(uint32_t status)
{
    return status - 1U;
}
