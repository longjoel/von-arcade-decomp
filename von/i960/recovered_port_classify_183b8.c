/* Port-word classifier recovered from i960 0x183b8-0x18420. */
#include <stdint.h>

typedef uint32_t u32;

u32 recovered_port_classify(u32 word_before, u32 word_high, u32 word_mid)
{
    /* Three unsigned greater-than gates over masked words: the entry
     * saves the return link into g1 and clears g14, then reports the
     * class in g0 through bx (g1). cmpobg compares ordinally with the
     * first operand on the left. */
    if (word_before <= 0x3ffeU)
        return 3U;
    if (word_high <= 0x4000U)
        return 0U;
    if (word_mid <= 0x3ffeU)
        return 2U;
    return 1U;
}
