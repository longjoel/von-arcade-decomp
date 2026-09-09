/* Packed record write plan from the boot initializer at 0x866c0-0x8680c. */
#include "recovered_common.h"

typedef struct {
    uint16_t table_5050a0[64][0x90 / 2];
    uint16_t table_5074a0[64][0x88 / 2];
} recovered_stage_record_tables_866c0;

/* The initializer writes only the listed lanes; the gaps are intentionally
 * left untouched to preserve the packed-record contract. */
void recovered_stage_record_tables_write_plan_866c0(
    recovered_stage_record_tables_866c0 *state, uint16_t fill_value)
{
    recovered_u32 record;
    recovered_u32 lane;

    /* The body builds eight records per pass.  The tail at 0x86810 adds
     * 0x440/0x480 to the two table cursors and repeats while the first
     * cursor is <= 0x1dc0, yielding eight passes (64 records total). */
    for (record = 0U; record < 64U; ++record) {
        for (lane = 0U; lane < 10U; ++lane)
            state->table_5050a0[record][lane] = fill_value;
        for (lane = 0U; lane < 59U; ++lane)
            state->table_5050a0[record][10U + lane] = fill_value;
        state->table_5050a0[record][0x8cU / 2U] = fill_value;
        state->table_5050a0[record][0x8eU / 2U] = fill_value;

        for (lane = 0U; lane < 6U; ++lane)
            state->table_5074a0[record][lane] = fill_value;
        for (lane = 0U; lane < 59U; ++lane)
            state->table_5074a0[record][6U + lane] = fill_value;
        state->table_5074a0[record][0x86U / 2U] = fill_value;
    }
}
