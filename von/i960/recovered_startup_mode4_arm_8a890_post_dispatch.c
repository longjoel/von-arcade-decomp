/* Post-selector packet dispatch recovered from i960 0x8a890-0x8a960. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selector_51c99c;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 linked_record_8;
    recovered_u32 linked_record_10;
    recovered_u32 fifo_response;
    recovered_u32 packet_10[3];
    recovered_u32 state_51c940;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 target;
} recovered_startup_mode4_arm_8a890_post_dispatch_result;

recovered_startup_mode4_arm_8a890_post_dispatch_result
recovered_startup_mode4_arm_8a890_post_dispatch(
    recovered_u32 selector_51c99c, recovered_u32 current_record_8,
    recovered_u32 current_record_10, recovered_u32 linked_record_8,
    recovered_u32 linked_record_10, recovered_u32 fifo_response)
{
    recovered_startup_mode4_arm_8a890_post_dispatch_result result;

    result.selector_51c99c = selector_51c99c;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.linked_record_8 = linked_record_8;
    result.linked_record_10 = linked_record_10;
    result.fifo_response = fifo_response;
    result.packet_10[0] = 10U;
    result.packet_10[1] = current_record_10 - linked_record_10;
    result.packet_10[2] = linked_record_8 - current_record_8;
    result.state_51c940 = fifo_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    switch (selector_51c99c) {
    case 0U:
        result.target = 0x0008a964U;
        break;
    case 1U:
        result.target = 0x0008aba4U;
        break;
    case 2U:
        result.target = 0x0008aed8U;
        break;
    case 3U:
        result.target = 0x0008b21cU;
        break;
    default:
        result.target = 0U;
        break;
    }
    return result;
}
