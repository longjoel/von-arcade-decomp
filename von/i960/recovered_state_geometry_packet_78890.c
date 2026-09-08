/* Geometry packet plan recovered from i960 0x78890-0x78a28. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_packet_78890 {
    u32 selector;
    u32 status;
    u32 transition;
    u32 action;
    /* command 29, command 30, command 10, then command 31+31 tail */
    u32 packet[15];
};

/* Keep the i960 ldos sign extension before the 16-bit FIFO wrapping. */
static u32 wrapped_coordinate_with_bias(uint16_t raw_coordinate,
                                        int32_t bias)
{
    int32_t coordinate = (int32_t)(int16_t)raw_coordinate;
    return ((u32)(coordinate + bias)) & 0xffffU;
}

/*
 * scale_bits is the result of the 0x504df8 conversion/division prologue;
 * first_response and second_response are the two 0x884000 reads. The
 * command-31 response is deliberately not modeled: only its six input words
 * and the subsequent status override are within this boundary.
 */
static void recovered_state_geometry_packet_with_bias(
    uint32_t selector_table_value,
    uint32_t scale_bits,
    uint16_t object_184,
    uint32_t object_08,
    uint32_t object_10,
    uint32_t related_08,
    uint32_t related_10,
    uint32_t first_response,
    uint32_t second_response,
    uint32_t mode_bits,
    uint32_t control_504dc8,
    int32_t coordinate_bias,
    struct recovered_state_geometry_packet_78890 *out)
{
    u32 object_184_wrapped = wrapped_coordinate_with_bias(object_184,
                                                           coordinate_bias);
    u32 current_08_minus_response = object_08 - first_response;
    u32 current_10_plus_response = object_10 + second_response;

    out->selector = selector_table_value;
    out->status = 0U;
    out->transition = 0U;
    out->action = 5U;

    out->packet[0] = 29U;
    out->packet[1] = object_184_wrapped;
    out->packet[2] = scale_bits;
    out->packet[3] = 30U;
    out->packet[4] = object_184_wrapped;
    out->packet[5] = scale_bits;
    out->packet[6] = 10U;
    out->packet[7] = related_10 - current_10_plus_response;
    out->packet[8] = current_08_minus_response - related_08;
    out->packet[9] = 62U;
    out->packet[10] = current_08_minus_response;
    out->packet[11] = related_08;
    out->packet[12] = current_10_plus_response;
    out->packet[13] = related_10;
    out->packet[14] = scale_bits;

    if ((mode_bits & 0x20U) != 0U && control_504dc8 == 1U) {
        out->status = 1U;
        out->transition = 6U;
        out->action = 20U;
    }
}

void recovered_state_geometry_packet_78890(
    uint32_t selector_table_value,
    uint32_t scale_bits,
    uint16_t object_184,
    uint32_t object_08,
    uint32_t object_10,
    uint32_t related_08,
    uint32_t related_10,
    uint32_t first_response,
    uint32_t second_response,
    uint32_t mode_bits,
    uint32_t control_504dc8,
    struct recovered_state_geometry_packet_78890 *out)
{
    recovered_state_geometry_packet_with_bias(
        selector_table_value, scale_bits, object_184, object_08, object_10,
        related_08, related_10, first_response, second_response, mode_bits,
        control_504dc8, 0x5000, out);
}

/* 0x78a30 sibling: table 0x72a20 and the opposite coordinate bias. */
void recovered_state_geometry_packet_78a30(
    uint32_t selector_table_value,
    uint32_t scale_bits,
    uint16_t object_184,
    uint32_t object_08,
    uint32_t object_10,
    uint32_t related_08,
    uint32_t related_10,
    uint32_t first_response,
    uint32_t second_response,
    uint32_t mode_bits,
    uint32_t control_504dc8,
    struct recovered_state_geometry_packet_78890 *out)
{
    recovered_state_geometry_packet_with_bias(
        selector_table_value, scale_bits, object_184, object_08, object_10,
        related_08, related_10, first_response, second_response, mode_bits,
        control_504dc8, -0x5000, out);
}
