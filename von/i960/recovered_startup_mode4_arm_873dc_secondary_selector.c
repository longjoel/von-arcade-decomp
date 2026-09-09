/* Secondary slot-20 response selector recovered from i960 0x873dc-0x87428. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_value, response_value, response_mask, normalized_response;
    recovered_u32 status_source_address, response_source_address;
    recovered_u32 special_response, special_mode, special_store_address, special_store_value;
    recovered_u32 special_path, special_target, response_byte, normalization_remainder;
    recovered_u32 threshold, failure_target, table_address, dispatch_index;
    recovered_u32 dispatch_slot_address, dispatch_target;
} recovered_startup_mode4_arm_result_873dc_secondary_selector;

int recovered_startup_mode4_arm_873dc_secondary_selector(
    recovered_u32 status_value, recovered_u32 response_value,
    recovered_startup_mode4_arm_result_873dc_secondary_selector *result)
{
    recovered_startup_mode4_arm_result_873dc_secondary_selector r = {0};
    static const recovered_u32 targets[14][2] = {
        {0x01U, 0x876e8U}, {0x1fU, 0x87704U}, {0x25U, 0x87720U},
        {0x31U, 0x8775cU}, {0x37U, 0x87778U}, {0x3dU, 0x87794U},
        {0x49U, 0x8779cU}, {0x4fU, 0x877d0U}, {0x7fU, 0x8780cU},
        {0x85U, 0x87828U}, {0x8bU, 0x87844U}, {0x9dU, 0x8784cU},
        {0xa9U, 0x87888U}, {0U, 0U}
    };

    r.status_value = status_value;
    r.response_value = response_value;
    /* g0 is the preceding FIFO result; the selector value is reloaded from
     * 0x51c990 after the zero-status gate. */
    r.status_source_address = 0x51c9d0U;
    r.response_source_address = 0x51c990U;
    r.response_mask = 0xffU;
    r.special_response = 10U;
    r.special_mode = 9U;
    r.special_store_address = 0x51c97cU;
    r.special_store_value = 9U;
    r.special_target = 0x878d8U;
    r.threshold = 0xafU;
    r.failure_target = 0x878e8U;
    r.table_address = 0x87428U;
    if (status_value != 0U) {
        r.dispatch_target = r.failure_target;
    } else if (response_value == r.special_response) {
        r.special_path = 1U;
        r.dispatch_target = r.special_target;
    } else {
        r.response_byte = response_value & r.response_mask;
        r.normalized_response = r.response_byte;
        if (r.normalized_response != 0U)
            r.normalization_remainder = (r.normalized_response - 1U) % 6U,
            r.normalized_response -= r.normalization_remainder;
        r.dispatch_target = r.failure_target;
        if (r.normalized_response <= r.threshold) {
            r.dispatch_index = r.normalized_response;
            r.dispatch_slot_address = r.table_address + r.dispatch_index * 4U;
            for (recovered_u32 i = 0; targets[i][0] != 0U; ++i) {
                if (targets[i][0] == r.normalized_response) {
                    r.dispatch_target = targets[i][1];
                    break;
                }
            }
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
