/* Non-state status bridge recovered from i960 0x83750-0x837cc. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_nonstate_status_prefix_83750_route {
    RECOVERED_NONSTATE_83750_CALL_82800 = 0,
    RECOVERED_NONSTATE_83750_STATUS_18 = 1,
    RECOVERED_NONSTATE_83750_MOD5_TABLE = 2,
    RECOVERED_NONSTATE_83750_STATUS_42 = 3
};

struct recovered_state_scheduler_nonstate_status_prefix_83750 {
    enum recovered_state_scheduler_nonstate_status_prefix_83750_route route;
    u32 status;
    u32 random_calls;
    u32 calls_82800;
    u32 table_remainder_5;
};

struct recovered_state_scheduler_nonstate_status_prefix_83750
recovered_state_scheduler_nonstate_status_prefix_83750(
    double threshold_504df8,
    double current_504d60,
    u32 control_504e28,
    int32_t random_remainder_10,
    int32_t random_remainder_5)
{
    struct recovered_state_scheduler_nonstate_status_prefix_83750 out = {
        RECOVERED_NONSTATE_83750_CALL_82800, 0U, 0U, 0U, 0U
    };
    int32_t remainder_5;

    if (current_504d60 < threshold_504df8) {
        out.calls_82800 = 1U;
        return out;
    }
    if (current_504d60 < 0.0) {
        out.route = RECOVERED_NONSTATE_83750_STATUS_18;
        out.status = 18U;
        return out;
    }
    if (control_504e28 == 1U) {
        out.random_calls = 1U;
        if (random_remainder_10 > 3) {
            out.route = RECOVERED_NONSTATE_83750_STATUS_42;
            out.status = 42U;
            out.random_calls = 2U;
            return out;
        }
    }
    out.route = RECOVERED_NONSTATE_83750_MOD5_TABLE;
    out.random_calls += 1U;
    remainder_5 = random_remainder_5 % 5;
    if (remainder_5 >= 0 && remainder_5 < 5)
        out.table_remainder_5 = (u32)remainder_5;
    return out;
}
