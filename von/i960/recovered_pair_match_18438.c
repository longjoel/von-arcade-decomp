/* Pair-swap matcher recovered from i960 0x18438-0x1846c. */
#include <stdint.h>

typedef uint32_t u32;

u32 recovered_pair_match(u32 first, u32 second)
{
    /* Four ordered pairs share one shape: (0,1), (1,0), (2,3), (3,2).
     * The entry saves the return link into g2 and clears g14, then
     * returns the boolean in g0 through bx (g2). */
    if (first == 0U)
        return second == 1U ? 1U : 0U;
    if (first == 1U)
        return second == 0U ? 1U : 0U;
    if (first == 2U)
        return second == 3U ? 1U : 0U;
    if (first == 3U)
        return second == 2U ? 1U : 0U;
    return 0U;
}
