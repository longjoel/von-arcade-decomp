/* Four e2120 asset calls selected by the runtime record at 0x95a00. */
#include "recovered_common.h"

struct recovered_geometry_asset_dispatch_95a00_plan {
    recovered_u32 record_type, record_flag;
    recovered_u32 mode_address, mode_value;
    recovered_u32 helper_target, call_count;
    recovered_u32 selector[4], index_word[4];
};

void recovered_geometry_asset_dispatch_95a00(
    recovered_u32 record_type, recovered_u32 record_flag,
    struct recovered_geometry_asset_dispatch_95a00_plan *plan)
{
    static const recovered_u32 selectors[4] = {1U, 3U, 5U, 7U};
    recovered_u32 repeated_pair = record_type == 7U && record_flag == 0U;

    plan->record_type = record_type;
    plan->record_flag = record_flag;
    plan->mode_address = 0x577590U;
    plan->mode_value = record_type == 5U ? 15U : 18U;
    plan->helper_target = 0xe2120U;
    plan->call_count = 4U;
    for (unsigned i = 0; i < 4; ++i) {
        plan->selector[i] = selectors[i];
        plan->index_word[i] = (record_type << 2) +
            (repeated_pair ? (i & 1U) : i);
    }
}
