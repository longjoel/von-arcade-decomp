/* Shared scheduler control handlers recovered from i960 0x82c18-0x82c60. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_scheduler_control_handler_route {
    RECOVERED_CONTROL_HANDLER_SET_STATE_7 = 0,
    RECOVERED_CONTROL_HANDLER_CALL_81E60 = 1,
    RECOVERED_CONTROL_HANDLER_INVALID = 2
};

struct recovered_state_scheduler_control_handlers_82c18 {
    enum recovered_scheduler_control_handler_route route;
    u32 handled;
    u32 state_504d7c;
    u32 target;
};

struct recovered_state_scheduler_control_handlers_82c18
recovered_state_scheduler_control_handlers_82c18(u32 entry,
                                                 u32 control_504e1c,
                                                 u32 prior_state_504d7c)
{
    struct recovered_state_scheduler_control_handlers_82c18 out = {
        RECOVERED_CONTROL_HANDLER_INVALID, 0U, prior_state_504d7c, 0U
    };

    if (entry != 0x82c18U && entry != 0x82c28U &&
        entry != 0x82c38U && entry != 0x82c54U)
        return out;
    out.handled = 1U;
    if (entry != 0x82c54U && control_504e1c == 0U) {
        out.route = RECOVERED_CONTROL_HANDLER_SET_STATE_7;
        out.state_504d7c = 7U;
    } else {
        out.route = RECOVERED_CONTROL_HANDLER_CALL_81E60;
        out.target = 0x00081e60U;
    }
    return out;
}
