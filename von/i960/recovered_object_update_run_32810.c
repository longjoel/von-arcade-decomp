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

/* Real locomotion arms replace the stubs for the indices that produce
 * movement; the remaining arms are still stubs. */
void recovered_locomotion_action_0_run(volatile unsigned char *object);
void recovered_locomotion_action_12_run(volatile unsigned char *object);
void recovered_locomotion_state_31_run(volatile unsigned char *object);
void recovered_locomotion_state_34_run(volatile unsigned char *object);
void recovered_state_attack_2_run(volatile unsigned char *object);
void recovered_state_attack_3_run(volatile unsigned char *object);
void recovered_state_attack_4_run(volatile unsigned char *object);
void recovered_state_attack_5_run(volatile unsigned char *object);
void recovered_state_attack_6_run(volatile unsigned char *object);
void recovered_state_attack_7_run(volatile unsigned char *object);
void recovered_state_attack_8_run(volatile unsigned char *object);
void recovered_state_attack_9_run(volatile unsigned char *object);
void recovered_state_attack_11_run(volatile unsigned char *object);
void recovered_state_locomotion_0_run(volatile unsigned char *object);
void recovered_state_locomotion_1_run(volatile unsigned char *object);
void recovered_state_locomotion_15_run(volatile unsigned char *object);
void recovered_state_locomotion_16_run(volatile unsigned char *object);
void recovered_state_locomotion_17_run(volatile unsigned char *object);
void recovered_state_locomotion_32_run(volatile unsigned char *object);
void recovered_state_locomotion_36_run(volatile unsigned char *object);
void recovered_state_dash_20_run(volatile unsigned char *object);
void recovered_state_21_run(volatile unsigned char *object);

static void recovered_object_update_32810_state_locomotion(
    volatile unsigned char *object, u16 state)
{
    switch (state)
    {
    case 0U: recovered_state_locomotion_0_run(object); break;
    case 1U: recovered_state_locomotion_1_run(object); break;
    case 15U: recovered_state_locomotion_15_run(object); break;
    case 16U: recovered_state_locomotion_16_run(object); break;
    case 17U: recovered_state_locomotion_17_run(object); break;
    case 32U: recovered_state_locomotion_32_run(object); break;
    case 36U: recovered_state_locomotion_36_run(object); break;
    default: break;
    }
}

static void recovered_object_update_32810_state_attack(
    volatile unsigned char *object, u16 state)
{
    switch (state)
    {
    case 2U: recovered_state_attack_2_run(object); break;
    case 3U: recovered_state_attack_3_run(object); break;
    case 4U: recovered_state_attack_4_run(object); break;
    case 5U: recovered_state_attack_5_run(object); break;
    case 6U: recovered_state_attack_6_run(object); break;
    case 7U: recovered_state_attack_7_run(object); break;
    case 8U: recovered_state_attack_8_run(object); break;
    case 9U: recovered_state_attack_9_run(object); break;
    case 11U: recovered_state_attack_11_run(object); break;
    default: break;
    }
}

u32 recovered_object_update_32810_state_count(void)
{
    return 43U;
}

void recovered_object_update_32810_run(volatile unsigned char *object)
{
    u16 action = *(volatile u16 *)(object + 0x1b2);
    u16 state = *(volatile u16 *)(object + 0x172);
    union {
        u32 bits;
        float value;
    } x, z, vx, vz;

    if (action <= 13U)
    {
        if (action == 0U)
            recovered_locomotion_action_0_run(object);
        else if (action == 12U)
            recovered_locomotion_action_12_run(object);
        else
            recovered_object_update_32810_actions[action](object);
    }
    if ((state & 0x8000U) == 0U && state <= 42U)
    {
        if (state == 31U)
            recovered_locomotion_state_31_run(object);
        else if (state == 34U)
            recovered_locomotion_state_34_run(object);
        else if (state == 20U)
            recovered_state_dash_20_run(object);
        else if (state == 21U)
            recovered_state_21_run(object);
        else if (state >= 2U && state <= 11U)
            recovered_object_update_32810_state_attack(object, state);
        else if (state == 0U || state == 1U || state == 15U || state == 16U ||
                 state == 17U || state == 32U || state == 36U)
            recovered_object_update_32810_state_locomotion(object, state);
        else
            recovered_object_update_32810_states[state](object);
    }

    /* i960 `addr` is add-real: object+0x08/+0x10 += object+0x1c8/+0x1cc. */
    x.bits = *(volatile u32 *)(object + 0x08);
    z.bits = *(volatile u32 *)(object + 0x10);
    vx.bits = *(volatile u32 *)(object + 0x1c8);
    vz.bits = *(volatile u32 *)(object + 0x1cc);
    x.value += vx.value;
    z.value += vz.value;
    *(volatile u32 *)(object + 0x08) = x.bits;
    *(volatile u32 *)(object + 0x10) = z.bits;
}
