/* Slot-12 terminal publication tail recovered from i960 0x1b914-0x1b950. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 row_address, row_value;
    recovered_u32 row_gate, row_match;
    recovered_u32 register_19_value;
    recovered_u32 command_address, command_value;
    recovered_u32 state_address, state_value, state_published;
    recovered_u32 row_publication_address, row_publication_value;
    recovered_u32 record_helper_call;
    recovered_u32 setup_argument, setup_call;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_1b914_terminal_tail;

int recovered_startup_mode4_arm_1b914_terminal_tail(
    recovered_u32 row_value, recovered_u32 register_19_value,
    recovered_u32 prior_state,
    recovered_startup_mode4_arm_result_1b914_terminal_tail *result)
{
    recovered_startup_mode4_arm_result_1b914_terminal_tail r = {0};

    r.row_address = 0x503a80U;
    r.row_value = row_value;
    r.row_gate = 6U;
    r.row_match = row_value == r.row_gate ? 1U : 0U;
    r.register_19_value = register_19_value;
    r.command_address = 0x5032f4U;
    /* stos at 0x5032f4 stores only the low halfword. */
    r.command_value = (register_19_value + 31U) & 0xffffU;
    r.state_address = 0x503a00U;
    r.state_value = r.row_match != 0U ? 28U : prior_state;
    r.state_published = r.row_match;
    r.row_publication_address = 0x5032f8U;
    r.row_publication_value = row_value & 0xffffU;
    r.record_helper_call = 0x1fe90U;
    r.setup_argument = 3U;
    r.setup_call = 0x2a4e0U;
    r.return_target = 0x1b95cU;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
