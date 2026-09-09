/* State-4 difference route recovered from i960 0x7f774-0x7f7d4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_difference_route_7f774_plan {
    u32 published_status;
    int32_t related_184;
    int32_t current_184;
    u32 positive_bias_arm;
    int32_t bias;
    int32_t biased_current;
    int32_t reverse_difference;
    u32 classifier_target;
    u32 result_table;
    u32 common_publication_target;
};

void recovered_transition_state4_difference_route_7f774(
    u32 published_status, int32_t related_184, int32_t current_184,
    struct recovered_transition_state4_difference_route_7f774_plan *plan)
{
    const u32 positive = published_status > 4U ? 1U : 0U;
    const int32_t bias = positive ? 0x5000 : -0x5000;
    const int32_t biased = current_184 + bias;

    plan->published_status = published_status;
    plan->related_184 = related_184;
    plan->current_184 = current_184;
    plan->positive_bias_arm = positive;
    plan->bias = bias;
    plan->biased_current = biased;
    plan->reverse_difference = related_184 - biased;
    plan->classifier_target = 0x00073508U;
    plan->result_table = 0x00072780U;
    plan->common_publication_target = 0x0007f7d4U;
}
