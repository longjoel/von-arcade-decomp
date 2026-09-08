/* State-3 selector body recovered from i960 0x7d404-0x7d4c4. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_selector_body_3_7d404_route {
    RECOVERED_STATE_3_7D404_SELECTOR_FALLBACK = 0,
    RECOVERED_STATE_3_7D404_SELECTOR_OVERRIDE = 1,
    RECOVERED_STATE_3_7D404_SHARED_TARGET = 2,
};

struct recovered_state_selector_body_3_7d404_plan {
    u32 route;
    u32 target;
    u32 writes_selector;
    u32 selector_value;
};

/*
 * remainder_after_299 abstracts (0x5024e8 % 600) > 299.  outer_gate_passed
 * represents the combined 0x504e2c/0x504e28/mode-bit-2 predicate before the
 * coordinate comparison.  coordinate_override_passed represents the
 * signed-difference and related-selector checks that reach 0x7d4b4.
 */
void recovered_state_selector_body_3_7d404(
    u32 remainder_after_299, u32 outer_gate_passed,
    u32 coordinate_override_passed, u32 g3, u32 g13,
    u32 control_504dc8, u32 mode_bits,
    struct recovered_state_selector_body_3_7d404_plan *plan)
{
    plan->route = RECOVERED_STATE_3_7D404_SELECTOR_FALLBACK;
    plan->target = 0x0007d644U;
    plan->writes_selector = 0U;
    plan->selector_value = 0U;

    if (remainder_after_299 == 0U)
        return;

    if (outer_gate_passed != 0U && coordinate_override_passed != 0U) {
        plan->route = RECOVERED_STATE_3_7D404_SELECTOR_OVERRIDE;
        plan->target = 0x0007d4b4U;
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
        return;
    }

    plan->route = RECOVERED_STATE_3_7D404_SHARED_TARGET;
    if ((g3 != 0U || g13 != 0U) && control_504dc8 == 1U &&
        (mode_bits & (1U << 1)) != 0U)
        plan->target = 0x0007d5f4U;
    else
        plan->target = 0x0007d654U;
}
