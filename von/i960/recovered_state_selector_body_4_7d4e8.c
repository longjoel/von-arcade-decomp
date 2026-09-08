/* State-4 selector body recovered from i960 0x7d4e8-0x7d568. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * coordinate_band_passed abstracts the same four signed range checks used by
 * the neighboring state-2 body.  periodic_after_199 represents
 * (0x5024e8 % 600) > 199.  The g3/g13 and control predicates are kept as
 * inputs because they are produced by the shared pre-dispatch scan.
 */
u32 recovered_state_selector_body_4_7d4e8(
    u32 mode_bits, u32 coordinate_band_passed,
    u32 g3, u32 g13, u32 control_504dc8,
    u32 periodic_after_199)
{
    if ((mode_bits & (1U << 1)) != 0U)
        return 0x0007d5f4U;
    if (coordinate_band_passed == 0U)
        return 0x0007d654U;
    if ((g3 == 0U && g13 == 0U) || control_504dc8 != 1U)
        return 0x0007d654U;
    return periodic_after_199 != 0U ? 0x0007d654U : 0x0007d644U;
}
