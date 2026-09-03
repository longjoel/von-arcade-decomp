#ifndef VON_RECOVERED_OBJECT_STATE_PIPELINE_H
#define VON_RECOVERED_OBJECT_STATE_PIPELINE_H

typedef unsigned int recovered_object_state_u32;

struct recovered_object_state_context
{
    recovered_object_state_u32 state;
    recovered_object_state_u32 timer_bits;
    recovered_object_state_u32 mode_bits;
    recovered_object_state_u32 role_d94;
    recovered_object_state_u32 object_d68;
    recovered_object_state_u32 related_state;
    recovered_object_state_u32 related_tag;
    recovered_object_state_u32 global_state;
    recovered_object_state_u32 global_substate;
    recovered_object_state_u32 caller_state;
};

recovered_object_state_u32 recovered_object_state_dispatch(
    const struct recovered_object_state_context *context,
    recovered_object_state_u32 *transition);
recovered_object_state_u32 recovered_object_state_runtime_tick(void);

#endif
