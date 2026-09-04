/* Proven routing and FIFO framing for the dynamic command-6 phase at 0x24690. */
#include <stdint.h>
#include <string.h>
#include "recovered_float.h"

typedef uint32_t u32;

enum recovered_geometry_command6_route {
    RECOVERED_GEOMETRY_COMMAND6_MODE_ZERO = 0,
    RECOVERED_GEOMETRY_COMMAND6_DYNAMIC = 1,
};

struct recovered_geometry_command6_loop_plan {
    u32 route;
    u32 initial_index;
    u32 iteration_limit;
    u32 active_mask;
    u32 active_packet_header[2];
    u32 fallback_packet_header[2];
    u32 packet_word_count_before_readback;
    u32 readback_address;
    u32 publish_address;
    u32 loop_increment;
};

struct recovered_geometry_command6_packet {
    u32 words[6];
};

/*
 * The disassembly compares 0x503a78 against zero before entering the loop.
 * The loop starts at index zero and compares that index against 0x503a6c;
 * the active form additionally requires bit 2 of the separate 0x5024e8 mask.
 */
void recovered_geometry_command6_loop_plan(
    int32_t mode_status, u32 per_iteration_limit, u32 active_mask,
    struct recovered_geometry_command6_loop_plan *plan)
{
    plan->route = mode_status < 0
        ? RECOVERED_GEOMETRY_COMMAND6_MODE_ZERO
        : RECOVERED_GEOMETRY_COMMAND6_DYNAMIC;
    plan->initial_index = 0U;
    plan->iteration_limit = per_iteration_limit;
    plan->active_mask = active_mask;
    plan->active_packet_header[0] = 5U;
    plan->active_packet_header[1] = 19U;
    plan->fallback_packet_header[0] = 5U;
    plan->fallback_packet_header[1] = 19U;
    /* 5, 19, two computed words, constants 1 and 58, then readback. */
    plan->packet_word_count_before_readback = 6U;
    plan->readback_address = 0x00802008U;
    plan->publish_address = 0x00801008U;
    plan->loop_increment = 1U;
}

u32 recovered_geometry_command6_active_iteration(
    u32 index, u32 per_iteration_limit, u32 active_mask)
{
    return index < per_iteration_limit && (active_mask & 4U) != 0U;
}

/* Both 0x24788 and 0x248cc forms share this six-word FIFO shape. */
void recovered_geometry_command6_packet(
    u32 computed0, u32 computed1,
    struct recovered_geometry_command6_packet *packet)
{
    packet->words[0] = 5U;
    packet->words[1] = 19U;
    packet->words[2] = computed0;
    packet->words[3] = computed1;
    packet->words[4] = 1U;
    packet->words[5] = 58U;
}

/* The two computed words are rounded to single precision after i960 divrl. */
void recovered_geometry_command6_packet_from_r6_bits(
    u32 r6_bits, struct recovered_geometry_command6_packet *packet)
{
    float r6_value;

    memcpy(&r6_value, &r6_bits, sizeof(r6_value));
    recovered_geometry_command6_packet(
        recovered_float_to_bits((float)(4.0 / 600.0)),
        recovered_float_to_bits((float)((double)r6_value / 600.0)),
        packet);
}
