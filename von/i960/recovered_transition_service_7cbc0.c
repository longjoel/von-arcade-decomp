/* Bounded transition service recovered from i960 0x7cbc0-0x7cc44. */

#include <stdint.h>

struct recovered_transition_service_7cbc0 {
    uint32_t route;
    uint32_t selector;
    uint32_t status;
    uint32_t transition;
    uint32_t action;
};

enum recovered_transition_service_route_7cbc0 {
    RECOVERED_TRANSITION_SERVICE_ACTION5 = 0,
    RECOVERED_TRANSITION_SERVICE_ACTION10 = 1
};

/*
 * timing_passed abstracts the compare at 0x7cbd4.  A clear result tail-calls
 * 0x783c8; the passed result selects the 0x72900 selector and publishes the
 * action-10 service state.  The selector table value remains an explicit
 * input because ROM-table provenance is outside this pure helper.
 */
void recovered_transition_service_7cbc0(
    uint32_t timing_passed,
    uint32_t control_504dc8,
    uint32_t object_state,
    uint32_t selector_table_value,
    struct recovered_transition_service_7cbc0 *out)
{
    out->route = RECOVERED_TRANSITION_SERVICE_ACTION5;
    out->selector = 0U;
    out->status = 0U;
    out->transition = 0U;
    out->action = 0U;

    if (timing_passed == 0U)
        return;

    out->route = RECOVERED_TRANSITION_SERVICE_ACTION10;
    out->selector = selector_table_value;
    out->action = 10U;
    if (control_504dc8 != 1U)
        return;

    out->status = 1U;
    out->transition = object_state == 4U ? 3U : 2U;
    out->action = 25U;
}
