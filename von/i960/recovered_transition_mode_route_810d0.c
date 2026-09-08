/* Transition mode route recovered from i960 0x810d0-0x811b4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_mode_route_810d0 {
    u32 accepted;
    u32 mode_gate_used;
    u32 status_504d94;
    u32 status_504db8;
    u32 status_504d9c;
    u32 value_504da0;
    u32 secondary_dispatch;
};

/* Models the complete successful prefix; the dispatcher call is represented
 * as a plan flag because its ABI and side effects are modeled separately. */
struct recovered_transition_mode_route_810d0
recovered_transition_mode_route_810d0(
    int32_t counter_509b2c, uint16_t related_172, float current_timing,
    u32 mode_504e50, u32 object_state, u32 related_state)
{
    struct recovered_transition_mode_route_810d0 out = {
        0U, 0U, 0U, 0U, 0U, 0U, 0U
    };
    const u32 normalized_172 = (u32)related_172 << 16;

    if (counter_509b2c <= 0x1f3 || normalized_172 < 0x150000U ||
        normalized_172 > 0x190000U)
        return out;
    if (current_timing <= 0.0f) {
        out.mode_gate_used = 1U;
        if ((mode_504e50 & (1U << 3)) == 0U)
            return out;
    }
    if ((object_state != 1U && object_state != 5U) ||
        related_state == 1U || related_state == 5U ||
        related_state == 6U || related_state == 7U)
        return out;
    out.accepted = 1U;
    out.status_504d94 = 7U;
    out.status_504db8 = 30U;
    out.status_504d9c = 2U;
    out.value_504da0 = 0x64U;
    out.secondary_dispatch = 1U;
    return out;
}
