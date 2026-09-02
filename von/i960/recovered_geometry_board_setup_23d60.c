/* Deterministic setup prefix recovered from i960 0x23d60-0x23ee8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_board_setup_plan {
    u32 control_address;
    u32 control_value;
    u32 secondary_control_address[2];
    u32 secondary_control_value;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word[20];
    u32 derived_word;
    u32 board_readback_address;
    u32 published_pointer_address;
    u32 published_pointer_offset;
    u32 fixed_pointer_bias;
};

void recovered_geometry_board_setup_prefix_plan(
    u32 derived_word, u32 board_readback_address,
    struct recovered_geometry_board_setup_plan *plan)
{
    plan->control_address = 0x00800090U;
    plan->control_value = 0x00000909U;
    plan->secondary_control_address[0] = 0x00804000U;
    plan->secondary_control_address[1] = 0x00804004U;
    plan->secondary_control_value = 0x44160000U;
    plan->fifo_address = 0x00884000U;
    plan->fifo_word_count = 20U;

    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 16U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = 0xbd5a740eU;
    plan->fifo_word[4] = 0x3e8f5c29U;
    plan->fifo_word[5] = 0x3f800000U;

    plan->fifo_word[6] = 19U;
    plan->fifo_word[7] = derived_word;
    plan->fifo_word[8] = 0x3ada740eU;
    plan->fifo_word[9] = 0x3ada740eU;
    plan->fifo_word[10] = 0x3f800000U;
    plan->fifo_word[11] = 5U;

    plan->fifo_word[12] = 19U;
    plan->fifo_word[13] = derived_word;
    plan->fifo_word[14] = 0x41100000U;
    plan->fifo_word[15] = 0x3f800000U;
    plan->fifo_word[16] = 18U;
    plan->fifo_word[17] = 0U;
    plan->fifo_word[18] = 0U;
    plan->fifo_word[19] = 58U;

    plan->derived_word = derived_word;
    plan->board_readback_address = board_readback_address;
    plan->published_pointer_address = 0x00801008U;
    plan->published_pointer_offset = 0x34U;
    plan->fixed_pointer_bias = 0x34U;
}
