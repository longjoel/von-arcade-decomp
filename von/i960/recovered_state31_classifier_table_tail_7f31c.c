/* Classifier table tail recovered from i960 0x7f31c-0x7f32c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_classifier_table_tail_7f31c_plan {
    u32 classifier_index;
    u32 table_address;
    u32 table_value;
    u32 related_pointer;
    u32 result_register;
    u32 next_argument;
    u32 target;
};

void recovered_state31_classifier_table_tail_7f31c(
    u32 classifier_index, u32 table_value, u32 related_pointer,
    struct recovered_state31_classifier_table_tail_7f31c_plan *plan)
{
    plan->classifier_index = classifier_index;
    plan->table_address = 0x00072780U + classifier_index * 4U;
    plan->table_value = table_value;
    plan->related_pointer = related_pointer;
    plan->result_register = table_value;
    plan->next_argument = related_pointer;
    plan->target = 0x0007ecb0U;
}
