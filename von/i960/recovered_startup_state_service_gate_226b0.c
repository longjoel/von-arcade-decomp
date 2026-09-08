/* Startup state-service gate recovered from i960 0x226b0-0x227a8. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_service_route_226b0 {
    RECOVERED_STATE_SET_SENTINEL = 0,
    RECOVERED_STATE_TRANSFER = 1,
    RECOVERED_STATE_CLEAR_FIELDS = 2,
    RECOVERED_STATE_NOOP = 3,
};

struct recovered_state_service_gate_226b0 {
    u32 route;
    int32_t counter_minus_ten;
    u32 sentinel_value;
    u32 transfer_source;
    u32 transfer_destination;
    u32 transfer_width;
    u32 transfer_height;
    u32 cleared_field_count;
    u32 counter_incremented;
};

void recovered_startup_state_service_gate_226b0(
    u32 service_counter, struct recovered_state_service_gate_226b0 *out)
{
    int32_t adjusted = (int32_t)service_counter - 10;

    out->counter_minus_ten = adjusted;
    out->sentinel_value = 0x8000U;
    out->transfer_source = 0x021fd49d0U;
    out->transfer_destination = 0x01004000U;
    out->transfer_width = 48U;
    out->transfer_height = 2U;
    out->cleared_field_count = 0U;
    if (adjusted <= 0) {
        out->route = RECOVERED_STATE_SET_SENTINEL;
    } else if (adjusted == 1) {
        out->route = RECOVERED_STATE_TRANSFER;
    } else if (adjusted == 2) {
        out->route = RECOVERED_STATE_CLEAR_FIELDS;
        out->cleared_field_count = 2U;
    } else {
        out->route = RECOVERED_STATE_NOOP;
    }
    out->counter_incremented = 1U;
}
