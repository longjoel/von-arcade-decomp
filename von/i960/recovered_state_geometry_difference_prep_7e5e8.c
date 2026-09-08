/* Geometry response/difference preparation recovered from i960 0x7e5e8-0x7e660. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_difference_prep_7e5e8_plan {
    u32 frame_plus_60;
    u32 g1;
    u32 g2;
    u32 g3;
    u32 g5;
    u32 g6;
    u32 g7;
    u32 g8;
    u32 r4;
    u32 r5;
    u32 r7;
    u32 r8;
    u32 r9;
    u32 r10;
    u32 r11;
    u32 r12;
    u32 r13;
    u32 r15;
    u32 g13;
    u32 command10_payload;
};

/* i960 subr source,destination,result is destination - source. */
static u32 subr(u32 source, u32 destination)
{
    return destination - source;
}

void recovered_state_geometry_difference_prep_7e5e8(
    u32 fifo_response_g4, u32 fifo_response_g5, u32 fifo_response_g13,
    u32 fifo_response_r4, u32 fifo_response_g2, u32 fifo_response_g1,
    u32 object_plus_8, u32 object_plus_10, u32 descriptor_field_10,
    u32 descriptor_field_18,
    struct recovered_state_geometry_difference_prep_7e5e8_plan *plan)
{
    u32 g1 = fifo_response_g1;
    u32 g2 = fifo_response_g2;
    u32 g3 = descriptor_field_10;
    u32 g4 = fifo_response_g4;
    u32 g5;
    u32 g6 = object_plus_10;
    u32 g7 = object_plus_8;
    u32 g8;
    u32 r4;
    u32 g13 = fifo_response_g13 + descriptor_field_18;

    /* 0x7e5f8-0x7e624: first response/object differences. */
    g5 = subr(fifo_response_g5, g3);
    g1 += g2;
    g8 = subr(descriptor_field_10, descriptor_field_10);
    /* r6 is the same descriptor +0x10 value loaded at 0x7e480. */
    r4 = subr(fifo_response_r4, descriptor_field_10);

    plan->r11 = subr(g13, g2);
    plan->r10 = descriptor_field_18;
    plan->r15 = subr(g3, g5);
    plan->r9 = subr(g2, g1);
    plan->frame_plus_60 = g8;

    /* 0x7e63c-0x7e660: post-command-10 difference preparation. */
    plan->r12 = subr(descriptor_field_10, g7);
    g4 += g13;
    plan->command10_payload = g4;
    plan->r7 = subr(g13, g6);
    g3 = subr(g7, g3);
    g2 = subr(fifo_response_g2, g6);
    plan->r13 = subr(g5, g7);
    plan->r5 = subr(g1, g6);
    g7 = subr(r4, g7);
    g1 = subr(g1, g4);
    g6 = subr(g4, g6);
    g13 = subr(g4, g13);
    plan->r10 = subr(object_plus_10, descriptor_field_18);
    plan->r8 = subr(descriptor_field_10, object_plus_8);

    plan->g1 = g1;
    plan->g2 = g2;
    plan->g3 = g3;
    plan->g5 = g5;
    plan->g6 = g6;
    plan->g7 = g7;
    plan->g8 = plan->frame_plus_60;
    plan->r4 = r4;
    plan->g13 = g13;
}
