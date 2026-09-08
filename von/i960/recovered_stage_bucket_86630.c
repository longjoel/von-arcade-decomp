/* Stage/profile bucket helper at i960 0x86630-0x866ac. */
#include "recovered_common.h"

/* The ROM uses the byte table at 0x842a0, supplied here by the caller so the
 * table's data provenance remains separate from this control-flow contract.
 * Inputs are the nonnegative counters used by the stage/profile callers. */
recovered_u32 recovered_stage_bucket_86630(
    recovered_u32 value, const uint8_t *table, recovered_u32 table_bytes)
{
    recovered_u32 residue;
    recovered_u32 bucket;

    if (value == 0U) {
        if (table_bytes == 0U)
            return 0U;
        return (recovered_u32)table[0];
    }

    residue = (value - 1U) % 6U;
    if (residue >= 1U && residue <= 3U)
        return 4U;
    if (residue == 4U)
        return 3U;

    bucket = (value - residue + 5U) / 6U;
    if (bucket >= table_bytes)
        return 0U;
    return (recovered_u32)table[bucket];
}

static const uint8_t stage_bucket_table_842a0[0x30] = {
    0x06, 0x02, 0x05, 0x01, 0x01, 0x05, 0x01, 0x02,
    0x05, 0x01, 0x01, 0x02, 0x05, 0x01, 0x01, 0x05,
    0x02, 0x02, 0x01, 0x01, 0x05, 0x05, 0x01, 0x01,
    0x02, 0x05, 0x01, 0x01, 0x05, 0x01, 0x01, 0x01,
    0x05, 0x01, 0x05, 0x01, 0x02, 0x02, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

recovered_u32 recovered_stage_bucket_86630_rom(recovered_u32 value)
{
    return recovered_stage_bucket_86630(
        value, stage_bucket_table_842a0,
        (recovered_u32)(sizeof(stage_bucket_table_842a0) /
                        sizeof(stage_bucket_table_842a0[0])));
}
