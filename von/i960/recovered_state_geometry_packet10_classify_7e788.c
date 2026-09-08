/* Geometry packet-10/classifier setup recovered from 0x7e788-0x7e834. */
#include <stdint.h>

typedef uint32_t u32;

extern u32 recovered_signed_band(u32 raw);

struct recovered_state_geometry_packet10_classify_7e788_plan {
    u32 record_offset;
    u32 packet[3];
    u32 fifo_response;
    u32 response_minus_record_08;
    u32 response_bit15_set;
    u32 signed_record_08;
    u32 signed_object_184;
    u32 classifier_bias;
    u32 classifier_input;
    u32 classifier_band;
    u32 classifier_target;
    u32 result_table;
};

static u32 sign_extend_halfword(u32 value)
{
    return (u32)(int32_t)(int16_t)(uint16_t)value;
}

void recovered_state_geometry_packet10_classify_7e788(
    u32 frame_selector, u32 record_field_08, u32 record_field_10,
    u32 record_field_18, u32 fifo_response, uint16_t object_184,
    struct recovered_state_geometry_packet10_classify_7e788_plan *plan)
{
    const u32 signed_record_08 = sign_extend_halfword(record_field_08);
    const u32 signed_object_184 = sign_extend_halfword(object_184);
    const u32 response_delta = fifo_response - record_field_08;
    const u32 bit15 = response_delta & 0x8000U;
    const u32 bias = bit15 != 0U ? 0x504de4U : 0U;
    const u32 signed_bias = bit15 != 0U ? 0x504de4U : 0U;
    const u32 input = bit15 != 0U
        ? signed_record_08 - signed_bias - signed_object_184
        : signed_record_08 + signed_bias - signed_object_184;

    plan->record_offset = frame_selector << 5;
    plan->packet[0] = 10U;
    plan->packet[1] = record_field_10 - record_field_18;
    plan->packet[2] = record_field_10 - record_field_08;
    plan->fifo_response = fifo_response;
    plan->response_minus_record_08 = response_delta;
    plan->response_bit15_set = bit15 != 0U ? 1U : 0U;
    plan->signed_record_08 = signed_record_08;
    plan->signed_object_184 = signed_object_184;
    plan->classifier_bias = bias;
    plan->classifier_input = input;
    plan->classifier_band = recovered_signed_band(input);
    plan->classifier_target = 0x00073508U;
    plan->result_table = 0x0072660U;
}
