/* Random/timing connector recovered from i960 0x840e8-0x841ec. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_random_timing_prefix_840e8_route {
    RECOVERED_840E8_CALL_82800 = 0,
    RECOVERED_840E8_STATUS_32 = 1,
    RECOVERED_840E8_STATUS_37 = 2,
    RECOVERED_840E8_STATUS_33 = 3
};

struct recovered_state_scheduler_random_timing_prefix_840e8 {
    enum recovered_state_scheduler_random_timing_prefix_840e8_route route;
    int32_t helper_value;
    u32 status;
    u32 write_504e1c;
    u32 value_504e1c;
    u32 reaches_tail;
    u32 tail_504d8c;
    u32 tail_504d90;
};

static int32_t normalize_helper(int32_t random_value)
{
    int32_t adjusted = random_value;
    int32_t block;

    if (adjusted < 0)
        adjusted += 7;
    block = adjusted & ~7;
    return random_value - block;
}

struct recovered_state_scheduler_random_timing_prefix_840e8
recovered_state_scheduler_random_timing_prefix_840e8(
    u32 object_state, int32_t random_value, int32_t current_timing,
    int32_t converted_504df8, u32 mode_504e30, u32 handler_status,
    u32 caller_g14)
{
    struct recovered_state_scheduler_random_timing_prefix_840e8 out = {
        RECOVERED_840E8_STATUS_33, 0, 33U, 1U, 1U, 0U, 0U, 0U
    };

    out.helper_value = normalize_helper(random_value);
    if (current_timing < converted_504df8) {
        out.route = RECOVERED_840E8_CALL_82800;
        out.status = handler_status;
        out.reaches_tail = object_state == 5U ? 0U : 1U;
    } else if (out.helper_value > 4 && (mode_504e30 & 4U) != 0U) {
        out.route = RECOVERED_840E8_STATUS_32;
        out.status = 32U;
    } else if (out.helper_value > 0 && (mode_504e30 & 2U) != 0U) {
        out.route = RECOVERED_840E8_STATUS_37;
        out.status = 37U;
    }
    if (object_state != 5U)
        out.reaches_tail = 1U;
    if (out.reaches_tail != 0U) {
        out.tail_504d8c = caller_g14;
        out.tail_504d90 = 15U;
    }
    return out;
}
