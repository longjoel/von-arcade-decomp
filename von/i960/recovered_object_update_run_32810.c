/* Runnable geometry object-update backbone recovered from i960 0x32810.
 *
 * Reproduces the per-object update call structure: dispatch the 14-entry
 * action arm table on object+0x1b2, dispatch the 43-entry state handler table
 * on object+0x172 (masked, 0..42), then integrate position with velocity
 * (object+0x08/+0x10 += object+0x1c8/+0x1cc). The individual action/state arm
 * bodies and the geometry projection call remain stubbed no-ops in this
 * development backbone.
 */

typedef unsigned int u32;
typedef unsigned short u16;

typedef void (*recovered_object_update_32810_arm)(volatile unsigned char *object);

static void recovered_object_update_32810_stub(volatile unsigned char *object)
{
    (void)object;
}

static const recovered_object_update_32810_arm recovered_object_update_32810_actions[14] = {
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub
};

static const recovered_object_update_32810_arm recovered_object_update_32810_states[43] = {
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub, recovered_object_update_32810_stub,
    recovered_object_update_32810_stub
};

u32 recovered_object_update_32810_action_count(void)
{
    return 14U;
}

u32 recovered_object_update_32810_state_count(void)
{
    return 43U;
}

void recovered_object_update_32810_run(volatile unsigned char *object)
{
    u16 action = *(volatile u16 *)(object + 0x1b2);
    u16 state = *(volatile u16 *)(object + 0x172);

    if (action <= 13U)
        recovered_object_update_32810_actions[action](object);
    if ((state & 0x8000U) == 0U && state <= 42U)
        recovered_object_update_32810_states[state](object);

    *(volatile u32 *)(object + 0x08) += *(volatile u32 *)(object + 0x1c8);
    *(volatile u32 *)(object + 0x10) += *(volatile u32 *)(object + 0x1cc);
}
