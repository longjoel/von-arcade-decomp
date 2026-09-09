/* Fixed packet prefix recovered from i960 0xbe304-0xbe3ac. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 linked_halfword_2;
    recovered_u32 linked_field_64;
    recovered_u32 linked_field_172;
    recovered_u32 linked_word_14;
    recovered_u32 linked_word_18;
    recovered_u32 linked_word_1c;
    recovered_u32 profile_word_0;
    recovered_u32 profile_word_4;
    recovered_u32 profile_word_8;
    recovered_u32 profile_word_c;
} recovered_object_profile_packet_prefix_input_be304;

typedef struct {
    recovered_u32 accepted;
    recovered_u32 profile_index;
    recovered_u32 scale_bits;
    recovered_u32 fifo_word[8];
    recovered_u32 fifo_count;
} recovered_object_profile_packet_prefix_result_be304;

static recovered_u32 multiply_float_bits(recovered_u32 value_bits,
                                         recovered_u32 scale_bits)
{
    union { recovered_u32 bits; float value; } value;
    union { recovered_u32 bits; float value; } scale;
    union { recovered_u32 bits; float product; } result;

    value.bits = value_bits;
    scale.bits = scale_bits;
    result.product = value.value * scale.value;
    return result.bits;
}

void recovered_object_profile_packet_prefix_be304(
    const recovered_object_profile_packet_prefix_input_be304 *input,
    recovered_object_profile_packet_prefix_result_be304 *result)
{
    int16_t field_172 = (int16_t)(input->linked_field_172 & 0xffffU);

    result->accepted = input->linked_halfword_2 == 0U ? 1U : 0U;
    result->profile_index = input->linked_field_64;
    result->scale_bits = field_172 == 14 ? 0x3f000000U : 0x3f800000U;
    result->fifo_count = 0U;
    if (!result->accepted)
        return;
    result->fifo_word[0] = 70U;
    result->fifo_word[1] = input->linked_word_14;
    result->fifo_word[2] = input->linked_word_18;
    result->fifo_word[3] = input->linked_word_1c;
    result->fifo_word[4] = multiply_float_bits(input->profile_word_4,
                                                result->scale_bits);
    result->fifo_word[5] = input->profile_word_8;
    result->fifo_word[6] = input->profile_word_0;
    result->fifo_word[7] = input->profile_word_c;
    result->fifo_count = 8U;
}
