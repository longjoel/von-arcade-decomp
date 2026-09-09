/* Packet-row layout recovered from i960 0x84a34-0x84a74. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_row_84a34 {
    u32 destination_offset;
    int32_t source_0;
    int32_t source_2;
    int32_t source_4;
    int32_t source_6;
    int32_t source_a;
    int32_t field_8c;
};

struct recovered_scheduler_packet_row_84a34
recovered_scheduler_packet_row_84a34(u32 table_base,
                                     u32 selected_index,
                                     int32_t source_0,
                                     int32_t source_2,
                                     int32_t source_4,
                                     int32_t source_6,
                                     int32_t source_a,
                                     int32_t normalized_delay)
{
    struct recovered_scheduler_packet_row_84a34 out = {
        table_base + selected_index * 144U,
        source_0, source_2, source_4, source_6, source_a,
        240 - 4 * normalized_delay
    };
    return out;
}
