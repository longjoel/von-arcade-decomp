/* Mode-1 phase-table arm 11 recovered from i960 0xd2560-0xd25ac.
 *
 * A guarded status-selector dispatcher. It first calls 0xc8fa0; when that
 * returns nonzero the arm returns without doing anything. Otherwise it reads
 * the selector at 0x577280 and dispatches: 0 -> 0xd0820, 1 -> 0xd0d10,
 * 2 -> 0xd1280, anything else -> 0xd1ab0, then calls 0x20460.
 *
 * Runtime probe (von/tools/probe_mode1_handlers.py): at the attract phase-11
 * entry the selector is 0 and the guard proceeds, so the arm dispatches
 * 0xd0820 and the follow-up.
 */
#include <stdint.h>

enum {
    RECOVERED_D2560_D0820 = 1,
    RECOVERED_D2560_D0D10 = 2,
    RECOVERED_D2560_D1280 = 3,
    RECOVERED_D2560_D1AB0 = 4
};

struct recovered_startup_mode1_phase11_result_d2560 {
    uint32_t early;      /* 1 when the 0xc8fa0 guard was nonzero */
    uint32_t dispatched; /* RECOVERED_D2560_* */
    uint32_t followup;   /* 1 when 0x20460 was called */
};

void recovered_startup_mode1_phase11_run_d2560(
    uint32_t guard, uint32_t selector,
    struct recovered_startup_mode1_phase11_result_d2560 *out)
{
    out->early = 0U;
    out->dispatched = 0U;
    out->followup = 0U;

    if (guard != 0U) {          /* 0xd2560-0xd2568 */
        out->early = 1U;
        return;
    }
    /* 0xd256c-0xd25a4 branch ladder. */
    if (selector == 1U)
        out->dispatched = RECOVERED_D2560_D0D10;
    else if (selector == 0U)
        out->dispatched = RECOVERED_D2560_D0820;
    else if (selector == 2U)
        out->dispatched = RECOVERED_D2560_D1280;
    else
        out->dispatched = RECOVERED_D2560_D1AB0;
    out->followup = 1U;         /* 0xd25a8 call 0x20460 */
}
