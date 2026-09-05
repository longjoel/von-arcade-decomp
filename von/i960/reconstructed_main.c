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

void i960_reconstructed_main(void)
{
    volatile u32 *const state = WORKRAM + 0x20;
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

    {
        const struct recovered_attract_platform presentation_platform = {
            (void *)state, recovered_i960_present
        };

        for (;;) {
        state[5] = state[5] + 1;
        /* These are frame-scale services, not inner-loop operations.  The
         * recovered startup loop advances about 400 iterations per frame;
         * keep a bounded polling interval so the generated image does not
         * spend the entire attract run repeating MMIO reads. */
        if ((state[5] & 0x1ffU) == 0U) {
            recovered_io_service();
            recovered_audio_service_pending();
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
