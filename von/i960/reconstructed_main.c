/*
 * C reconstruction of the confirmed early vonj host path.
 *
 * This is intentionally separate from main.c, which remains the small
 * hardware smoke-test prototype.  The routines below preserve observed host
 * bus transfers; they do not claim to implement the SHARC or geometry
 * processors themselves.
 */

#include "recovered_geometry_pipeline.h"
#include "recovered_object_state_pipeline.h"
#include "recovered_attract_schedule.h"
#include "recovered_attract_platform.h"
#include "recovered_sega_tiles.h"
#include "von_symbols.h"


typedef unsigned long u32;
typedef unsigned short u16;

static const unsigned char TEXT_COPRO_STATUS[] = "Downloading COPRO prog ... Done";
static const unsigned char TEXT_GEO_STATUS[] = "Downloading GEO prog   ... Done";
static const unsigned char TEXT_TEXTURE_STATUS[] = "Loading Texture  Bank0 ... Done";
static const unsigned char TEXT_BANK1_STATUS[] = "Loading Texture  Bank1 ... Done";
static const unsigned char TEXT_INSERT_COIN[] = "INSERT COIN(S)";
static const unsigned char TEXT_MACHINE_SELECT[] = "MACHINE SELECT";
static const unsigned char TEXT_MECH_NAME[] = "VR.TEMJIN";
static const unsigned char TEXT_WEAPON_RIFLE[] = "BEAM RIFLE";
static const unsigned char TEXT_WEAPON_BOMB[] = "BOMB";
static const unsigned char TEXT_WEAPON_SWORD[] = "BEAM SWORD";
static const unsigned char TEXT_TAKEOFF[] = "TAKEOFF SEQUENCE";
static const unsigned char TEXT_LEVEL_INTRO[] = "LEVEL INTRO";
static const unsigned char TEXT_MATCH_ENTRY[] = "MATCH ENTRY";

#define WORKRAM ((volatile u32 *)0x00500000)

u32 recovered_io_self_test(void);
u32 recovered_upload_cluster_service(volatile unsigned *fade_slot,
                                     volatile unsigned *counter_slot,
                                     volatile unsigned *mode_slot,
                                     volatile unsigned *base_src0,
                                     volatile unsigned *base_dst0,
                                     volatile unsigned *base_src1,
                                     volatile unsigned *base_dst1,
                                     volatile unsigned *base_src2,
                                     volatile unsigned *base_dst2);
void recovered_io_failure_prepare(void);
void recovered_io_input_initialize(void);
void recovered_io_service(void);
void recovered_host_queue_initialize(void);
void recovered_audio_initialize_scsp(void);
void recovered_audio_service_pending(void);
void recovered_object_update_32810_run(volatile unsigned char *object);
void recovered_object_initializer_27550_run(volatile unsigned char *object,
    unsigned int config_pointer, unsigned int callback_pointer,
    unsigned int related_pointer, unsigned int kind, unsigned int team,
    unsigned int x, unsigned int z, unsigned int facing);
void recovered_gameplay_velocity_de990_run(void);
void recovered_sharc_upload_run(void);
void recovered_input_service_run(volatile unsigned char *object);
void recovered_input_commit_run_72ea0(volatile unsigned char *object);
unsigned int recovered_input_consumer_24fc0_translate(
    volatile unsigned char *object, unsigned int ma, unsigned int mb);
unsigned int recovered_action_31_run(volatile unsigned char *object);
unsigned int recovered_framestate_dispatch_run(volatile unsigned char *object);
void recovered_velocity_accumulate_358ac_run(volatile unsigned char *object);
void recovered_object_update_prefix_32810_run(volatile unsigned char *object);
extern const unsigned int recovered_von_config_kind0[];
void recovered_text_video_initialize(void);
void recovered_text_video_control_bootstrap(u32 caller_g14);
void recovered_text_font_asset_initialize(void);
void recovered_text_ascii_font_initialize(void);
void recovered_text_video_upload(void);
void recovered_text_palette_initialize(void);
void recovered_text_startup_asset_transfer(u32 profile);
void recovered_texture_initializer(void);
int recovered_texture_loader_profile_setup(void);
void recovered_text_set_position(u32 column, u32 row);
void recovered_text_write_string(volatile const unsigned char *text);
void recovered_text_write_glyph_string(volatile const unsigned char *text);
static void recovered_render_mech_select(void);
static void recovered_render_phase(const unsigned char *title);
static void recovered_render_sega_logo(void);

