/* Result publication handoff recovered from i960 0x7fabc-0x7fac8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_result_publication_handoff_7fabc_plan {
    u32 result_value;
    u32 status_destination;
    u32 published_status;
    u32 target;
};

void recovered_transition_result_publication_handoff_7fabc(
    u32 result_value,
    struct recovered_transition_result_publication_handoff_7fabc_plan *plan)
{
    plan->result_value = result_value;
    plan->status_destination = 0x00504d94U;
    plan->published_status = result_value;
    plan->target = 0x0007fc84U;
}
