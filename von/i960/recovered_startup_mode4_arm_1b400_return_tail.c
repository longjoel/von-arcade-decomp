/* Slot-11 return/publication tail recovered from i960 0x1b400-0x1b460. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_value;
    recovered_u32 state_input, state_publication_address, state_publication;
    recovered_u32 progress_address, progress_value;
    recovered_u32 counter_address, counter_value, limit_value;
    recovered_u32 ready_address, ready_value;
    recovered_u32 command_address, command_value, command_published;
    recovered_u32 return_address;
} recovered_startup_mode4_arm_result_1b400_return_tail;

int recovered_startup_mode4_arm_1b400_return_tail(
    recovered_u32 status_value, recovered_u32 state_input,
    recovered_u32 counter_value, recovered_u32 limit_value,
    recovered_u32 ready_value,
    recovered_startup_mode4_arm_result_1b400_return_tail *result)
{
    recovered_startup_mode4_arm_result_1b400_return_tail r = {0};

    r.status_address = 0x5042a2U;
    r.status_value = status_value;
    r.state_input = state_input;
    r.state_publication_address = 0x503a00U;
    r.state_publication = status_value == 0U ? 31U : state_input + 31U;
    r.counter_address = 0x503a70U;
    r.counter_value = counter_value;
    r.limit_value = limit_value;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.command_address = 0x5032f4U;
    r.command_value = 20U;
    r.command_published = (int32_t)counter_value <= (int32_t)limit_value &&
                          ready_value == 0U ? 1U : 0U;
    r.progress_address = 0x503a04U;
    r.progress_value = 90U;
    r.return_address = 0x1b460U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
