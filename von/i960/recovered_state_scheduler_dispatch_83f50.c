/* State-scheduler bridge recovered from i960 0x83f50-0x83f9c. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_dispatch_83f50_route {
    RECOVERED_83F50_EARLY_RETURN = 0,
    RECOVERED_83F50_STATE5_HANDLER = 1,
    RECOVERED_83F50_NONSTATE_TAIL = 2
};

struct recovered_state_scheduler_dispatch_83f50 {
    enum recovered_state_scheduler_dispatch_83f50_route route;
    u32 terminal;
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504e1c;
    u32 value_504e1c;
    u32 next_address;
};

struct recovered_state_scheduler_dispatch_83f50
recovered_state_scheduler_dispatch_83f50(int32_t value_504dc0,
                                         int32_t related_state,
                                         u32 state_504d7c,
                                         u32 caller_g14)
{
    struct recovered_state_scheduler_dispatch_83f50 out = {
        RECOVERED_83F50_EARLY_RETURN, 0U, 0U, 0U, 0U, 0U, 0U
    };

    if (value_504dc0 <= 149
        && (related_state == 19 || related_state == 20)) {
        out.terminal = 1U;
        out.write_504d98 = 1U;
        out.value_504d98 = caller_g14;
        return out;
    }

    out.write_504e1c = 1U;
    out.value_504e1c = 1U;
    if (state_504d7c == 5U) {
        out.route = RECOVERED_83F50_STATE5_HANDLER;
        out.next_address = 0x00083f9cU;
    } else {
        out.route = RECOVERED_83F50_NONSTATE_TAIL;
        out.next_address = 0x00084018U;
    }
    return out;
}
