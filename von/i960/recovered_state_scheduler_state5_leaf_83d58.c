/* State-5 status leaf recovered from i960 0x83d58-0x83de4. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_state5_leaf_83d58_route {
    RECOVERED_STATE5_83D58_CALL_82800 = 0,
    RECOVERED_STATE5_83D58_STATUS_18 = 1,
    RECOVERED_STATE5_83D58_STATUS_19 = 2,
    RECOVERED_STATE5_83D58_STATUS_25 = 3,
    RECOVERED_STATE5_83D58_STATUS_27 = 4,
    RECOVERED_STATE5_83D58_STATUS_33 = 5
};

struct recovered_state_scheduler_state5_leaf_83d58 {
    enum recovered_state_scheduler_state5_leaf_83d58_route route;
    u32 status;
    u32 random_calls;
};

struct recovered_state_scheduler_state5_leaf_83d58
recovered_state_scheduler_state5_leaf_83d58(int32_t current_timing,
                                            int32_t negative_limit,
                                            int32_t random_value,
                                            u32 control_504e28,
                                            int32_t pair_504e20,
                                            u32 handler_status)
{
    struct recovered_state_scheduler_state5_leaf_83d58 out = {
        RECOVERED_STATE5_83D58_STATUS_18, 18U, 0U
    };
    int32_t remainder;

    if (current_timing < negative_limit) {
        out.route = RECOVERED_STATE5_83D58_CALL_82800;
        out.status = handler_status;
        return out;
    }
    if (current_timing < 0)
        return out;
    out.random_calls = 1U;
    remainder = random_value % 10;
    /* Literal-first cmpibge 5 enters 0x83d98 for remainders <= 5.
     * The nested literal-first cmpibge 3 sends <= 3 to status 33;
     * remainders 4 and 5 use the control/pair equality block. */
    if (remainder > 5) {
        out.route = RECOVERED_STATE5_83D58_STATUS_25;
        out.status = 25U;
    } else if (remainder <= 3) {
        out.route = RECOVERED_STATE5_83D58_STATUS_33;
        out.status = 33U;
    } else if (control_504e28 == 1U && pair_504e20 == 0x40340000) {
        out.route = RECOVERED_STATE5_83D58_STATUS_27;
        out.status = 27U;
    } else {
        out.route = RECOVERED_STATE5_83D58_STATUS_19;
        out.status = 19U;
    }
    return out;
}
