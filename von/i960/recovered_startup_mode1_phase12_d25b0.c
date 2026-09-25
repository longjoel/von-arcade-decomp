/* Mode-1 phase-table arm 12 recovered from i960 0xd25b0-0xd25ec.
 *
 * A status-selector dispatcher on 0x577280: 0 -> 0xd0970, 1 -> 0xd0e60,
 * 2 -> 0xd13b0, anything else -> 0xd1be0. Each sub-function returns directly
 * to the caller.
 *
 * Runtime probe (von/tools/probe_mode1_handlers.py): at the attract phase-12
 * entry the selector is 0, so the arm dispatches 0xd0970.
 */
#include <stdint.h>

enum {
    RECOVERED_D25B0_D0970 = 1,
    RECOVERED_D25B0_D0E60 = 2,
    RECOVERED_D25B0_D13B0 = 3,
    RECOVERED_D25B0_D1BE0 = 4
};

struct recovered_startup_mode1_phase12_result_d25b0 {
    uint32_t dispatched; /* RECOVERED_D25B0_* */
};

void recovered_startup_mode1_phase12_run_d25b0(
    uint32_t selector, struct recovered_startup_mode1_phase12_result_d25b0 *out)
{
    if (selector == 0U)
        out->dispatched = RECOVERED_D25B0_D0970;   /* 0xd25d0 */
    else if (selector == 1U)
        out->dispatched = RECOVERED_D25B0_D0E60;   /* 0xd25d8 */
    else if (selector == 2U)
        out->dispatched = RECOVERED_D25B0_D13B0;   /* 0xd25e0 */
    else
        out->dispatched = RECOVERED_D25B0_D1BE0;   /* 0xd25e8 */
}
