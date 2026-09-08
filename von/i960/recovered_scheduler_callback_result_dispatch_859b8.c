/* Callback result dispatch recovered from i960 0x859b8-0x859d8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_result_dispatch_859b8 {
    u32 value_509b8c_low_byte;
    u32 helper_result;
    u32 normalized_index;
    u32 exits_to_85af0;
    u32 target;
};

static const u32 recovered_callback_targets[5] = {
    0x000859ecU, 0x00085a20U, 0x00085a54U, 0x00085a88U, 0x00085abcU
};

struct recovered_scheduler_callback_result_dispatch_859b8
recovered_scheduler_callback_result_dispatch_859b8(u32 value_509b8c,
                                                    u32 helper_result)
{
    struct recovered_scheduler_callback_result_dispatch_859b8 out;

    out.value_509b8c_low_byte = value_509b8c & 0xffU;
    out.helper_result = helper_result;
    out.normalized_index = helper_result - 1U;
    out.exits_to_85af0 = out.normalized_index > 4U ? 1U : 0U;
    out.target = out.exits_to_85af0 == 0U
        ? recovered_callback_targets[out.normalized_index] : 0U;
    return out;
}
