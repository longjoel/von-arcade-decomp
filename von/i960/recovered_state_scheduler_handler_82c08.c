/* Scheduler handler for table selector 6, recovered from i960 0x82c08. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_handler_82c08_route {
    RECOVERED_SCHEDULER_HANDLER_SET_STATE_7 = 0,
    RECOVERED_SCHEDULER_HANDLER_CALL_81E60 = 1
};

struct recovered_state_scheduler_handler_82c08 {
    enum recovered_state_scheduler_handler_82c08_route route;
    u32 state_504d7c;
};

struct recovered_state_scheduler_handler_82c08
recovered_state_scheduler_handler_82c08(u32 control_504e1c,
                                        u32 prior_state_504d7c)
{
    struct recovered_state_scheduler_handler_82c08 out = {
        RECOVERED_SCHEDULER_HANDLER_CALL_81E60, prior_state_504d7c
    };

    if (control_504e1c == 0U) {
        out.route = RECOVERED_SCHEDULER_HANDLER_SET_STATE_7;
        out.state_504d7c = 7U;
    }
    return out;
}
