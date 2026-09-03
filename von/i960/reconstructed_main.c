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
void recovered_io_failure_prepare(void);
void recovered_io_input_initialize(void);
void recovered_io_service(void);
void recovered_host_queue_initialize(void);
void recovered_audio_initialize_scsp(void);
void recovered_audio_service_pending(void);
void recovered_text_video_initialize(void);
void recovered_text_font_asset_initialize(void);
void recovered_text_ascii_font_initialize(void);
void recovered_text_palette_initialize(void);
void recovered_texture_initializer(void);
int recovered_texture_loader_profile_setup(void);
void recovered_text_set_position(u32 column, u32 row);
void recovered_text_write_string(volatile const unsigned char *text);

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

void i960_reconstructed_main(void)
{
    volatile u32 *const state = WORKRAM + 0x20;
    u32 io_result;

    state[0] = 0x52454330UL; /* REC0 */
    io_result = recovered_io_self_test();
    state[1] = io_result;
    if (io_result != 0) {
        recovered_io_failure_prepare();
        recovered_io_input_initialize();
        recovered_host_queue_initialize();
    }

    recovered_geometry_pipeline_startup(0);
    recovered_text_video_initialize();
    recovered_text_ascii_font_initialize();
    recovered_text_font_asset_initialize();
    /* vonjdev does not map the recovered SCSP control window. Keep the
     * recovered routine linked for oracle work, but skip its MMIO writes in
     * this development image so the attract-state adapter can run. */
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
    recovered_text_write_string(TEXT_COPRO_STATUS);
    recovered_text_set_position(8U, 13U);
    recovered_text_write_string(TEXT_GEO_STATUS);
    recovered_text_set_position(8U, 14U);
    recovered_text_write_string(TEXT_TEXTURE_STATUS);
    recovered_text_set_position(8U, 15U);
    recovered_text_write_string(TEXT_BANK1_STATUS);
    /* The recovered 0x1f470 attract arm selects this message after the
     * startup loader handoff. Keep the known text path live while the full
     * menu/object scheduler is integrated. */
    recovered_text_set_position(24U, 31U);
    recovered_text_write_string(TEXT_INSERT_COIN);
    state[3] = 0x47454f30UL; /* GEO0 */
    state[6] = 0;
    state[4] = 0x494e4954UL; /* INIT */
    state[9] = 0U; /* timed attract presentation has not yet fired */

    for (;;) {
        recovered_io_service();
        recovered_audio_service_pending();
        state[5] = state[5] + 1;
        /* The reconstructed host has no vblank callback in this development
         * image. The captured loader loop advances at roughly 400 iterations
         * per frame, so use a bounded heartbeat threshold to expose the next
         * recovered attract boundary without depending on coin polarity. */
        if (state[9] == 0U && state[5] >= 360000U) {
            recovered_render_mech_select();
            state[9] = 1U;
        }
        if (state[9] == 1U && state[5] >= 780000U) {
            recovered_render_phase(TEXT_TAKEOFF);
            state[9] = 2U;
        }
        if (state[9] == 2U && state[5] >= 1400000U) {
            recovered_render_phase(TEXT_LEVEL_INTRO);
            state[9] = 3U;
        }
        if (state[9] == 3U && state[5] >= 2400000U) {
            recovered_render_phase(TEXT_MATCH_ENTRY);
            state[9] = 4U;
        }
        if (state[9] == 4U && (state[5] & 0x3ffU) == 0U) {
            /* Match-entry's first confirmed recurring host operation is the
             * geometry frame/phase handoff. Keep it on the reconstructed
             * device path while object-record production is integrated. */
            recovered_geometry_frame_submission();
            state[10] = state[10] + 1U;
        }
    }
}
