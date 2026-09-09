/* Input-state rejoin recovered from i960 0x3884-0x3a20. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_input_rejoin_route_3884 {
    RECOVERED_INPUT_REJOIN_RESET_TAIL = 0U,
    RECOVERED_INPUT_REJOIN_STATE_BODY = 1U
};

struct recovered_input_state_rejoin_plan_3884 {
    u32 g0_input;
    u32 g7_marker;
    u32 combined_value;
    u32 route;
    u32 reset_tail_called;
    u32 checksum_helper;
    u32 table_copy_helper;
    u32 reset_tail_return;
    u32 state_body_entry;
};

void recovered_input_state_rejoin_plan_3884(
    u32 g0_input, u32 g7_marker,
    struct recovered_input_state_rejoin_plan_3884 *plan)
{
    u32 combined = g0_input | g7_marker;

    plan->g0_input = g0_input;
    plan->g7_marker = g7_marker;
    plan->combined_value = combined;
    plan->route = combined == 0U ? RECOVERED_INPUT_REJOIN_RESET_TAIL
                                 : RECOVERED_INPUT_REJOIN_STATE_BODY;
    plan->reset_tail_called = combined == 0U ? 1U : 0U;
    plan->checksum_helper = 0x000022f0U;
    plan->table_copy_helper = 0x00002330U;
    plan->reset_tail_return = 0x00003a20U;
    plan->state_body_entry = 0x0000388cU;
}
