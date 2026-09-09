/* Slot-20 response selector recovered from i960 0x86eec-0x86f30. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_value;
    recovered_u32 response_source_address;
    recovered_u32 special_response, special_store_address, special_store_value;
    recovered_u32 special_path;
    recovered_u32 response_mask, response_byte;
    recovered_u32 normalized_response;
    recovered_u32 normalization_remainder;
    recovered_u32 threshold, threshold_exceeded;
    recovered_u32 dispatch_table_address, dispatch_index, dispatch_slot_address;
    recovered_u32 dispatch_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_86eec_response_selector;

int recovered_startup_mode4_arm_86eec_response_selector(
    recovered_u32 response_value,
    recovered_startup_mode4_arm_result_86eec_response_selector *result)
{
    recovered_startup_mode4_arm_result_86eec_response_selector r = {0};

    r.response_value = response_value;
    /* 0x86eec reloads this selector input from 0x51c98c; it is distinct
     * from the preceding FIFO response loaded from 0x51c9d0. */
    r.response_source_address = 0x51c98cU;
    r.special_response = 10U;
    r.special_store_address = 0x51c97cU;
    r.special_store_value = 8U;
    r.response_mask = 0xffU;
    r.response_byte = response_value & r.response_mask;
    r.threshold = 0xafU;
    r.dispatch_table_address = 0x86f34U;
    if (response_value == r.special_response) {
        r.special_path = 1U;
        r.continuation_target = 0x873ccU;
    } else {
        r.normalized_response = r.response_byte;
        if (r.normalized_response != 0U) {
            r.normalization_remainder = (r.normalized_response - 1U) % 6U;
            r.normalized_response -= r.normalization_remainder;
        }
        r.threshold_exceeded = r.normalized_response > r.threshold ? 1U : 0U;
        if (r.threshold_exceeded != 0U) {
            r.continuation_target = 0x878e8U;
        } else {
            r.dispatch_index = r.normalized_response;
            r.dispatch_slot_address = r.dispatch_table_address +
                                       r.dispatch_index * 4U;
            r.dispatch_target = 0x878e8U;
            switch (r.dispatch_index) {
            case 0x01U: r.dispatch_target = 0x871f4U; break;
            case 0x1fU: r.dispatch_target = 0x87210U; break;
            case 0x25U: r.dispatch_target = 0x8722cU; break;
            case 0x31U: r.dispatch_target = 0x87248U; break;
            case 0x37U: r.dispatch_target = 0x87264U; break;
            case 0x3dU: r.dispatch_target = 0x87280U; break;
            case 0x49U: r.dispatch_target = 0x8729cU; break;
            case 0x4fU: r.dispatch_target = 0x872d0U; break;
            case 0x7fU: r.dispatch_target = 0x8730cU; break;
            case 0x85U: r.dispatch_target = 0x87328U; break;
            case 0x8bU: r.dispatch_target = 0x87344U; break;
            case 0x9dU: r.dispatch_target = 0x87360U; break;
            case 0xa9U: r.dispatch_target = 0x8737cU; break;
            default: break;
            }
            r.continuation_target = r.dispatch_target;
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
