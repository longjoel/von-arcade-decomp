/* Count service recovered from i960 0xbf120-0xbf174. */
#include "recovered_common.h"

/* The caller supplies the base of rows whose active byte is at row +0;
 * successive rows are separated by 0x20 bytes. */
int recovered_object_active_row_count_bf120(
    const uint8_t active_byte[32], recovered_u32 entry_count,
    recovered_u32 *nonzero_count)
{
    recovered_u32 index;
    recovered_u32 count = 0U;

    if (entry_count > 32U || nonzero_count == (void *)0)
        return 0;
    for (index = entry_count; index != 0U; --index) {
        if (active_byte[index - 1U] != 0U)
            ++count;
    }
    *nonzero_count = count;
    return 1;
}
