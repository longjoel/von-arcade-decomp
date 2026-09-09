/* Command-62 geometry-board packet recovered from i960 0x80400-0x80448. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_command62_packet_80400_plan {
    u32 selected_word_10;
    u32 selected_word_18;
    u32 object_word_8;
    u32 object_word_10;
    u32 packet_opcode;
    u32 packet_payload_0;
    u32 packet_payload_1;
    u32 packet_payload_2;
    u32 packet_payload_3;
    u32 board_response;
    u32 packet_words;
    u32 fifo_destination;
    u32 floating_gate_start;
};

/*
 * The four loads immediately before the FIFO stores are unambiguous:
 * [selected +0x10, object +0x08, selected +0x18, object +0x10].  The opcode
 * is addo(31,31), or 62.  The response is read before the first floating
 * comparison at 0x80428; its value is therefore a caller-provided input.
 */
void recovered_geometry_command62_packet_80400(
    u32 selected_word_10,
    u32 selected_word_18,
    u32 object_word_8,
    u32 object_word_10,
    u32 board_response,
    struct recovered_geometry_command62_packet_80400_plan *plan)
{
    plan->selected_word_10 = selected_word_10;
    plan->selected_word_18 = selected_word_18;
    plan->object_word_8 = object_word_8;
    plan->object_word_10 = object_word_10;
    plan->packet_opcode = 62U;
    plan->packet_payload_0 = selected_word_10;
    plan->packet_payload_1 = object_word_8;
    plan->packet_payload_2 = selected_word_18;
    plan->packet_payload_3 = object_word_10;
    plan->board_response = board_response;
    plan->packet_words = 5U;
    plan->fifo_destination = 0x00884000U;
    plan->floating_gate_start = 0x00080428U;
}
