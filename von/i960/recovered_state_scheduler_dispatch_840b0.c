/* Random/timing dispatch bridge recovered from i960 0x840b0-0x84104. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_dispatch_840b0_route {
    RECOVERED_840B0_EARLY_RETURN = 0,
    RECOVERED_840B0_STATE5_RANDOM = 1,
    RECOVERED_840B0_NONSTATE_RANDOM = 2
};

struct recovered_state_scheduler_dispatch_840b0 {
    enum recovered_state_scheduler_dispatch_840b0_route route;
    u32 terminal;
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504e1c;
    u32 value_504e1c;
    u32 next_address;
};

struct recovered_state_scheduler_dispatch_840b0
recovered_state_scheduler_dispatch_840b0(int32_t value_504dc0,
                                         int32_t related_state,
                                         u32 state_504d7c,
                                         u32 caller_g14)
{
    struct recovered_state_scheduler_dispatch_840b0 out = {
        RECOVERED_840B0_EARLY_RETURN, 0U, 0U, 0U, 0U, 0U, 0U
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
        out.route = RECOVERED_840B0_STATE5_RANDOM;
        out.next_address = 0x00084104U;
    } else {
        out.route = RECOVERED_840B0_NONSTATE_RANDOM;
        out.next_address = 0x000841a0U;
    }
    return out;
}
