/* State-5 status leaf recovered from i960 0x839a8-0x83ab8. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_status_leaf_839a8_route {
    RECOVERED_STATUS_LEAF_CALL_82800 = 0,
    RECOVERED_STATUS_LEAF_STATUS_19 = 1,
    RECOVERED_STATUS_LEAF_STATUS_21 = 2,
    RECOVERED_STATUS_LEAF_STATUS_27 = 3,
    RECOVERED_STATUS_LEAF_STATUS_28 = 4,
    RECOVERED_STATUS_LEAF_STATUS_37 = 5
};

struct recovered_state_scheduler_status_leaf_839a8 {
    enum recovered_state_scheduler_status_leaf_839a8_route route;
    u32 status;
    u32 random_calls;
    u32 write_504d8c;
    u32 value_504d8c;
    u32 write_504d90;
    u32 value_504d90;
};

static u32 equality_status(u32 mode_504e30, u32 control_504e28,
                           int32_t pair_504e20, int32_t threshold_504e0c,
                           enum recovered_state_scheduler_status_leaf_839a8_route *route)
{
    if ((mode_504e30 & 4U) != 0U && control_504e28 == 1U &&
        pair_504e20 == threshold_504e0c) {
        *route = RECOVERED_STATUS_LEAF_STATUS_27;
        return 27U;
    }
    *route = RECOVERED_STATUS_LEAF_STATUS_19;
    return 19U;
}

struct recovered_state_scheduler_status_leaf_839a8
recovered_state_scheduler_status_leaf_839a8(int32_t current_timing,
                                            int32_t converted_504df8,
                                            int32_t random_value,
                                            int32_t threshold_504e0c,
                                            u32 mode_504e30,
                                            u32 control_504e28,
                                            int32_t pair_504e20,
                                            u32 handler_status,
                                            u32 caller_g14)
{
    struct recovered_state_scheduler_status_leaf_839a8 out = {
        RECOVERED_STATUS_LEAF_STATUS_19, 19U, 0U, 1U, 0U, 1U, 15U
    };
    int32_t remainder;

    out.value_504d8c = caller_g14;
    if (current_timing < converted_504df8) {
        out.route = RECOVERED_STATUS_LEAF_CALL_82800;
        out.status = handler_status;
        return out;
    }
    remainder = random_value % 10;
    out.random_calls = 1U;
    if (remainder >= 3 && current_timing < threshold_504e0c &&
        (mode_504e30 & 4U) != 0U) {
        out.status = equality_status(mode_504e30, control_504e28,
                                     pair_504e20, threshold_504e0c,
                                     &out.route);
    } else if (remainder > 6 && (mode_504e30 & 2U) != 0U) {
        if (control_504e28 != 1U) {
            out.route = RECOVERED_STATUS_LEAF_STATUS_37;
            out.status = 37U;
        } else {
            out.route = RECOVERED_STATUS_LEAF_STATUS_28;
            out.status = 28U;
        }
    } else if (remainder <= 1 || (mode_504e30 & 4U) == 0U) {
        out.route = RECOVERED_STATUS_LEAF_STATUS_21;
        out.status = 21U;
    } else {
        out.status = equality_status(mode_504e30, control_504e28,
                                     pair_504e20, threshold_504e0c,
                                     &out.route);
    }
    return out;
}
