/* Non-state remi-6 continuation recovered from i960 0x83e74-0x83f38. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_nonstate_remainder6_83e74_route {
    RECOVERED_NONSTATE_83E74_TAIL = 0,
    RECOVERED_NONSTATE_83E74_STATUS_27 = 1,
    RECOVERED_NONSTATE_83E74_CALL_82800_PARITY = 2,
    RECOVERED_NONSTATE_83E74_CALL_82800_RANDOM = 3,
    RECOVERED_NONSTATE_83E74_STATUS_40 = 4,
    RECOVERED_NONSTATE_83E74_STATUS_19 = 5
};

struct recovered_state_scheduler_nonstate_remainder6_83e74 {
    enum recovered_state_scheduler_nonstate_remainder6_83e74_route route;
    u32 status;
    u32 random_calls;
    u32 write_status;
};

struct recovered_state_scheduler_nonstate_remainder6_83e74
recovered_state_scheduler_nonstate_remainder6_83e74(
    int32_t remainder_6, u32 mode_504e30, u32 control_504e28,
    int32_t pair_504e20, int32_t original_random_value,
    int32_t random_value_3, u32 handler_status)
{
    struct recovered_state_scheduler_nonstate_remainder6_83e74 out = {
        RECOVERED_NONSTATE_83E74_TAIL, 0U, 0U, 0U
    };
    int32_t sign;
    int32_t half;
    int32_t parity;
    int32_t remainder_3;

    if (remainder_6 <= 2 || (mode_504e30 & 0x2U) == 0U) {
        sign = original_random_value >> 31;
        half = (original_random_value + sign) >> 1;
        parity = original_random_value - (half * 2);
        if (parity == 1) {
            out.route = RECOVERED_NONSTATE_83E74_CALL_82800_PARITY;
            out.status = handler_status;
        }
        return out;
    }

    if (control_504e28 == 1U && pair_504e20 == (int32_t)0x40340000) {
        out.route = RECOVERED_NONSTATE_83E74_STATUS_27;
        out.status = 27U;
        out.write_status = 1U;
        return out;
    }

    out.random_calls = 1U;
    remainder_3 = random_value_3 % 3;
    if (remainder_3 == 1) {
        out.route = RECOVERED_NONSTATE_83E74_STATUS_40;
        out.status = 40U;
        out.write_status = 1U;
    } else if (remainder_3 > 1) {
        if (remainder_3 == 2) {
            out.route = RECOVERED_NONSTATE_83E74_STATUS_19;
            out.status = 19U;
            out.write_status = 1U;
        }
    } else if (remainder_3 == 0) {
        out.route = RECOVERED_NONSTATE_83E74_STATUS_40;
        out.status = 40U;
        out.write_status = 1U;
    }
    return out;
}
