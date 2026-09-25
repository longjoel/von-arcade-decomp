/* Mode-1 phase-table arm 13 recovered from i960 0xe3ab0-0xe3b28.
 *
 * The arm reads the device status byte at 0x1d00026. When it is zero the arm
 * just advances VON_MODE_PHASE (0x503a00) by two. Otherwise it clamps the
 * status sub-state at 0x5783b4 into 0..2 (wrapping higher values to zero),
 * dispatches one of three sub-functions by that value, and stores value+1.
 *
 * Runtime probe (original input-free attract, `probe_e3ab0`): at the single
 * attract pass the entry sub-state is 0 with 0x1d00026 = 1 and the arm
 * dispatches 0xe3b70, then stores 1. The listing's branch ladder maps
 * 1 -> 0xe3dc0 and 2 -> 0xe3f30; `boot-path.md` previously read state 0 as
 * 0xe3dc0, which this probe corrects.
 *
 * The dispatch target is reported as an enum; the three sub-functions are
 * separate units and are not modeled here.
 */
#include <stdint.h>

enum {
    RECOVERED_E3AB0_DISPATCH_E3B70 = 1,
    RECOVERED_E3AB0_DISPATCH_E3DC0 = 2,
    RECOVERED_E3AB0_DISPATCH_E3F30 = 3
};

struct recovered_startup_mode1_phase13_result_e3ab0 {
    uint32_t phase;         /* 0x503a00 */
    uint32_t substate;      /* 0x5783b4 after the arm */
    uint32_t dispatched;    /* one of RECOVERED_E3AB0_DISPATCH_* */
    uint32_t device_status; /* 0x1d00026 byte */
    uint32_t early;         /* 1 when the device byte was zero */
};

void recovered_startup_mode1_phase13_run_e3ab0(
    uint32_t phase, uint32_t device_status, uint32_t substate,
    struct recovered_startup_mode1_phase13_result_e3ab0 *out)
{
    out->device_status = device_status;
    out->phase = phase;
    out->substate = substate;
    out->dispatched = 0U;
    out->early = 0U;

    if (device_status == 0U) {
        out->phase = phase + 2U;   /* 0xe3abc-0xe3ac8, then 0xe3ad0 ret */
        out->early = 1U;
        return;
    }

    {
        uint32_t const clamped = (substate <= 2U) ? substate : 0U;  /* 0xe3adc-0xe3ae0 */
        out->substate = clamped + 1U;                               /* 0xe3b20 */
        if (clamped == 1U)
            out->dispatched = RECOVERED_E3AB0_DISPATCH_E3DC0;       /* 0xe3b00 */
        else if (clamped == 2U)
            out->dispatched = RECOVERED_E3AB0_DISPATCH_E3F30;       /* 0xe3b08 */
        else
            out->dispatched = RECOVERED_E3AB0_DISPATCH_E3B70;       /* 0xe3b10 */
    }
}
