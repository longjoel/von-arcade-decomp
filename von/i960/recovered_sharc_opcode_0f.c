/* Semantic model of the SHARC opcode-0x0f signed angle service. */

#include <stdint.h>

typedef unsigned int u32;

float recovered_sharc_helper_20d68_candidate(float first, float second);

void recovered_sharc_opcode_0f_angle(const u32 input[4], u32 output[1])
{
    union { u32 bits; float value; } a, b, c, d;
    a.bits = input[0];
    b.bits = input[1];
    c.bits = input[2];
    d.bits = input[3];
    /* The handler forms F1=(a-c), F0=(b-d), then helper 0x20d68(F0,F1). */
    float x = a.value - c.value;
    float y = b.value - d.value;
    /* The ROM's negative Y-axis endpoint is one FIX unit below the result
       obtained by rescaling its rounded -pi/2 helper value. */
    if (x == 0.0f && y < 0.0f) {
        output[0] = 0xffffc000U;
        return;
    }
    /* The handler passes F0 (the Y difference) as the helper's first
       argument and F1 (the X difference) as its second argument. */
    float angle = recovered_sharc_helper_20d68_candidate(y, x);
    float scaled = angle * 10430.0595703125f; /* 0x4622f83d */
    output[0] = (u32)(int32_t)scaled;
}
