/* Five callback accumulators recovered from i960 0x859ec-0x85aec. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_accumulator_update_859ec {
    u32 handler_index;
    s32 value_509b90;
    s32 value_503a78;
    s32 current_accumulator;
    s32 divisor;
    s32 quotient;
    s32 unclamped_value;
    s32 updated_accumulator;
    u32 destination_address;
    u32 clamped;
};

struct recovered_scheduler_callback_accumulator_update_859ec
recovered_scheduler_callback_accumulator_update_859ec(u32 handler_index,
                                                      s32 value_509b90,
                                                      s32 value_503a78,
                                                      s32 current_accumulator)
{
    struct recovered_scheduler_callback_accumulator_update_859ec out;

    out.handler_index = handler_index;
    out.value_509b90 = value_509b90;
    out.value_503a78 = value_503a78;
    out.current_accumulator = current_accumulator;
    out.divisor = value_503a78 + 1;
    out.quotient = value_509b90 / out.divisor;
    out.unclamped_value = current_accumulator + out.quotient;
    out.clamped = out.unclamped_value > 10000 ? 1U : 0U;
    out.updated_accumulator = out.clamped ? 10000 : out.unclamped_value;
    out.destination_address = (handler_index < 5U)
        ? 0x00509b24U + handler_index * 4U : 0U;
    return out;
}
