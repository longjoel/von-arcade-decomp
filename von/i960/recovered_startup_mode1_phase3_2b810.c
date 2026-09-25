/* Mode-1 phase-table arm 3 recovered from i960 0x2b810-0x2b868.
 *
 * The arm increments VON_MODE_PHASE (0x503a00), runs the text/video helpers
 * (0x1c618 and the 0x7fff doorbell through 0x1ccf8), publishes the ORed video
 * and text attribute words through 0x100a004, 0x504d28 and 0x504d30, then
 * stores the 0x1f060 result (returned in g14) into the progress word 0x503a04.
 *
 * The helper result registers are explicit inputs so this model is independent
 * of the helper implementations. The original input-free attract fixture
 * (von/build/disasm/mode-transitions.log) leaves g4 = g1 = g14 = 0 and yields
 * video/text attributes 0x200/0x200/0x4000 with a cleared progress word; the
 * same fixture confirms the phase 3 -> 4 transition and the 0x503a04 clear.
 */
#include <stdint.h>

struct recovered_startup_mode1_phase3_result_2b810 {
    uint32_t phase;      /* 0x503a00, phase + 1 */
    uint32_t video_attr;  /* 0x100a004, (helper g4) | (1 << 9) */
    uint32_t text_attr;   /* 0x504d28, (helper g4) | (1 << 9) */
    uint32_t text_attr2;  /* 0x504d30, (helper g1) | (1 << 14) */
    uint32_t progress;    /* 0x503a04, 0x1f060 result from g14 */
};

void recovered_startup_mode1_phase3_run_2b810(
    uint32_t phase, uint32_t helper_g4, uint32_t helper_g1,
    uint32_t helper_g14,
    struct recovered_startup_mode1_phase3_result_2b810 *out)
{
    uint32_t const attr_g4 = helper_g4 | (1U << 9);   /* 0x2b834 setbit 9,0,g4 */
    uint32_t const attr_g1 = helper_g1 | (1U << 14);  /* 0x2b840 setbit 14,0,g1 */

    out->phase = phase + 1U;   /* 0x2b81c st g4,0x503a00 */
    out->video_attr = attr_g4; /* 0x2b838 stos g4,0x100a004 */
    out->text_attr = attr_g4;  /* 0x2b844 stos g4,0x504d28 */
    out->text_attr2 = attr_g1; /* 0x2b84c stos g1,0x504d30 */
    out->progress = helper_g14;/* 0x2b858 st g14,0x503a04 */
}
