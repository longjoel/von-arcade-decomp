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
recovered_state_scheduler_dispatch_82b4c(u32 status,
                                          u32 max_selector,
                                          u32 selector)
{
    struct recovered_state_scheduler_dispatch_82b4c out = {0U, 0U};

    if (status != 1U || selector > max_selector || selector >= 44U)
        return out;
    out.dispatched = 1U;
    out.target = targets[selector];
    return out;
}
