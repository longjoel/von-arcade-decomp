/* Reverse first-hit row search recovered from i960 0xbf0c0-0xbf114. */
#include "recovered_common.h"

int recovered_object_last_active_row_bf0c0(
    const uint8_t active_byte[32], recovered_u32 entry_count,
    recovered_u32 *row_index)
{
    recovered_u32 index;

    if (entry_count > 32U || row_index == (void *)0)
        return 0;
    for (index = entry_count; index != 0U; --index) {
        if (active_byte[index - 1U] != 0U) {
            *row_index = index - 1U;
            return 1;
        }
    }
    *row_index = 0xffffffffU;
    return 1;
}
