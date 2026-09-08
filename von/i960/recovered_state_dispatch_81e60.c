/* State dispatcher recovered from i960 0x81e60-0x81f54. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_dispatch_81e60 {
    u32 startup_call_84d90;
    u32 dispatched;
    u32 target;
};

static const u32 targets[10] = {
    0x81edcU, 0x81ee8U, 0x81ef4U, 0x81f00U, 0x81f0cU,
    0x81f18U, 0x81f24U, 0x81f30U, 0x81f3cU, 0x81f48U
};

struct recovered_state_dispatch_81e60
recovered_state_dispatch_81e60(
    u32 global_5039f4, u32 global_503a00, int16_t mode_504e42,
    u32 object_state)
{
    struct recovered_state_dispatch_81e60 out = {0U, 0U, 0U};

    out.startup_call_84d90 = global_5039f4 == 4U &&
                             global_503a00 == 10U && mode_504e42 == 0;
    if (mode_504e42 != 0 || object_state > 9U)
        return out;
    out.dispatched = 1U;
    out.target = targets[object_state];
    return out;
}
