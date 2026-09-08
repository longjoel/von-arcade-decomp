/* Bounded entry gate and dispatch table for i960 0x74860. */

#include <stdint.h>

struct recovered_match_status_transition_gate_plan {
    uint32_t status_address;
    uint32_t object_pointer_offset;
    uint32_t setup_helper;
    uint32_t mode_address;
    uint32_t mode_required;
    uint32_t status_flag_address;
    uint32_t status_flag_required;
    uint32_t window_low;
    uint32_t window_high;
    uint32_t fallback_pair_address;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[23];
    uint32_t external_route;
};

void recovered_match_status_transition_gate_plan(
    struct recovered_match_status_transition_gate_plan *plan)
{
    static const uint32_t targets[23] = {
        0x00074d20U, 0x000749dcU, 0x00074a30U, 0x00074a6cU,
        0x00074aecU, 0x00074afcU, 0x00074b10U, 0x00074b20U,
        0x00074b30U, 0x00074b44U, 0x00074c24U, 0x00074c38U,
        0x00074c50U, 0x00074b54U, 0x00074b80U, 0x00074bb0U,
        0x00074bdcU, 0x00074becU, 0x00074c00U, 0x00074c6cU,
        0x00074c88U, 0x00074cc0U, 0x00074d20U
    };
    uint32_t index;

    plan->status_address = 0x00504e42U;
    plan->object_pointer_offset = 0x74U;
    plan->setup_helper = 0x0007d1f0U;
    plan->mode_address = 0x00504e28U;
    plan->mode_required = 1U;
    plan->status_flag_address = 0x00504d98U;
    plan->status_flag_required = 1U;
    plan->window_low = 0x150000U;
    plan->window_high = 0x190000U;
    plan->fallback_pair_address = 0x00504d90U;
    plan->dispatch_table = 0x0007497cU;
    plan->dispatch_count = 23U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->external_route = 0x000854a0U;
}

uint32_t recovered_match_status_transition_window(uint32_t shifted_value)
{
    return shifted_value >= 0x150000U && shifted_value <= 0x190000U;
}
