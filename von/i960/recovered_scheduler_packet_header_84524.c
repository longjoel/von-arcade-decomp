/* Scheduler packet header recovered from i960 0x84524-0x8459c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_header_84524 {
    u32 row_offset;
    u32 field_0e;
    u32 field_00;
    u32 field_02;
    u32 field_04;
    u32 writes_field_06;
    u32 field_06;
    u32 direct_continuation;
    u32 continuation_r7;
};

struct recovered_scheduler_packet_header_84524
recovered_scheduler_packet_header_84524(u32 counter_509a68,
                                        u32 object_field_1d0,
                                        u32 value_504d70,
                                        u32 value_504e20,
                                        u32 value_504e2c,
                                        u32 value_504e28,
                                        u32 caller_g14,
                                        u32 converted_value_504e28)
{
    struct recovered_scheduler_packet_header_84524 out = {
        counter_509a68 << 4,
        object_field_1d0,
        value_504d70,
        converted_value_504e28,
        ((value_504e28 & 0xffffU) << 8) | (value_504e2c & 0xffffU),
        0U, 0U, 0U, 0U
    };

    if (value_504e20 == UINT32_MAX) {
        out.writes_field_06 = 1U;
        out.field_06 = caller_g14;
        out.direct_continuation = 1U;
        out.continuation_r7 = 16U;
    }
    return out;
}
