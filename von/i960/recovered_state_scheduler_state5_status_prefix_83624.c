/* State-5 status bridge recovered from i960 0x83624-0x836d0. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_state5_status_prefix_83624_route {
    RECOVERED_STATE5_83624_NONSTATE = 0,
    RECOVERED_STATE5_83624_CALL_82800 = 1,
    RECOVERED_STATE5_83624_STATUS_18 = 2,
    RECOVERED_STATE5_83624_MOD5_TABLE = 3,
    RECOVERED_STATE5_83624_STATUS_35 = 4,
    RECOVERED_STATE5_83624_STATUS_42 = 5
};

struct recovered_state_scheduler_state5_status_prefix_83624 {
    enum recovered_state_scheduler_state5_status_prefix_83624_route route;
    u32 value_504e1c;
    u32 status;
    u32 random_calls;
    u32 calls_82800;
    u32 table_remainder_5;
};

struct recovered_state_scheduler_state5_status_prefix_83624
recovered_state_scheduler_state5_status_prefix_83624(
    u32 state_504d7c,
    double threshold_504df8,
    double current_504d60,
    u32 control_504e28,
    int32_t random_remainder_10,
    int32_t random_remainder_5,
    u32 random_value_2)
{
    struct recovered_state_scheduler_state5_status_prefix_83624 out = {
        RECOVERED_STATE5_83624_NONSTATE, 1U, 0U, 0U, 0U, 0U
    };
    int32_t remainder_5;

    if (state_504d7c != 5U)
        return out;
    if (current_504d60 < threshold_504df8) {
        out.route = RECOVERED_STATE5_83624_CALL_82800;
        out.calls_82800 = 1U;
        return out;
    }
    if (current_504d60 < 0.0) {
        out.route = RECOVERED_STATE5_83624_STATUS_18;
        out.status = 18U;
        return out;
    }
    if (control_504e28 != 1U)
        goto modulo5;
    out.random_calls = 1U;
    remainder_5 = random_remainder_10 % 10;
    if (remainder_5 <= 3)
        goto modulo5;
    out.random_calls = 2U;
    if ((random_value_2 & 1U) != 0U) {
        out.route = RECOVERED_STATE5_83624_STATUS_42;
        out.status = 42U;
    } else {
        out.route = RECOVERED_STATE5_83624_STATUS_35;
        out.status = 35U;
    }
    return out;

modulo5:
    out.route = RECOVERED_STATE5_83624_MOD5_TABLE;
    out.random_calls += 1U;
    remainder_5 = random_remainder_5 % 5;
    if (remainder_5 >= 0 && remainder_5 < 5)
        out.table_remainder_5 = (u32)remainder_5;
    return out;
}
