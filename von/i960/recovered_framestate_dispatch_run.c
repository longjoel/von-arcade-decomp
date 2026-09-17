/* Runnable 0x371e0 frame-step entry: binds 0x37130 to the recovered arm bodies.
 *
 * The table is the observed 0x37130 target table. Entries the ROM leaves zero,
 * and states whose arm is not yet recovered, are null and skipped by the core,
 * matching `ld 0x37130[state]; cmpibe 0` at 0x37378. State 0 is the committed
 * action -> state-31 transition (0x36460, recovered_action_31.c); the remaining
 * non-null entries are the 0x37130 locomotion/air arms
 * (recovered_framestate_arms.c).
 */

#include "recovered_framestate_dispatch.h"

recovered_framestate_u32 recovered_action_31_run(volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_15_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_16_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_17_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_19_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_air_23_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_landing_24_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_26_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_28_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_landing_29_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_31_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_state_33_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_air_35_run(
    volatile unsigned char *object);
recovered_framestate_u32 recovered_framestate_air_37_run(
    volatile unsigned char *object);

static const recovered_framestate_arm recovered_framestate_arms_37130[43] = {
    [0] = recovered_action_31_run,
    [15] = recovered_framestate_state_15_run,
    [16] = recovered_framestate_state_16_run,
    [17] = recovered_framestate_state_17_run,
    [19] = recovered_framestate_state_19_run,
    [23] = recovered_framestate_air_23_run,
    [24] = recovered_framestate_landing_24_run,
    [26] = recovered_framestate_state_26_run,
    [28] = recovered_framestate_state_28_run,
    [29] = recovered_framestate_landing_29_run,
    [31] = recovered_framestate_state_31_run,
    [33] = recovered_framestate_state_33_run,
    [35] = recovered_framestate_air_35_run,
    [37] = recovered_framestate_air_37_run,
};

recovered_framestate_u32 recovered_framestate_dispatch_run(
    volatile unsigned char *object)
{
    return recovered_framestate_dispatch_core(
        object, recovered_framestate_arms_37130, 43U);
}
