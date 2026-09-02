/* Plan recovered from i960 0x20a20. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_strip_segment {
    u32 repetitions;
    u32 first_value;
    u32 second_value;
    u32 third_value;
};

struct recovered_text_strip_plan {
    u32 destination;
    u32 amount;
    struct recovered_text_strip_segment segment[3];
};

void recovered_text_strip_plan(u32 input, u32 width, u32 scale,
                               u32 first_value, u32 second_value,
                               u32 third_value, u32 row, u32 fill_value,
                               struct recovered_text_strip_plan *plan)
{
    u32 product = input * scale;
    u32 amount = product < width ? product : width;
    u32 empty = (width - amount) >> 1;

    plan->destination = 0x0100c000U + (row << 6);
    plan->amount = amount;
    plan->segment[0] = (struct recovered_text_strip_segment){empty, fill_value,
                                                              fill_value, fill_value};
    plan->segment[1] = (struct recovered_text_strip_segment){amount, first_value,
                                                              second_value, third_value};
    plan->segment[2] = (struct recovered_text_strip_segment){empty, fill_value,
                                                              fill_value, fill_value};
}
