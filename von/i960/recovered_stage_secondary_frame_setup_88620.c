/* Secondary frame setup recovered from i960 0x88620-0x88680. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_frame_setup_88620 {
    u32 incoming_counter;
    u32 mode_value;
    u32 g14_value;
    u32 setup_call;
    u32 setup_argument;
    u32 setup_seed;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 published_byte_address;
    u32 published_byte_value;
    u32 next_counter;
    u32 counter_limit;
    u32 dispatch_table_address;
    u32 dispatch_boundary;
    u32 dispatch_target;
    u32 dispatch_buffer;
    u32 dispatch_helper;
};

struct recovered_stage_secondary_frame_setup_88620
recovered_stage_secondary_frame_setup_88620(u32 incoming_counter,
                                            u32 mode_value,
                                            u32 g14_value)
{
    struct recovered_stage_secondary_frame_setup_88620 out;

    out.incoming_counter = incoming_counter;
    out.mode_value = mode_value;
    out.g14_value = g14_value;
    out.setup_call = 0x000295d0U;
    out.setup_argument = 0xd000U;
    out.setup_seed = 0U;
    out.fifo_address = 0x00884000U;
    out.fifo_word_count = 2U;
    out.published_byte_address = 0x00503c7aU;
    out.published_byte_value = g14_value & 0xffU;
    out.next_counter = incoming_counter + 1U;
    out.counter_limit = 0xb4U;
    if (out.next_counter > out.counter_limit)
        out.next_counter = out.counter_limit;
    out.dispatch_table_address = 0x00088690U;
    out.dispatch_boundary = 15U;
    out.dispatch_target = 0x00088780U;
    out.dispatch_buffer = 0x00503ad0U;
    out.dispatch_helper = 0x0008a890U;
    if (mode_value >= out.dispatch_boundary) {
        switch (mode_value) {
        case 15U:
            out.dispatch_target = 0x00088770U;
            out.dispatch_buffer = 0x00503ad0U;
            out.dispatch_helper = 0x0008ca80U;
            break;
        default:
            out.dispatch_target = 0x00088780U;
            break;
        }
    } else {
        switch (mode_value) {
        case 1U:
            out.dispatch_target = 0x000886d0U;
            out.dispatch_buffer = 0x005040d0U;
            break;
        case 4U:
            out.dispatch_target = 0x000886e0U;
            out.dispatch_buffer = 0x005040d0U;
            out.dispatch_helper = 0x00088bd0U;
            break;
        case 5U:
            out.dispatch_target = 0x000886f0U;
            out.dispatch_helper = 0x00088bd0U;
            break;
        case 6U:
            out.dispatch_target = 0x00088700U;
            out.dispatch_buffer = 0x005040d0U;
            out.dispatch_helper = 0x00089b30U;
            break;
        case 7U:
            out.dispatch_target = 0x00088710U;
            out.dispatch_helper = 0x00089b30U;
            break;
        case 8U:
            out.dispatch_target = 0x00088720U;
            out.dispatch_buffer = 0x005040d0U;
            out.dispatch_helper = 0x0008b620U;
            break;
        case 9U:
            out.dispatch_target = 0x00088730U;
            out.dispatch_helper = 0x0008b620U;
            break;
        case 10U:
            out.dispatch_target = 0x00088740U;
            out.dispatch_buffer = 0x005040d0U;
            out.dispatch_helper = 0x0008bfd0U;
            break;
        case 11U:
            out.dispatch_target = 0x00088750U;
            out.dispatch_helper = 0x0008bfd0U;
            break;
        case 14U:
            out.dispatch_target = 0x00088760U;
            out.dispatch_buffer = 0x005040d0U;
            out.dispatch_helper = 0x0008ca80U;
            break;
        default:
            break;
        }
    }
    return out;
}
