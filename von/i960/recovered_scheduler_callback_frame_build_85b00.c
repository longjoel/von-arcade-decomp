/* Callback frame construction and six-value rank scan recovered from
 * i960 0x85b00-0x85bf8. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_frame_build_85b00 {
    s32 frame[6];
    s32 scaled_r7;
    s32 scaled_r5;
    s32 scaled_g7;
    s32 frame_slot_40;
    s32 frame_slot_44;
    s32 frame_slot_48;
    s32 frame_slot_4c;
    s32 frame_slot_50;
    s32 frame_slot_54;
    s32 lowest_value;
    s32 third_value;
    u32 lowest_index;
    u32 selected_504e48;
    u32 return_stub;
};

static s32 div3(s32 value)
{
    /* The source operands are positive counters in the observed path. */
    return value / 3;
}

struct recovered_scheduler_callback_frame_build_85b00
recovered_scheduler_callback_frame_build_85b00(
    const s32 accumulator_words[6])
{
    struct recovered_scheduler_callback_frame_build_85b00 out;
    s32 second_value = 0;
    s32 third_value = 0;
    s32 lowest_value = 0;
    u32 lowest_index = 6U;
    u32 index;

    out.scaled_r7 = div3(accumulator_words[3] * 5);
    out.scaled_r5 = div3(accumulator_words[1] * 5);
    out.scaled_g7 = div3(accumulator_words[5] * 5);
    out.frame_slot_40 = accumulator_words[0];
    out.frame_slot_44 = out.scaled_r5;
    out.frame_slot_48 = accumulator_words[2] << 1;
    out.frame_slot_4c = (accumulator_words[4] * 5) >> 2;
    out.frame_slot_50 = out.scaled_r7;
    out.frame_slot_54 = out.scaled_g7;

    /* The rank loop reads the six values written at fp+0x40, not the raw
     * accumulator array: [r4, g2, 2*r6, 5*g6/4, g1, g0]. */
    out.frame[0] = out.frame_slot_40;
    out.frame[1] = out.frame_slot_44;
    out.frame[2] = out.frame_slot_48;
    out.frame[3] = out.frame_slot_4c;
    out.frame[4] = out.frame_slot_50;
    out.frame[5] = out.frame_slot_54;

    /* 0x85b78-0x85bd0 keeps the three smallest signed frame values. */
    for (index = 0U; index < 6U; ++index) {
        s32 value = out.frame[index];

        if (lowest_value <= value) {
            if (second_value <= value)
                continue;
            third_value = second_value;
            second_value = value;
        } else {
            third_value = second_value;
            second_value = lowest_value;
            lowest_value = value;
            lowest_index = index;
        }
    }

    out.lowest_value = lowest_value;
    out.third_value = third_value;
    out.lowest_index = lowest_index;
    out.selected_504e48 = (third_value - lowest_value > 0x1f3)
        ? 6U : lowest_index;
    out.return_stub = 0x00085becU;
    return out;
}
