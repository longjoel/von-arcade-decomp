/* Dispatch-table slot 15 recovered from i960 0x1b960-0x1b97c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 setup_call;
    recovered_u32 incoming_value;
    recovered_u32 value_address, value;
    recovered_u32 state_address, state;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_1b960;

int recovered_startup_mode4_arm_1b960(
    recovered_u32 incoming_value,
    recovered_startup_mode4_arm_result_1b960 *result)
{
    recovered_startup_mode4_arm_result_1b960 r = {0};

    r.setup_call = 0x29c08U;
    r.incoming_value = incoming_value;
    r.value_address = 0x5024c6U;
    /* stob at 0x1b96c stores only the low byte of g14. */
    r.value = incoming_value & 0xffU;
    r.state_address = 0x503a00U;
    r.state = 25U;
    r.return_target = 0x1b97cU;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
