/* Secondary stage clear/callback gate recovered from i960 0x87a10-0x87a98. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_clear_gate_87a10 {
    u32 control_value;
    u32 flag_word_5024a4;
    u32 exception_word_5024f4;
    u32 value_503a70;
    u32 value_503a78;
    u32 bit4_forced;
    u32 exception_path;
    u32 command_address;
    u32 command_value;
    u32 callback_g0;
    u32 callback_target;
};

struct recovered_stage_secondary_clear_gate_87a10
recovered_stage_secondary_clear_gate_87a10(u32 control_value,
                                           u32 flag_word_5024a4,
                                           u32 exception_word_5024f4,
                                           u32 value_503a70,
                                           u32 value_503a78)
{
    struct recovered_stage_secondary_clear_gate_87a10 out;
    u32 exception_path = control_value != 0U &&
                         (exception_word_5024f4 == 0x61U ||
                          exception_word_5024f4 == 0x63U);

    out.control_value = control_value;
    out.flag_word_5024a4 = flag_word_5024a4;
    out.exception_word_5024f4 = exception_word_5024f4;
    out.value_503a70 = value_503a70;
    out.value_503a78 = value_503a78;
    out.bit4_forced = ((flag_word_5024a4 >> 4U) & 1U) != 0U ? 1U : 0U;
    out.exception_path = exception_path;
    out.command_address = 0x005032f4U;
    out.command_value = 0U;
    if (out.bit4_forced == 0U && exception_path != 0U)
        out.command_value = value_503a70 <= value_503a78 ? 0x63U : 0x61U;
    out.callback_g0 = out.bit4_forced != 0U || exception_path != 0U ? 1U : 0U;
    out.callback_target = 0x00087a98U;
    return out;
}
