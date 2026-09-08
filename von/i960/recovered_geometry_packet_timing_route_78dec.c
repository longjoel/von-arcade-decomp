/* Geometry packet timing route recovered from i960 0x78dec-0x79040. */

#include <stdint.h>

enum recovered_geometry_packet_timing_route_78dec {
    RECOVERED_GEOMETRY_PACKET_PRIMARY_OVERRIDE = 0,
    RECOVERED_GEOMETRY_PACKET_ACTION10 = 1,
    RECOVERED_GEOMETRY_PACKET_ACTION5 = 2,
    RECOVERED_GEOMETRY_PACKET_SELECTOR_FALLBACK = 3,
    RECOVERED_GEOMETRY_PACKET_CONTROL_OVERRIDE = 4
};

struct recovered_geometry_packet_timing_plan_78dec {
    enum recovered_geometry_packet_timing_route_78dec route;
    uint32_t status;
    uint32_t transition;
    uint32_t action;
    uint32_t action_target;
    uint32_t selector_value;
};

/*
 * primary_passed and secondary_route stand for the response/FPU comparisons
 * at 0x78eec and 0x78f7c-0x78f94.  Their producers are intentionally outside
 * this model; the branch bodies and literal writes are exact.
 */
struct recovered_geometry_packet_timing_plan_78dec
recovered_geometry_packet_timing_route_78dec(
    uint32_t primary_passed,
    uint32_t secondary_route,
    uint32_t object_state,
    uint32_t mode_control_504e28,
    uint32_t related_selector,
    uint32_t caller_g14)
{
    struct recovered_geometry_packet_timing_plan_78dec plan = {
        RECOVERED_GEOMETRY_PACKET_PRIMARY_OVERRIDE, 0U, 0U, 0U, 0U, 0U
    };

    if (primary_passed == 0U) {
        plan.route = RECOVERED_GEOMETRY_PACKET_PRIMARY_OVERRIDE;
        plan.status = 1U;
        plan.transition = object_state == 4U ? 3U : 2U;
        if (mode_control_504e28 == 1U && object_state == 4U) {
            plan.selector_value = 23U;
        } else {
            plan.selector_value = caller_g14;
        }
        plan.action = 25U;
        return plan;
    }

    if (secondary_route == 1U) {
        plan.route = RECOVERED_GEOMETRY_PACKET_ACTION10;
        plan.action = 10U;
        plan.action_target = 0x00078408U;
        return plan;
    }
    if (secondary_route == 2U) {
        plan.route = RECOVERED_GEOMETRY_PACKET_ACTION5;
        plan.action = 5U;
        plan.action_target = 0x000783c8U;
        return plan;
    }

    plan.route = RECOVERED_GEOMETRY_PACKET_SELECTOR_FALLBACK;
    plan.action = 5U;
    plan.selector_value = related_selector <= 3U ? 13U : 12U;
    if (related_selector >= 8U) {
        plan.route = RECOVERED_GEOMETRY_PACKET_CONTROL_OVERRIDE;
        plan.status = 1U;
        plan.transition = object_state == 4U ? 3U : 2U;
        plan.selector_value = mode_control_504e28 == 1U && object_state == 4U
            ? 23U : caller_g14;
        plan.action = 25U;
    }
    return plan;
}
