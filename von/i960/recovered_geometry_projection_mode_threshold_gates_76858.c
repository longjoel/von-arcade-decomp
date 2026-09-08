/* Mode-dependent threshold gates, i960 0x76858-0x768f0.
 *
 * This is the integer continuation after the 0x76808 projection re-clamp.
 * For mode != 1, the object +0x1d0/+0x1d8 comparison and the
 * (0x503a18 - (0x503a14 / 48)) <= 19 gate can raise the threshold to 101
 * when it is at most 99.  Two subsequent guards raise low-r4 thresholds to
 * 90 (r4 <= 2) and 100 (r4 <= 4).  Inputs retain listing-oriented names;
 * field semantics and the mode-global provenance remain unresolved.
 */

#include <stdint.h>

uint32_t recovered_geometry_projection_mode_threshold_gates_76858(
    uint32_t mode, uint16_t object_1d0, uint16_t object_1d8,
    uint32_t global_503a14, uint32_t global_503a18,
    uint32_t r4, uint32_t threshold)
{
    if (mode != 1U) {
        uint32_t quarter = ((uint32_t)object_1d8) >> 2;
        uint32_t span = global_503a18 - (global_503a14 / 48U);

        if ((uint32_t)object_1d0 >= quarter && span <= 19U &&
            threshold <= 99U)
            threshold = 101U;
    }

    if (r4 <= 2U && threshold > 85U)
        threshold = 90U;
    if (r4 <= 4U && threshold > 90U)
        threshold = 100U;
    return threshold;
}
