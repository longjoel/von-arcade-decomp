/* State-5 status branch recovered from i960 0x83884-0x839a8. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_state5_status_branch_83884_route {
    RECOVERED_STATE5_83884_NONSTATE = 0,
    RECOVERED_STATE5_83884_CALL_82800 = 1,
    RECOVERED_STATE5_83884_STATUS_19 = 2,
    RECOVERED_STATE5_83884_STATUS_21 = 3,
    RECOVERED_STATE5_83884_STATUS_27 = 4,
    RECOVERED_STATE5_83884_STATUS_28 = 5,
    RECOVERED_STATE5_83884_STATUS_37 = 6
};

struct recovered_state_scheduler_state5_status_branch_83884 {
    enum recovered_state_scheduler_state5_status_branch_83884_route route;
    u32 value_504e1c;
    u32 status;
    u32 random_calls;
    u32 calls_82800;
};

struct recovered_state_scheduler_state5_status_branch_83884
recovered_state_scheduler_state5_status_branch_83884(
    u32 state_504d7c,
    double threshold_504df8,
    double current_504d60,
    u32 control_504e28,
    int32_t random_remainder_initial,
    int32_t random_remainder_followup,
    double threshold_504e0c,
    int32_t pair_504e20)
{
    struct recovered_state_scheduler_state5_status_branch_83884 out = {
        RECOVERED_STATE5_83884_NONSTATE, 1U, 0U, 0U, 0U
    };
    int32_t remainder;

    if (state_504d7c != 5U)
        return out;
    if (current_504d60 < threshold_504df8) {
        out.route = RECOVERED_STATE5_83884_CALL_82800;
        out.calls_82800 = 1U;
        return out;
    }
    if (control_504e28 == 1U) {
        out.random_calls = 1U;
        remainder = random_remainder_initial % 10;
        if (remainder < 3) {
            out.route = RECOVERED_STATE5_83884_STATUS_28;
            out.status = 28U;
            return out;
        }
        out.random_calls = 2U;
    } else {
        out.random_calls = 1U;
    }
    remainder = random_remainder_followup % 10;
    if (remainder <= 6) {
        if (remainder <= 1) {
            out.route = RECOVERED_STATE5_83884_STATUS_21;
            out.status = 21U;
        } else if (control_504e28 == 1U &&
                   pair_504e20 == threshold_504e0c) {
            out.route = RECOVERED_STATE5_83884_STATUS_27;
            out.status = 27U;
        } else {
            out.route = RECOVERED_STATE5_83884_STATUS_19;
            out.status = 19U;
        }
    } else if (current_504d60 >= threshold_504e0c) {
        if (control_504e28 == 1U) {
            out.route = RECOVERED_STATE5_83884_STATUS_28;
            out.status = 28U;
        } else {
            out.route = RECOVERED_STATE5_83884_STATUS_37;
            out.status = 37U;
        }
    } else if (control_504e28 == 1U && pair_504e20 == threshold_504e0c) {
        out.route = RECOVERED_STATE5_83884_STATUS_27;
        out.status = 27U;
    } else {
        out.route = RECOVERED_STATE5_83884_STATUS_19;
        out.status = 19U;
    }
    return out;
}
