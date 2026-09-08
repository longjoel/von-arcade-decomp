/* Exact dispatch prefix recovered from i960 0x7bf10-0x7bf58. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_route_7bf10_kind {
    RECOVERED_TRANSITION_7BF10_TIMING = 0,
    RECOVERED_TRANSITION_7BF10_PACKET = 1,
};

struct recovered_transition_route_7bf10_plan {
    u32 route;
    u32 calls_timing_variant;
    u32 timing_target;
    u32 packet_target;
    u32 writes_504d84;
    u32 value_504d84;
    u32 packet_table_base;
    u32 selector;
    u32 object_state_offset;
    u32 related_pointer_offset;
};

void recovered_transition_route_7bf10(
    u32 selector_504e20, u32 object_state,
    struct recovered_transition_route_7bf10_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7BF10_PACKET;
    plan->calls_timing_variant = 0U;
    plan->timing_target = 0U;
    plan->packet_target = 0x0007bf58U;
    plan->writes_504d84 = 0U;
    plan->value_504d84 = 0U;
    plan->packet_table_base = 0x00505060U;
    plan->selector = selector_504e20;
    plan->object_state_offset = 0x64U;
    plan->related_pointer_offset = 0x74U;

    if (selector_504e20 == 0xffffffffU) {
        plan->route = RECOVERED_TRANSITION_7BF10_TIMING;
        plan->calls_timing_variant = 1U;
        plan->timing_target = object_state == 2U || object_state == 7U
            ? 0x00078740U : 0x000786d0U;
        plan->writes_504d84 = 1U;
        plan->value_504d84 = 1U;
    }
}
