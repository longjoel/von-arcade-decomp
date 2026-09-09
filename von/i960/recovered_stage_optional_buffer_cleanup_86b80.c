/* Optional stage buffer cleanup recovered from i960 0x86b80-0x86b98. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_optional_buffer_cleanup_86b80 {
    u32 control_value;
    u32 calls_cleanup;
    u32 target;
    u32 argument;
    u32 continuation;
};

struct recovered_stage_optional_buffer_cleanup_86b80
recovered_stage_optional_buffer_cleanup_86b80(u32 value_503a7c)
{
    struct recovered_stage_optional_buffer_cleanup_86b80 out;

    out.control_value = value_503a7c;
    out.calls_cleanup = value_503a7c == 0U ? 1U : 0U;
    out.target = 0x000df070U;
    out.argument = 0x005040d0U;
    out.continuation = 0x00086b98U;
    return out;
}
