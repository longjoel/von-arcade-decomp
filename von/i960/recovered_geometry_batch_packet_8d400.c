/* Pure host contract for the record emitter at i960 0x8d400-0x8d5c0.
 *
 * The original routine writes the FIFO and geometry command window directly.
 * This helper deliberately only describes those writes; the device/MMIO side
 * remains owned by the runtime.
 */
#include "recovered_common.h"

struct recovered_geometry_batch_packet_8d400_input {
    recovered_u32 record_word;
    recovered_u32 record_word4;
    recovered_u32 parameter_word;
    recovered_u32 coordinate_2;
    recovered_u32 coordinate_0;
    recovered_u32 coordinate_4;
    recovered_u32 coordinate_6;
    recovered_u32 coordinate_8;
    recovered_u32 readback_word;
    recovered_u32 fifo_read_value;
};

struct recovered_geometry_batch_packet_8d400_plan {
    recovered_u32 fifo_word[13];
    recovered_u32 fifo_count;
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 window_word[4];
    recovered_u32 window_address[4];
    recovered_u32 completion_word;
    recovered_u32 readback_address;
    recovered_u32 fifo_read_address;
    recovered_u32 fifo_read_value;
    recovered_u32 publication_address;
    recovered_u32 publication_value;
};

void recovered_geometry_batch_packet_8d400(
    const struct recovered_geometry_batch_packet_8d400_input *input,
    struct recovered_geometry_batch_packet_8d400_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 47U; /* 31 + 16 */
    plan->fifo_word[2] = input->coordinate_4 & 0xffffU;
    plan->fifo_word[3] = input->coordinate_6 & 0xffffU;
    plan->fifo_word[4] = input->coordinate_8 & 0xffffU;
    plan->fifo_word[5] = 22U;
    plan->fifo_word[6] = input->coordinate_2 & 0xffffU;
    plan->fifo_word[7] = 21U;
    plan->fifo_word[8] = input->coordinate_0 & 0xffffU;
    plan->fifo_word[9] = 20U;
    plan->fifo_word[10] = input->parameter_word & 0xffffU;
    plan->fifo_word[11] = 58U;
    plan->fifo_word[12] = input->readback_word;
    plan->fifo_count = 13U;

    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->window_address[0] = 0x00804000U;
    plan->window_address[1] = 0x00804004U;
    plan->window_address[2] = 0x00804008U;
    plan->window_address[3] = 0x0080400cU;
    plan->window_word[0] = input->record_word;
    plan->window_word[1] = input->record_word4;
    plan->window_word[2] = input->coordinate_6 & 0xffffU;
    plan->window_word[3] = 0U;
    plan->completion_word = 6U;
    plan->fifo_read_address = 0x00884000U;
    plan->fifo_read_value = input->fifo_read_value;
    plan->readback_address = 0x00802008U;
    plan->publication_address = 0x00801008U;
    plan->publication_value = input->readback_word + 0x34U;
}
