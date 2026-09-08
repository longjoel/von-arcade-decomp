/* Shared service dispatch recovered from i960 0x82fac-0x82fdc. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_shared_dispatch_82fac {
    u32 dispatched;
    u32 target;
};

static const u32 targets[8] = {
    0x82fdcU, 0x82ff4U, 0x8300cU, 0x83024U,
    0x8303cU, 0x83050U, 0x83058U, 0x8307cU
};

struct recovered_state_service_shared_dispatch_82fac
recovered_state_service_shared_dispatch_82fac(u32 selector)
{
    struct recovered_state_service_shared_dispatch_82fac out = {0U, 0U};

    if (selector > 7U)
        return out;
    out.dispatched = 1U;
    out.target = targets[selector];
    return out;
}
