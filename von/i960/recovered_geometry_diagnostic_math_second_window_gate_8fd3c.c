/* Second math-window response/publication gate from i960 0x8fd3c-0x8fd64. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_second_window_gate_8fd3c_input {
    recovered_u32 state_flag;
    recovered_u32 frame_readback;
    recovered_u32 fifo_response;
};

struct recovered_geometry_diagnostic_math_second_window_gate_8fd3c_plan {
    recovered_u32 frame_readback;
    recovered_u32 published_address;
    recovered_u32 published_value;
    recovered_u32 fifo_address;
    recovered_u32 fifo_response;
    recovered_u32 selected_target;
};

void recovered_geometry_diagnostic_math_second_window_gate_8fd3c(
    const struct recovered_geometry_diagnostic_math_second_window_gate_8fd3c_input *input,
    struct recovered_geometry_diagnostic_math_second_window_gate_8fd3c_plan *plan)
{
    plan->frame_readback = input->frame_readback;
    plan->published_address = 0x801008U;
    plan->published_value = input->frame_readback + 0x34U;
    plan->fifo_address = 0x884000U;
    plan->fifo_response = input->fifo_response;
    plan->selected_target = input->state_flag != 0U ? 0x8fda4U : 0x8fd68U;
}