static void recovered_i960_present(void *opaque,
                                    recovered_attract_platform_u32 event,
                                    recovered_attract_platform_u32 tick)
{
    volatile u32 *state = (volatile u32 *)opaque;
    state[11] = tick;
    switch (event) {
    case RECOVERED_ATTRACT_EVENT_SEGA_LOGO:
        recovered_render_sega_logo();
        state[4] = 0x53454741UL; /* SEGA */
        break;
    case RECOVERED_ATTRACT_EVENT_MACHINE_SELECT:
        recovered_render_mech_select();
        state[4] = 0x494e4954UL; /* INIT */
        break;
    case RECOVERED_ATTRACT_EVENT_TAKEOFF:
        recovered_render_phase(TEXT_TAKEOFF);
        break;
    case RECOVERED_ATTRACT_EVENT_LEVEL_INTRO:
        recovered_render_phase(TEXT_LEVEL_INTRO);
        break;
    case RECOVERED_ATTRACT_EVENT_MATCH_ENTRY:
        recovered_render_phase(TEXT_MATCH_ENTRY);
        break;
    default:
        break;
    }
}

static void recovered_render_mech_select(void)
{
    recovered_text_video_initialize();
    recovered_text_set_position(16U, 30U);
    recovered_text_write_string(TEXT_MACHINE_SELECT);
    recovered_text_set_position(8U, 16U);
    recovered_text_write_string(TEXT_MECH_NAME);
    recovered_text_set_position(8U, 20U);
    recovered_text_write_string(TEXT_WEAPON_RIFLE);
    recovered_text_set_position(8U, 21U);
    recovered_text_write_string(TEXT_WEAPON_BOMB);
    recovered_text_set_position(8U, 22U);
    recovered_text_write_string(TEXT_WEAPON_SWORD);
}

static void recovered_render_phase(const unsigned char *title)
{
    recovered_text_video_initialize();
    recovered_text_set_position(20U, 30U);
    recovered_text_write_string(title);
}

/* The original input-free attract path holds the SEGA bumper before its
 * graphics-only title screen.  The development renderer consumes this state
 * marker while the title geometry command stream is still being recovered. */
static void recovered_render_sega_logo(void)
{
    recovered_sega_logo_char_data();
    recovered_sega_logo_tiles();
}

/* Reconstructed VON_MAIN_LOOP (0x18724, entered from VON_MAIN 0x186f0) mode
 * dispatch and the runnable modes.
 *
 * Mode 3 (0x190d0) is the play-setup arm: it resets the play globals and
 * advances VON_GAME_MODE to 4. Mode 4 (0x19180) is the gameplay arm: it drives
 * the SHARC (opcodes 8/16 to 0x884000) and runs the per-object update
 * VON_FN_OBJECT_UPDATE. The helper calls inside the original arms
 * (0x2a4e0, 0x1c618, 0x1bda0, 0x295d0) and the other mode handlers are not yet
 * runnable, so only the state transitions and the gameplay tick are modeled. */

static void reconstructed_gameplay_tick(void)
{
    recovered_io_service();
    recovered_audio_service_pending();
    /* Read the controller ports, derive the command/MA/MB inputs, then commit
     * them into the player object's held-action state. */
    recovered_input_service_run((volatile unsigned char *)VON_PLAYER_OBJECT);
    recovered_input_commit_run_72ea0((volatile unsigned char *)VON_PLAYER_OBJECT);
    /* VON_FN_INPUT_CONSUMER (0x25040): decode the packed controller word into
     * VON_OBJ_COMMAND, VON_OBJ_ACTION_SEL and the counters. */
    (void)recovered_input_consumer_24fc0_translate(
        (volatile unsigned char *)VON_PLAYER_OBJECT,
        *(volatile unsigned int *)(VON_PLAYER_OBJECT + VON_OBJ_INPUT_BASE),
        *(volatile unsigned int *)(VON_PLAYER_OBJECT + VON_OBJ_INPUT_WORK));
    /* VON_FN_FRAME_STEP (0x371e0): dispatch the 0x37130 arm selected by the
     * object's phase/state (+0x172). State 0 is the committed-action ->
     * state-31 transition; the non-null entries are the locomotion/air arms.
     * This replaces the former direct action-31 call so the input -> state
     * route runs through the recovered frame-step table. */
    (void)recovered_framestate_dispatch_run(
        (volatile unsigned char *)VON_PLAYER_OBJECT);
    /* Velocity producer + prefix + accumulation feed VON_OBJ_VEL_X/VEL_Z. */
    recovered_gameplay_velocity_de990_run();
    recovered_object_update_prefix_32810_run((volatile unsigned char *)VON_PLAYER_OBJECT);
    recovered_velocity_accumulate_358ac_run((volatile unsigned char *)VON_PLAYER_OBJECT);
    /* VON_FN_BACKBONE (0x32810): dispatch the action/state tables, integrate. */
    recovered_object_update_32810_run((volatile unsigned char *)VON_PLAYER_OBJECT);
    recovered_object_update_32810_run((volatile unsigned char *)VON_CPU_OBJECT);
}

