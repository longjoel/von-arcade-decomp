/* Mode-1 phase-table arm 0 recovered from i960 0x2b500-0x2b548.
 *
 * The attract-sequence entry arm: runs the text/video helper 0x1c220, the
 * 0x1bda0 helper, a 0x8000 command-0 doorbell through 0x1ccf8, and the two
 * geometry/status helpers 0x6f9e8/0x6fa48; then stores g14 (zero across the
 * call ABI, runtime-confirmed) to 0x51aac4 and 0x503aac, stores g0 to
 * 0x51c850, and advances 0x503a00.
 *
 * Observed on the original attract (von/tools/probe_mode1_handlers.py):
 * phase 0 -> 1; 0x51aac4, 0x503aac and 0x51c850 all stay zero, while the
 * helpers fill 0x51c864..0x51c95c with 1..0x3f and reset 0x504cdc/e0/e4.
 */
#include <stdint.h>

struct recovered_startup_mode1_phase0_result_2b500 {
    uint32_t phase;    /* 0x503a00 */
    uint32_t clear_a;  /* 0x51aac4 = 0 */
    uint32_t clear_b;  /* 0x503aac = 0 */
    uint32_t work;     /* 0x51c850 = g0 */
};

void recovered_startup_mode1_phase0_run_2b500(
    uint32_t phase, uint32_t helper_g0,
    struct recovered_startup_mode1_phase0_result_2b500 *out)
{
    out->phase = phase + 1U;     /* 0x2b514-0x2b520 st g4,0x503a00 */
    out->clear_a = 0U;           /* 0x2b530 st g14,0x51aac4 */
    out->clear_b = 0U;           /* 0x2b538 st g14,0x503aac */
    out->work = helper_g0;       /* 0x2b540 st g0,0x51c850 */
}
