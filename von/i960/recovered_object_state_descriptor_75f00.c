/* Pure descriptor selection/copy from the original-ROM object initializer
 * at 0x75fe4-0x7602c. Records are 0x48 bytes (18 words) apart. */
#include "recovered_common.h"

recovered_u32 recovered_object_state_descriptor_75f00(
    recovered_u32 selector, const recovered_u32 *table,
    recovered_u32 table_records, recovered_u32 output[18])
{
    recovered_u32 index;
    if (selector >= table_records)
        return 0U;
    for (index = 0U; index < 18U; ++index)
        /* The table expression is byte-addressed as table[record * 8],
         * hence 9 * 8 bytes = 18 32-bit words per selected record. */
        output[index] = table[selector * 18U + index];
    return 1U;
}
