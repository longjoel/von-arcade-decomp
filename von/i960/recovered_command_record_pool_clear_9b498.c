/* Command-record pool reset at i960 0x9b498. */
#include "recovered_command_record_9b2xx.h"

/* The clear loop writes one byte at the start of each 16-byte slot, walking
 * from the last slot down to the first, then resets the allocation cursor. */
void recovered_command_record_pool_clear_9b498(
    recovered_command_record_table_9b2xx *pool)
{
    recovered_u32 offset;
    for (offset = 0U; offset < 0x100U; offset += 0x10U)
        pool->record[offset / 0x10U].active = 0U;
    pool->cursor = 0U;
}
