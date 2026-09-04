/* Pure threshold selection from original-ROM 0x761b0-0x76234. */
#include "recovered_common.h"

recovered_u32 recovered_object_threshold_constant_761b0(
    recovered_u32 counter, recovered_u32 *selector)
{
    recovered_u32 value;
    if (counter <= 0x54U)
        value = 0x45000000U;
    else if (counter <= 0x59U)
        value = 0x45800000U;
    else if (counter <= 0x5eU)
        value = 0x46000000U;
    else
        value = 0x46800000U;
    *selector = 29U;
    return value;
}
