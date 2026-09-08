/* Capture-derived first attract scheduler tick around i960 0x79050. */

#include <stdint.h>

#include "recovered_object_state_pipeline.h"

#define ATTRACT_OBJECT  ((volatile unsigned int *)0x005040d0U)
#define GLOBAL_TIMER    (*(volatile unsigned int *)0x00504d60U)
#define GLOBAL_MODE     (*(volatile unsigned int *)0x00504e30U)
#define GLOBAL_ROLE     (*(volatile unsigned int *)0x00504d94U)
#define GLOBAL_OBJECT   (*(volatile unsigned int *)0x00504d68U)
#define GLOBAL_STATE    (*(volatile unsigned int *)0x00504d9cU)
#define GLOBAL_SUBSTATE (*(volatile unsigned int *)0x00504e4cU)
#define GLOBAL_TRANSITION (*(volatile unsigned int *)0x00504d98U)

/*
 * Pointer-accurate adapter for 0x79050.  The ROM receives the object in g0,
 * loads the related-object pointer from object+0x74 into r4, then uses r5 and
 * r4 independently throughout the state arms and common tail.
 */
recovered_object_state_u32
recovered_object_state_runtime_tick_for_object(volatile unsigned char *object)
{
    struct recovered_object_state_context context;
    /* The ROM pointer field is one i960 word, even when this adapter is
     * compiled on a 64-bit host. */
    uintptr_t related_address =
        (uintptr_t)*(volatile uint32_t *)(object + 0x74U);
    volatile unsigned char *related =
        (volatile unsigned char *)related_address;
    recovered_object_state_u32 caller_state = recovered_random_next();
    recovered_object_state_u32 transition = GLOBAL_TRANSITION;

    context.state = *(volatile unsigned int *)(object + 0x64U);
    context.timer_bits = GLOBAL_TIMER;
    context.mode_bits = GLOBAL_MODE;
    context.role_d94 = GLOBAL_ROLE;
    context.object_d68 = GLOBAL_OBJECT;
    context.related_state = *(volatile unsigned int *)(related + 0x64U);
    context.related_tag = *(volatile unsigned short *)
        (related + 0x172U);
    context.global_state = GLOBAL_STATE;
    context.global_substate = GLOBAL_SUBSTATE;
    /* 0xf5058 advances 0x5785d0 and returns the new value in g0. */
    context.caller_state = caller_state;

    if (recovered_object_state_dispatch(&context, &transition) == 0U)
        return 0U;
    GLOBAL_TRANSITION = transition;
    return 1U;
}

/* The current reconstructed attract harness has one capture-derived object. */
recovered_object_state_u32 recovered_object_state_runtime_tick(void)
{
    return recovered_object_state_runtime_tick_for_object(
        (volatile unsigned char *)0x005040d0U);
}
