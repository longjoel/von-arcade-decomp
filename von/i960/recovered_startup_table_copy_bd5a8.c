/* Startup ROM-table copier at i960 0xbd5a8, called from 0x189f4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 fifo_word;
    recovered_u32 startup_cursor;
} recovered_startup_table_copy_result_bd5a8;

/* Copy the four fixed-size ROM blocks and publish the observed startup
 * command/cursor values.  The source data itself remains supplied by the
 * caller, preserving this as a table-layout contract. */
void recovered_startup_table_copy_bd5a8(
    const recovered_u32 *source_13da68,
    recovered_u32 *destination_565e30,
    const recovered_u32 *source_13b3f8,
    recovered_u32 *destination_562cb0,
    const recovered_u32 *source_13a728,
    recovered_u32 *destination_565ed0,
    const recovered_u32 *source_12a728,
    recovered_u32 *destination_566ba0,
    recovered_startup_table_copy_result_bd5a8 *result)
{
    recovered_u32 index;
    for (index = 0U; index < 39U; ++index)
        destination_565e30[index] = source_13da68[index];
    for (index = 0U; index < 0x99bU; ++index)
        destination_562cb0[index] = source_13b3f8[index];
    for (index = 0U; index < 0x333U; ++index)
        destination_565ed0[index] = source_13a728[index];
    for (index = 0U; index < 0x3fffU; ++index)
        destination_566ba0[index] = source_12a728[index];
    result->fifo_word = 0x44U;
    result->startup_cursor = 0xffffffffU;
}
