/* Runtime event arm 3 short-path packet prefix recovered from i960 0xe9e00-0xe9e50. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 event_count;
    recovered_u32 first_fifo_value;
    recovered_u32 lookup_word;
    recovered_u32 second_fifo_value;
    recovered_u32 scaled_index;
    recovered_u32 lookup_offset;
    recovered_u32 masked_lookup_word;
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 fifo_address;
    recovered_u32 lookup_mask;
    recovered_u32 scale_shift;
    recovered_u32 scale_divisor;
    recovered_u32 next_target;
} recovered_geometry_runtime_event_arm3_short_result_e9e00;

recovered_geometry_runtime_event_arm3_short_result_e9e00
recovered_geometry_runtime_event_arm3_short_e9e00(
    recovered_u32 event_count, recovered_u32 first_fifo_value,
    recovered_u32 lookup_word, recovered_u32 second_fifo_value)
{
    recovered_geometry_runtime_event_arm3_short_result_e9e00 result;
    recovered_u32 shifted_count = event_count << 14;

    result.event_count = event_count;
    result.first_fifo_value = first_fifo_value;
    result.lookup_word = lookup_word;
    result.second_fifo_value = second_fifo_value;
    result.scaled_index = shifted_count / 45U;
    result.lookup_offset = result.scaled_index - 0x8000U;
    result.masked_lookup_word = lookup_word & 0xffffU;
    result.packet[0] = 29U;
    result.packet[1] = result.masked_lookup_word;
    result.packet[2] = 0x43020000U;
    result.packet[3] = 30U;
    result.packet[4] = result.masked_lookup_word;
    result.packet_count = 5U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.lookup_mask = 0xffffU;
    result.scale_shift = 14U;
    result.scale_divisor = 45U;
    result.next_target = 0x000e9e50U;
    return result;
}
