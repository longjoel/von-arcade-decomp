/* Ordered startup service wrapper recovered from i960 0x18960-0x18a0c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_system_setup_18960 {
    u32 io_self_test;
    u32 video_control_bootstrap;
    u32 startup_asset_transfer;
    u32 audio_table_clear;
    u32 text_position_set;
    u32 status_string_kind; /* 0=original, 1=BC RX, 2=generic fallback */
    u32 geometry_startup;
    u32 stage_latch_published;
    u32 audio_queue_initialize;
    u32 video_dispatch;
    u32 audio_buffer_copy;
    u32 audio_service_reset;
    u32 stage_record_tables;
    u32 continuation_thunk;
    u32 io_wrapper;
    u32 host_queue_initialize;
};

void recovered_startup_system_setup_18960(
    u32 io_result, u32 prior_stage_latch,
    struct recovered_startup_system_setup_18960 *out)
{
    out->io_self_test = 1U;
    out->video_control_bootstrap = 1U;
    out->startup_asset_transfer = 1U;
    out->audio_table_clear = 1U;
    out->text_position_set = 1U;
    out->status_string_kind = io_result == 0U ? 0U
                             : io_result == 1U ? 1U : 2U;
    out->geometry_startup = 1U;
    out->stage_latch_published = 1U;
    out->audio_queue_initialize = 1U;
    out->video_dispatch = 1U;
    out->audio_buffer_copy = 1U;
    out->audio_service_reset = 1U;
    out->stage_record_tables = 1U;
    out->continuation_thunk = 1U;
    out->io_wrapper = 1U;
    out->host_queue_initialize = 1U;
    (void)prior_stage_latch;
}
