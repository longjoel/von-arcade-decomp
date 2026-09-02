/* Object-state packet and status latch recovered from i960 0x24eb4-0x24f70. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_object_state_packet_plan {
    u32 lookup_helper;
    u32 lookup_arg0;
    u32 lookup_arg1;
    u32 fifo_address;
    u32 packet_count;
    u32 packet[7];
    u32 board_readback_address;
    u32 response_consumer;
    u32 status_byte;
    u32 status_threshold;
    u32 status_global_active;
    u32 state_word;
    u32 current_status;
    u32 current_frame_value;
    u32 status_store;
    u32 status_update_helper;
    u32 status_update_arg;
    u32 status_update_called;
};

void recovered_geometry_object_state_packet_plan(
    const u32 helper_fields[3], const u32 object_fields[3],
    u32 board_readback_address, u32 status_byte,
    u32 status_global_active, u32 state_word, u32 current_status,
    u32 current_frame_value,
    struct recovered_geometry_object_state_packet_plan *plan)
{
    plan->lookup_helper = 0x01cac8U;
    plan->lookup_arg0 = 10U;
    plan->lookup_arg1 = 24U;
    plan->fifo_address = 0x00884000U;
    plan->packet_count = 7U;
    plan->packet[0] = 31U;
    plan->packet[1] = helper_fields[0];
    plan->packet[2] = object_fields[0];
    plan->packet[3] = helper_fields[1];
    plan->packet[4] = object_fields[1];
    plan->packet[5] = helper_fields[2];
    plan->packet[6] = object_fields[2];
    plan->board_readback_address = board_readback_address;
    plan->response_consumer = 0x01e370U;
    plan->status_byte = status_byte & 0xffU;
    plan->status_threshold = 0xc8U;
    plan->status_global_active = status_global_active;
    plan->state_word = state_word;
    plan->current_status = current_status;
    plan->current_frame_value = current_frame_value;
    plan->status_store = current_status;
    plan->status_update_helper = 0U;
    plan->status_update_arg = 0U;
    plan->status_update_called = 0U;

    /* cmpoble +0x1da,0xc8: the active status path requires a value > 200. */
    if (plan->status_byte > plan->status_threshold && status_global_active != 0U) {
        plan->status_store = state_word & 2U;
        plan->status_update_helper = 0x01f080U;
        plan->status_update_arg = plan->status_store;
        plan->status_update_called = 1U;
        return;
    }

    /* Otherwise the persistent latch is only initialized once. At 0x24f60
     * the original stores g14, which still holds the frame-control word
     * loaded at 0x24d9c (0x101), rather than the board/frame input. */
    if (current_status == 0U) {
        plan->status_store = 0x101U;
        plan->status_update_helper = 0x01f080U;
        plan->status_update_arg = 0U;
        plan->status_update_called = 1U;
    }
}
