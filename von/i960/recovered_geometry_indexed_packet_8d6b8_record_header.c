/* Indexed geometry record header recovered from i960 0x8d6b8-0x8d6e8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_pointer;
    recovered_u32 record_pointer_after;
    recovered_u32 record_field_6;
    recovered_u32 record_field_8;
    recovered_u32 record_field_a;
    recovered_u32 xor_mask;
    recovered_u32 gated_value;
    recovered_u32 masked_field_6;
    recovered_u32 masked_field_8;
    recovered_u32 masked_field_a;
    recovered_u32 packet[4];
    recovered_u32 command_47;
    recovered_u32 continuation;
} recovered_geometry_indexed_packet_8d6b8_record_header_result;

recovered_geometry_indexed_packet_8d6b8_record_header_result
recovered_geometry_indexed_packet_8d6b8_record_header(
    recovered_u32 record_pointer, recovered_u32 record_field_6,
    recovered_u32 record_field_8, recovered_u32 record_field_a,
    recovered_u32 xor_mask, recovered_u32 gated_value)
{
    recovered_geometry_indexed_packet_8d6b8_record_header_result result;

    result.record_pointer = record_pointer;
    result.record_pointer_after = record_pointer + 0xcU;
    result.record_field_6 = record_field_6;
    result.record_field_8 = record_field_8;
    result.record_field_a = record_field_a;
    result.xor_mask = xor_mask;
    result.gated_value = gated_value;
    result.masked_field_6 = record_field_6 ^ xor_mask;
    result.masked_field_8 = record_field_8 ^ xor_mask;
    result.masked_field_a = record_field_a ^ xor_mask;
    result.packet[0] = 47U;
    result.packet[1] = result.masked_field_6;
    result.packet[2] = result.masked_field_8;
    result.packet[3] = result.masked_field_a;
    result.command_47 = 47U;
    result.continuation = (int32_t)gated_value <= 1 ? 0x0008d848U : 0x0008d6ecU;
    return result;
}
