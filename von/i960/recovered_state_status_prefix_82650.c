/* Early status prefix recovered from i960 0x82650-0x826ac. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_status_prefix_82650 {
    u32 terminal;
    u32 status_504d80;
};

struct recovered_state_status_prefix_82650
recovered_state_status_prefix_82650(int32_t r5, int32_t r6,
                                    int32_t global_504d70)
{
    struct recovered_state_status_prefix_82650 out = {0U, 0U};

    if (r5 == 0 && r6 == 0) {
        out.terminal = 1U;
        out.status_504d80 = 8U;
    } else if (r5 == 0 && r6 == 1) {
        out.terminal = 1U;
        out.status_504d80 = global_504d70 > 4 ? 4U : 3U;
    }
    return out;
}
