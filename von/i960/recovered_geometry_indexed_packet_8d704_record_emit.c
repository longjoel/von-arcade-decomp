/* Indexed geometry active-record emitter recovered from i960 0x8d704-0x8d848. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_record_0;
    recovered_u32 source_record_4;
    recovered_u32 source_record_8;
    recovered_u32 selected_record_0;
    recovered_u32 selected_record_2;
    recovered_u32 selected_record_4;
    recovered_u32 selected_record_6;
    recovered_u32 selected_record_8;
    recovered_u32 xor_mask;
    recovered_u32 readback_word;
    recovered_u32 more_records;
    recovered_u32 packet[13];
    recovered_u32 window_word[4];
    recovered_u32 window_address[4];
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 completion_word;
    recovered_u32 fifo_address;
    recovered_u32 packet_emitted;
    recovered_u32 continuation;
} recovered_geometry_indexed_packet_8d704_record_emit_result;

static recovered_u32 sign_extend_halfword(recovered_u32 value)
{
    return (recovered_u32)(int32_t)(int16_t)(value & 0xffffU);
}

recovered_geometry_indexed_packet_8d704_record_emit_result
recovered_geometry_indexed_packet_8d704_record_emit(
    recovered_u32 source_record_0, recovered_u32 source_record_4,
    recovered_u32 source_record_8, recovered_u32 selected_record_0,
    recovered_u32 selected_record_2, recovered_u32 selected_record_4,
    recovered_u32 selected_record_6, recovered_u32 selected_record_8,
    recovered_u32 xor_mask, recovered_u32 readback_word,
    recovered_u32 more_records)
{
    recovered_geometry_indexed_packet_8d704_record_emit_result result;

    result.source_record_0 = source_record_0;
    result.source_record_4 = source_record_4;
    result.source_record_8 = source_record_8;
    result.selected_record_0 = selected_record_0;
    result.selected_record_2 = selected_record_2;
    result.selected_record_4 = selected_record_4;
    result.selected_record_6 = selected_record_6;
    result.selected_record_8 = selected_record_8;
    result.xor_mask = xor_mask;
    result.readback_word = readback_word;
    result.more_records = more_records != 0U ? 1U : 0U;
    result.packet[0] = 5U;
    result.packet[1] = 47U;
    result.packet[2] = selected_record_4 & xor_mask;
    result.packet[3] = selected_record_6 & xor_mask;
    result.packet[4] = selected_record_8 & xor_mask;
    result.packet[5] = 22U;
    result.packet[6] = sign_extend_halfword(selected_record_2);
    result.packet[7] = 21U;
    result.packet[8] = sign_extend_halfword(selected_record_0);
    result.packet[9] = 20U;
    result.packet[10] = sign_extend_halfword(selected_record_0);
    result.packet[11] = 58U;
    result.packet[12] = readback_word;
    result.window_word[0] = source_record_0;
    result.window_word[1] = source_record_4;
    result.window_word[2] = source_record_8;
    result.window_word[3] = 0U;
    result.window_address[0] = 0x804000U;
    result.window_address[1] = 0x804004U;
    result.window_address[2] = 0x804008U;
    result.window_address[3] = 0x80400cU;
    result.control_address = 0x800010U;
    result.control_value = 0x101U;
    result.completion_word = 6U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.packet_emitted = 1U;
    result.continuation = result.more_records != 0U ? 0x0008d704U : 0x0008d848U;
    return result;
}
