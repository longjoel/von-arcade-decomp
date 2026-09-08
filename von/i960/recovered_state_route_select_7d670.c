/* Selector scan recovered from i960 0x7d670-0x7d7f0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_route_record_7d670 {
    int16_t first;
    int16_t metric;
    int16_t enabled;
};

struct recovered_state_route_selection_7d670 {
    u32 selected_index; /* 0..6, or 0xffffffff when no record is enabled. */
    int16_t selected_metric;
    u32 fallback_status; /* 10 or 11 when selected_index is 0xffffffff. */
    u32 packet_target; /* 0x7d7f4 when a record is selected, else 0. */
    u32 record_table_base;
    u32 record_stride;
};

/*
 * The original table is addressed from 0x505060 with a six-byte stride.  It
 * skips an entry when its signed halfword at +4 is zero and compares the
 * signed halfword at +2 against the running minimum.  The first entry wins
 * ties because the update is strict (best > candidate).
 */
struct recovered_state_route_selection_7d670
recovered_state_route_select_7d670(
    const struct recovered_state_route_record_7d670 records[7],
    int32_t status_504d70)
{
    struct recovered_state_route_selection_7d670 out = {
        0xffffffffU, 0, 0, 0U, 0x00505060U, 6U
    };
    int i;

    for (i = 0; i < 7; ++i) {
        if (records[i].enabled == 0)
            continue;
        if (out.selected_index == 0xffffffffU ||
            records[i].metric < out.selected_metric) {
            out.selected_index = (u32)i;
            out.selected_metric = records[i].metric;
        }
    }
    if (out.selected_index == 0xffffffffU)
        out.fallback_status = status_504d70 > 4 ? 10U : 11U;
    else
        out.packet_target = 0x0007d7f4U;
    return out;
}
