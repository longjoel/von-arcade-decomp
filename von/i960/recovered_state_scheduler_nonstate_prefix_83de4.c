/* Non-state scheduler prefix recovered from i960 0x83de4-0x83e74. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_nonstate_prefix_83de4_route {
    RECOVERED_NONSTATE_83DE4_CALL_82800_TIMING = 0,
    RECOVERED_NONSTATE_83DE4_STATUS_18 = 1,
    RECOVERED_NONSTATE_83DE4_CALL_82800_REMAINDER = 2,
    RECOVERED_NONSTATE_83DE4_STATUS_25 = 3,
    RECOVERED_NONSTATE_83DE4_STATUS_34 = 4,
    RECOVERED_NONSTATE_83DE4_REMAINDER6_HANDOFF = 5
};

struct recovered_state_scheduler_nonstate_prefix_83de4 {
    enum recovered_state_scheduler_nonstate_prefix_83de4_route route;
    u32 status;
    u32 random_calls;
};

struct recovered_state_scheduler_nonstate_prefix_83de4
recovered_state_scheduler_nonstate_prefix_83de4(int32_t current_timing,
                                                int32_t negative_limit,
                                                int32_t random_value,
                                                u32 handler_status)
{
    struct recovered_state_scheduler_nonstate_prefix_83de4 out = {
        RECOVERED_NONSTATE_83DE4_STATUS_18, 18U, 0U
    };
    int32_t remainder_18;
    int32_t remainder_3;
    int32_t sign;
    int32_t evenized;

    if (current_timing < negative_limit) {
        out.route = RECOVERED_NONSTATE_83DE4_CALL_82800_TIMING;
        out.status = handler_status;
        return out;
    }
    if (current_timing < 0)
        return out;

    out.random_calls = 1U;
    remainder_18 = random_value % 18;
    if (remainder_18 <= 11) {
        out.route = RECOVERED_NONSTATE_83DE4_REMAINDER6_HANDOFF;
        out.status = 0U;
        return out;
    }

    remainder_3 = remainder_18 % 3;
    if (remainder_3 == 2) {
        out.route = RECOVERED_NONSTATE_83DE4_CALL_82800_REMAINDER;
        out.status = handler_status;
        return out;
    }

    sign = remainder_18 >> 31;
    evenized = (remainder_18 + sign) & ~1;
    if (evenized == remainder_18) {
        out.route = RECOVERED_NONSTATE_83DE4_STATUS_25;
        out.status = 25U;
    } else {
        out.route = RECOVERED_NONSTATE_83DE4_STATUS_34;
        out.status = 34U;
    }
    return out;
}
