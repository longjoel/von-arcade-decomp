/* Variant diagnostic response/publication gate from i960 0x8eaf4-0x8eb18. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_response_gate_8eaf4_input {
    recovered_u32 persistent_seed;
    recovered_u32 frame_readback;
    recovered_u32 fifo_response;
};

struct recovered_geometry_diagnostic_variant_response_gate_8eaf4_plan {
    recovered_u32 frame_readback;
    recovered_u32 published_address;
    recovered_u32 published_value;
    recovered_u32 fifo_address;
    recovered_u32 fifo_response;
    recovered_u32 selected_target;
};

void recovered_geometry_diagnostic_variant_response_gate_8eaf4(
    const struct recovered_geometry_diagnostic_variant_response_gate_8eaf4_input *input,
    struct recovered_geometry_diagnostic_variant_response_gate_8eaf4_plan *plan)
{
    plan->frame_readback = input->frame_readback;
    plan->published_address = 0x801008U;
    plan->published_value = input->frame_readback + 0x34U;
    plan->fifo_address = 0x884000U;
    plan->fifo_response = input->fifo_response;
    plan->selected_target = input->persistent_seed != 0U ? 0x8eb6cU : 0x8eb18U;
}
