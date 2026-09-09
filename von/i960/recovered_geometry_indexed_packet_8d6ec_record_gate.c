/* Indexed geometry record gate recovered from i960 0x8d6ec-0x8d704. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_base;
    recovered_u32 table_base;
    recovered_u32 record_index;
    recovered_u32 record_active_word;
    recovered_u32 source_cursor_after;
    recovered_u32 table_cursor;
    recovered_u32 record_address;
    recovered_u32 record_stride;
    recovered_u32 table_record_bias;
    recovered_u32 active_path;
    recovered_u32 continuation;
} recovered_geometry_indexed_packet_8d6ec_record_gate_result;

recovered_geometry_indexed_packet_8d6ec_record_gate_result
recovered_geometry_indexed_packet_8d6ec_record_gate(
    recovered_u32 source_base, recovered_u32 table_base,
    recovered_u32 record_index, recovered_u32 record_active_word)
{
    recovered_geometry_indexed_packet_8d6ec_record_gate_result result;

    result.source_base = source_base;
    result.table_base = table_base;
    result.record_index = record_index;
    result.record_active_word = record_active_word;
    result.source_cursor_after = source_base + 0xcU;
    result.table_cursor = table_base + 2U;
    result.record_stride = 0xcU;
    result.table_record_bias = 2U;
    result.record_address = source_base + record_index * 0xcU;
    result.active_path = record_active_word == 0U ? 0U : 1U;
    result.continuation = record_active_word == 0U ? 0x0008d834U : 0x0008d704U;
    return result;
}
