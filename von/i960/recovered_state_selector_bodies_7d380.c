/* First two selector bodies recovered from i960 0x7d380-0x7d3a4. */
#include <stdint.h>

typedef uint32_t u32;

u32 recovered_state_selector_body_0_7d380(u32 mode_bits)
{
    return (mode_bits & (1U << 1)) != 0U ? 0x0007d5f4U : 0x0007d644U;
}

u32 recovered_state_selector_body_1_7d390(u32 mode_bits)
{
    if ((mode_bits & (1U << 1)) != 0U)
        return 0x0007d5f4U;
    if ((mode_bits & (1U << 2)) != 0U)
        return 0x0007d4b4U;
    return 0x0007d644U;
}
