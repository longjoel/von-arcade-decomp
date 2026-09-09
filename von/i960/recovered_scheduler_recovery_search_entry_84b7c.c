/* Recovery-search entry bridge recovered from i960 0x84b7c-0x84bb4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_search_entry_84b7c {
    u32 exits_to_84d60;
    u32 writes_509a6c;
    u32 value_509a6c;
    u32 search_index;
    u32 enters_search_84bb4;
};

struct recovered_scheduler_recovery_search_entry_84b7c
recovered_scheduler_recovery_search_entry_84b7c(u32 gate_continues)
{
    struct recovered_scheduler_recovery_search_entry_84b7c out = {
        gate_continues == 0U ? 1U : 0U, 0U, 0U, 0U, 0U
    };

    if (out.exits_to_84d60 == 0U) {
        out.writes_509a6c = 1U;
        out.value_509a6c = 1U;
        out.enters_search_84bb4 = 1U;
    }
    return out;
}
