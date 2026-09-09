/* Post-status scheduler table recovered from i960 0x82b38-0x82c08. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_dispatch_82b4c {
    u32 dispatched;
    u32 target;
};

static const u32 targets[44] = {
    0x82d68U, 0x82d68U, 0x82d68U, 0x82d68U, 0x82d68U,
    0x82c54U, 0x82c08U, 0x82c54U, 0x82c18U, 0x82c28U,
    0x82c38U, 0x82c60U, 0x82d68U, 0x82d68U, 0x82d68U,
    0x82d68U, 0x82d68U, 0x82d68U, 0x82d68U, 0x82c6cU,
    0x82cc0U, 0x82cc8U, 0x82cd0U, 0x82cd8U, 0x82ce0U,
    0x82cc8U, 0x82cb0U, 0x82ce8U, 0x82d04U, 0x82d68U,
    0x82d68U, 0x82d68U, 0x82d18U, 0x82cc8U, 0x82cc8U,
    0x82cc0U, 0x82cc0U, 0x82cb0U, 0x82d34U, 0x82d48U,
    0x82d68U, 0x82d68U, 0x82d68U, 0x82d5cU
};

struct recovered_state_scheduler_dispatch_82b4c
recovered_state_scheduler_dispatch_82b4c(u32 low_status_504d80,
                                          u32 max_status,
                                          u32 high_selector_504d84)
{
    struct recovered_state_scheduler_dispatch_82b4c out = {0U, 0U};

    /* ldl 0x504d80 loads the low status into g4 and the high selector into
     * g5; cmpibne gates g5 before cmpobg bounds and indexes g4. */
    if (high_selector_504d84 != 1U || low_status_504d80 > max_status ||
        low_status_504d80 >= 44U)
        return out;
    out.dispatched = 1U;
    out.target = targets[low_status_504d80];
    return out;
}
