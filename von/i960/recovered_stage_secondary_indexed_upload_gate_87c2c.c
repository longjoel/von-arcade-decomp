/* Secondary indexed-upload gate recovered from i960 0x87c2c-0x87ce8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_indexed_upload_gate_87c2c {
    u32 ready_value;
    int32_t state_value;
    int32_t timing_value;
    u32 cleanup_call;
    u32 cleanup_called;
    u32 upload_gate_admitted;
    u32 timing_aligned;
    u32 timing_index;
    u32 table_offset;
    u32 first_source;
    u32 second_source;
    u32 destination_first;
    u32 destination_second;
    u32 upload_bytes;
    u32 upload_call;
    u32 common_call_targets[6];
};

struct recovered_stage_secondary_indexed_upload_gate_87c2c
recovered_stage_secondary_indexed_upload_gate_87c2c(u32 ready_value,
                                                    int32_t state_value,
                                                    int32_t timing_value)
{
    struct recovered_stage_secondary_indexed_upload_gate_87c2c out;
    int32_t rounded_timing = timing_value;
    int32_t aligned_timing;
    int32_t index;

    out.ready_value = ready_value;
    out.state_value = state_value;
    out.timing_value = timing_value;
    out.cleanup_call = 0x000df070U;
    out.cleanup_called = ready_value == 0U ? 1U : 0U;
    out.upload_gate_admitted = 0U;
    out.timing_aligned = 0U;
    out.timing_index = 0U;
    out.table_offset = 0U;
    out.first_source = 0U;
    out.second_source = 0U;
    out.destination_first = 0x00503cd0U;
    out.destination_second = 0x005042d0U;
    out.upload_bytes = 0x400U;
    out.upload_call = 0x000f5d40U;
    out.common_call_targets[0] = 0x000bece0U;
    out.common_call_targets[1] = 0x0009b320U;
    out.common_call_targets[2] = 0x00041f20U;
    out.common_call_targets[3] = 0x000c5530U;
    out.common_call_targets[4] = 0x0006fec0U;
    out.common_call_targets[5] = 0x00071080U;

    if (state_value < 0) {
        if (timing_value > 0)
            rounded_timing = timing_value + 3;
        aligned_timing = rounded_timing & ~3;
        out.timing_aligned = timing_value == aligned_timing ? 1U : 0U;
        if (timing_value != aligned_timing) {
            out.upload_gate_admitted = 1U;
            index = aligned_timing - (aligned_timing >> 2);
            if (index > 0x59)
                index %= 0x5a;
            out.timing_index = (u32)index;
            out.table_offset = out.timing_index << 10U;
            out.first_source = 0x00533df0U + out.table_offset;
            out.second_source = 0x0054a5f0U + out.table_offset;
        }
    }
    return out;
}
