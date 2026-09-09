/* Secondary timer publication gate recovered from i960 0x87ce8-0x87d14. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_timer_publication_87ce8 {
    int32_t state_value;
    int16_t source_51cbb0;
    int16_t source_51d1b0;
    u32 controller_value;
    u32 state_nonnegative;
    int16_t timer_503ca0;
    int16_t timer_5042a0;
    u32 timer_a_address;
    u32 timer_b_address;
    u32 first_service_target;
    u32 first_service_argument;
    u32 formatter_target;
    u32 formatter_argument_0;
    u32 formatter_argument_1;
    u32 controller_service_target;
    u32 controller_service_argument;
};

struct recovered_stage_secondary_timer_publication_87ce8
recovered_stage_secondary_timer_publication_87ce8(int32_t state_value,
                                                  int16_t source_51cbb0,
                                                  int16_t source_51d1b0,
                                                  u32 controller_value)
{
    struct recovered_stage_secondary_timer_publication_87ce8 out;

    out.state_value = state_value;
    out.source_51cbb0 = source_51cbb0;
    out.source_51d1b0 = source_51d1b0;
    out.controller_value = controller_value;
    out.state_nonnegative = state_value >= 0 ? 1U : 0U;
    out.timer_503ca0 = state_value >= 0 ? source_51cbb0 : 0;
    out.timer_5042a0 = state_value >= 0 ? source_51d1b0 : 0;
    out.timer_a_address = 0x00503ca0U;
    out.timer_b_address = 0x005042a0U;
    out.first_service_target = 0x00023d60U;
    out.first_service_argument = 1U;
    out.formatter_target = 0x0001cac8U;
    out.formatter_argument_0 = 21U;
    out.formatter_argument_1 = 14U;
    out.controller_service_target = 0x0001fe60U;
    out.controller_service_argument = controller_value & 4U;
    return out;
}
