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

    (void)von_movement_commit(object, env);

    if (von_mv_ld16(object, VON_OBJ_STATE) != (uint16_t)VON_STATE_CRUISE)
        return 0;

    /* 0x30ad4-0x30c18 (f174 == 0, the default profile): select 0 -> cfg+0x570,
     * select 1 -> cfg+0x574, else cfg+0x56c. Matches
     * recovered_locomotion_state31_speed. */
    select = von_mv_ld16(object, VON_OBJ_DIR_SELECT);
    if (select == 0u)
        speed = von_mv_cfg_u32(config, VON_CFG_SPEED_SEL1);
    else if (select == 1u)
        speed = von_mv_cfg_u32(config, VON_CFG_SPEED_SEL2);
    else
        speed = von_mv_cfg_u32(config, VON_CFG_SPEED_DEFAULT);
    von_mv_st32(object, VON_OBJ_SPEED, speed);

    if (env->trig != NULL) {
        float sine, cosine;

        env->trig((uint32_t)(int16_t)von_mv_ld16(object, VON_OBJ_FACING),
                  &sine, &cosine);
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
