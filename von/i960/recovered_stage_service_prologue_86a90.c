/* Stage service prologue recovered from i960 0x86a90-0x86ac0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_service_prologue_86a90 {
    u32 marker_503a60;
    uint16_t halfword_504b94;
    u32 call_count;
    u32 call_targets[6];
    u32 zero_argument_call_indices[2];
    u32 falls_through_to_86ac0;
};

struct recovered_stage_service_prologue_86a90
recovered_stage_service_prologue_86a90(u32 callback_g14)
{
    struct recovered_stage_service_prologue_86a90 out;

    out.marker_503a60 = callback_g14;
    out.halfword_504b94 = (uint16_t)callback_g14;
    out.call_count = 6U;
    out.call_targets[0] = 0x000de630U;
    out.call_targets[1] = 0x000c8f10U;
    out.call_targets[2] = 0x0006fec0U;
    out.call_targets[3] = 0x0009b308U;
    out.call_targets[4] = 0x0006fec0U;
    out.call_targets[5] = 0x000c8f60U;
    out.zero_argument_call_indices[0] = 2U;
    out.zero_argument_call_indices[1] = 4U;
    out.falls_through_to_86ac0 = 1U;
    return out;
}
