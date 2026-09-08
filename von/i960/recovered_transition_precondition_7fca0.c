/* Transition precondition recovered from i960 0x7fca0-0x7fd24. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_precondition_route_7fca0 {
    RECOVERED_TRANSITION_PRECONDITION_REJECT = 0,
    RECOVERED_TRANSITION_PRECONDITION_RANGE = 1,
    RECOVERED_TRANSITION_PRECONDITION_STATE = 2
};

struct recovered_transition_precondition_7fca0 {
    enum recovered_transition_precondition_route_7fca0 route;
    u32 accepted;
    u32 normalized_172;
};

/*
 * ldos followed by shlo16/shri16 is a zero-extension of the low halfword.
 * The first arm is entered only for 0x10000 < value <= 0xd0000.  The
 * alternate arm is selected by the exact state tuple visible at 0x7fcd0.
 */
struct recovered_transition_precondition_7fca0
recovered_transition_precondition_7fca0(
    uint16_t related_172, u32 related_state64, u32 related_state170)
{
    struct recovered_transition_precondition_7fca0 out = {
        RECOVERED_TRANSITION_PRECONDITION_REJECT, 0U,
        (u32)related_172 << 16
    };

    if (out.normalized_172 > 0x10000U &&
        out.normalized_172 <= 0xd0000U) {
        out.route = RECOVERED_TRANSITION_PRECONDITION_RANGE;
        out.accepted = 1U;
        return out;
    }
    if ((related_state64 == 0U || related_state64 == 6U) &&
        (related_172 == 1U || related_172 == 14U) &&
        related_state170 == 6U) {
        out.route = RECOVERED_TRANSITION_PRECONDITION_STATE;
        out.accepted = 1U;
    }
    return out;
}
