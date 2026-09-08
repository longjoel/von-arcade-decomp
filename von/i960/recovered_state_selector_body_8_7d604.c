/* State-8 selector body recovered from i960 0x7d604-0x7d660. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * remainder_after_299 represents (0x5024e8 % 600) > 299.  Mode bit 2 and
 * control 0x504dc8 are tested before that remainder path.
 */
u32 recovered_state_selector_body_8_7d604(
    u32 mode_bits, u32 control_504dc8, u32 remainder_after_299)
{
    if ((mode_bits & (1U << 2)) != 0U && control_504dc8 == 1U)
        return 0x0007d4b4U;
    return remainder_after_299 != 0U ? 0x0007d654U : 0x0007d644U;
}
