/* Published-frame decoder recovered from i960 0x853c0-0x85494. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_decode_853c0 {
    u32 bit8_mode;
    u32 selector;
    u32 table_index;
    u32 table_address;
    u32 table_value;
    u32 packed_value;
    u32 destination_address;
    u32 value_504e42;
    u32 value_504e44;
    u32 return_trampoline;
};

struct recovered_scheduler_frame_decode_853c0
recovered_scheduler_frame_decode_853c0(u32 value_504e42,
                                       u32 value_504e44,
                                       u32 object_field_ec,
                                       u32 object_state,
                                       u32 mode_a_value,
                                       u32 mode_b_value)
{
    struct recovered_scheduler_frame_decode_853c0 out;
    u32 selector;
    u32 table_offset;

    out.bit8_mode = (value_504e42 & (1U << 8)) != 0U ? 1U : 0U;
    selector = value_504e42 & 0xfU;
    out.selector = selector;
    out.table_index = value_504e44 >> 2;
    if (out.bit8_mode != 0U) {
        /* shlo 3,selector; add selector; shlo 4 => selector * 144. */
        table_offset = object_state * 1152U + selector * 144U + 20U;
        out.table_address = 0x005050a0U + table_offset
            + out.table_index * 2U;
        out.table_value = mode_a_value;
    } else {
        /* shlo 4,selector; add selector; shlo 3 => selector * 136. */
        table_offset = object_state * 1088U + selector * 136U + 12U;
        out.table_address = 0x005074a0U + table_offset
            + out.table_index * 2U;
        out.table_value = mode_b_value;
    }
    out.packed_value = ((out.table_value & 0xf00U) << 4)
        | (out.table_value & 0xfU);
    out.destination_address = object_field_ec + 0x1cU;
    out.value_504e44 = value_504e44 + 1U;
    out.value_504e42 = out.value_504e44 > 239U ? 0U : value_504e42;
    out.return_trampoline = 0x00085494U;
    return out;
}
