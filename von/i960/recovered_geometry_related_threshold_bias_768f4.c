/* Related-object threshold bias, i960 0x768f4-0x76930.
 *
 * After the projection threshold gates, the listing checks related-object
 * state +0x64 against four literals.  States 0, 3, 4, and 6, as well as
 * global stage ordinal 2 at 0x503a80, take the same path: load 0x504dc0,
 * add 10, and store it back.  All other states leave the threshold alone.
 */

#include <stdint.h>

uint32_t recovered_geometry_related_threshold_bias_768f4(
    uint32_t related_state, uint32_t stage_ordinal, uint32_t threshold)
{
    if (related_state == 0U || related_state == 3U ||
        related_state == 4U || related_state == 6U || stage_ordinal == 2U)
        threshold += 10U;
    return threshold;
}
