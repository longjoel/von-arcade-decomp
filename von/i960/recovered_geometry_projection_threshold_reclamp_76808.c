/* Projection-threshold re-clamp, i960 0x76808-0x76850.
 *
 * The preceding floating-point path has already produced the quantized g4
 * value.  This slice preserves only the integer tail: for r4 <= 20 it uses
 * (g4 + 2*g4) >> 1, otherwise it uses 100; it adds 0x50 + r4, clamps the
 * result to 300, forces a nonpositive result to 1, and publishes it as the
 * new 0x504dc0 value.  The original register names are retained because the
 * caller-level meanings of g4 and r4 are not yet established.
 */

#include <stdint.h>

uint32_t recovered_geometry_projection_threshold_reclamp_76808(
    uint32_t quantized_g4, uint32_t r4)
{
    uint32_t base = (r4 <= 20U) ? (quantized_g4 * 3U) / 2U : 100U;
    uint32_t candidate = base + 0x50U + r4;

    if ((int32_t)candidate > 300)
        candidate = 300U;
    if ((int32_t)candidate <= 0)
        candidate = 1U;
    return candidate;
}
