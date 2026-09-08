/* Bounded per-frame prefix and dispatch contract at i960 0x371e0. */

#include <stdint.h>

struct recovered_geometry_frame_step_plan {
    uint32_t global_gate_address;
    uint32_t object_pointer_offset;
    uint32_t timer_offsets[2];
    uint32_t fixed_point_offsets[2];
    uint32_t phase_offset;
    uint32_t secondary_state_offset;
    uint32_t dispatch_table_address;
    uint32_t dispatch_helper_when_gated;
    uint32_t dispatch_helper_when_clear;
};

void recovered_geometry_frame_step_plan(
    struct recovered_geometry_frame_step_plan *plan)
{
    plan->global_gate_address = 0x00503a60U;
    plan->object_pointer_offset = 0x6cU;
    plan->timer_offsets[0] = 0x1dbU;
    plan->timer_offsets[1] = 0x1dcU;
    plan->fixed_point_offsets[0] = 0x32U;
    plan->fixed_point_offsets[1] = 0x34U;
    plan->phase_offset = 0x172U;
    plan->secondary_state_offset = 0x198U;
    plan->dispatch_table_address = 0x00037130U;
    plan->dispatch_helper_when_gated = 0x00025040U;
    plan->dispatch_helper_when_clear = 0x00024f98U;
}

uint8_t recovered_geometry_frame_timer_step(uint8_t timer)
{
    return timer == 0U ? 0U : (uint8_t)(timer - 1U);
}

/* The dispatch table is indexed by the signed halfword phase value. */
int32_t recovered_geometry_frame_phase_index(uint32_t phase_word)
{
    return (int32_t)(int16_t)(phase_word & 0xffffU);
}
