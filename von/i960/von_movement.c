/*
 * Shared Virtual-On movement kernel. See von_movement.h for the contract.
 *
 * This is the single source of truth for the locomotion tick: the committed
 * action -> state 31 transition (recovered at 0x36460 / recovered_action_31.c),
 * the cruise speed selection from the cfg+0x56c/0x570/0x574 triplet by
 * +0x176 (recovered in recovered_locomotion_states.c), and the position
 * integration (recovered in recovered_object_update_32810.c).
 *
 * The i960 build runs it against the real object and lets the SHARC velocity
 * unit own VON_OBJ_VEL_X/VEL_Z (trig == NULL); the host build computes the
 * velocity itself from the facing with the env->trig callback.
 */

#include "von_movement.h"

#include <stddef.h>

static uint16_t von_mv_ld16(const uint8_t *object, uint32_t offset)
{
    return *(const uint16_t *)(object + offset);
}

static void von_mv_st16(uint8_t *object, uint32_t offset, uint16_t value)
{
    *(uint16_t *)(object + offset) = value;
}

static uint32_t von_mv_ld32(const uint8_t *object, uint32_t offset)
{
    return *(const uint32_t *)(object + offset);
}

static void von_mv_st32(uint8_t *object, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(object + offset) = value;
}

typedef union { uint32_t bits; float value; } von_mv_f32;

static float von_mv_float(uint32_t bits)
{
    von_mv_f32 u;
    u.bits = bits;
    return u.value;
}

static uint32_t von_mv_bits(float value)
{
    von_mv_f32 u;
    u.value = value;
    return u.bits;
}

static uint32_t von_mv_cfg_u32(const uint8_t *config, uint32_t offset)
{
    return von_mv_ld32(config, offset);
}

int von_movement_commit(uint8_t *object, const VonMovementEnv *env)
{
    uint32_t action = (uint32_t)object[VON_OBJ_COMMITTED] & 0xffu;
    int16_t facing;
    uint32_t select;

    if (action == VON_ACTION_NONE)
        return 0;

    /* 0x3649c-0x364fc. */
    von_mv_st16(object, VON_OBJ_STATE, (uint16_t)VON_STATE_CRUISE);
    von_mv_st16(object, VON_OBJ_MODE, 0u);

    select = (uint32_t)env->dir_18350[action];
    von_mv_st16(object, VON_OBJ_DIR_SELECT, (uint16_t)select);
    von_mv_st16(object, VON_OBJ_SELECTOR_188, (uint16_t)select);

    facing = (int16_t)von_mv_ld16(object, VON_OBJ_FACING);
    von_mv_st16(object, VON_OBJ_TURN_TARGET,
        (uint16_t)(facing + (int16_t)env->dir_18360[action]));
    von_mv_st16(object, VON_OBJ_HALF_HEADING, 0u);
    return 1;
}

int von_movement_tick(uint8_t *object, const VonMovementEnv *env)
{
    const uint8_t *config = env->config != NULL
        ? env->config
        : (const uint8_t *)(uintptr_t)von_mv_ld32(object, VON_OBJ_CONFIG);
    uint32_t select;
    uint32_t speed;
    float vx, vz;
    uint16_t state_before = von_mv_ld16(object, VON_OBJ_STATE);

    (void)von_movement_commit(object, env);

    if (von_mv_ld16(object, VON_OBJ_STATE) != (uint16_t)VON_STATE_CRUISE)
        return 0;

    /* 0x36500-0x36508: the clip cursor restarts when the cruise state is
     * entered, then advances one frame per tick (the ROM's 0x51ab10 cursor
     * rule). The host reads it to phase the clip. */
    if (state_before != (uint16_t)VON_STATE_CRUISE)
        von_mv_st16(object, VON_OBJ_CLIP_COUNTER, 0u);
    von_mv_st16(object, VON_OBJ_CLIP_COUNTER,
        (uint16_t)(von_mv_ld16(object, VON_OBJ_CLIP_COUNTER) + 1u));

    /* 0x30ad4-0x30c18: the cruise speed is a (selector, select) pair, matching
     * recovered_locomotion_state31_speed. The selector is object+0x174 (the
     * movement mode the state machine sets); select is +0x176 (dir_18350). */
    select = von_mv_ld16(object, VON_OBJ_DIR_SELECT);
    switch (von_mv_ld16(object, VON_OBJ_MOVE_SELECTOR)) {
    case 1u:
        speed = von_mv_cfg_u32(config,
            select == 0u ? 0x57cu : select == 1u ? 0x580u : 0x578u);
        break;
    case 2u:
        speed = von_mv_cfg_u32(config,
            select == 0u ? 0x588u : select == 1u ? 0x58cu : 0x584u);
        break;
    case 3u:
        speed = von_mv_cfg_u32(config,
            select == 0u ? 0x594u : select == 1u ? 0x598u : 0x590u);
        break;
    default:
        speed = von_mv_cfg_u32(config,
            select == 0u ? VON_CFG_SPEED_SEL1
                         : select == 1u ? VON_CFG_SPEED_SEL2
                                        : VON_CFG_SPEED_DEFAULT);
        break;
    }
    von_mv_st32(object, VON_OBJ_SPEED, speed);

    if (env->trig != NULL) {
        float sine, cosine;
        uint32_t action = (uint32_t)object[VON_OBJ_COMMITTED] & 0xffu;
        uint32_t heading =
            (uint32_t)(int16_t)von_mv_ld16(object, VON_OBJ_FACING);

        /* The action's heading offset (0x18360: 0 forward, 0x8000 back,
         * 0x2000/0x4000/0x6000/0xe000/0xc000/0xa000 the turns) steers the
         * velocity; without it every action would move along +facing and the
         * mech would only ever drift forward. */
        if (action <= 7u)
            heading = (heading
                + (uint32_t)(int16_t)env->dir_18360[action]) & 0xffffu;

        env->trig(heading, &sine, &cosine);
        vx = von_mv_float(speed) * sine;
        vz = von_mv_float(speed) * cosine;
        von_mv_st32(object, VON_OBJ_VEL_X, von_mv_bits(vx));
        von_mv_st32(object, VON_OBJ_VEL_Z, von_mv_bits(vz));
    }

    /* 0x32810 integrator: x += vx, z += vz. */
    vx = von_mv_float(von_mv_ld32(object, VON_OBJ_X))
       + von_mv_float(von_mv_ld32(object, VON_OBJ_VEL_X));
    vz = von_mv_float(von_mv_ld32(object, VON_OBJ_Z))
       + von_mv_float(von_mv_ld32(object, VON_OBJ_VEL_Z));
    von_mv_st32(object, VON_OBJ_X, von_mv_bits(vx));
    von_mv_st32(object, VON_OBJ_Z, von_mv_bits(vz));
    return 1;
}

#ifdef __IS_I960__
/* Target env: original table addresses, SHARC owns the velocity. */
static const VonMovementEnv von_movement_i960_env = {
    (const uint16_t *)(uintptr_t)0x00018350u,
    (const uint16_t *)(uintptr_t)0x00018360u,
    (const uint16_t *)(uintptr_t)0x00018370u,
    NULL,
    NULL,
    NULL
};

const VonMovementEnv *von_movement_env(void)
{
    return &von_movement_i960_env;
}
#endif
