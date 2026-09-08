/* Bulk packet-row copy recovered from i960 0x84a80-0x84b08. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_row_copy_84a80 {
    u32 field_0;
    u32 field_2;
    u32 field_4;
    u32 field_6;
    u32 field_a;
    u32 field_8e;
    u32 copied_count;
    uint16_t field_c[60];
};

struct recovered_scheduler_packet_row_copy_84a80
recovered_scheduler_packet_row_copy_84a80(u32 field_0,
                                          u32 field_2,
                                          u32 field_4,
                                          u32 field_6,
                                          u32 field_a,
                                          const uint16_t source_field_c[60])
{
    struct recovered_scheduler_packet_row_copy_84a80 out = {
        field_0, field_2, field_4, field_6, field_a, 100U, 60U, {0}
    };
    u32 index;

    for (index = 0U; index < 60U; ++index)
        out.field_c[index] = source_field_c[index];
    return out;
}