/* Mode 3, 0x190d0-0x19170. */
static void reconstructed_mode_3(void)
{
    *(volatile unsigned short *)0x00504b96U = 1U;
    *(volatile unsigned int *)0x00503b48U = 0x005046d0U;
    *(volatile unsigned int *)0x00504148U = 0x00504930U;
    *(volatile unsigned int *)0x00503a84U = 0U;
    *(volatile unsigned int *)0x00503a80U = 0U;
    *(volatile unsigned int *)0x00503a88U = 0U;
    *(volatile unsigned int *)0x00504c98U = 0U;
    *(volatile unsigned int *)0x00503a8cU = 0U;
    *(volatile unsigned int *)0x00503a90U = 0U;
    *(volatile unsigned int *)0x00503a1cU = 0U;
    *(volatile unsigned int *)0x00504c90U = 0U;
    *(volatile unsigned int *)0x00503ac0U = 0U;
    *(volatile unsigned int *)(VON_GAME_MODE) =
        *(volatile unsigned int *)(VON_GAME_MODE) + 1U;
}

/* Mode 0, 0x3c40-0x3d60: attract/UI.  It initializes the text console, walks
 * the UI record list in main_data at 0x2ea2918 (each record = u16 x, u16 y, a
 * NUL-terminated string, then the next record's x/y; a negative x/y word ends
 * the list), and runs a 0x234-frame countdown that then advances the mode. */
static void reconstructed_ui_walk(const volatile unsigned char *base)
{
    const volatile unsigned char *p = base;

    while ((int)*(const volatile unsigned int *)p >= 0) {
        unsigned int x = *(const volatile unsigned short *)p;
        unsigned int y = *(const volatile unsigned short *)(p + 2);

        p += 4;
        recovered_text_console_set_cursor_run(x, y);
        while (*p != 0U)
            recovered_text_console_putc_run((unsigned int)*p++);
        p += 1U;
    }
}

static void reconstructed_mode_0(void)
{
    unsigned int phase = *(volatile unsigned int *)(VON_MODE_PHASE);

    /* 0x3c40: hardware init 0x294b0 is not yet runnable; 0x3c54 raises the
     * SHARC opcode-8 service. */
    *(volatile unsigned int *)0x00884000U = 8U;

    if (phase == 0U) {
        recovered_text_console_reset_run();          /* 0x3c60 */
        recovered_text_console_emit_run(0U);         /* 0x3c68 */
        *(volatile unsigned int *)0x00503a04U = 0x234U;
        if (*(volatile unsigned int *)0x005024d4U != 0U) {
            *(volatile unsigned int *)(VON_MODE_PHASE) = 0U;   /* 0x3cfc */
            *(volatile unsigned int *)(VON_GAME_MODE) += 1U;
        } else {
            reconstructed_ui_walk(
                (const volatile unsigned char *)0x02ea2918U);  /* 0x3c88 */
            *(volatile unsigned int *)(VON_MODE_PHASE) += 1U;
        }
    }

    /* 0x3d18-0x3d60: 0x503a04 countdown; on underflow force the attract
     * restart and advance the mode. */
    {
        unsigned int timer = *(volatile unsigned int *)0x00503a04U - 1U;

        *(volatile unsigned int *)0x00503a04U = timer;
        if (timer == 0xffffffffU) {
            *(volatile unsigned int *)0x005024d4U = 1U;
            *(volatile unsigned int *)(VON_MODE_PHASE) = 0U;
            *(volatile unsigned int *)(VON_GAME_MODE) += 1U;
        }
    }
}

/* Mode 2, 0x18650-0x18678: idle advance (calls helper 0x1ccf8, then mode++). */
static void reconstructed_mode_2(void)
{
    *(volatile unsigned int *)(VON_MODE_PHASE) = 0U;
    *(volatile unsigned int *)(VON_GAME_MODE) =
        *(volatile unsigned int *)(VON_GAME_MODE) + 1U;
}

/* Modes 8/15, 0x18620-0x18648: reset back to attract (mode 0, phase 0). */
static void reconstructed_mode_8(void)
{
    *(volatile unsigned int *)(VON_GAME_MODE) = 0U;
    *(volatile unsigned int *)(VON_MODE_PHASE) = 0U;
}

