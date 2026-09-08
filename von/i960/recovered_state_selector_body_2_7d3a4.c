/* State-2 selector body recovered from i960 0x7d3a4-0x7d404. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * coordinate_band_passed abstracts the four signed coordinate range checks
 * before 0x7d3d8.  remainder_is_after_449 represents
 * (0x5024e8 % 600) > 449; the assembly's <=449 arm reaches 0x7d644.
 */
u32 recovered_state_selector_body_2_7d3a4(
    u32 mode_bits, u32 coordinate_band_passed,
    u32 remainder_is_after_449)
{
    if ((mode_bits & (1U << 1)) != 0U)
        return 0x0007d5f4U;
    if (coordinate_band_passed == 0U)
        return 0x0007d654U;
    return remainder_is_after_449 != 0U ? 0x0007d654U : 0x0007d644U;
}
