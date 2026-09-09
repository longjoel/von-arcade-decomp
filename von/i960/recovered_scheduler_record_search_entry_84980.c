/* Record-search entry bridge recovered from i960 0x84980-0x84994. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_record_search_entry_84980 {
    u32 zero_product_exit_84b08;
    u32 writes_509a6c;
    u32 value_509a6c;
    u32 search_index;
    u32 enters_search_84994;
};

struct recovered_scheduler_record_search_entry_84980
recovered_scheduler_record_search_entry_84980(int32_t scaled_value)
{
    struct recovered_scheduler_record_search_entry_84980 out = {
        scaled_value == 0 ? 1U : 0U,
        0U, 0U, 0U, 0U
    };

    if (out.zero_product_exit_84b08 == 0U) {
        out.writes_509a6c = 1U;
        out.value_509a6c = 1U;
        out.enters_search_84994 = 1U;
    }
    return out;
}
