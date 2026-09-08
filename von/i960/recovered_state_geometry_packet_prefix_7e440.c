/* Geometry packet prefix recovered from i960 0x7e440-0x7e514. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_packet_prefix_7e440_plan {
    u32 command[8];
    u32 lane[8];
    u32 payload[8];
};

static u32 lane_add(int16_t sample, int32_t delta)
{
    return (u32)((uint32_t)((int32_t)sample + delta) & 0xffffU);
}

static u32 lane_add_register(int16_t sample, u32 delta)
{
    return ((u32)(int32_t)sample + delta) & 0xffffU;
}

static u32 lane_sub_register(int16_t sample, u32 delta)
{
    return ((u32)(int32_t)sample - delta) & 0xffffU;
}

/*
 * The two product arguments are intentionally supplied as raw i960 real
 * results. They are produced by mulr at 0x7e418/0x7e41c; this boundary
 * records the FIFO protocol without reinterpreting the target's real format.
 */
void recovered_state_geometry_packet_prefix_7e440(
    int16_t descriptor_sample,
    u32 coordinate_product_r4, u32 coordinate_product_r9, u32 r10,
    struct recovered_state_geometry_packet_prefix_7e440_plan *plan)
{
    const u32 plus_three_pages = 3U << 13;

    plan->command[0] = 29U;
    plan->lane[0] = lane_add(descriptor_sample, (int32_t)plus_three_pages);
    plan->payload[0] = coordinate_product_r4;

    plan->command[1] = 30U;
    plan->lane[1] = lane_add(descriptor_sample, (int32_t)plus_three_pages);
    plan->payload[1] = coordinate_product_r4;

    plan->command[2] = 29U;
    plan->lane[2] = lane_add(descriptor_sample, -0x6000);
    plan->payload[2] = coordinate_product_r4;

    plan->command[3] = 30U;
    /* g1 retains the original sample; g4 retains sample + 3<<13. */
    plan->lane[3] = ((u32)(int32_t)descriptor_sample + plan->lane[0]) & 0xffffU;
    plan->payload[3] = coordinate_product_r4;

    plan->command[4] = 29U;
    plan->lane[4] = lane_sub_register(descriptor_sample, r10);
    plan->payload[4] = coordinate_product_r9;

    plan->command[5] = 30U;
    plan->lane[5] = lane_sub_register(descriptor_sample, r10);
    plan->payload[5] = coordinate_product_r9;

    plan->command[6] = 29U;
    plan->lane[6] = lane_add_register(descriptor_sample, r10);
    plan->payload[6] = coordinate_product_r9;

    plan->command[7] = 30U;
    plan->lane[7] = lane_add_register(descriptor_sample, r10);
    plan->payload[7] = coordinate_product_r9;
}
