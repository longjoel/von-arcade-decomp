/* Stage asset dispatch plan recovered from i960 0x86960-0x869c4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_asset_dispatch_86960 {
    u32 helper_arg0;
    u32 helper_arg1;
    u32 descriptor;
    u32 target;
    u32 target_arg1;
    u32 target_arg2;
};

struct recovered_stage_asset_dispatch_86960
recovered_stage_asset_dispatch_86960(
    u32 input_g20, u32 input_g13, u32 value_504e42)
{
    struct recovered_stage_asset_dispatch_86960 out;

    out.helper_arg0 = input_g20 + 31U;
    out.helper_arg1 = input_g13 + 31U;
    out.target_arg1 = 1U;
    out.target_arg2 = 2U;
    if ((value_504e42 & (1U << 8)) != 0U) {
        out.descriptor = 0x02fd8872U;
        out.target = 0x0001dc10U;
    } else if ((value_504e42 & (1U << 9)) != 0U) {
        out.descriptor = 0x02fd8872U;
        out.target = 0x0001d7d0U;
    } else {
        out.descriptor = 0x02fd8876U;
        out.target = 0x0001dc10U;
    }
    return out;
}
