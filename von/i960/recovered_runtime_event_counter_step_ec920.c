/* Event counter step recovered from i960 0xec920-ec938. */
#include "recovered_common.h"
typedef struct { recovered_u32 service_call, counter_before, counter_after, counter_address, return_target; } recovered_runtime_event_counter_step_result_ec920;
recovered_runtime_event_counter_step_result_ec920 recovered_runtime_event_counter_step_ec920(recovered_u32 counter_before) {
    recovered_runtime_event_counter_step_result_ec920 result;
    result.service_call=0x28418U; result.counter_before=counter_before; result.counter_after=counter_before+1U; result.counter_address=0x578510U; result.return_target=0xec938U; return result;
}
