/* Match/time diagnostic service contract recovered from i960 0xf0980-f0b38. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_state_address, result_state_before, result_state_after;
    recovered_u32 initialization_call, initialization_performed;
    recovered_u32 counter_address, counter_value;
    recovered_u32 header_x, header_y, header_string, label_wrapper;
    recovered_u32 mode_state_address, mode_state;
    recovered_u32 prompt_x, prompt_y, prompt_string;
    recovered_u32 builder_count;
    recovered_u32 builder_destination[8], builder_source[8], builder_flags[8];
    recovered_u32 structure_destination, structure_first_value;
    recovered_u32 structure_repeat_value, structure_repeat_count;
    recovered_u32 structure_tail_value, structure_tail_count;
    recovered_u32 fallback_call, state_reset_value;
    recovered_u32 mode_counter_after, pending_state_address, pending_state_value;
    recovered_u32 return_target;
} recovered_diagnostic_match_time_test_service_result_f0980;

int
recovered_diagnostic_match_time_test_service_f0980(
    recovered_u32 result_state, recovered_u32 mode_state,
    recovered_u32 register_10, recovered_u32 register_15,
    recovered_diagnostic_match_time_test_service_result_f0980 *result)
{
    recovered_diagnostic_match_time_test_service_result_f0980 local = {0};
    local.result_state_address = 0x00578500U;
    local.result_state_before = result_state;
    local.result_state_after = result_state;
    local.initialization_call = 0x0001c618U;
    local.initialization_performed = (result_state == 0U);
    if (local.initialization_performed)
        local.result_state_after = 1U;
    local.counter_address = 0x00578504U;
    local.counter_value = mode_state;
    local.header_x = 23U; local.header_y = 1U;
    local.header_string = 0x000f0940U; local.label_wrapper = 0x000eaeb0U;
    local.mode_state_address = 0x00578504U;
    local.mode_state = mode_state;
    local.prompt_x = (mode_state == 0U) ? 17U : 19U;
    local.prompt_y = 46U;
    local.prompt_string = (mode_state == 0U) ? 0x000f0960U : 0x000ed1e0U;
    local.structure_destination = 0x01004000U;
    local.fallback_call = 0x000eade8U;
    local.return_target = 0x000f0b38U;
    local.state_reset_value = 0U;
    local.mode_counter_after = mode_state;
    local.pending_state_address = 0x005784f8U;
    local.pending_state_value = 2U;

    if (mode_state == 0U) {
        local.builder_count = 2U;
        local.builder_destination[0] = 0x01004000U;
        local.builder_source[0] = 0x02bde7acU;
        local.builder_flags[0] = 0x80U;
        local.builder_destination[1] = 0x01004000U;
        local.builder_source[1] = 0x02be27ecU;
        local.builder_flags[1] = 0x80U;
        local.structure_first_value = 23U;
        local.structure_repeat_value = 0U;
        local.structure_repeat_count = 0U;
        local.structure_tail_value = 24U;
        local.structure_tail_count = 1U;
    } else {
        local.builder_count = 5U;
        local.builder_destination[0] = 0x01004000U;
        local.builder_source[0] = 0x02bde82cU;
        local.builder_flags[0] = 0x80U;
        local.builder_destination[1] = 0U;
        local.builder_source[1] = 0x02be286cU;
        local.builder_flags[1] = 0x80U;
        local.builder_destination[2] = 0U;
        local.builder_source[2] = 0x02be28acU;
        local.builder_flags[2] = 0x80U;
        local.builder_destination[3] = 0U;
        local.builder_source[3] = 0x02be28ecU;
        local.builder_flags[3] = 0x80U;
        local.builder_destination[4] = 0U;
        local.builder_source[4] = 0x02be292cU;
        local.builder_flags[4] = 0x80U;
        local.structure_repeat_count = 31U + register_15;
        local.structure_tail_count = 1U;
    }
    /* The final service call advances the mode counter only on success. */
    if (mode_state != 0U && register_10 == 0U) {
        local.mode_counter_after = mode_state + 0xffffffffU;
        local.pending_state_value = 2U;
    }
    (void)register_10;
    if (result != (recovered_diagnostic_match_time_test_service_result_f0980 *)0)
        *result = local;
    return 1;
}
