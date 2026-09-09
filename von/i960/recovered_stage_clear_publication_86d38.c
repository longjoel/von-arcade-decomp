/* Post-clear publication sequence recovered from i960 0x86d38-0x86db4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_clear_publication_86d38 {
    u32 service_targets[3];
    u32 service_count;
    u32 clear_service_g0;
    u32 state_service_g0;
    u32 publication_51c9a4;
    u32 publication_51c9ac;
    u32 value_503a70;
    u32 value_503a78;
    u32 command_value;
    u32 state_marker;
    u32 state_marker_halfword_address;
    u32 state_marker_address_1;
    u32 state_marker_address_2;
    u32 state_address;
    u32 phase_address;
    u32 progress_address;
    u32 command_address;
    u32 continuation;
};

struct recovered_stage_clear_publication_86d38
recovered_stage_clear_publication_86d38(u32 publication_51c9a4,
                                        u32 publication_51c9ac,
                                        u32 value_503a70,
                                        u32 value_503a78,
                                        u32 state_marker,
                                        u32 caller_g0)
{
    struct recovered_stage_clear_publication_86d38 out;

    out.service_targets[0] = 0x0001fe90U;
    out.service_targets[1] = 0x0001f080U;
    out.service_targets[2] = 0x000423a8U;
    out.service_count = 3U;
    /* 0x1fe90 is called before the explicit mov 0,g0 at 0x86d3c. */
    out.clear_service_g0 = caller_g0;
    out.state_service_g0 = 0U;
    out.publication_51c9a4 = publication_51c9a4;
    out.publication_51c9ac = publication_51c9ac;
    out.value_503a70 = value_503a70;
    out.value_503a78 = value_503a78;
    out.command_value = value_503a70 <= value_503a78 ? 0x60U : 0x62U;
    out.state_marker = state_marker;
    out.state_marker_halfword_address = 0x0051c942U;
    out.state_marker_address_1 = 0x0051d5e0U;
    out.state_marker_address_2 = 0x0051c9c0U;
    out.state_address = 0x00503a60U;
    out.phase_address = 0x00503a00U;
    out.progress_address = 0x00503a04U;
    out.command_address = 0x005032f4U;
    out.continuation = 0x00086db4U;
    return out;
}
