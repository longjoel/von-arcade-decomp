/* Recovery-record search recovered from i960 0x84bb4-0x84bec. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_search_84bb4 {
    u32 selected_index;
    int32_t selected_value;
    u32 selected_valid;
    u32 compared_records;
};

struct recovered_scheduler_recovery_search_84bb4
recovered_scheduler_recovery_search_84bb4(int32_t target,
                                          const int32_t records[8])
{
    struct recovered_scheduler_recovery_search_84bb4 out = {
        0U, 0U, 0U, 0U
    };
    int32_t working_target = target;
    u32 index;

    for (index = 0U; index < 8U; ++index) {
        out.compared_records++;
        /* -1 is the recovery loop's explicit select-current-record sentinel. */
        if (working_target == -1 || working_target > records[index]) {
            out.selected_index = index;
            out.selected_value = records[index];
            out.selected_valid = 1U;
            working_target = records[index];
        }
    }
    return out;
}
