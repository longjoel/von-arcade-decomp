/* Mode-1 phase-table arm 10 recovered from i960 0xd24b0-0xd255c.
 *
 * This is the attract "VR / machine-select" arm: it sets the arena selector
 * (0x5770f0) to 13, stores the two mode words 0x503ab4/0x503ab8, clears the
 * eight 0x57727x continuation slots and the two 0x503a7c/0x503a20 latches
 * (g14 is zero across the call ABI here, confirmed by the runtime probe), runs
 * the text/video helper and two command sends, then advances 0x503a00.
 *
 * Net effect from the original attract probe (von/tools/probe_mode1_handlers.py):
 * phase 10 -> 11, 0x5770f0 3 -> 13, 0x503ab4 0x64 -> 0x73, and the cleared
 * slots unchanged at zero.
 */
#include <stdint.h>

struct recovered_startup_mode1_phase10_result_d24b0 {
    uint32_t phase;      /* 0x503a00 */
    uint32_t selector;   /* 0x5770f0 = 13 */
    uint32_t mode_a;     /* 0x503ab4 = 0x73 */
    uint32_t mode_b;     /* 0x503ab8 = 0x258 */
    uint32_t cleared;    /* zero stored to 0x5771d4, 0x577268, 0x577270..7e,
                            0x503a7c and 0x503a20 */
};

void recovered_startup_mode1_phase10_run_d24b0(
    uint32_t phase, struct recovered_startup_mode1_phase10_result_d24b0 *out)
{
    out->phase = phase + 1U;   /* 0xd2550-0xd2554 st g4,0x503a00 */
    out->selector = 13U;       /* 0xd24b0-0xd24c4 st g1,0x5770f0 */
    out->mode_a = 0x73U;       /* 0xd24e0-0xd24e4 st g1,0x503ab4 */
    out->mode_b = 0x258U;      /* 0xd24ec-0xd24f0 st g1,0x503ab8 */
    out->cleared = 0U;         /* 0xd24b4..d2530 and 0xd2540..d2548 st g14 */
}
