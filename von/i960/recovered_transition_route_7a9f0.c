/* Exact entry gate recovered from i960 0x7a9f0-0x7aa30. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_route_7a9f0_kind {
    RECOVERED_TRANSITION_ROUTE_TIMING = 0,
    RECOVERED_TRANSITION_ROUTE_PACKET = 1,
};

struct recovered_transition_route_7a9f0_plan {
    u32 initial_state_504db8;
    u32 route;
    u32 calls_timing_variant;
    u32 timing_target;
    u32 packet_threshold;
    u32 record_selector;
    u32 table_base;
    u32 packet_target;
    u32 related_field_offset;
};

void recovered_transition_route_7a9f0(
    u32 record_selector, u32 timing_value,
    struct recovered_transition_route_7a9f0_plan *plan)
{
    plan->initial_state_504db8 = 10U;
    plan->packet_threshold = 99U;
    plan->record_selector = record_selector;
    plan->table_base = 0x00505060U;
    plan->packet_target = 0x0007aa30U;
    plan->related_field_offset = 0x74U;
    plan->timing_target = 0x000786d0U;

    /* 0x504e24 == -1 is the sentinel; cmpibg selects packet work only
     * when the timing value is strictly above 99. */
    if (record_selector == 0xffffffffU || timing_value <= 99U) {
        plan->route = RECOVERED_TRANSITION_ROUTE_TIMING;
        plan->calls_timing_variant = 1U;
    } else {
        plan->route = RECOVERED_TRANSITION_ROUTE_PACKET;
        plan->calls_timing_variant = 0U;
    }
}
