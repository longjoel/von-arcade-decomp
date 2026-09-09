/* Post-service math response/publication gate from i960 0x8fb0c-0x8fb2c. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_post_response_gate_8fb0c_input {
    recovered_u32 state_flag;
    recovered_u32 frame_readback;
    recovered_u32 fifo_response;
};

struct recovered_geometry_diagnostic_math_post_response_gate_8fb0c_plan {
    recovered_u32 frame_readback;
    recovered_u32 published_address;
    recovered_u32 published_value;
    recovered_u32 fifo_address;
    recovered_u32 fifo_response;
    recovered_u32 selected_target;
};

void recovered_geometry_diagnostic_math_post_response_gate_8fb0c(
    const struct recovered_geometry_diagnostic_math_post_response_gate_8fb0c_input *input,
    struct recovered_geometry_diagnostic_math_post_response_gate_8fb0c_plan *plan)
{
    plan->frame_readback = input->frame_readback;
    plan->published_address = 0x801008U;
    plan->published_value = input->frame_readback + 0x34U;
    plan->fifo_address = 0x884000U;
    plan->fifo_response = input->fifo_response;
    plan->selected_target = input->state_flag != 0U ? 0x8fb84U : 0x8fb30U;
}
