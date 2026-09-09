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
    u32 stage_latch_before;
    u32 stage_latch_after;
    u32 stage_latch_initialize_call;
    u32 call_count;
    u32 call_targets[16];
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
    out->stage_latch_before = prior_stage_latch;
    out->stage_latch_after = 1U;
    out->stage_latch_initialize_call = prior_stage_latch == 0U ? 1U : 0U;

    /* Preserve the listing order.  The 0x28d80 initializer is the only
     * conditional call; all later setup calls are unconditional. */
    {
        u32 i = 0U;
        out->call_targets[i++] = 0x2730U;
        out->call_targets[i++] = 0x1c220U;
        out->call_targets[i++] = 0x1bda0U;
        out->call_targets[i++] = 0x29a80U;
        out->call_targets[i++] = 0x1cac8U;
        out->call_targets[i++] = 0x1da90U;
        if (prior_stage_latch == 0U)
            out->call_targets[i++] = 0x28d80U;
        out->call_targets[i++] = 0x2a8a0U;
        out->call_targets[i++] = 0xe2130U;
        out->call_targets[i++] = 0x29ca0U;
        out->call_targets[i++] = 0x29ae8U;
        out->call_targets[i++] = 0xbd5a8U;
        out->call_targets[i++] = 0x866c0U;
        out->call_targets[i++] = 0x18918U;
        out->call_targets[i++] = 0x2440U;
        out->call_targets[i++] = 0x1bb8U;
        out->call_count = i;
    }
}
