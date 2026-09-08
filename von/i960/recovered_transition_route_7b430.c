/* Exact dispatch prefix recovered from i960 0x7b430-0x7b46c. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_route_7b430_kind {
    RECOVERED_TRANSITION_7B430_TIMING = 0,
    RECOVERED_TRANSITION_7B430_PACKET = 1,
};

struct recovered_transition_route_7b430_plan {
    u32 route;
    u32 calls_timing_variant;
    u32 timing_target;
    u32 packet_target;
    u32 packet_table_base;
    u32 selector;
    u32 object_state_offset;
    u32 related_pointer_offset;
};

void recovered_transition_route_7b430(
    u32 selector_504e20, u32 object_state,
    struct recovered_transition_route_7b430_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7B430_PACKET;
    plan->calls_timing_variant = 0U;
    plan->timing_target = 0U;
    plan->packet_target = 0x0007b46cU;
    plan->packet_table_base = 0x00505060U;
    plan->selector = selector_504e20;
    plan->object_state_offset = 0x64U;
    plan->related_pointer_offset = 0x74U;

    /* The equality arm is the only path that dispatches on object state. */
    if (selector_504e20 == 0xffffffffU) {
        plan->route = RECOVERED_TRANSITION_7B430_TIMING;
        plan->calls_timing_variant = 1U;
        plan->timing_target = object_state == 2U || object_state == 7U
            ? 0x00078740U : 0x000786d0U;
    }
}
