#ifndef VON_SYMBOLS_H
#define VON_SYMBOLS_H

/*
 * Named constants for the i960 host kernel addresses the reconstruction uses.
 *
 * Replaces the raw "magic numbers". See von/i960/symbols.md for the meaning and
 * provenance of each name. Keeping the numeric value next to the name lets the
 * generated image stay byte-identical while the C reads semantically.
 */

/* Boot / root entry. */
#define VON_SAT                   0x00000000UL  /* system address table */
#define VON_PRCB                  0x000000b0UL  /* processor control block */
#define VON_RESET_IP              0x00000930UL  /* reset handler */
#define VON_RUNTIME_INIT          0x000009f0UL  /* C runtime startup */
#define VON_MAIN                  0x000186f0UL  /* program main */
#define VON_MAIN_LOOP             0x00018724UL  /* main loop top */
#define VON_MODE_TABLE            0x00018680UL  /* mode -> handler, 16 entries */
#define VON_MAIN_STACK            0x000500400UL /* fp set by the runtime init */

/* Game mode. */
#define VON_GAME_MODE             0x005039f4UL  /* current mode */
#define VON_MODE_PHASE            0x00503a00UL  /* per-mode phase counter */
#define VON_MAIN_HOLD             0x005039f0UL  /* main-loop hold gate (candidate) */
#define VON_START_REQUEST         0x005024f4UL  /* start/coin request (candidate) */
#define VON_MODE_TABLE_MASK       0x0000000fUL

/* Key functions. */
#define VON_FN_INPUT_RESET        0x00024f98UL
#define VON_FN_INPUT_CONSUMER     0x00025040UL
#define VON_FN_OBJECT_UPDATE      0x00026cb8UL
#define VON_FN_HW_INIT            0x000294b0UL
#define VON_FN_BACKBONE           0x00032810UL
#define VON_FN_ACTION_COMMIT      0x00036460UL
#define VON_FN_FRAME_STEP         0x000371e0UL
#define VON_FN_PROJECTION         0x0006f6f0UL
#define VON_FN_CONFIG_COPY        0x00018ab0UL

/* Tables. */
#define VON_BACKBONE_STATE_TABLE  0x00032560UL
#define VON_ACTION_TABLE          0x00032968UL
#define VON_FRAME_STEP_TABLE      0x00037130UL
#define VON_DIR_TABLE_18350       0x00018350UL
#define VON_DIR_TABLE_18360       0x00018360UL
#define VON_DIR_TABLE_18370       0x00018370UL

/* Globals. */
#define VON_CONFIG_PTR            0x0051ab14UL
#define VON_INPUT_WORD_A          0x0050249cUL
#define VON_INPUT_WORD_B          0x005024a4UL
#define VON_INPUT_MA              0x00504dacUL
#define VON_INPUT_MB              0x00504db0UL

/* Objects. */
#define VON_PLAYER_OBJECT         0x00503ad0UL
#define VON_CPU_OBJECT            0x005040d0UL

/* Object field offsets (relative to an object base). */
#define VON_OBJ_CALLBACK          0x004U
#define VON_OBJ_X                 0x008U
#define VON_OBJ_Y                 0x00cU  /* height */
#define VON_OBJ_Z                 0x010U
#define VON_OBJ_HEADING           0x02eU
#define VON_OBJ_YAW_RATE          0x034U
#define VON_OBJ_TURN_TARGET       0x03cU
#define VON_OBJ_ACCUM             0x04eU
#define VON_OBJ_KIND              0x064U
#define VON_OBJ_TEAM              0x068U
#define VON_OBJ_CONFIG            0x06cU
#define VON_OBJ_RELATED           0x074U
#define VON_OBJ_PACKET31          0x07cU
#define VON_OBJ_HEIGHT_DELTA      0x080U
#define VON_OBJ_PACKET10          0x084U
#define VON_OBJ_RANGE_FLAG        0x086U
#define VON_OBJ_INPUT_BASE        0x0ecU
#define VON_OBJ_INPUT_WORK        0x0f0U
#define VON_OBJ_COMMAND           0x108U
#define VON_OBJ_ACTION_SEL        0x136U
#define VON_OBJ_COMMITTED         0x137U
#define VON_OBJ_VY                0x150U
#define VON_OBJ_MODE              0x170U
#define VON_OBJ_STATE             0x172U
#define VON_OBJ_DIR_SELECT        0x176U
#define VON_OBJ_CLIP_COUNTER      0x17aU
#define VON_OBJ_SUBPHASE          0x180U
#define VON_OBJ_FACING            0x184U
#define VON_OBJ_ACTION            0x1b2U
#define VON_OBJ_SPEED             0x1c4U
#define VON_OBJ_VEL_X             0x1c8U
#define VON_OBJ_VEL_Z             0x1ccU

#endif /* VON_SYMBOLS_H */
