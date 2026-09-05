/* Object-state routing head recovered from i960 0x7a3e0-0x7a438. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_route_outcome {
    RECOVERED_ROUTE_A = 0U,
    RECOVERED_ROUTE_C = 1U,
    RECOVERED_ROUTE_RATIO = 2U,
    RECOVERED_ROUTE_D = 3U
};

struct recovered_route_plan {
    u32 outcome;
    u32 mode_value;
    u32 callee;
};

void recovered_route_plan(u32 own_state, u32 peer_state,
                          struct recovered_route_plan *plan)
{
    /* All arms test equality, so operand order needs no disambiguation:
     * the own==8 arm runs before the peer arms, and own==3 falls into
     * the ratio path only after the peer arms miss. */
    if (own_state == 8U) {
        plan->outcome = RECOVERED_ROUTE_A;
        plan->mode_value = 11U;
        plan->callee = 0x00078790U;
    } else if (peer_state == 0U || peer_state == 3U) {
        plan->outcome = RECOVERED_ROUTE_C;
        plan->mode_value = 9U;
        plan->callee = 0x0007a9f0U;
    } else if (own_state == 1U || own_state == 3U || own_state == 4U
            || own_state == 5U) {
        plan->outcome = RECOVERED_ROUTE_RATIO;
        plan->mode_value = 0U;
        plan->callee = 0U;
    } else {
        plan->outcome = RECOVERED_ROUTE_D;
        plan->mode_value = 0U;
        plan->callee = 0U;
    }
}
