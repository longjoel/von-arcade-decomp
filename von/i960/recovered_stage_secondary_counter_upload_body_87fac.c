/* Secondary counter upload body recovered from i960 0x87fac-0x88030. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_counter_upload_body_87fac {
    u32 counter_value;
    u32 destination_first;
    u32 destination_second;
    u32 modulo_divisor;
    u32 counter_remainder;
    u32 row_index;
    u32 table_offset;
    u32 indexed_source_first;
    u32 indexed_source_second;
    u32 indexed_bytes;
    u32 fixed_source_first;
    u32 fixed_source_second;
    u32 fixed_destination_first;
    u32 fixed_destination_second;
    u32 fixed_bytes;
    u32 upload_call;
    u32 upload_count;
    u32 continuation;
};

struct recovered_stage_secondary_counter_upload_body_87fac
recovered_stage_secondary_counter_upload_body_87fac(u32 counter_value,
                                                    u32 destination_first,
                                                    u32 destination_second)
{
    struct recovered_stage_secondary_counter_upload_body_87fac out;

    out.counter_value = counter_value;
    out.destination_first = destination_first;
    out.destination_second = destination_second;
    out.modulo_divisor = 120U;
    out.counter_remainder = counter_value % out.modulo_divisor;
    out.row_index = out.counter_remainder >> 2U;
    out.table_offset = out.row_index * 3U << 9U;
    out.indexed_source_first = 0x0051d5f0U + out.table_offset;
    out.indexed_source_second = 0x005289f0U + out.table_offset;
    out.indexed_bytes = 0x600U;
    out.fixed_source_first = 0x00560df0U;
    out.fixed_source_second = 0x00561370U;
    out.fixed_destination_first = 0x00565320U;
    out.fixed_destination_second = 0x005658a0U;
    out.fixed_bytes = 0x580U;
    out.upload_call = 0x000f5d40U;
    out.upload_count = 4U;
    out.continuation = 0x00088030U;
    return out;
}
