/* Shared mode-4 dispatch gate recovered from i960 0x89b30-0x89c04. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_51c984;
    recovered_u32 g14_value;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 linked_record_8;
    recovered_u32 linked_record_10;
    recovered_u32 fifo_response;
    recovered_u32 selector_51c99c;
    recovered_u32 packet_10[3];
    recovered_u32 state_51c940;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 target;
} recovered_startup_mode4_arm_common_dispatch_89b30_result;

recovered_startup_mode4_arm_common_dispatch_89b30_result
recovered_startup_mode4_arm_common_dispatch_89b30(
    recovered_u32 counter_51c984, recovered_u32 g14_value,
    recovered_u32 current_record_8, recovered_u32 current_record_10,
    recovered_u32 linked_record_8, recovered_u32 linked_record_10,
    recovered_u32 fifo_response)
{
    recovered_startup_mode4_arm_common_dispatch_89b30_result result;

    result.counter_51c984 = counter_51c984;
    result.g14_value = g14_value;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.linked_record_8 = linked_record_8;
    result.linked_record_10 = linked_record_10;
    result.fifo_response = fifo_response;
    if (counter_51c984 <= 59U) {
        result.selector_51c99c = g14_value;
    } else if (counter_51c984 <= 0x77U) {
        result.selector_51c99c = 1U;
    } else if (counter_51c984 <= 0x95U) {
        result.selector_51c99c = 2U;
    } else {
        result.selector_51c99c = 3U;
    }
    result.packet_10[0] = 10U;
    result.packet_10[1] = current_record_10 - linked_record_10;
    result.packet_10[2] = linked_record_8 - current_record_8;
    result.state_51c940 = fifo_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    switch (result.selector_51c99c) {
    case 1U:
        result.target = 0x00089e44U;
        break;
    case 2U:
        result.target = 0x0008a178U;
        break;
    case 3U:
        result.target = 0x0008a4bcU;
        break;
    case 0U:
        result.target = 0x00089c04U;
        break;
    default:
        result.target = 0U;
        break;
    }
    return result;
}
