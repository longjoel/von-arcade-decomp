/* Pure phase/poll plan for the geometry handoff at i960 0x28de8-0x28e7c. */
#include "recovered_common.h"

struct recovered_geometry_frame_plan_28de8 {
    recovered_u32 read_start;
    recovered_u32 expected_status_bit;
    recovered_u32 completed;
    recovered_u32 next_phase;
    recovered_u32 write_start;
};

void recovered_geometry_frame_plan_28de8(
    recovered_u32 prior_phase, recovered_u32 status_before,
    recovered_u32 status_after, recovered_u32 *spins,
    struct recovered_geometry_frame_plan_28de8 *result)
{
    recovered_u32 phase = prior_phase & 1U;
    recovered_u32 expected = status_before & 4U;
    result->read_start = phase ? 0x10000U : 0U;
    result->expected_status_bit = expected;
    result->completed = ((status_after & 4U) != expected);
    if (!result->completed && *spins < 0x1000U)
        *spins = 0x1000U;
    result->next_phase = (phase + 1U) & 1U;
    result->write_start = result->next_phase ? 0x10000U : 0U;
}
