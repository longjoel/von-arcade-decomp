/* State-31 32-slot scan recovered from i960 0x7ebcc-0x7ecc0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_slot_scan_7ebcc_plan {
    u32 candidate_count;
    u32 best_found;
    u32 best_index;
    u32 best_response;
    u32 best_mask;
    u32 packet_command;
    u32 packet_words[4];
    u32 state8_tail;
    u32 tail_control;
    u32 tail_selector;
    u32 tail_action;
    u32 tail_table_index;
    u32 tail_result;
    u32 tail_result_table;
    u32 tail_call_target;
    u32 scan_target;
};

/*
 * response_below_best[i] is the result of the target-real comparison at
 * 0x7ec54. Keeping that comparison injected preserves the exact selection
 * loop while leaving the i960 real encoding outside this integer model.
 */
void recovered_state31_slot_scan_7ebcc(
    const uint8_t active_bytes[32],
    const uint8_t response_below_best[32],
    const u32 related_minus_8[32], const u32 related_0[32],
    const u32 responses[32], u32 object_plus_8, u32 object_plus_10,
    u32 object_state, u32 status_504d68, u32 status_table_value,
    struct recovered_state31_slot_scan_7ebcc_plan *plan)
{
    u32 best_response = 0xbf800000U;
    u32 best_index = 0U;
    u32 best_mask = 0U;
    u32 candidate_count = 0U;
    u32 best_found = 0U;

    for (u32 index = 0U; index < 32U; ++index) {
        if (active_bytes[index] == 0U)
            continue;
        ++candidate_count;
        if (response_below_best[index] == 0U)
            continue;
        best_response = responses[index];
        best_index = index;
        best_mask = (u32)active_bytes[index] & 0xffU;
        best_found = 1U;
    }

    plan->candidate_count = candidate_count;
    plan->best_found = best_found;
    plan->best_index = best_index;
    plan->best_response = best_response;
    plan->best_mask = best_mask;
    plan->packet_command = 62U;
    plan->packet_words[0] = related_minus_8[best_index];
    plan->packet_words[1] = object_plus_8;
    plan->packet_words[2] = related_0[best_index];
    plan->packet_words[3] = object_plus_10;
    plan->state8_tail = object_state == 8U ? 1U : 0U;
    plan->tail_control = plan->state8_tail ? 3U : 0U;
    plan->tail_selector = plan->state8_tail ? 0x64U : 0U;
    plan->tail_action = 0U;
    plan->tail_table_index = plan->state8_tail ? status_504d68 : 0U;
    plan->tail_result = plan->state8_tail ? status_table_value : 0U;
    plan->tail_result_table = 0x0072780U;
    plan->tail_call_target = 0x00079050U;
    plan->scan_target = 0x0007ebccU;
}
