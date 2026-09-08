/* Packet-31 and signed gate recovered from i960 0x7e6d4-0x7e788. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_packet31_gate_7e6d4_plan {
    u32 packet[5];
    u32 fifo_response_r4;
    u32 first_three_positive;
    u32 fourth_nonzero;
    u32 enters_7e788;
    u32 continues_7e778;
    u32 packet_target;
    u32 continue_target;
};

void recovered_state_geometry_packet31_gate_7e6d4(
    u32 descriptor_field_10, u32 related_field_08, u32 descriptor_field_18,
    u32 related_field_10, u32 fifo_response_r4,
    int32_t product_r7, int32_t product_r6, int32_t product_r5,
    int32_t product_r8,
    struct recovered_state_geometry_packet31_gate_7e6d4_plan *plan)
{
    const u32 first_three_positive = product_r7 > 0 && product_r6 > 0 &&
                                    product_r5 > 0;
    const u32 fourth_nonzero = product_r8 != 0;

    plan->packet[0] = 31U;
    plan->packet[1] = descriptor_field_10;
    plan->packet[2] = related_field_08;
    plan->packet[3] = descriptor_field_18;
    plan->packet[4] = related_field_10;
    plan->fifo_response_r4 = fifo_response_r4;
    plan->first_three_positive = first_three_positive;
    plan->fourth_nonzero = fourth_nonzero;
    plan->enters_7e788 = first_three_positive && fourth_nonzero;
    plan->continues_7e778 = plan->enters_7e788 ? 0U : 1U;
    plan->packet_target = 0x000884000U;
    plan->continue_target = plan->enters_7e788 ? 0x0007e788U : 0x0007e778U;
}
