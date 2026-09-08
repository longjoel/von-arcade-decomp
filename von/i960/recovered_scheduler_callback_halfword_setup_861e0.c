/* Callback halfword setup recovered from i960 0x861e0-0x86238. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_halfword_setup_861e0 {
    int16_t input_g0;
    int16_t input_g1;
    int16_t value_503b18;
    int16_t value_503b1a;
    s32 stored_509b94;
    s32 stored_509b98;
    u32 zeroed_by_503b18;
    u32 overridden_by_503b1a;
    u32 return_stub;
};

struct recovered_scheduler_callback_halfword_setup_861e0
recovered_scheduler_callback_halfword_setup_861e0(
    int16_t input_g0, int16_t input_g1, int16_t value_503b18,
    int16_t value_503b1a)
{
    struct recovered_scheduler_callback_halfword_setup_861e0 out;

    out.input_g0 = input_g0;
    out.input_g1 = input_g1;
    out.value_503b18 = value_503b18;
    out.value_503b1a = value_503b1a;
    out.stored_509b94 = input_g0;
    out.stored_509b98 = input_g1;
    out.zeroed_by_503b18 = 0U;
    out.overridden_by_503b1a = 0U;

    if (value_503b18 == 0) {
        out.stored_509b98 = 0;
        out.zeroed_by_503b18 = 1U;
    }
    if (value_503b1a != 0) {
        out.stored_509b98 = value_503b1a;
        out.overridden_by_503b1a = 1U;
    }
    out.return_stub = 0x00086238U;
    return out;
}
