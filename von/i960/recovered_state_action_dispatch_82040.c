/* State-action dispatcher recovered from i960 0x82040-0x82088. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_action_dispatch_82040 {
    u32 dispatched;
    u32 target;
};

static const u32 targets[10] = {
    0x82088U, 0x820ccU, 0x82120U, 0x8218cU, 0x82248U,
    0x82330U, 0x823ccU, 0x824b8U, 0x82534U, 0x825c0U
};

struct recovered_state_action_dispatch_82040
recovered_state_action_dispatch_82040(u32 object_state)
{
    struct recovered_state_action_dispatch_82040 out = {0U, 0U};

    if (object_state > 9U)
        return out;
    out.dispatched = 1U;
    out.target = targets[object_state];
    return out;
}
