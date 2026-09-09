/* State-handler dispatcher recovered from i960 0x82800-0x82814. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_handler_dispatch_82800 {
    u32 dispatched;
    u32 target;
    u32 rejected;
    u32 reject_target;
    u32 handler_selector;
};

static const u32 targets[10] = {
    0x82840U, 0x82874U, 0x8288cU, 0x828a4U, 0x828bcU,
    0x828d4U, 0x828f0U, 0x8293cU, 0x828e8U, 0x82950U
};

struct recovered_state_handler_dispatch_82800
recovered_state_handler_dispatch_82800(u32 selector)
{
    struct recovered_state_handler_dispatch_82800 out = {0U, 0U, 0U,
                                                         0U, selector};

    if (selector > 9U) {
        out.rejected = 1U;
        out.reject_target = 0x00082950U;
        return out;
    }
    out.dispatched = 1U;
    out.target = targets[selector];
    return out;
}
