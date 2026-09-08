/* Counter update recovered from i960 0x848d0-0x8490c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_counter_update_848d0 {
    u32 writes_509a6c;
    u32 continues_to_8490c;
    int32_t value_509a6c;
};

struct recovered_scheduler_counter_update_848d0
recovered_scheduler_counter_update_848d0(int32_t value_509a6c,
                                         int32_t value_503a14)
{
    struct recovered_scheduler_counter_update_848d0 out = {
        0U, 0U, value_509a6c
    };

    if (value_509a6c >= 0) {
        out.value_509a6c = value_509a6c + 1;
        if (out.value_509a6c > 120)
            out.value_509a6c = 0;
        out.writes_509a6c = 1U;
    } else if (value_503a14 > 239) {
        out.continues_to_8490c = 1U;
    }
    return out;
}