/* Mode 4, 0x19180-0x1922c (gameplay arm). */
static void reconstructed_mode_4(void)
{
    reconstructed_gameplay_tick();
}

static void reconstructed_main_loop(void)
{
    unsigned int mode = *(volatile unsigned int *)(VON_GAME_MODE);

    switch (mode & VON_MODE_TABLE_MASK) {
    case 0U: reconstructed_mode_0(); break;
    case 2U: reconstructed_mode_2(); break;
    case 3U: reconstructed_mode_3(); break;
    case 4U: reconstructed_mode_4(); break;
    case 8U:
    case 15U: reconstructed_mode_8(); break;
    default: break;
    }
}

void i960_reconstructed_main(void)
{
    /* Byte-relative +0x20: state[12..15] lands on 0x00500050..5c, the
     * words the Lua upload-state observer samples. (WORKRAM is a u32*
     * so plain +0x20 would land on 0x00500080 instead.) */
    volatile u32 *const state =
        (volatile u32 *)((volatile unsigned char *)WORKRAM + 0x20);
    u32 io_result;

    state[0] = 0x52454330UL; /* REC0 */
    io_result = recovered_io_self_test();
    state[1] = io_result;
    state[4] = 0x424f4f54UL; /* BOOT */
    if (io_result != 0) {
        recovered_io_failure_prepare();
        recovered_io_input_initialize();
        recovered_host_queue_initialize();
    }

    recovered_text_startup_asset_transfer(0U);
    state[4] = 0x5452414eUL; /* TRAN */
    /* Upload and boot the SHARC geometry coprocessor so 0x884000 services
     * are answered; the bootstrap is embedded in the host image. */
    recovered_sharc_upload_run();
    recovered_geometry_pipeline_startup_development();
    state[4] = 0x47454f30UL; /* GEO0 */
    /* The SCSP FIFO is part of the board's host-visible audio boundary.  Its
     * initializer emits the observed 0xff startup command and arms the
     * generated consumer path below. */
    recovered_audio_initialize_scsp();
    state[4] = 0x41554430UL; /* AUD0 */
    recovered_text_video_control_bootstrap(0U);
    state[4] = 0x56494430UL; /* VID0 */
    recovered_text_font_asset_initialize();
    recovered_text_video_upload();
    /* M2 live cluster call: seed the upload state the way the 0x29d2c
     * setup tail does (counter preset past the sub-3 guard, direct
     * path selected), then run one full pass over the mapped device
     * windows. Expected: 768 stores, counter 5, every destination
     * word the scale form of its source word. Results land in
     * state[12..15] for the Lua upload-state observer. If these
     * windows are unmapped the fault itself answers U-0004. */
    {
        volatile unsigned *fade_slot = (volatile unsigned *)0x0051a260;
        volatile unsigned *counter_slot = (volatile unsigned *)0x0051a264;
        volatile unsigned *mode_slot = (volatile unsigned *)0x0051a268;
        volatile unsigned *dst0 = (volatile unsigned *)0x01814000;
        *fade_slot = 0x80U;
        *counter_slot = 4U;
        *mode_slot = 0U;
        state[12] = recovered_upload_cluster_service(
            fade_slot, counter_slot, mode_slot,
            (volatile unsigned *)0x01810100, (volatile unsigned *)0x01810000,
            (volatile unsigned *)0x01814100, (volatile unsigned *)0x01814000,
            (volatile unsigned *)0x01818100, (volatile unsigned *)0x01818000);
        state[13] = *counter_slot;
        state[14] = dst0[0];
        state[15] = dst0[927];
    }
    state[7] = recovered_object_state_runtime_tick();
    recovered_text_palette_initialize();
    /* The recovered texture loader is retained for offline analysis, but its
     * completion latch is not modeled by vonjdev and its stream can run
     * indefinitely. Record the observed development status and continue with
     * the captured startup status screen. */
    state[8] = 7U;
    /* vonjdev has no recovered texture-device completion latch. Preserve its
     * status in state[8], then render the captured post-loader status screen
     * from local strings so the reconstructed host has a deterministic handoff
     * point for attract-state recovery. */
    recovered_text_set_position(8U, 12U);
    recovered_text_write_glyph_string(TEXT_COPRO_STATUS);
    recovered_text_set_position(8U, 13U);
    recovered_text_write_glyph_string(TEXT_GEO_STATUS);
    recovered_text_set_position(8U, 14U);
    recovered_text_write_glyph_string(TEXT_TEXTURE_STATUS);
    recovered_text_set_position(8U, 15U);
    recovered_text_write_glyph_string(TEXT_BANK1_STATUS);
    /* The recovered 0x1f470 attract arm selects this message after the
     * startup loader handoff. Keep the known text path live while the full
     * menu/object scheduler is integrated. */
    recovered_text_set_position(24U, 31U);
    recovered_text_write_glyph_string(TEXT_INSERT_COIN);
    state[3] = 0x47454f30UL; /* GEO0 */
    state[6] = 0;
    state[4] = 0x494e4954UL; /* INIT */
    state[9] = 0U; /* timed attract presentation has not yet fired */

    /* Seed the two static fighters so the update backbone and the geometry
     * seek exchange have a defined record. Positions are placed apart so the
     * seek can produce nonzero velocity.
     *
     * This reproduces the per-kind of the original VON_FN_OBJECT_UPDATE
     * (0x26cb8) object seed. The ROM config blocks at 0x57d0 are overwritten by
     * the generated image, so the config lives in the generated image; point
     * both objects at it. */
    recovered_object_initializer_27550_run((volatile unsigned char *)VON_PLAYER_OBJECT,
        (unsigned int)(unsigned long)recovered_von_config_kind0, 0U, VON_CPU_OBJECT, 0U, 0U, 0x00000000U, 0xc2700000U, 0U);
    recovered_object_initializer_27550_run((volatile unsigned char *)VON_CPU_OBJECT,
        (unsigned int)(unsigned long)recovered_von_config_kind0, 0U, VON_PLAYER_OBJECT, 0U, 1U, 0x00000000U, 0x42700000U, 0U);

    /* Provisional locomotion seed until the state-31/34 arms are ported:
     * facing angle 0 and speed scalar 3.0f feed the velocity accumulation
     * block's opcode-29/30 exchanges. */
    *(volatile unsigned short *)(VON_PLAYER_OBJECT + VON_OBJ_FACING) = 0U;
    *(volatile unsigned int *)(VON_PLAYER_OBJECT + VON_OBJ_SPEED) = 0x40400000U;   /* 3.0f */
    *(volatile unsigned int *)(VON_PLAYER_OBJECT + VON_OBJ_PACKET31) = 0x42c80000U; /* 100.0f limit */
    *(volatile unsigned short *)(VON_PLAYER_OBJECT + VON_OBJ_STATE) = 16U;         /* input-facing locomotion state */
    *(volatile unsigned short *)(VON_PLAYER_OBJECT + VON_OBJ_TURN_TARGET) = 0U;

    /* Enter the reconstructed root mode loop at mode 0 (attract), which walks
     * the UI records and advances like the original 0x3c40 arm. */
    *(volatile unsigned int *)(VON_GAME_MODE) = 0U;
    *(volatile unsigned int *)(VON_MODE_PHASE) = 0U;

    {
        const struct recovered_attract_platform presentation_platform = {
            (void *)state, recovered_i960_present
        };

        /* This loop models VON_MAIN_LOOP (0x18724) of the real root: the
         * original dispatches VON_MODE_TABLE[VON_GAME_MODE & 15] each
         * iteration. Modes 3/4 reach gameplay through VON_FN_OBJECT_UPDATE
         * (0x26cb8); the other mode handlers are not yet runnable. See
         * von/i960/symbols.md. */
        for (;;) {
        state[5] = state[5] + 1;
        if ((state[5] & 0x1ffU) == 0U) {
            reconstructed_main_loop();
        }
        /* The reconstructed host has no vblank callback in this development
         * image. The captured loader loop advances at roughly 400 iterations
         * per frame, so use a bounded heartbeat threshold to expose the next
         * recovered attract boundary without depending on coin polarity. */
        /* The generated image's tight loop advances about 300,000 counts per
         * emulated second. Keep this pure scheduler shared with Linux so the
         * phase boundaries can be debugged without hardware MMIO. */
        {
            recovered_schedule_u32 next_phase;
            recovered_schedule_u32 event;
            recovered_attract_step((recovered_schedule_u32)state[5],
                                   (recovered_schedule_u32)state[9],
                                   &next_phase, &event);
            if (next_phase != state[9]) {
                recovered_attract_present(&presentation_platform, event, state[5]);
                state[9] = next_phase;
            }
        }
    if (state[9] == RECOVERED_ATTRACT_MATCH_ENTRY &&
            (state[5] & 0x3fffU) == 0U) {
            /* Match-entry's first confirmed recurring host operation is the
             * geometry frame/phase handoff. Repeat the parser-accepted seed
             * on a bounded cadence so the attract run has continuing video
             * activity while object-record production is integrated. */
            recovered_geometry_frame_submission();
            recovered_geometry_object_packet_probe();
            recovered_geometry_match_object_seed();
            state[10] = state[10] + 1U;
        }
        }
    }
}
