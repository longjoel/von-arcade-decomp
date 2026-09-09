/* Secondary timing upload arm recovered from i960 0x87d38-0x87de4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_timing_upload_87d38 {
    int32_t state_value;
    int32_t timing_value;
    u32 timing_aligned;
    u32 upload_admitted;
    u32 timing_index;
    u32 table_offset;
    u32 indexed_bytes;
    u32 fixed_bytes;
    u32 indexed_source_first;
    u32 indexed_source_second;
    u32 indexed_destination_first;
    u32 indexed_destination_second;
    u32 fixed_source_first;
    u32 fixed_source_second;
    u32 fixed_destination_first;
    u32 fixed_destination_second;
    u32 upload_call;
    u32 upload_count;
};

struct recovered_stage_secondary_timing_upload_87d38
recovered_stage_secondary_timing_upload_87d38(int32_t state_value,
                                              int32_t timing_value)
{
    struct recovered_stage_secondary_timing_upload_87d38 out;
    int32_t rounded_timing = timing_value;
    int32_t aligned_timing;
    int32_t index;

    out.state_value = state_value;
    out.timing_value = timing_value;
    out.timing_aligned = 0U;
    out.upload_admitted = 0U;
    out.timing_index = 0U;
    out.table_offset = 0U;
    out.indexed_bytes = 0x600U;
    out.fixed_bytes = 0x580U;
    out.indexed_source_first = 0U;
    out.indexed_source_second = 0U;
    out.indexed_destination_first = 0x00503ad0U;
    out.indexed_destination_second = 0x005040d0U;
    out.fixed_source_first = 0x00560df0U;
    out.fixed_source_second = 0x00561370U;
    out.fixed_destination_first = 0x00565320U;
    out.fixed_destination_second = 0x005658a0U;
    out.upload_call = 0x000f5d40U;
    out.upload_count = 0U;

    if (timing_value > 0)
        rounded_timing = timing_value + 3;
    aligned_timing = rounded_timing & ~3;
    out.timing_aligned = timing_value == aligned_timing ? 1U : 0U;
    if (state_value < 0 && timing_value != aligned_timing) {
        out.upload_admitted = 1U;
        index = aligned_timing - (aligned_timing >> 2);
        if (index > 0x59)
            index %= 0x5a;
        out.timing_index = (u32)index;
        out.table_offset = out.timing_index << 9U;
        out.indexed_source_first = 0x0051d5f0U + out.table_offset;
        out.indexed_source_second = 0x005289f0U + out.table_offset;
        out.upload_count = 4U;
    }
    return out;
}
