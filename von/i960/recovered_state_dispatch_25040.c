/* Explicit state-dispatch prefix recovered from i960 0x25040-0x25160. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_dispatch_route_25040 {
    RECOVERED_STATE_ROUTE_DEFAULT = 0,
    RECOVERED_STATE_ROUTE_44390 = 1,
    RECOVERED_STATE_ROUTE_88208 = 2,
    RECOVERED_STATE_ROUTE_88258 = 3,
    RECOVERED_STATE_ROUTE_72C10 = 4,
    RECOVERED_STATE_ROUTE_D5A58 = 5,
    RECOVERED_STATE_ROUTE_STATE6_RESET = 6,
    RECOVERED_STATE_ROUTE_NIBBLE_TABLE = 7,
};

struct recovered_state_dispatch_25040 {
    u32 route;
    u32 record_status_copied;
    u32 record_work_copied;
    u32 record_halfword_copied;
    u32 state6_record_cleared;
    u32 state6_association_cleared;
    u32 state6_work_cleared;
    u32 common_tail_present;
};

void recovered_state_dispatch_25040(
    u32 service_counter, u32 record_state,
    struct recovered_state_dispatch_25040 *out)
{
    out->record_status_copied = 1U;
    out->record_work_copied = 1U;
    out->record_halfword_copied = 1U;
    out->state6_record_cleared = 0U;
    out->state6_association_cleared = 0U;
    out->state6_work_cleared = 0U;
    out->common_tail_present = 1U;

    if (service_counter == 12U) {
        out->route = (record_state == 0U || record_state == 1U)
            ? RECOVERED_STATE_ROUTE_44390 : RECOVERED_STATE_ROUTE_DEFAULT;
    } else if (service_counter == 20U) {
        if (record_state == 0U)
            out->route = RECOVERED_STATE_ROUTE_88208;
        else if (record_state == 1U)
            out->route = RECOVERED_STATE_ROUTE_88258;
        else
            out->route = RECOVERED_STATE_ROUTE_DEFAULT;
    } else if (record_state == 1U) {
        out->route = RECOVERED_STATE_ROUTE_72C10;
    } else if (record_state == 5U) {
        out->route = RECOVERED_STATE_ROUTE_D5A58;
    } else if (record_state == 6U) {
        out->route = RECOVERED_STATE_ROUTE_STATE6_RESET;
        out->state6_record_cleared = 1U;
        out->state6_association_cleared = 1U;
        out->state6_work_cleared = 1U;
    } else {
        out->route = RECOVERED_STATE_ROUTE_NIBBLE_TABLE;
    }
}
