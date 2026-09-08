/* High-state service normalization recovered from i960 0x82f90-0x82fbc. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_high_dispatch_82f90 {
    int32_t remainder;
    u32 dispatched;
    u32 target;
};

static const u32 targets[8] = {
    0x82fdcU, 0x82ff4U, 0x8300cU, 0x83024U,
    0x8303cU, 0x83050U, 0x83058U, 0x8307cU
};

struct recovered_state_service_high_dispatch_82f90
recovered_state_service_high_dispatch_82f90(int32_t random_value)
{
    struct recovered_state_service_high_dispatch_82f90 out = {0, 0U, 0U};
    int32_t adjusted = random_value;
    int32_t block;

    if (random_value < 0)
        adjusted += 3;
    block = adjusted & ~3;
    out.remainder = random_value - block;
    if (out.remainder < 0 || out.remainder > 7)
        return out;
    out.dispatched = 1U;
    out.target = targets[out.remainder];
    return out;
}
