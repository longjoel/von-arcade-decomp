/* Geometry-board request prefix recovered from i960 0x80180-0x80240. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_command29_30_prefix_80180_plan {
    int32_t object_word_8;
    int32_t object_word_10;
    u32 anchor_word;
    u32 plus_6000_word;
    u32 minus_6000_word;
    u32 response_command29;
    u32 response_command30_plus;
    u32 response_command30_minus;
    u32 command29_difference;
    u32 command30_minus_difference;
    u32 packet_words;
    u32 fifo_destination;
};

static u32 masked_halfword(int32_t value)
{
    return (u32)value & 0xffffU;
}

/*
 * The source loads object +0x08 with ldos but loads +0x10 as a full word,
 * emits the three request triplets below, and reads one response after each
 * triplet.  The i960 subr operations then form field_10-response for the
 * first and third responses.  Inputs are explicit because the object record
 * and board reply are runtime state outside this pure packet model.
 */
void recovered_geometry_command29_30_prefix_80180(
    int32_t object_word_8,
    int32_t object_word_10,
    u32 anchor_word,
    u32 response_command29,
    u32 response_command30_plus,
    u32 response_command30_minus,
    struct recovered_geometry_command29_30_prefix_80180_plan *plan)
{
    const u32 plus_6000_word = masked_halfword(object_word_8 + 0x6000);
    const u32 minus_6000_word = masked_halfword(object_word_8 - 0x6000);

    plan->object_word_8 = object_word_8;
    plan->object_word_10 = object_word_10;
    plan->anchor_word = anchor_word;
    plan->plus_6000_word = plus_6000_word;
    plan->minus_6000_word = minus_6000_word;
    plan->response_command29 = response_command29;
    plan->response_command30_plus = response_command30_plus;
    plan->response_command30_minus = response_command30_minus;
    plan->command29_difference =
        (u32)(object_word_10 - (int32_t)response_command29);
    plan->command30_minus_difference =
        (u32)(object_word_10 - (int32_t)response_command30_minus);
    plan->packet_words = 9U;
    plan->fifo_destination = 0x00884000U;
}
