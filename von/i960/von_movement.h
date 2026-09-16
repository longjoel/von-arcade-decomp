#ifndef VON_MOVEMENT_H
#define VON_MOVEMENT_H

/*
 * Shared Virtual-On movement kernel: one source, two builds.
 *
 * Compiled for the i960 (with __IS_I960__) into the reconstructed ROM image,
 * and for the host (godot/runner kernel) without it. The object is the i960
 * byte layout, addressed by offset, so both builds run the *same* recovered
 * logic; only the target glue differs:
 *
 *   __IS_I960__ : config is read through the absolute pointer at object+0x6c,
 *                 the SHARC supplies sin/cos (opcodes 29/30) and the ground
 *                 projection, all via the real MMIO.
 *   host        : no MMIO; the object/config live in a MAP_32BIT buffer so the
 *                 32-bit config pointer is valid, sin/cos come from libm, and
 *                 the projection is supplied by the env.
 *
 * See von/i960/symbols.md for the field provenance.
 */

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Object field offsets (i960 layout). */
#define VON_OBJ_X              0x08u
#define VON_OBJ_Y              0x0cu   /* height */
#define VON_OBJ_Z              0x10u
#define VON_OBJ_HEADING        0x2eu
#define VON_OBJ_TURN_TARGET    0x3cu
#define VON_OBJ_CONFIG         0x6cu
#define VON_OBJ_STATE          0x172u
#define VON_OBJ_MODE           0x170u
#define VON_OBJ_DIR_SELECT     0x176u
#define VON_OBJ_MOVE_FAMILY    0x174u
#define VON_OBJ_COMMITTED      0x137u
#define VON_OBJ_FACING         0x184u
#define VON_OBJ_HALF_HEADING   0x186u
#define VON_OBJ_SELECTOR_188   0x188u
#define VON_OBJ_SPEED          0x1c4u
#define VON_OBJ_VEL_X          0x1c8u
#define VON_OBJ_VEL_Z          0x1ccu
#define VON_OBJ_CLIP_COUNTER   0x17au

/* Recovered speed triplet (cfg+0x56c default, 0x570 for +0x176==1, 0x574 for
 * +0x176==2) and the cruise state. */
#define VON_CFG_SPEED_DEFAULT  0x56cu
#define VON_CFG_SPEED_SEL1     0x570u
#define VON_CFG_SPEED_SEL2     0x574u
#define VON_STATE_CRUISE       31u
#define VON_ACTION_NONE        0xffu

/* Direction tables 0x18350/0x18360/0x18370 (i960 addresses; the host supplies
 * copies). */
typedef struct VonMovementEnv {
    const uint16_t *dir_18350;
    const uint16_t *dir_18360;
    const uint16_t *dir_18370;
    /* SHARC ground projection: returns the ground height as raw float bits.
     * NULL => keep the object's current Y. */
    uint32_t (*project)(uint8_t *object);
    /* Facing (16-bit angle units) -> sin/cos. NULL => the caller (the i960
     * SHARC velocity unit) has already written VON_OBJ_VEL_X/VEL_Z. */
    void (*trig)(uint32_t facing, float *out_sin, float *out_cos);
    /* Per-kind config block. NULL => read the absolute pointer at object+0x6c
     * (the i960 target). The host kernel passes its own config buffer, which
     * avoids needing object+0x6c to hold a valid 32-bit pointer. */
    const uint8_t *config;
} VonMovementEnv;

/* Advance one movement frame on an i960-layout object. Returns 1 when the
 * object is cruising (state 31). */
int von_movement_tick(uint8_t *object, const VonMovementEnv *env);

/* Committed action (+0x137) -> state 31 + direction. Returns 1 when applied. */
int von_movement_commit(uint8_t *object, const VonMovementEnv *env);

#ifdef __IS_I960__
/* Target env: the recovered direction tables live at their original addresses
 * and the SHARC velocity unit owns VEL_X/VEL_Z (trig == NULL). */
const VonMovementEnv *von_movement_env(void);
#endif

#ifdef __cplusplus
}
#endif

#endif /* VON_MOVEMENT_H */
