/* Conditional stage asset-copy gate recovered from i960 0x86ac0-0x86b0c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_asset_copy_gate_86ac0 {
    u32 initial_service;
    u32 initial_service_argument;
    u32 control_value;
    u32 copies_enabled;
    u32 copy_count;
    u32 source[2];
    u32 destination[2];
    u32 length[2];
    u32 continuation;
};

struct recovered_stage_asset_copy_gate_86ac0
recovered_stage_asset_copy_gate_86ac0(u32 value_503a04)
{
    struct recovered_stage_asset_copy_gate_86ac0 out;

    out.initial_service = 0x0009baa0U;
    out.initial_service_argument = 0x00503ad0U;
    out.control_value = value_503a04;
    out.copies_enabled = value_503a04 == 0x5aU ? 1U : 0U;
    out.copy_count = out.copies_enabled != 0U ? 2U : 0U;
    out.source[0] = 0x0051c9e0U;
    out.source[1] = 0x0051cfe0U;
    out.destination[0] = 0x00503ad0U;
    out.destination[1] = 0x005040d0U;
    out.length[0] = 0x600U;
    out.length[1] = 0x600U;
    out.continuation = 0x00086b0cU;
    return out;
}
