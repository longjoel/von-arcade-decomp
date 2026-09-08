/* State-6 selector body recovered from i960 0x7d5a4-0x7d5dc. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * timing_above_504df8 abstracts the final comparison against the converted
 * 0x504df8 threshold.  post_mode_bits is separate because the assembly
 * performs a second mode-word load after checking control 0x504dc8.
 */
u32 recovered_state_selector_body_6_7d5a4(
    u32 mode_bits, u32 control_504dc8, u32 post_mode_bits,
    u32 timing_above_504df8)
{
    if ((mode_bits & (1U << 1)) != 0U)
        return 0x0007d5f4U;
    if (control_504dc8 != 1U)
        return 0x0007d644U;
    if ((post_mode_bits & (1U << 1)) != 0U)
        return 0x0007d5f4U;
    return timing_above_504df8 != 0U ? 0x0007d4b4U : 0x0007d644U;
}
