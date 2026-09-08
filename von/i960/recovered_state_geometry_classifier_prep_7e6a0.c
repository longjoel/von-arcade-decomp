/* Geometry classifier argument preparation recovered from 0x7e6a0-0x7e6d0. */
#include <stdint.h>

typedef uint32_t u32;

extern u32 recovered_signed_band(u32 raw);

struct recovered_state_geometry_classifier_prep_7e6a0_plan {
    u32 object_response_delta;
    u32 classifier_g0;
    u32 classifier_g1;
    u32 classifier_g2;
    u32 classifier_g6;
    u32 classifier_r5;
    u32 classifier_r6;
    u32 classifier_r7;
    u32 classifier_r8;
    u32 classifier_target;
    u32 classifier_band;
};

/* i960 subr source,destination,result is destination - source. */
static u32 subr(u32 source, u32 destination)
{
    return destination - source;
}

/*
 * The mulr outputs are supplied as raw registers. The preceding sequence has
 * already produced product_r7/product_r11/product_g2/product_r9/product_g1/
 * product_g13/product_g6/product_r5; this boundary only models the exact
 * integer delta and subr combinations immediately before bal 0x73508.
 */
void recovered_state_geometry_classifier_prep_7e6a0(
    u32 fifo_response_g4, uint16_t object_184,
    u32 product_r7, u32 product_r11, u32 product_g2, u32 product_r9,
    u32 product_g1, u32 product_g13, u32 product_g6, u32 product_r5,
    struct recovered_state_geometry_classifier_prep_7e6a0_plan *plan)
{
    const u32 object_value = (u32)(int32_t)(int16_t)object_184;
    const u32 delta = fifo_response_g4 - object_value;
    const u32 signed_delta = (u32)(int32_t)(int16_t)(uint16_t)delta;

    plan->object_response_delta = signed_delta;
    plan->classifier_g0 = signed_delta;
    plan->classifier_g1 = product_g1;
    plan->classifier_g2 = product_g2;
    plan->classifier_g6 = product_g6;
    plan->classifier_r5 = subr(product_g1, product_r5);
    plan->classifier_r6 = subr(product_r9, product_g2);
    plan->classifier_r7 = subr(product_r11, product_r7);
    plan->classifier_r8 = subr(product_g13, product_g6);
    plan->classifier_target = 0x00073508U;
    plan->classifier_band = recovered_signed_band(signed_delta);
}
