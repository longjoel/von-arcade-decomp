/* Packed record write plan from the boot initializer at 0x866c0-0x8680c. */
#include "recovered_common.h"

typedef struct {
    uint16_t table_5050a0[8][0x90 / 2];
    uint16_t table_5074a0[8][0x88 / 2];
} recovered_stage_record_tables_866c0;

/* The initializer writes only the listed lanes; the gaps are intentionally
 * left untouched to preserve the packed-record contract. */
void recovered_stage_record_tables_write_plan_866c0(
    recovered_stage_record_tables_866c0 *state)
{
    recovered_u32 record;
    recovered_u32 lane;

    for (record = 0U; record < 8U; ++record) {
        for (lane = 0U; lane < 10U; ++lane)
            state->table_5050a0[record][lane] = 0U;
        for (lane = 0U; lane < 59U; ++lane)
            state->table_5050a0[record][10U + lane] = 0U;
        state->table_5050a0[record][0x8cU / 2U] = 0U;
        state->table_5050a0[record][0x8eU / 2U] = 0U;

        for (lane = 0U; lane < 6U; ++lane)
            state->table_5074a0[record][lane] = 0U;
        for (lane = 0U; lane < 59U; ++lane)
            state->table_5074a0[record][6U + lane] = 0U;
        state->table_5074a0[record][0x86U / 2U] = 0U;
    }
}
