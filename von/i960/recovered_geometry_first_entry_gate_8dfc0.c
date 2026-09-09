/* Entry gate recovered from i960 0x8dfc0-0x8e000. */
#include "recovered_common.h"

struct recovered_geometry_first_entry_gate_8dfc0_input {
    recovered_u32 object_pointer;
    recovered_u32 object_count;
};

struct recovered_geometry_first_entry_gate_8dfc0_plan {
    recovered_u32 packet_body_admitted;
    recovered_u32 early_return;
};

void recovered_geometry_first_entry_gate_8dfc0(
    const struct recovered_geometry_first_entry_gate_8dfc0_input *input,
    struct recovered_geometry_first_entry_gate_8dfc0_plan *plan)
{
    plan->packet_body_admitted =
        (input->object_pointer != 0U && input->object_count != 0U) ? 1U : 0U;
    plan->early_return = plan->packet_body_admitted == 0U ? 1U : 0U;
}
