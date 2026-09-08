/* Recovery packet-row layout recovered from i960 0x84c98-0x84d5c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_row_84c98 {
    u32 destination_offset;
    u32 field_0;
    u32 field_2;
    u32 field_4;
    u32 field_6;
    u32 field_8;
    u32 field_a;
    int32_t field_84;
    u32 source_start;
    u32 recovery_record_field_86;
    uint16_t field_c[60];
};

struct recovered_scheduler_recovery_row_84c98
recovered_scheduler_recovery_row_84c98(u32 table_base,
                                       u32 selected_index,
                                       u32 field_0,
                                       u32 field_2,
                                       u32 field_4,
                                       u32 field_6,
                                       u32 field_8,
                                       u32 field_a,
                                       int32_t normalized_delay,
                                       int32_t counter_509a68,
                                       const uint16_t source_field_c[60])
{
    struct recovered_scheduler_recovery_row_84c98 out = {
        table_base + selected_index * 144U,
        field_0, field_2, field_4, field_6, field_8, field_a,
        240 - 4 * normalized_delay,
        (u32)((counter_509a68 + 1) % 60), 100U, {0}
    };
    u32 index;

    for (index = 0U; index < 60U; ++index)
        out.field_c[index] = source_field_c[(out.source_start + index) % 60U];
    return out;
}
