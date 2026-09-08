/* State-handler address table recovered from i960 0x7d358-0x7d380. */
#include <stdint.h>

typedef uint32_t u32;

u32 recovered_state_selector_target_7d358(u32 state)
{
    static const u32 targets[10] = {
        0x0007d380U, 0x0007d390U, 0x0007d3a4U, 0x0007d404U,
        0x0007d4e8U, 0x0007d568U, 0x0007d5a4U, 0x0007d5dcU,
        0x0007d604U, 0x0007d660U,
    };

    return state < 10U ? targets[state] : 0U;
}
