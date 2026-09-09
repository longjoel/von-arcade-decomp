/* Math-packet response/publication handoff from i960 0x8f910-0x8f928. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_response_handoff_8f910_input {
    recovered_u32 frame_readback;
    recovered_u32 fifo_response;
};

struct recovered_geometry_diagnostic_math_response_handoff_8f910_plan {
    recovered_u32 frame_readback;
    recovered_u32 published_address;
    recovered_u32 published_value;
    recovered_u32 fifo_address;
    recovered_u32 fifo_response;
    recovered_u32 next_packet_entry;
};

void recovered_geometry_diagnostic_math_response_handoff_8f910(
    const struct recovered_geometry_diagnostic_math_response_handoff_8f910_input *input,
    struct recovered_geometry_diagnostic_math_response_handoff_8f910_plan *plan)
{
    plan->frame_readback = input->frame_readback;
    plan->published_address = 0x801008U;
    plan->published_value = input->frame_readback + 0x34U;
    plan->fifo_address = 0x884000U;
    plan->fifo_response = input->fifo_response;
    plan->next_packet_entry = 0x8f928U;
}
