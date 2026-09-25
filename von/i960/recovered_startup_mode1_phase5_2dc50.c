/* Mode-1 phase-table arm 5 recovered from i960 0x2dc50-0x2dd28.
 *
 * This is the attract "stage intro" arm. It runs the text/video helper and a
 * command-0 doorbell, calls the 0x296d0 service, stores the fixed status/audio
 * words, samples the random helper 0xf5058 three times and masks each result
 * with 7 (into 0x503a98, 0x503a9c and the arena selector 0x5770f0), then
 * advances 0x503a00. g14 is zero across the call ABI here (runtime probe), so
 * the 0x503a18/0x503a84/0x503a64/0x503a68/0x51aae8/0x51aaf0/0x503a7c/
 * 0x504b96 stores are zero clears.
 *
 * Observed on the original attract (von/tools/probe_mode1_handlers.py):
 * phase 5 -> 6, 0x503a80 = 4, 0x503ab0 = 0xff, 0x51aaf4 = 0x870,
 * 0x51aaf8/0x51aafc/0x51ab00 = 1, 0x503a9c = 5, 0x5770f0 = 3.
 */
#include <stdint.h>

struct recovered_startup_mode1_phase5_result_2dc50 {
    uint32_t phase;      /* 0x503a00 */
    uint32_t selector;   /* 0x5770f0 = rng3 & 7 */
    uint32_t status_a80; /* 0x503a80 = 4 */
    uint32_t status_ab0; /* 0x503ab0 = 0xff */
    uint32_t rng_a98;    /* 0x503a98 = rng1 & 7 */
    uint32_t rng_a9c;    /* 0x503a9c = rng2 & 7 */
    uint32_t audio_f4;   /* 0x51aaf4 = 0x870 */
    uint32_t audio_f8;   /* 0x51aaf8 = 1 */
    uint32_t audio_fc;   /* 0x51aafc = 1 */
    uint32_t audio_00;   /* 0x51ab00 = 1 */
    uint32_t cleared;    /* zeros */
};

void recovered_startup_mode1_phase5_run_2dc50(
    uint32_t phase, uint32_t rng1, uint32_t rng2, uint32_t rng3,
    struct recovered_startup_mode1_phase5_result_2dc50 *out)
{
    out->phase = phase + 1U;          /* 0x2dd14-0x2dd20 st g4,0x503a00 */
    out->status_a80 = 4U;             /* 0x2dc98-0x2dcac st g1,0x503a80 */
    out->status_ab0 = 0xffU;          /* 0x2dc78-0x2dc7c st g1,0x503ab0 */
    out->rng_a98 = rng1 & 7U;         /* 0x2dcb4-0x2dcbc and/st 0x503a98 */
    out->rng_a9c = rng2 & 7U;         /* 0x2dcc4-0x2dccc and/st 0x503a9c */
    out->selector = rng3 & 7U;        /* 0x2dd10-0x2dd18 and/st 0x5770f0 */
    out->audio_f4 = 0x870U;           /* 0x2dcd8-0x2dcdc st g1,0x51aaf4 */
    out->audio_f8 = 1U;               /* 0x2dc84-0x2dc88 st g1,0x51aaf8 */
    out->audio_fc = 1U;               /* 0x2dc90 st g1,0x51aafc */
    out->audio_00 = 1U;               /* 0x2dce4-0x2dce8 st g1,0x51ab00 */
    out->cleared = 0U;                /* 0x2dc60..dca4, 0x2dcf0, 0x2dd00, 0x2dd08 */
}
