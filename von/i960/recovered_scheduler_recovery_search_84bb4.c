/* Recovery-record search recovered from i960 0x84bb4-0x84bec. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_search_84bb4 {
    u32 selected_index;
    u32 selected_value;
    u32 selected_valid;
    u32 compared_records;
};

struct recovered_scheduler_recovery_search_84bb4
recovered_scheduler_recovery_search_84bb4(u32 target,
                                          const u32 records[8])
{
    struct recovered_scheduler_recovery_search_84bb4 out = {
        0U, 0U, 0U, 0U
    };
    u32 working_target = target;
    u32 index;

    for (index = 0U; index < 8U; ++index) {
        out.compared_records++;
        if (working_target > records[index]) {
            out.selected_index = index;
            out.selected_value = records[index];
            out.selected_valid = 1U;
            working_target = records[index];
        }
    }
    return out;
}
