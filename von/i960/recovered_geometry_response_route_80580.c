/* Converged response route recovered from i960 0x80580-0x80600. */
#include <stdint.h>

typedef uint32_t u32;

extern u32 recovered_signed_band(u32 raw);

struct recovered_geometry_response_route_80580_plan {
    u32 bit15_set;
    int32_t record_word_8;
    int32_t object_word_184;
    int32_t bias_504de4;
    int32_t signed_classifier_input;
    u32 classifier_band;
    u32 classifier_target;
    u32 result_table;
    u32 classifier_result;
    u32 action_destination;
    u32 action_value;
    u32 status_destination;
    u32 published_status;
    u32 callback_target;
    u32 callback_argument;
    u32 global_counter;
    u32 global_threshold;
    u32 counter_gate_passed;
    u32 next_target;
};

static int32_t sign_extend_halfword(int32_t value)
{
    const u32 low = (u32)value & 0xffffU;
    return (int32_t)((low & 0x8000U) != 0U ? low | 0xffff0000U : low);
}

/*
 * Both bit arms normalize the record +0x08 and object +0x184 halfwords.  The
 * clear-bit arm uses no bias; the set-bit arm subtracts the 0x504de4 bias.
 * The common tail calls the
 * classifier, selects 0x72660[classifier*4], publishes action 20 and the
 * result, calls 0x7d1f0 with the original object pointer, then tests the
 * 0x509b24 counter against 0x5dc.
 */
void recovered_geometry_response_route_80580(
    u32 bit15_set,
    int32_t record_word_8,
    int32_t object_word_184,
    int32_t bias_504de4,
    u32 classifier_result,
    u32 object_pointer,
    u32 global_counter,
    struct recovered_geometry_response_route_80580_plan *plan)
{
    const int32_t record = sign_extend_halfword(record_word_8);
    const int32_t object = sign_extend_halfword(object_word_184);
    const int32_t bias = bit15_set != 0U ? bias_504de4 : 0;
    const int64_t input = bit15_set != 0U
        ? (int64_t)record - bias - object
        : (int64_t)record - object;

    plan->bit15_set = bit15_set != 0U ? 1U : 0U;
    plan->record_word_8 = record;
    plan->object_word_184 = object;
    plan->bias_504de4 = bias;
    plan->signed_classifier_input = (int32_t)input;
    plan->classifier_band = recovered_signed_band((u32)(int32_t)input);
    plan->classifier_target = 0x00073508U;
    plan->result_table = 0x00072660U;
    plan->classifier_result = classifier_result;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 20U;
    plan->status_destination = 0x00504d94U;
    plan->published_status = classifier_result;
    plan->callback_target = 0x0007d1f0U;
    plan->callback_argument = object_pointer;
    plan->global_counter = global_counter;
    plan->global_threshold = 0x5dcU;
    plan->counter_gate_passed = global_counter > 0x5dcU ? 1U : 0U;
    plan->next_target = plan->counter_gate_passed != 0U
        ? 0x00080600U : 0x000806f4U;
}
