/* Slot-20 timing normalization recovered from i960 0x86df0-0x86e74. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_slot20_timing_86df0 {
    u32 slot_index;
    u32 marker;
    u32 remainder;
    u32 bucket_candidate;
    u32 published_state;
    u32 published_timing;
    u32 state_address;
    u32 timing_address;
    u32 modulus;
    u32 group_shift;
    u32 continuation;
};

struct recovered_stage_slot20_timing_86df0
recovered_stage_slot20_timing_86df0(u32 slot_index, u32 marker)
{
    struct recovered_stage_slot20_timing_86df0 out;
    u32 published_state;
    u32 remainder;
    u32 bucket_candidate;

    out.slot_index = slot_index;
    out.marker = marker;
    out.modulus = 120U;
    out.group_shift = 2U;
    if (slot_index <= 0x77U) {
        remainder = slot_index;
        bucket_candidate = 0U;
        published_state = marker;
    } else {
        remainder = slot_index % out.modulus;
        bucket_candidate = 4U + ((remainder >> out.group_shift) * 4U);
        published_state = bucket_candidate <= 0x77U ? bucket_candidate : marker;
    }
    if (published_state > 0x77U)
        published_state -= out.modulus;

    out.remainder = remainder;
    out.bucket_candidate = bucket_candidate;
    out.published_state = published_state;
    out.published_timing = remainder;
    out.state_address = 0x0051d5e4U;
    out.timing_address = 0x0051d5e8U;
    out.continuation = 0x00086e74U;
    return out;
}
