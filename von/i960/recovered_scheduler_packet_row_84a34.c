/* Packet-row layout recovered from i960 0x84a34-0x84a74. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_row_84a34 {
    u32 destination_offset;
    u32 source_0;
    u32 source_2;
    u32 source_4;
    u32 source_6;
    u32 source_a;
    int32_t field_8c;
};

struct recovered_scheduler_packet_row_84a34
recovered_scheduler_packet_row_84a34(u32 table_base,
                                     u32 selected_index,
                                     u32 source_0,
                                     u32 source_2,
                                     u32 source_4,
                                     u32 source_6,
                                     u32 source_a,
                                     int32_t normalized_delay)
{
    struct recovered_scheduler_packet_row_84a34 out = {
        table_base + selected_index * 144U,
        source_0, source_2, source_4, source_6, source_a,
        240 - 4 * normalized_delay
    };
    return out;
}
