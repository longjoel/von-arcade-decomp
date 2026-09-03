/* Capture-derived first attract scheduler tick around i960 0x79050. */

#include "recovered_object_state_pipeline.h"

#define ATTRACT_OBJECT  ((volatile unsigned int *)0x005040d0U)
#define ATTRACT_RELATED ((volatile unsigned int *)0x00503ad0U)
#define GLOBAL_TIMER    (*(volatile unsigned int *)0x00504d60U)
#define GLOBAL_MODE     (*(volatile unsigned int *)0x00504e30U)
#define GLOBAL_ROLE     (*(volatile unsigned int *)0x00504d94U)
#define GLOBAL_OBJECT   (*(volatile unsigned int *)0x00504d68U)
#define GLOBAL_STATE    (*(volatile unsigned int *)0x00504d9cU)
#define GLOBAL_SUBSTATE (*(volatile unsigned int *)0x00504e4cU)
#define GLOBAL_TRANSITION (*(volatile unsigned int *)0x00504d98U)

/* These object addresses are capture-derived, not a generalized pool model. */
recovered_object_state_u32 recovered_object_state_runtime_tick(void)
{
    struct recovered_object_state_context context;
    recovered_object_state_u32 transition = GLOBAL_TRANSITION;

    context.state = ATTRACT_OBJECT[0x64U / 4U];
    context.timer_bits = GLOBAL_TIMER;
    context.mode_bits = GLOBAL_MODE;
    context.role_d94 = GLOBAL_ROLE;
    context.object_d68 = GLOBAL_OBJECT;
    context.related_state = ATTRACT_RELATED[0x64U / 4U];
    context.related_tag = *(volatile unsigned short *)
        ((unsigned long)ATTRACT_RELATED + 0x172U);
    context.global_state = GLOBAL_STATE;
    context.global_substate = GLOBAL_SUBSTATE;
    /* State zero does not consume caller_state; later arms remain gated. */
    context.caller_state = 0U;

    if (recovered_object_state_dispatch(&context, &transition) == 0U)
        return 0U;
    GLOBAL_TRANSITION = transition;
    return 1U;
}
