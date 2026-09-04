/*
 * Pure argument preparation from original vonj 0x76240-0x76340.
 *
 * The routine loads a signed 16-bit object coordinate, forms the two
 * 16-bit-wrapped +/-0x6000 offsets, and also retains the wrapped center
 * coordinate for later FIFO packets.  FIFO/MMIO responses and the FPU
 * transform are deliberately outside this helper.
 */
#include <stdint.h>

struct recovered_geometry_fifo_argument_plan_76240 {
    uint32_t plus_6000;
    uint32_t minus_6000;
    uint32_t center;
};

struct recovered_geometry_fifo_argument_plan_76240
recovered_geometry_fifo_argument_plan_76240(uint16_t raw_coordinate)
{
    int32_t coordinate = (int32_t)(int16_t)raw_coordinate;
    struct recovered_geometry_fifo_argument_plan_76240 plan;

    plan.plus_6000 = (uint32_t)(coordinate + 0x6000) & 0xffffU;
    plan.minus_6000 = (uint32_t)(coordinate - 0x6000) & 0xffffU;
    plan.center = (uint32_t)coordinate & 0xffffU;
    return plan;
}
