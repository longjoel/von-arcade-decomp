/* Descriptor/table selection prefix recovered from i960 0x9c050. */
#include "recovered_common.h"

int recovered_geometry_projection_grid_index(recovered_u32 first_bits,
                                             recovered_u32 second_bits,
                                             recovered_u32 r9,
                                             int *first_quotient,
                                             int *second_quotient,
                                             recovered_u32 *index);

typedef struct {
    recovered_u32 first_coordinate_bits;
    recovered_u32 second_coordinate_bits;
    recovered_u32 linked_first_coordinate_bits;
    recovered_u32 linked_second_coordinate_bits;
    recovered_u32 r9;
    recovered_u32 descriptor_gate_passed;
} recovered_geometry_descriptor_select_input_9c050;

typedef struct {
    recovered_u32 first_index;
    recovered_u32 linked_index;
    recovered_u32 first_table_index;
    recovered_u32 linked_table_index;
    recovered_u32 first_value_562c80;
    recovered_u32 linked_value_562c84;
    recovered_u32 first_fallback;
    recovered_u32 linked_fallback;
} recovered_geometry_descriptor_select_result_9c050;

int recovered_geometry_descriptor_select_9c050(
    const recovered_geometry_descriptor_select_input_9c050 *input,
    const recovered_u32 table[576],
    recovered_geometry_descriptor_select_result_9c050 *result)
{
    int first_index;
    int linked_index;
    if (input->descriptor_gate_passed == 0U)
        return 0;
    if (!recovered_geometry_projection_grid_index(
            input->first_coordinate_bits, input->second_coordinate_bits,
            input->r9, (int *)0, (int *)0, &result->first_index))
        return 0;
    if (!recovered_geometry_projection_grid_index(
        input->linked_first_coordinate_bits,
        input->linked_second_coordinate_bits, input->r9,
        (int *)0, (int *)0, &result->linked_index))
        return 0;
    first_index = (int)result->first_index;
    linked_index = (int)result->linked_index;
    result->first_fallback = (first_index < 0 || first_index > 0x23f) ? 1U : 0U;
    result->linked_fallback = (linked_index < 0 || linked_index > 0x23f) ? 1U : 0U;
    result->first_table_index = result->first_fallback ? 0U : result->first_index;
    result->linked_table_index = result->linked_fallback ? 0U : result->linked_index;
    result->first_value_562c80 = table[result->first_table_index];
    result->linked_value_562c84 = table[result->linked_table_index];
    return 1;
}
