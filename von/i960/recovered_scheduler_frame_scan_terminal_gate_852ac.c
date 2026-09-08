/* Terminal count gate recovered from i960 0x852ac-0x852b4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_scan_terminal_gate_852ac {
    u32 r5;
    u32 r7;
    u32 exits_to_853a0;
    u32 continues_to_852b4;
};

struct recovered_scheduler_frame_scan_terminal_gate_852ac
recovered_scheduler_frame_scan_terminal_gate_852ac(u32 r5, u32 r7)
{
    struct recovered_scheduler_frame_scan_terminal_gate_852ac out = {
        r5, r7, 0U, 0U
    };

    /* cmpibge 2,r5 and cmpibge 1,r7 are literal-first. */
    out.exits_to_853a0 = (r5 <= 2U || r7 <= 1U) ? 1U : 0U;
    out.continues_to_852b4 = out.exits_to_853a0 == 0U ? 1U : 0U;
    return out;
}
