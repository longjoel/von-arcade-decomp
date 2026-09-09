/* Stage slot update helper at 0x881b8, called by 0x72e90. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 words[120][3];
} recovered_stage_slot_table_561e90;

/* The original computes (counter % (15 * 8)) * 12, then stores the two
 * caller-supplied words at offsets +4 and +8.  Offset +0 is untouched. */
void recovered_stage_slot_update_881b8(
    recovered_stage_slot_table_561e90 *table,
    recovered_u32 counter,
    recovered_u32 first,
    recovered_u32 second)
{
    recovered_u32 slot = counter % 120U;
    table->words[slot][1] = first;
    table->words[slot][2] = second;
}
