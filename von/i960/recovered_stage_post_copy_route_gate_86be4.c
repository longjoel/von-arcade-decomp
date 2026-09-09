/* Post-copy route gate recovered from i960 0x86be4-0x86c08. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_stage_post_copy_route_86be4 {
    RECOVERED_STAGE_ROUTE_86C08 = 0,
    RECOVERED_STAGE_ROUTE_86C64 = 1,
    RECOVERED_STAGE_ROUTE_86CB8 = 2
};

struct recovered_stage_post_copy_route_gate_86be4 {
    u32 value_503a04;
    u32 value_503ca2;
    u32 value_5042a2;
    u32 expected_503a04;
    u32 route;
    u32 target;
};

struct recovered_stage_post_copy_route_gate_86be4
recovered_stage_post_copy_route_gate_86be4(u32 value_503a04,
                                            u32 value_503ca2,
                                            u32 value_5042a2)
{
    struct recovered_stage_post_copy_route_gate_86be4 out;

    out.value_503a04 = value_503a04;
    out.value_503ca2 = value_503ca2;
    out.value_5042a2 = value_5042a2;
    out.expected_503a04 = 0x5aU;
    if (value_503a04 != out.expected_503a04) {
        out.route = RECOVERED_STAGE_ROUTE_86CB8;
        out.target = 0x00086cb8U;
    } else if (value_503ca2 == 0U || value_5042a2 == 0U) {
        out.route = RECOVERED_STAGE_ROUTE_86C08;
        out.target = 0x00086c08U;
    } else {
        out.route = RECOVERED_STAGE_ROUTE_86C64;
        out.target = 0x00086c64U;
    }
    return out;
}
