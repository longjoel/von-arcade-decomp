/* Response selector prefix recovered from i960 0x8d2a0-0x8d2d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter;
    recovered_u32 modulo, counter_remainder, shifted_index, capped_index;
    recovered_u32 response;
    recovered_u32 result_value;
    recovered_u32 special_response, special_result;
    recovered_u32 special_return;
    recovered_u32 normal_continuation;
} recovered_scheduler_response_selector_8d2a0_result;

int recovered_scheduler_response_selector_8d2a0(
    recovered_u32 counter, recovered_u32 response,
    recovered_scheduler_response_selector_8d2a0_result *result)
{
    recovered_scheduler_response_selector_8d2a0_result r = {0};
    r.counter = counter;
    r.modulo = 120U;
    r.counter_remainder = counter % r.modulo;
    r.shifted_index = r.counter_remainder >> 2U;
    r.capped_index = r.shifted_index > 29U ? 29U : r.shifted_index;
    r.response = response;
    r.special_response = 10U;
    r.special_result = 10U;
    r.special_return = 0x8d3ecU;
    r.normal_continuation = 0x8d2d0U;
    r.result_value = response == r.special_response ? r.special_result : 0U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
