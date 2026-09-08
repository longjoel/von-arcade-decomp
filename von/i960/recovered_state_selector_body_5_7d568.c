/* State-5 selector body recovered from i960 0x7d568-0x7d5a4. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * remainder_after_119 represents (0x5024e8 % 600) > 119.  The remaining
 * inputs are the shared scan flags/control and the mode word tested by the
 * literal branches at 0x7d580-0x7d59c.
 */
u32 recovered_state_selector_body_5_7d568(
    u32 remainder_after_119, u32 g3, u32 g13,
    u32 control_504dc8, u32 mode_bits)
{
    if (remainder_after_119 == 0U || (g3 == 0U && g13 == 0U) ||
        control_504dc8 != 1U || (mode_bits & (1U << 1)) == 0U)
        return 0x0007d644U;
    return 0x0007d5f4U;
}
