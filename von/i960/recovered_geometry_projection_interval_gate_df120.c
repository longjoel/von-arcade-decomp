/* Signed Y-window gate recovered from i960 0xdf120 and its duplicate route. */

#include <stdint.h>

/*
 * The selected response vector is staged as (g2,g1,g3), so g1 is its Y
 * component. The object supplies a signed fixed-point base at +0x0c and a
 * signed extent at +0x54. The two i960 comparisons reject values below the
 * base or above base+extent; equality survives both branches.
 */
uint32_t recovered_geometry_projection_y_window_passes(
    int32_t selected_y, int32_t window_base, int32_t window_extent)
{
    int64_t upper = (int64_t)window_base + (int64_t)window_extent;
    return selected_y >= window_base && (int64_t)selected_y <= upper;
}
